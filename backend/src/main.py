"""
The Sovereign Council - Main Application

A privacy-first local LLM council for deliberative AI assistance.
Your deliberations belong to you.
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from .config import load_config, SovereignCouncilConfig
from .council import CouncilOrchestrator, Deliberation
from .gateway import InferenceGateway, GatewayError
from .privacy import verify_privacy_mode, PrivacyViolation, PrivacyVerification
from .persistence import (
    DeliberationStore,
    PersistenceError,
    DecryptionError,
    SecureDeletionError,
)

# Configure logging (never log query content)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sovereign_council")


# Global state
_config: SovereignCouncilConfig | None = None
_gateway: InferenceGateway | None = None
_privacy_verification: PrivacyVerification | None = None
_store: DeliberationStore | None = None

# In-memory cache for current session deliberations (ephemeral by default)
_session_deliberations: dict[str, Deliberation] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _config, _gateway, _privacy_verification, _store

    # Load configuration
    logger.info("Loading configuration...")
    config_path_str = os.getenv("SOVEREIGN_COUNCIL_CONFIG")
    config_path = Path(config_path_str) if config_path_str else None
    _config = load_config(config_path)

    # Initialize deliberation store
    # Use environment variable if set, otherwise fall back to calculated path
    data_dir = os.getenv("SOVEREIGN_COUNCIL_DATA_DIR")
    if data_dir:
        storage_dir = Path(data_dir) / "deliberations"
    else:
        # Fallback: two parents up from src/main.py = /app, then /app/data
        storage_dir = Path(__file__).parent.parent / "data" / "deliberations"
    _store = DeliberationStore(storage_dir)
    logger.info(f"Deliberation store initialized at {storage_dir}")
    logger.info(f"Privacy mode: {_config.privacy_mode.value}")

    # Verify privacy mode
    logger.info("Verifying privacy mode...")
    try:
        _privacy_verification = verify_privacy_mode(_config.privacy_mode)
        logger.info(_privacy_verification.message)
        for warning in _privacy_verification.warnings:
            logger.warning(warning)
    except PrivacyViolation as e:
        logger.error(f"Privacy violation: {e}")
        raise

    # Initialize gateway
    logger.info(f"Connecting to inference gateway at {_config.gateway.url}...")
    _gateway = InferenceGateway(_config.gateway)
    await _gateway.__aenter__()

    # Health check
    health = await _gateway.health_check()
    if health.healthy:
        logger.info(f"Gateway healthy. Available models: {health.available_models}")
    else:
        logger.warning(f"Gateway health check failed: {health.message}")

    # Warmup models if configured
    if _config.gateway.warmup:
        logger.info("Warming up council models...")
        for member in _config.council.members:
            success = await _gateway.warmup(member.model)
            if success:
                logger.info(f"  {member.model}: ready")
            else:
                logger.warning(f"  {member.model}: warmup failed")

    logger.info("Sovereign Council initialized. Your deliberations belong to you.")

    yield

    # Cleanup
    if _gateway:
        await _gateway.__aexit__(None, None, None)
    logger.info("Sovereign Council shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="The Sovereign Council",
    description="A privacy-first local LLM council for deliberative AI assistance",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware (for local frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function for SSE formatting
def sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event message."""
    import json
    message = {"type": event_type, **data}
    return f"data: {json.dumps(message)}\n\n"


# Request/Response models
class DeliberationRequest(BaseModel):
    """Request to deliberate on a question."""

    question: str


class ConfidenceResponse(BaseModel):
    """Confidence assessment for synthesis."""

    overall: float
    consensus_strength: float
    dissent_strength: float
    reasoning: str


class DeliberationResponse(BaseModel):
    """Response from deliberation."""

    id: str
    question: str
    synthesis: dict  # Changed from str to dict to match frontend expectations
    confidence: ConfidenceResponse | None = None
    perspectives: list[dict]
    disagreements: list[dict]
    minority_reports: list[dict]
    timestamp: str  # ISO 8601 format timestamp
    session_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    privacy_mode: str
    gateway_healthy: bool
    available_models: list[str]
    consent_banner: str


class ConsentBannerResponse(BaseModel):
    """Consent banner information."""

    text: str
    dismissable: bool


# Persistence request/response models
class SaveDeliberationRequest(BaseModel):
    """Request to save a deliberation."""

    deliberation_id: str
    passphrase: str  # User-provided encryption passphrase


class SaveDeliberationResponse(BaseModel):
    """Response after saving a deliberation."""

    id: str
    saved: bool
    message: str


class LoadDeliberationRequest(BaseModel):
    """Request to load a deliberation."""

    deliberation_id: str
    passphrase: str


class ForgetDeliberationRequest(BaseModel):
    """Request to securely delete a deliberation."""

    deliberation_id: str


class ListDeliberationsResponse(BaseModel):
    """Response listing saved deliberation IDs."""

    deliberation_ids: list[str]
    count: int


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health and privacy status."""
    if not _gateway or not _config:
        raise HTTPException(status_code=503, detail="System not initialized")

    health = await _gateway.health_check()

    return HealthResponse(
        status="healthy" if health.healthy else "degraded",
        privacy_mode=_config.privacy_mode.value,
        gateway_healthy=health.healthy,
        available_models=health.available_models,
        consent_banner=_config.consent_banner.text,
    )


@app.get("/consent-banner", response_model=ConsentBannerResponse)
async def get_consent_banner():
    """Get the consent banner that must be shown to users."""
    if not _config:
        raise HTTPException(status_code=503, detail="System not initialized")

    return ConsentBannerResponse(
        text=_config.consent_banner.text,
        dismissable=_config.consent_banner.user_dismissable,
    )


@app.post("/deliberate", response_model=DeliberationResponse)
async def deliberate(request: DeliberationRequest):
    """
    Submit a question for council deliberation.

    The question is processed entirely locally.
    Nothing leaves your machine.
    """
    if not _gateway or not _config:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Log that a deliberation is occurring (but not the content)
    logger.info("Deliberation requested")

    try:
        # Check gateway health before attempting deliberation
        if _gateway:
            gateway_health = await _gateway.health_check()
            if not gateway_health.healthy:
                raise HTTPException(
                    status_code=503,
                    detail=(
                        f"Inference gateway is unavailable: {gateway_health.message}. "
                        f"Please ensure Ollama is running at {_config.gateway.url} "
                        f"and the required models are pulled."
                    )
                )

        orchestrator = CouncilOrchestrator(
            gateway=_gateway,
            config=_config.council,
            degradation=_config.degradation,
        )

        deliberation = await orchestrator.deliberate(request.question)

        # Cache in session for potential saving (ephemeral by default)
        _session_deliberations[deliberation.id] = deliberation

        logger.info(f"Deliberation complete: {deliberation.id}")

        # Build confidence response if available
        confidence = None
        if deliberation.synthesis.confidence:
            confidence = ConfidenceResponse(
                overall=deliberation.synthesis.confidence.overall,
                consensus_strength=deliberation.synthesis.confidence.consensus_strength,
                dissent_strength=deliberation.synthesis.confidence.dissent_strength,
                reasoning=deliberation.synthesis.confidence.reasoning,
            )

        # Build disagreements with severity if available
        disagreement_list = []
        for d in deliberation.disagreements:
            disagreement_dict = {
                "topic": d.topic,
                "description": d.description,
                "positions": d.positions,
            }
            # Check if this is an AnalyzedDisagreement with severity
            if hasattr(d, "severity"):
                disagreement_dict["severity"] = d.severity.value if hasattr(d.severity, "value") else str(d.severity)
            if hasattr(d, "implications"):
                disagreement_dict["implications"] = d.implications
            disagreement_list.append(disagreement_dict)

        return DeliberationResponse(
            id=deliberation.id,
            question=deliberation.question,
            synthesis={
                "content": deliberation.synthesis.content,
                "consensus_points": deliberation.synthesis.consensus_points,
                "divisions": deliberation.synthesis.divisions,
                "unique_insights": deliberation.synthesis.unique_insights,
                "confidence": confidence.dict() if confidence else None,
            },
            confidence=None,  # Deprecated - confidence now inside synthesis
            perspectives=[
                {
                    "member_id": p.member_id,
                    "model": p.model,
                    "character": p.character,
                    "content": p.content,
                    "timestamp": p.timestamp.isoformat(),
                }
                for p in deliberation.perspectives
            ],
            disagreements=disagreement_list,
            minority_reports=[
                {
                    "member_id": mr.member_id,
                    "position": mr.position,
                    "rationale": mr.rationale,
                }
                for mr in deliberation.minority_reports
            ],
            timestamp=deliberation.timestamp.isoformat(),
            session_id=deliberation.session_id,
        )

    except ValueError as e:
        error_msg = str(e)

        # Provide more helpful message if it's about insufficient members
        if "Insufficient council members" in error_msg:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"{error_msg} This typically means the inference gateway "
                    f"(Ollama) is not responding. Please check:\n"
                    f"1. Ollama is running at {_config.gateway.url}\n"
                    f"2. Required models are pulled: {', '.join([m.model for m in _config.council.members])}\n"
                    f"3. Network connectivity to the gateway"
                )
            )
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except GatewayError as e:
        logger.error(f"Gateway error during deliberation: {e}")
        raise HTTPException(status_code=502, detail=f"Inference gateway error: {e}")


@app.get("/deliberate/stream")
async def deliberate_stream(question: str):
    """
    Submit a question for council deliberation with real-time status updates via SSE.

    The question is processed entirely locally.
    Nothing leaves your machine.

    Returns Server-Sent Events with three message types:
    - {"type": "status", "message": "progress text"}
    - {"type": "complete", "deliberation": {...}}
    - {"type": "error", "message": "error text"}
    """
    if not _gateway or not _config:
        async def error_stream():
            yield sse_event("error", {"message": "System not initialized"})
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    async def event_stream():
        try:
            # Log that a deliberation is occurring (but not the content)
            logger.info("Streaming deliberation requested")

            # Check gateway health before attempting deliberation
            if _gateway:
                gateway_health = await _gateway.health_check()
                if not gateway_health.healthy:
                    yield sse_event("error", {
                        "message": (
                            f"Inference gateway is unavailable: {gateway_health.message}. "
                            f"Please ensure Ollama is running at {_config.gateway.url} "
                            f"and the required models are pulled."
                        )
                    })
                    return

            # Create queue for status messages
            import asyncio
            status_queue = asyncio.Queue()

            # Start deliberation with callback
            orchestrator = CouncilOrchestrator(
                gateway=_gateway,
                config=_config.council,
                degradation=_config.degradation,
            )

            # Lambda captures queue for on_status callback
            deliberation_task = asyncio.create_task(
                orchestrator.deliberate(
                    question,
                    on_status=lambda msg: status_queue.put_nowait(msg)
                )
            )

            try:
                # Stream status updates as they arrive with heartbeat
                last_send_time = time.time()
                heartbeat_interval = 30  # Send heartbeat every 30 seconds

                while not deliberation_task.done():
                    try:
                        status = await asyncio.wait_for(status_queue.get(), timeout=0.1)
                        yield sse_event("status", {"message": status})
                        last_send_time = time.time()
                    except asyncio.TimeoutError:
                        # Send heartbeat if idle for too long to prevent timeout
                        if time.time() - last_send_time > heartbeat_interval:
                            yield ": heartbeat\n\n"  # SSE comment format
                            last_send_time = time.time()
                        continue

                # Drain remaining messages
                while not status_queue.empty():
                    status = status_queue.get_nowait()
                    yield sse_event("status", {"message": status})

                # Get result
                deliberation = await deliberation_task

            except asyncio.CancelledError:
                # Client disconnected - cancel the deliberation task
                logger.info("Client disconnected, cancelling deliberation")
                deliberation_task.cancel()
                try:
                    await deliberation_task
                except asyncio.CancelledError:
                    logger.info("Deliberation task cancelled successfully")
                raise

            # Cache in session (same as POST endpoint)
            _session_deliberations[deliberation.id] = deliberation
            logger.info(f"Streaming deliberation complete: {deliberation.id}")

            # Build confidence response if available
            confidence = None
            if deliberation.synthesis.confidence:
                confidence = {
                    "overall": deliberation.synthesis.confidence.overall,
                    "consensus_strength": deliberation.synthesis.confidence.consensus_strength,
                    "dissent_strength": deliberation.synthesis.confidence.dissent_strength,
                    "reasoning": deliberation.synthesis.confidence.reasoning,
                }

            # Build disagreements with severity if available
            disagreement_list = []
            for d in deliberation.disagreements:
                disagreement_dict = {
                    "topic": d.topic,
                    "description": d.description,
                    "positions": d.positions,
                }
                # Check if this is an AnalyzedDisagreement with severity
                if hasattr(d, "severity"):
                    disagreement_dict["severity"] = d.severity.value if hasattr(d.severity, "value") else str(d.severity)
                if hasattr(d, "implications"):
                    disagreement_dict["implications"] = d.implications
                disagreement_list.append(disagreement_dict)

            # Build deliberation response (matching POST endpoint structure)
            deliberation_response = {
                "id": deliberation.id,
                "question": deliberation.question,
                "synthesis": {
                    "content": deliberation.synthesis.content,
                    "consensus_points": deliberation.synthesis.consensus_points,
                    "divisions": deliberation.synthesis.divisions,
                    "unique_insights": deliberation.synthesis.unique_insights,
                    "confidence": confidence,
                },
                "confidence": None,  # Deprecated - confidence now inside synthesis
                "perspectives": [
                    {
                        "member_id": p.member_id,
                        "model": p.model,
                        "character": p.character,
                        "content": p.content,
                        "timestamp": p.timestamp.isoformat(),
                    }
                    for p in deliberation.perspectives
                ],
                "disagreements": disagreement_list,
                "minority_reports": [
                    {
                        "member_id": mr.member_id,
                        "position": mr.position,
                        "rationale": mr.rationale,
                    }
                    for mr in deliberation.minority_reports
                ],
                "timestamp": deliberation.timestamp.isoformat(),
                "session_id": deliberation.session_id,
            }

            # Send completion event
            yield sse_event("complete", {"deliberation": deliberation_response})

        except ValueError as e:
            error_msg = str(e)
            # Provide more helpful message if it's about insufficient members
            if "Insufficient council members" in error_msg:
                error_msg = (
                    f"{error_msg} This typically means the inference gateway "
                    f"(Ollama) is not responding. Please check:\n"
                    f"1. Ollama is running at {_config.gateway.url}\n"
                    f"2. Required models are pulled: {', '.join([m.model for m in _config.council.members])}\n"
                    f"3. Network connectivity to the gateway"
                )
            yield sse_event("error", {"message": error_msg})

        except GatewayError as e:
            logger.error(f"Gateway error during streaming deliberation: {e}")
            yield sse_event("error", {"message": f"Inference gateway error: {e}"})

        except Exception as e:
            logger.error(f"Unexpected error during streaming deliberation: {e}")
            yield sse_event("error", {"message": f"Unexpected error: {str(e)}"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/models")
async def list_models():
    """List available models on the local gateway."""
    if not _gateway:
        raise HTTPException(status_code=503, detail="System not initialized")

    models = await _gateway.list_models()
    return {"models": models}


@app.get("/privacy/status")
async def privacy_status():
    """Get current privacy mode verification status."""
    if not _privacy_verification or not _config or not _gateway:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Check if Ollama is actually reachable
    gateway_health = await _gateway.health_check()
    ollama_reachable = gateway_health.healthy

    # Determine network status booleans
    network_status_value = _privacy_verification.network_status.value
    external_reachable = network_status_value == "external_possible"
    local_only = network_status_value == "local_only"

    return {
        "mode": {
            "mode": _config.privacy_mode.value.upper(),
            "description": _privacy_verification.message,
        },
        "verified": _privacy_verification.verified,
        "network_status": {
            "external_reachable": external_reachable,
            "ollama_reachable": ollama_reachable,
            "local_only": local_only,
        },
        "message": _privacy_verification.message,
        "warnings": _privacy_verification.warnings,
    }


# Persistence endpoints
@app.post("/deliberations/save", response_model=SaveDeliberationResponse)
async def save_deliberation(request: SaveDeliberationRequest):
    """
    Save a deliberation with encryption.

    The deliberation is encrypted with your passphrase before storage.
    We cannot read your saved deliberations. If you lose your passphrase,
    your data is gone forever. This is a feature, not a bug.
    """
    if not _store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    # Check if deliberation exists in session
    deliberation = _session_deliberations.get(request.deliberation_id)
    if not deliberation:
        raise HTTPException(
            status_code=404,
            detail=f"Deliberation {request.deliberation_id} not found in current session",
        )

    try:
        path = _store.save(deliberation, request.passphrase)
        logger.info(f"Deliberation saved: {request.deliberation_id}")

        return SaveDeliberationResponse(
            id=request.deliberation_id,
            saved=True,
            message="Deliberation encrypted and saved successfully",
        )

    except PersistenceError as e:
        logger.error(f"Failed to save deliberation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deliberations/load", response_model=DeliberationResponse)
async def load_deliberation(request: LoadDeliberationRequest):
    """
    Load and decrypt a saved deliberation.

    Requires the passphrase used when saving. Wrong passphrase = no data.
    """
    if not _store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    try:
        deliberation = _store.load(request.deliberation_id, request.passphrase)

        # Cache in session
        _session_deliberations[deliberation.id] = deliberation

        logger.info(f"Deliberation loaded: {request.deliberation_id}")

        # Build response (same as deliberate endpoint)
        confidence = None
        if deliberation.synthesis.confidence:
            confidence = ConfidenceResponse(
                overall=deliberation.synthesis.confidence.overall,
                consensus_strength=deliberation.synthesis.confidence.consensus_strength,
                dissent_strength=deliberation.synthesis.confidence.dissent_strength,
                reasoning=deliberation.synthesis.confidence.reasoning,
            )

        return DeliberationResponse(
            id=deliberation.id,
            question=deliberation.question,
            synthesis={
                "content": deliberation.synthesis.content,
                "consensus_points": deliberation.synthesis.consensus_points,
                "divisions": deliberation.synthesis.divisions,
                "unique_insights": deliberation.synthesis.unique_insights,
                "confidence": confidence.dict() if confidence else None,
            },
            confidence=None,  # Deprecated - confidence now inside synthesis
            perspectives=[
                {
                    "member_id": p.member_id,
                    "model": p.model,
                    "character": p.character,
                    "content": p.content,
                    "timestamp": p.timestamp.isoformat(),
                }
                for p in deliberation.perspectives
            ],
            disagreements=[
                {
                    "topic": d.topic,
                    "description": d.description,
                    "positions": d.positions,
                }
                for d in deliberation.disagreements
            ],
            minority_reports=[
                {
                    "member_id": mr.member_id,
                    "position": mr.position,
                    "rationale": mr.rationale,
                }
                for mr in deliberation.minority_reports
            ],
            timestamp=deliberation.timestamp.isoformat(),
            session_id=deliberation.session_id,
        )

    except DecryptionError:
        raise HTTPException(
            status_code=401,
            detail="Decryption failed. Wrong passphrase or corrupted data.",
        )
    except PersistenceError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/deliberations/forget")
async def forget_deliberation(request: ForgetDeliberationRequest):
    """
    Securely delete a saved deliberation.

    The right to be forgotten, implemented literally.
    Data is overwritten before deletion.
    """
    if not _store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    try:
        _store.forget(request.deliberation_id)

        # Also remove from session cache if present
        _session_deliberations.pop(request.deliberation_id, None)

        logger.info(f"Deliberation forgotten: {request.deliberation_id}")

        return {
            "id": request.deliberation_id,
            "forgotten": True,
            "message": "Deliberation securely deleted",
        }

    except SecureDeletionError as e:
        logger.error(f"Failed to forget deliberation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/deliberations", response_model=ListDeliberationsResponse)
async def list_deliberations():
    """
    List saved deliberation IDs.

    Note: Only IDs are returned. Content requires passphrase to decrypt.
    """
    if not _store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    ids = _store.list_ids()
    return ListDeliberationsResponse(
        deliberation_ids=ids,
        count=len(ids),
    )


@app.get("/deliberations/{deliberation_id}/exists")
async def deliberation_exists(deliberation_id: str):
    """Check if a saved deliberation exists."""
    if not _store:
        raise HTTPException(status_code=503, detail="Store not initialized")

    exists = _store.exists(deliberation_id)
    return {"id": deliberation_id, "exists": exists}


# Error handlers
@app.exception_handler(PrivacyViolation)
async def privacy_violation_handler(request: Request, exc: PrivacyViolation):
    """Handle privacy violations - these are fatal."""
    logger.error(f"Privacy violation: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "privacy_violation",
            "message": str(exc),
            "detail": "The system cannot operate in the requested privacy mode.",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

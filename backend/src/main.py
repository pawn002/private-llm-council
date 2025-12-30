"""
The Sovereign Council - Main Application

A privacy-first local LLM council for deliberative AI assistance.
Your deliberations belong to you.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    _config = load_config()

    # Initialize deliberation store
    storage_dir = Path(__file__).parent.parent.parent / "data" / "deliberations"
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
    synthesis: str
    confidence: ConfidenceResponse | None = None
    perspectives: list[dict]
    disagreements: list[dict]
    minority_reports: list[dict]


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
            synthesis=deliberation.synthesis.content,
            confidence=confidence,
            perspectives=[
                {
                    "id": p.member_id,
                    "character": p.character,
                    "content": p.content,
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
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GatewayError as e:
        logger.error(f"Gateway error during deliberation: {e}")
        raise HTTPException(status_code=502, detail=f"Inference gateway error: {e}")


@app.get("/models")
async def list_models():
    """List available models on the local gateway."""
    if not _gateway:
        raise HTTPException(status_code=503, detail="System not initialized")

    models = await _gateway.list_models()
    return {"models": models}


@app.get("/privacy-status")
async def privacy_status():
    """Get current privacy mode verification status."""
    if not _privacy_verification or not _config:
        raise HTTPException(status_code=503, detail="System not initialized")

    return {
        "mode": _config.privacy_mode.value,
        "verified": _privacy_verification.verified,
        "network_status": _privacy_verification.network_status.value,
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
            synthesis=deliberation.synthesis.content,
            confidence=confidence,
            perspectives=[
                {
                    "id": p.member_id,
                    "character": p.character,
                    "content": p.content,
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

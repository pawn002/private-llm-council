"""
Inference gateway client for The Sovereign Council.

Connects to local LLM inference servers (Ollama, vLLM, llama.cpp).
All inference happens locally - your queries never leave your machine.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import AsyncIterator, Optional

import httpx

from .config import GatewayConfig, Temperature


class GatewayError(Exception):
    """Error communicating with inference gateway."""

    pass


class ModelUnavailableError(GatewayError):
    """Requested model is not available."""

    pass


@dataclass
class InferenceResponse:
    """Response from the inference gateway."""

    content: str
    model: str
    finish_reason: str | None = None
    usage: dict | None = None


@dataclass
class GatewayHealth:
    """Health status of the inference gateway."""

    healthy: bool
    message: str
    available_models: list[str]


class InferenceGateway:
    """
    Client for local inference gateways.

    Supports Ollama, vLLM, and other OpenAI-compatible APIs.
    All communication stays on localhost.
    """

    def __init__(self, config: GatewayConfig):
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "InferenceGateway":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.config.url.rstrip("/v1"),  # Remove /v1 suffix if present
            timeout=httpx.Timeout(
                timeout=self.config.timeout_seconds,  # 120s default
                connect=10.0,      # Fast connection timeout
                read=1800.0,       # Allow up to 30 minutes for model inference
                write=120.0,       # Reasonable write timeout
                pool=10.0,         # Connection pool timeout
            ),
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=100,
                keepalive_expiry=30.0,  # Keep idle connections for 30s
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not initialized."""
        if self._client is None:
            raise GatewayError("Gateway not initialized. Use 'async with' context manager.")
        return self._client

    async def health_check(self) -> GatewayHealth:
        """
        Check gateway health and available models.

        Returns:
            GatewayHealth with status and available models.
        """
        try:
            # Try Ollama-style tags endpoint first
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return GatewayHealth(
                    healthy=True,
                    message="Gateway healthy",
                    available_models=models,
                )
        except httpx.RequestError:
            pass

        try:
            # Try OpenAI-compatible models endpoint
            response = await self.client.get("/v1/models")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("id", "") for m in data.get("data", [])]
                return GatewayHealth(
                    healthy=True,
                    message="Gateway healthy",
                    available_models=models,
                )
        except httpx.RequestError as e:
            return GatewayHealth(
                healthy=False,
                message=f"Cannot connect to gateway: {e}",
                available_models=[],
            )

        return GatewayHealth(
            healthy=False,
            message="Gateway did not respond to health check",
            available_models=[],
        )

    async def complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> InferenceResponse:
        """
        Generate a completion from a local model.

        Args:
            model: Model identifier (e.g., "llama3.2:8b")
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            InferenceResponse with generated content.

        Raises:
            ModelUnavailableError: If model is not available.
            GatewayError: If gateway communication fails.
        """
        for attempt in range(self.config.retry_attempts):
            try:
                return await self._do_complete(model, messages, temperature, max_tokens)
            except httpx.RequestError as e:
                if attempt == self.config.retry_attempts - 1:
                    raise GatewayError(f"Gateway request failed after {attempt + 1} attempts: {e}")
                await asyncio.sleep(self.config.retry_delay_seconds * (attempt + 1))

        raise GatewayError("Unexpected: exhausted retries without result")

    async def _do_complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int | None,
    ) -> InferenceResponse:
        """Execute a single completion request."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = await self.client.post("/v1/chat/completions", json=payload)

        if response.status_code == 404:
            raise ModelUnavailableError(f"Model '{model}' not found on gateway")

        if response.status_code != 200:
            raise GatewayError(f"Gateway returned status {response.status_code}: {response.text}")

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise GatewayError("Gateway returned no choices")

        choice = choices[0]
        message = choice.get("message", {})

        return InferenceResponse(
            content=message.get("content", ""),
            model=data.get("model", model),
            finish_reason=choice.get("finish_reason"),
            usage=data.get("usage"),
        )

    async def stream_complete(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Stream a completion from a local model.

        Yields content chunks as they're generated.

        Args:
            model: Model identifier
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Content chunks as strings.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with self.client.stream("POST", "/v1/chat/completions", json=payload) as response:
            if response.status_code == 404:
                raise ModelUnavailableError(f"Model '{model}' not found on gateway")

            if response.status_code != 200:
                raise GatewayError(f"Gateway returned status {response.status_code}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json

                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def warmup(self, model: str, prompt: str = "Hello") -> bool:
        """
        Warm up a model with a simple prompt.

        First inference is slow due to model loading. This pre-loads the model.

        Args:
            model: Model to warm up
            prompt: Simple prompt for warmup

        Returns:
            True if warmup successful, False otherwise.
        """
        try:
            await self.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=Temperature.HEALTH_CHECK,
                max_tokens=1,
            )
            return True
        except GatewayError:
            return False

    async def list_models(self) -> list[str]:
        """
        List available models on the gateway.

        Returns:
            List of model identifiers.
        """
        health = await self.health_check()
        return health.available_models

    async def is_busy(self, since: Optional[datetime] = None) -> bool:
        """
        Check if Ollama is currently processing models from other requests.

        Queries the /api/ps endpoint to see if any models are loaded.
        If 'since' timestamp is provided, only considers models that were
        loaded BEFORE that timestamp (i.e., from previous/other requests).

        Args:
            since: Optional timestamp. If provided, only count models loaded
                   before this time as "busy" indicators. Models loaded after
                   this time are assumed to be from the current operation.

        Returns:
            True if models from other requests are loaded, False otherwise.
        """
        try:
            response = await self.client.get("/api/ps")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])

                if not since:
                    # No timestamp filter - any loaded model means busy
                    return len(models) > 0

                # Ollama's default keep-alive is 5 minutes
                # We'll use this to estimate when a model was loaded
                keep_alive = timedelta(minutes=5)

                for model in models:
                    expires_at_str = model.get("expires_at")
                    if not expires_at_str:
                        continue

                    try:
                        # Parse ISO 8601 timestamp
                        expires_at = datetime.fromisoformat(
                            expires_at_str.replace("Z", "+00:00")
                        )

                        # Estimate when model was loaded
                        # loaded_at ≈ expires_at - keep_alive
                        loaded_at = expires_at - keep_alive

                        # If model was loaded before 'since', it's from another request
                        if loaded_at < since:
                            return True

                    except (ValueError, TypeError):
                        # If we can't parse timestamp, be conservative and assume busy
                        continue

                # All models were loaded after 'since' or no valid timestamps
                return False

        except httpx.RequestError:
            # If we can't connect, assume not busy (fail gracefully)
            return False

        return False

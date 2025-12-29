"""
Tests for the inference gateway client.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.gateway import (
    InferenceGateway,
    InferenceResponse,
    GatewayHealth,
    GatewayError,
    ModelUnavailableError,
)
from src.config import GatewayConfig


@pytest.fixture
def gateway_config() -> GatewayConfig:
    """Create a gateway configuration for testing."""
    return GatewayConfig(
        provider="ollama",
        url="http://localhost:11434/v1",
        timeout_seconds=30,
        retry_attempts=2,
        retry_delay_seconds=1,
    )


class TestInferenceGateway:
    """Tests for the InferenceGateway class."""

    @pytest.mark.asyncio
    async def test_context_manager_initializes_client(self, gateway_config: GatewayConfig):
        """Test that context manager properly initializes the client."""
        gateway = InferenceGateway(gateway_config)
        assert gateway._client is None

        async with gateway:
            assert gateway._client is not None

        # Client should be closed after context exit
        # (we can't easily test this without mocking)

    @pytest.mark.asyncio
    async def test_client_property_raises_when_not_initialized(
        self, gateway_config: GatewayConfig
    ):
        """Test that accessing client before initialization raises error."""
        gateway = InferenceGateway(gateway_config)
        with pytest.raises(GatewayError) as exc_info:
            _ = gateway.client
        assert "not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_success(self, gateway_config: GatewayConfig):
        """Test successful health check."""
        gateway = InferenceGateway(gateway_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:8b"},
                {"name": "mistral:7b"},
            ]
        }

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            async with gateway:
                health = await gateway.health_check()

            assert health.healthy is True
            assert "llama3.2:8b" in health.available_models
            assert "mistral:7b" in health.available_models

    @pytest.mark.asyncio
    async def test_health_check_failure(self, gateway_config: GatewayConfig):
        """Test health check failure handling."""
        gateway = InferenceGateway(gateway_config)

        with patch.object(
            httpx.AsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection refused")
            async with gateway:
                health = await gateway.health_check()

            assert health.healthy is False
            assert "Cannot connect" in health.message

    @pytest.mark.asyncio
    async def test_complete_success(self, gateway_config: GatewayConfig):
        """Test successful completion request."""
        gateway = InferenceGateway(gateway_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "Test response"},
                    "finish_reason": "stop",
                }
            ],
            "model": "llama3.2:8b",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response
            async with gateway:
                response = await gateway.complete(
                    model="llama3.2:8b",
                    messages=[{"role": "user", "content": "Hello"}],
                )

            assert response.content == "Test response"
            assert response.model == "llama3.2:8b"
            assert response.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_complete_model_not_found(self, gateway_config: GatewayConfig):
        """Test completion with model not found."""
        gateway = InferenceGateway(gateway_config)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response
            async with gateway:
                with pytest.raises(ModelUnavailableError) as exc_info:
                    await gateway.complete(
                        model="nonexistent:model",
                        messages=[{"role": "user", "content": "Hello"}],
                    )
            assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_complete_retries_on_failure(self, gateway_config: GatewayConfig):
        """Test that completion retries on transient failures."""
        gateway = InferenceGateway(gateway_config)

        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.RequestError("Transient error")
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Success"}, "finish_reason": "stop"}],
                "model": "test",
            }
            return mock_response

        with patch.object(httpx.AsyncClient, "post", side_effect=mock_post):
            async with gateway:
                response = await gateway.complete(
                    model="test",
                    messages=[{"role": "user", "content": "Hello"}],
                )

            assert response.content == "Success"
            assert call_count == 2  # One failure, one success

    @pytest.mark.asyncio
    async def test_warmup_success(self, gateway_config: GatewayConfig):
        """Test successful model warmup."""
        gateway = InferenceGateway(gateway_config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OK"}, "finish_reason": "stop"}],
            "model": "test",
        }

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response
            async with gateway:
                result = await gateway.warmup("test:model")

            assert result is True

    @pytest.mark.asyncio
    async def test_warmup_failure(self, gateway_config: GatewayConfig):
        """Test warmup failure handling."""
        gateway = InferenceGateway(gateway_config)

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection refused")
            async with gateway:
                result = await gateway.warmup("test:model")

            assert result is False


class TestInferenceResponse:
    """Tests for the InferenceResponse dataclass."""

    def test_inference_response_creation(self):
        """Test creating an InferenceResponse."""
        response = InferenceResponse(
            content="Test content",
            model="test:model",
            finish_reason="stop",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )
        assert response.content == "Test content"
        assert response.model == "test:model"
        assert response.finish_reason == "stop"
        assert response.usage["prompt_tokens"] == 10

    def test_inference_response_optional_fields(self):
        """Test InferenceResponse with optional fields."""
        response = InferenceResponse(
            content="Test",
            model="test",
        )
        assert response.finish_reason is None
        assert response.usage is None


class TestGatewayHealth:
    """Tests for the GatewayHealth dataclass."""

    def test_healthy_gateway(self):
        """Test healthy gateway response."""
        health = GatewayHealth(
            healthy=True,
            message="All good",
            available_models=["model1", "model2"],
        )
        assert health.healthy is True
        assert len(health.available_models) == 2

    def test_unhealthy_gateway(self):
        """Test unhealthy gateway response."""
        health = GatewayHealth(
            healthy=False,
            message="Connection refused",
            available_models=[],
        )
        assert health.healthy is False
        assert len(health.available_models) == 0

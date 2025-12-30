"""
Integration tests for The Sovereign Council.

These tests require a running Ollama instance with models pulled.
Skip these tests in CI or when Ollama is not available.

Run with: pytest tests/test_integration.py -v --run-integration
"""

import pytest
import os
import asyncio

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires Ollama)"
    )


@pytest.fixture
def ollama_available():
    """Check if Ollama is available."""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 11434))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture
def skip_if_no_ollama(ollama_available):
    """Skip test if Ollama is not available."""
    if not ollama_available:
        pytest.skip("Ollama not available at localhost:11434")


class TestOllamaIntegration:
    """Integration tests with Ollama."""

    @pytest.mark.asyncio
    async def test_gateway_health_check(self, skip_if_no_ollama):
        """Test health check against real Ollama instance."""
        from src.config import GatewayConfig
        from src.gateway import InferenceGateway

        config = GatewayConfig(
            provider="ollama",
            url="http://localhost:11434/v1",
            timeout_seconds=30,
        )

        async with InferenceGateway(config) as gateway:
            health = await gateway.health_check()

        assert health.healthy is True
        print(f"Available models: {health.available_models}")

    @pytest.mark.asyncio
    async def test_simple_completion(self, skip_if_no_ollama):
        """Test simple completion against real Ollama instance."""
        from src.config import GatewayConfig
        from src.gateway import InferenceGateway

        config = GatewayConfig(
            provider="ollama",
            url="http://localhost:11434/v1",
            timeout_seconds=120,
        )

        async with InferenceGateway(config) as gateway:
            # First check what models are available
            health = await gateway.health_check()
            if not health.available_models:
                pytest.skip("No models available in Ollama")

            # Use the first available model
            model = health.available_models[0]
            print(f"Testing with model: {model}")

            response = await gateway.complete(
                model=model,
                messages=[{"role": "user", "content": "Say 'hello' and nothing else."}],
                temperature=0.0,
                max_tokens=10,
            )

        assert response.content is not None
        assert len(response.content) > 0
        print(f"Response: {response.content}")

    @pytest.mark.asyncio
    async def test_full_deliberation(self, skip_if_no_ollama):
        """Test full deliberation against real Ollama instance."""
        from src.config import (
            GatewayConfig,
            CouncilConfig,
            CouncilMember,
            ChairmanConfig,
            DegradationConfig,
        )
        from src.gateway import InferenceGateway
        from src.council import CouncilOrchestrator

        gateway_config = GatewayConfig(
            provider="ollama",
            url="http://localhost:11434/v1",
            timeout_seconds=120,
        )

        async with InferenceGateway(gateway_config) as gateway:
            # Check available models
            health = await gateway.health_check()
            if len(health.available_models) < 2:
                pytest.skip("Need at least 2 models for council deliberation")

            # Use available models for council
            models = health.available_models[:3]
            print(f"Using models for council: {models}")

            council_config = CouncilConfig(
                members=[
                    CouncilMember(
                        id=f"member_{i}",
                        model=model,
                        character=f"Perspective {i}",
                        temperature=0.7,
                    )
                    for i, model in enumerate(models)
                ],
                chairman=ChairmanConfig(
                    model=models[0],  # Use first model as chairman
                    temperature=0.3,
                    preserve_dissent=True,
                ),
            )

            degradation_config = DegradationConfig(
                silent_fallback=False,
                minimum_council_size=2,
                warn_below_size=3,
            )

            orchestrator = CouncilOrchestrator(
                gateway=gateway,
                config=council_config,
                degradation=degradation_config,
            )

            # Run deliberation
            deliberation = await orchestrator.deliberate(
                "What is 2 + 2? Provide a brief answer.",
                on_status=print,
            )

        assert len(deliberation.perspectives) >= 2
        assert deliberation.synthesis.content is not None
        print(f"\n=== Synthesis ===\n{deliberation.synthesis.content}")


class TestPrivacyModeIntegration:
    """Integration tests for privacy mode verification."""

    def test_current_network_status(self):
        """Test checking current network status."""
        from src.privacy import _check_network_status, NetworkStatus

        status = _check_network_status()
        print(f"Current network status: {status.value}")
        assert status in NetworkStatus

    def test_verify_sanctuary_mode(self):
        """Test verifying sanctuary mode with current network."""
        from src.privacy import verify_privacy_mode, PrivacyViolation
        from src.config import PrivacyMode

        # This may pass or fail depending on network config
        try:
            result = verify_privacy_mode(PrivacyMode.SANCTUARY)
            print(f"Sanctuary mode: {result.message}")
            for warning in result.warnings:
                print(f"Warning: {warning}")
        except PrivacyViolation as e:
            print(f"Privacy violation (expected if external network available): {e}")


# Convenience script to run integration tests
if __name__ == "__main__":
    import subprocess
    import sys

    # Run pytest with integration marker
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            __file__,
            "-v",
            "-s",
            "--tb=short",
        ],
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )
    sys.exit(result.returncode)

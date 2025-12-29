"""
Pytest configuration and fixtures for The Sovereign Council tests.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from src.config import (
    SovereignCouncilConfig,
    CouncilConfig,
    CouncilMember,
    ChairmanConfig,
    GatewayConfig,
    PrivacyMode,
)
from src.gateway import InferenceGateway, InferenceResponse, GatewayHealth


@pytest.fixture
def sample_config() -> SovereignCouncilConfig:
    """Create a sample configuration for testing."""
    return SovereignCouncilConfig(
        privacy_mode=PrivacyMode.SANCTUARY,
        gateway=GatewayConfig(
            provider="ollama",
            url="http://localhost:11434/v1",
            timeout_seconds=60,
            retry_attempts=2,
        ),
        council=CouncilConfig(
            members=[
                CouncilMember(
                    id="phi",
                    model="llama3.2:8b",
                    capability="Strong reasoning",
                    character="Western analytical",
                    temperature=0.7,
                ),
                CouncilMember(
                    id="psi",
                    model="mistral:7b",
                    capability="Good instruction following",
                    character="European regulatory",
                    temperature=0.7,
                ),
                CouncilMember(
                    id="omega",
                    model="qwen2.5:7b",
                    capability="Diverse corpus",
                    character="Eastern philosophical",
                    temperature=0.7,
                ),
            ],
            chairman=ChairmanConfig(
                model="llama3.2:70b",
                capability="Large context",
                role="Synthesizer",
                temperature=0.3,
                preserve_dissent=True,
            ),
        ),
    )


@pytest.fixture
def mock_gateway() -> MagicMock:
    """Create a mock inference gateway."""
    gateway = MagicMock(spec=InferenceGateway)
    gateway.__aenter__ = AsyncMock(return_value=gateway)
    gateway.__aexit__ = AsyncMock(return_value=None)

    # Default health check response
    gateway.health_check = AsyncMock(
        return_value=GatewayHealth(
            healthy=True,
            message="Gateway healthy",
            available_models=["llama3.2:8b", "mistral:7b", "qwen2.5:7b"],
        )
    )

    # Default complete response
    gateway.complete = AsyncMock(
        return_value=InferenceResponse(
            content="This is a test response from the model.",
            model="llama3.2:8b",
            finish_reason="stop",
        )
    )

    gateway.warmup = AsyncMock(return_value=True)
    gateway.list_models = AsyncMock(
        return_value=["llama3.2:8b", "mistral:7b", "qwen2.5:7b"]
    )

    return gateway


@pytest.fixture
def config_yaml_path(tmp_path: Path) -> Path:
    """Create a temporary config file."""
    config_content = """
identity:
  name: "Test Council"
  version: "0.1.0"

privacy:
  mode: "sanctuary"

gateway:
  provider: "ollama"
  url: "http://localhost:11434/v1"
  timeout_seconds: 60

council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
      capability: "Test capability"
      character: "Test character"
      temperature: 0.7
  chairman:
    model: "llama3.2:8b"
    temperature: 0.3

persistence:
  default: "ephemeral"
  save:
    encryption: "required"

degradation:
  minimum_council_size: 2
  warn_below_size: 3
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file

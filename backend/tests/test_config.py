"""
Tests for configuration loading and validation.
"""

import pytest
from pathlib import Path

from src.config import (
    load_config,
    SovereignCouncilConfig,
    PrivacyMode,
    CouncilMember,
)


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_default_config(self):
        """Test loading default configuration when no file exists."""
        config = load_config(Path("/nonexistent/path/config.yaml"))
        assert isinstance(config, SovereignCouncilConfig)
        assert config.privacy_mode == PrivacyMode.SANCTUARY
        assert config.telemetry_enabled is False

    def test_load_config_from_yaml(self, config_yaml_path: Path):
        """Test loading configuration from YAML file."""
        config = load_config(config_yaml_path)
        assert config.privacy_mode == PrivacyMode.SANCTUARY
        assert config.gateway.provider == "ollama"
        assert len(config.council.members) == 1

    def test_telemetry_always_disabled(self, config_yaml_path: Path):
        """Test that telemetry is always disabled regardless of config."""
        # Even if someone tries to enable telemetry in config,
        # it should always be False
        config = load_config(config_yaml_path)
        assert config.telemetry_enabled is False

    def test_silent_fallback_always_disabled(self, config_yaml_path: Path):
        """Test that silent fallback is always disabled."""
        config = load_config(config_yaml_path)
        assert config.degradation.silent_fallback is False


class TestPrivacyModes:
    """Tests for privacy mode configuration."""

    def test_sanctuary_is_default(self):
        """Test that SANCTUARY is the default privacy mode."""
        config = SovereignCouncilConfig()
        assert config.privacy_mode == PrivacyMode.SANCTUARY

    def test_all_privacy_modes_valid(self):
        """Test that all privacy modes are valid enum values."""
        assert PrivacyMode.SOVEREIGN.value == "sovereign"
        assert PrivacyMode.SANCTUARY.value == "sanctuary"
        assert PrivacyMode.CITADEL.value == "citadel"


class TestCouncilConfig:
    """Tests for council configuration."""

    def test_council_member_creation(self):
        """Test creating a council member."""
        member = CouncilMember(
            id="test",
            model="llama3.2:8b",
            capability="Test capability",
            character="Test character",
            temperature=0.7,
        )
        assert member.id == "test"
        assert member.model == "llama3.2:8b"
        assert member.temperature == 0.7

    def test_council_member_defaults(self):
        """Test council member default values."""
        member = CouncilMember(id="test", model="test:latest")
        assert member.capability == ""
        assert member.character == ""
        assert member.temperature == 0.7


class TestPersistenceConfig:
    """Tests for persistence configuration."""

    def test_ephemeral_default(self, sample_config: SovereignCouncilConfig):
        """Test that ephemeral is the default persistence mode."""
        assert sample_config.persistence.default == "ephemeral"

    def test_encryption_required(self, sample_config: SovereignCouncilConfig):
        """Test that encryption is required for saves."""
        assert sample_config.persistence.encryption_required is True


class TestDegradationConfig:
    """Tests for degradation configuration."""

    def test_minimum_council_size(self, sample_config: SovereignCouncilConfig):
        """Test minimum council size is 2."""
        assert sample_config.degradation.minimum_council_size == 2

    def test_warn_below_size(self, sample_config: SovereignCouncilConfig):
        """Test warning threshold is 3."""
        assert sample_config.degradation.warn_below_size == 3

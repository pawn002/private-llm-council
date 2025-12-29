"""
Tests for privacy mode verification.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.privacy import (
    verify_privacy_mode,
    PrivacyViolation,
    PrivacyVerification,
    NetworkStatus,
    _check_network_status,
    _can_reach_external,
    _can_reach_localhost,
)
from src.config import PrivacyMode


class TestPrivacyVerification:
    """Tests for privacy mode verification."""

    def test_sanctuary_mode_with_local_only(self):
        """Test SANCTUARY mode passes with local-only network."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.LOCAL_ONLY
            result = verify_privacy_mode(PrivacyMode.SANCTUARY)
            assert result.verified is True
            assert result.mode == PrivacyMode.SANCTUARY
            assert "Sanctuary mode verified" in result.message

    def test_sanctuary_mode_with_external_fails(self):
        """Test SANCTUARY mode fails with external connectivity."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.EXTERNAL_POSSIBLE
            with pytest.raises(PrivacyViolation) as exc_info:
                verify_privacy_mode(PrivacyMode.SANCTUARY)
            assert "no external egress" in str(exc_info.value)

    def test_sovereign_mode_with_isolated(self):
        """Test SOVEREIGN mode passes with complete isolation."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.ISOLATED
            result = verify_privacy_mode(PrivacyMode.SOVEREIGN)
            assert result.verified is True
            assert result.mode == PrivacyMode.SOVEREIGN

    def test_sovereign_mode_with_any_network_fails(self):
        """Test SOVEREIGN mode fails with any network activity."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.LOCAL_ONLY
            with pytest.raises(PrivacyViolation) as exc_info:
                verify_privacy_mode(PrivacyMode.SOVEREIGN)
            assert "complete network isolation" in str(exc_info.value)

    def test_citadel_mode_warns_on_external(self):
        """Test CITADEL mode warns but doesn't fail with external connectivity."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.EXTERNAL_POSSIBLE
            result = verify_privacy_mode(PrivacyMode.CITADEL)
            assert result.verified is True
            assert len(result.warnings) > 0
            assert "network policies" in result.warnings[0]

    def test_citadel_mode_passes_without_warning_when_isolated(self):
        """Test CITADEL mode passes without warning when isolated."""
        with patch("src.privacy._check_network_status") as mock_check:
            mock_check.return_value = NetworkStatus.ISOLATED
            result = verify_privacy_mode(PrivacyMode.CITADEL)
            assert result.verified is True
            assert len(result.warnings) == 0


class TestNetworkStatusChecks:
    """Tests for network status checking functions."""

    def test_network_status_unknown_on_error(self):
        """Test network status returns UNKNOWN on errors."""
        with patch("src.privacy._can_reach_external") as mock_external:
            mock_external.side_effect = Exception("Network error")
            status = _check_network_status()
            assert status == NetworkStatus.UNKNOWN

    def test_can_reach_localhost_returns_true_on_success(self):
        """Test localhost check returns True when socket connects."""
        with patch("socket.socket") as mock_socket:
            mock_instance = MagicMock()
            mock_socket.return_value = mock_instance
            mock_instance.connect_ex.return_value = 0
            result = _can_reach_localhost()
            assert result is True

    def test_can_reach_external_returns_false_on_timeout(self):
        """Test external check returns False on timeout."""
        with patch("socket.gethostbyname") as mock_dns:
            with patch("socket.socket") as mock_socket:
                import socket
                mock_dns.side_effect = socket.timeout()
                mock_instance = MagicMock()
                mock_socket.return_value = mock_instance
                mock_instance.connect_ex.side_effect = socket.timeout()
                result = _can_reach_external()
                assert result is False


class TestPrivacyViolationException:
    """Tests for the PrivacyViolation exception."""

    def test_privacy_violation_message(self):
        """Test PrivacyViolation contains descriptive message."""
        with pytest.raises(PrivacyViolation) as exc_info:
            raise PrivacyViolation("This is not a bug, it is a value.")
        assert "value" in str(exc_info.value)

    def test_privacy_violation_is_exception(self):
        """Test PrivacyViolation is a proper Exception."""
        exc = PrivacyViolation("Test message")
        assert isinstance(exc, Exception)

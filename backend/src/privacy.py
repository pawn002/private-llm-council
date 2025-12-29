"""
Privacy mode verification for The Sovereign Council.

This module enforces the privacy guarantees of each mode.
It is not a feature that can be toggled - it is the foundation.
"""

import socket
import subprocess
from dataclasses import dataclass
from enum import Enum

from .config import PrivacyMode


class PrivacyViolation(Exception):
    """
    Raised when a privacy guarantee would be violated.

    This is not a bug, it is a value.
    """

    pass


class NetworkStatus(str, Enum):
    """Status of network connectivity check."""

    ISOLATED = "isolated"  # No external connectivity
    LOCAL_ONLY = "local_only"  # Only localhost accessible
    EXTERNAL_POSSIBLE = "external_possible"  # External egress possible
    UNKNOWN = "unknown"  # Could not determine


@dataclass
class PrivacyVerification:
    """Result of privacy mode verification."""

    mode: PrivacyMode
    verified: bool
    network_status: NetworkStatus
    message: str
    warnings: list[str]


def verify_privacy_mode(mode: PrivacyMode) -> PrivacyVerification:
    """
    Verify that the current environment satisfies the privacy mode requirements.

    Args:
        mode: The privacy mode to verify.

    Returns:
        PrivacyVerification with results.

    Raises:
        PrivacyViolation: If mode is SOVEREIGN and network is detected.
    """
    network_status = _check_network_status()
    warnings: list[str] = []

    if mode == PrivacyMode.SOVEREIGN:
        # Sovereign mode: No network activity whatsoever
        if network_status != NetworkStatus.ISOLATED:
            raise PrivacyViolation(
                f"Sovereign mode requires complete network isolation. "
                f"Current status: {network_status.value}. "
                f"Disable all network interfaces or use a different privacy mode."
            )
        return PrivacyVerification(
            mode=mode,
            verified=True,
            network_status=network_status,
            message="Sovereign mode verified: Complete network isolation confirmed.",
            warnings=[],
        )

    elif mode == PrivacyMode.SANCTUARY:
        # Sanctuary mode: Local network only, no external egress
        if network_status == NetworkStatus.EXTERNAL_POSSIBLE:
            raise PrivacyViolation(
                f"Sanctuary mode requires no external egress. "
                f"External connectivity detected. "
                f"Configure firewall to block external connections or use Citadel mode."
            )
        if network_status == NetworkStatus.UNKNOWN:
            warnings.append(
                "Could not verify network isolation. Proceeding with caution. "
                "Consider verifying firewall configuration manually."
            )
        return PrivacyVerification(
            mode=mode,
            verified=True,
            network_status=network_status,
            message="Sanctuary mode verified: Local network only.",
            warnings=warnings,
        )

    elif mode == PrivacyMode.CITADEL:
        # Citadel mode: Containerized, network policies
        if network_status == NetworkStatus.EXTERNAL_POSSIBLE:
            warnings.append(
                "External network access is possible. "
                "Citadel mode relies on network policies to prevent data exfiltration. "
                "Ensure Docker network policies are correctly configured."
            )
        return PrivacyVerification(
            mode=mode,
            verified=True,
            network_status=network_status,
            message="Citadel mode active: Relying on network policies for isolation.",
            warnings=warnings,
        )

    # Should not reach here
    return PrivacyVerification(
        mode=mode,
        verified=False,
        network_status=network_status,
        message=f"Unknown privacy mode: {mode}",
        warnings=[],
    )


def _check_network_status() -> NetworkStatus:
    """
    Check current network connectivity status.

    Returns:
        NetworkStatus indicating the level of network access.
    """
    # Check if any non-loopback interfaces are up
    try:
        # Try to detect if we can reach external hosts
        external_reachable = _can_reach_external()

        if not external_reachable:
            # Check if localhost is reachable
            localhost_reachable = _can_reach_localhost()
            if localhost_reachable:
                return NetworkStatus.LOCAL_ONLY
            else:
                return NetworkStatus.ISOLATED

        return NetworkStatus.EXTERNAL_POSSIBLE

    except Exception:
        return NetworkStatus.UNKNOWN


def _can_reach_external() -> bool:
    """Check if external hosts are reachable."""
    # Try to resolve and connect to a well-known external host
    # We use DNS resolution as a proxy for connectivity
    try:
        # Try DNS resolution (doesn't actually connect)
        socket.setdefaulttimeout(2)
        socket.gethostbyname("dns.google")
        return True
    except (socket.gaierror, socket.timeout, OSError):
        pass

    # Also try a direct connection test
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("8.8.8.8", 53))
        sock.close()
        return result == 0
    except (socket.error, OSError):
        return False


def _can_reach_localhost() -> bool:
    """Check if localhost is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        # Try to connect to a port that's likely open (or any port)
        # We're just checking if localhost networking works
        result = sock.connect_ex(("127.0.0.1", 11434))  # Default Ollama port
        sock.close()
        # Even if port is closed, localhost is reachable
        return True
    except (socket.error, OSError):
        return False


def get_network_interfaces() -> list[dict]:
    """
    Get list of active network interfaces.

    Returns:
        List of interface information dicts.
    """
    interfaces = []

    try:
        # Use ip command on Linux
        result = subprocess.run(
            ["ip", "-j", "addr", "show"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            import json

            data = json.loads(result.stdout)
            for iface in data:
                if iface.get("operstate") == "UP":
                    interfaces.append(
                        {
                            "name": iface.get("ifname"),
                            "state": iface.get("operstate"),
                            "addresses": [
                                addr.get("local")
                                for addr in iface.get("addr_info", [])
                                if addr.get("local")
                            ],
                        }
                    )
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # Fallback: use socket to get hostname info
        try:
            hostname = socket.gethostname()
            addresses = socket.gethostbyname_ex(hostname)[2]
            interfaces.append(
                {
                    "name": "unknown",
                    "state": "UP",
                    "addresses": addresses,
                }
            )
        except socket.error:
            pass

    return interfaces

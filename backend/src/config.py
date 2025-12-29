"""
Configuration loader for The Sovereign Council.

This module loads and validates the council configuration,
treating configuration as a values declaration, not just settings.
"""

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class PrivacyMode(str, Enum):
    """
    The privacy mode spectrum.

    Each mode represents a position on the pragmatism-principle axis.
    Users choose their position; we do not choose it for them.
    """

    SOVEREIGN = "sovereign"  # Air-gapped, no network
    SANCTUARY = "sanctuary"  # Local network only, verified isolation
    CITADEL = "citadel"  # Containerized with network policies


class CouncilMember(BaseModel):
    """A member of the deliberation council."""

    id: str
    model: str
    capability: str = ""  # DevOps rationale
    character: str = ""  # Philosophical rationale
    temperature: float = 0.7


class ChairmanConfig(BaseModel):
    """Configuration for the chairman model."""

    model: str
    capability: str = ""
    role: str = "Synthesizer and dissent-preserver"
    temperature: float = 0.3
    preserve_dissent: bool = True


class GatewayConfig(BaseModel):
    """Inference gateway configuration."""

    provider: str = "ollama"
    url: str = "http://localhost:11434/v1"
    timeout_seconds: int = 120
    retry_attempts: int = 3
    retry_delay_seconds: int = 2


class PersistenceConfig(BaseModel):
    """
    Persistence configuration.

    Ephemeral by default - your deliberations vanish unless you
    explicitly choose to save them.
    """

    default: str = "ephemeral"
    encryption_required: bool = True  # Decision Point #4: Required
    algorithm: str = "AES-256-GCM"


class DegradationConfig(BaseModel):
    """
    Degradation policy configuration.

    We allow graceful degradation, but NEVER silently.
    The user always knows when operating at reduced capacity.
    """

    silent_fallback: bool = False  # This must remain False
    minimum_council_size: int = 2  # Decision Point #2
    warn_below_size: int = 3


class ConsentBannerConfig(BaseModel):
    """
    Consent banner configuration.

    Always shown on session start. Users can dismiss for their session.
    Operators cannot disable this - transparency is non-negotiable.
    """

    always_show_on_session_start: bool = True  # Cannot be disabled
    user_dismissable: bool = True
    persist_dismissal: str = "session_only"
    text: str = "This deliberation will be forgotten when you close the session."


class CouncilConfig(BaseModel):
    """Complete council configuration."""

    members: list[CouncilMember] = Field(default_factory=list)
    chairman: ChairmanConfig | None = None


class SovereignCouncilConfig(BaseModel):
    """
    Root configuration for The Sovereign Council.

    This configuration is a statement of values, not just settings.
    """

    privacy_mode: PrivacyMode = PrivacyMode.SANCTUARY  # Decision Point #1
    gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    council: CouncilConfig = Field(default_factory=CouncilConfig)
    persistence: PersistenceConfig = Field(default_factory=PersistenceConfig)
    degradation: DegradationConfig = Field(default_factory=DegradationConfig)
    consent_banner: ConsentBannerConfig = Field(default_factory=ConsentBannerConfig)
    telemetry_enabled: bool = False  # This must remain False


def load_config(config_path: Path | None = None) -> SovereignCouncilConfig:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file. If None, uses default.

    Returns:
        Validated configuration object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config is invalid.
    """
    if config_path is None:
        # Default config location
        config_path = Path(__file__).parent.parent.parent / "config" / "sovereign_council.yaml"

    if not config_path.exists():
        # Return defaults if no config file
        return SovereignCouncilConfig()

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    return _parse_config(raw_config)


def _parse_config(raw: dict[str, Any]) -> SovereignCouncilConfig:
    """Parse raw YAML config into validated config object."""

    # Extract privacy mode
    privacy_mode = PrivacyMode.SANCTUARY
    if "privacy" in raw and "mode" in raw["privacy"]:
        privacy_mode = PrivacyMode(raw["privacy"]["mode"])

    # Extract gateway config
    gateway = GatewayConfig()
    if "gateway" in raw:
        gw = raw["gateway"]
        gateway = GatewayConfig(
            provider=gw.get("provider", "ollama"),
            url=gw.get("url", "http://localhost:11434/v1"),
            timeout_seconds=gw.get("timeout_seconds", 120),
            retry_attempts=gw.get("retry_attempts", 3),
            retry_delay_seconds=gw.get("retry_delay_seconds", 2),
        )

    # Extract council config
    council = CouncilConfig()
    if "council" in raw:
        c = raw["council"]
        members = []
        for m in c.get("members", []):
            members.append(
                CouncilMember(
                    id=m["id"],
                    model=m["model"],
                    capability=m.get("capability", ""),
                    character=m.get("character", ""),
                    temperature=m.get("temperature", 0.7),
                )
            )

        chairman = None
        if "chairman" in c:
            ch = c["chairman"]
            chairman = ChairmanConfig(
                model=ch["model"],
                capability=ch.get("capability", ""),
                role=ch.get("role", "Synthesizer"),
                temperature=ch.get("temperature", 0.3),
                preserve_dissent=ch.get("preserve_dissent", True),
            )

        council = CouncilConfig(members=members, chairman=chairman)

    # Extract persistence config
    persistence = PersistenceConfig()
    if "persistence" in raw:
        p = raw["persistence"]
        persistence = PersistenceConfig(
            default=p.get("default", "ephemeral"),
            encryption_required=p.get("save", {}).get("encryption", "required") == "required",
            algorithm=p.get("save", {}).get("algorithm", "AES-256-GCM"),
        )

    # Extract degradation config
    degradation = DegradationConfig()
    if "degradation" in raw:
        d = raw["degradation"]
        degradation = DegradationConfig(
            silent_fallback=False,  # Always False, ignore config
            minimum_council_size=d.get("minimum_council_size", 2),
            warn_below_size=d.get("warn_below_size", 3),
        )

    # Extract consent banner config
    consent_banner = ConsentBannerConfig()
    if "persistence" in raw and "consent_banner" in raw["persistence"]:
        cb = raw["persistence"]["consent_banner"]
        consent_banner = ConsentBannerConfig(
            always_show_on_session_start=True,  # Always True, ignore config
            user_dismissable=cb.get("user_dismissable", True),
            persist_dismissal=cb.get("persist_dismissal", "session_only"),
            text=cb.get("text", consent_banner.text),
        )

    return SovereignCouncilConfig(
        privacy_mode=privacy_mode,
        gateway=gateway,
        council=council,
        persistence=persistence,
        degradation=degradation,
        consent_banner=consent_banner,
        telemetry_enabled=False,  # Always False, ignore config
    )

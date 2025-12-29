"""
Tests for the council orchestration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.council import (
    CouncilOrchestrator,
    Deliberation,
    Perspective,
    Critique,
    Disagreement,
    MinorityReport,
    Synthesis,
)
from src.config import (
    CouncilConfig,
    CouncilMember,
    ChairmanConfig,
    DegradationConfig,
)
from src.gateway import InferenceResponse, GatewayError, ModelUnavailableError


@pytest.fixture
def council_config() -> CouncilConfig:
    """Create a council configuration for testing."""
    return CouncilConfig(
        members=[
            CouncilMember(
                id="phi",
                model="llama3.2:8b",
                character="Western analytical",
                temperature=0.7,
            ),
            CouncilMember(
                id="psi",
                model="mistral:7b",
                character="European regulatory",
                temperature=0.7,
            ),
            CouncilMember(
                id="omega",
                model="qwen2.5:7b",
                character="Eastern philosophical",
                temperature=0.7,
            ),
        ],
        chairman=ChairmanConfig(
            model="llama3.2:70b",
            role="Synthesizer",
            temperature=0.3,
            preserve_dissent=True,
        ),
    )


@pytest.fixture
def degradation_config() -> DegradationConfig:
    """Create a degradation configuration for testing."""
    return DegradationConfig(
        silent_fallback=False,
        minimum_council_size=2,
        warn_below_size=3,
    )


class TestDeliberation:
    """Tests for the Deliberation dataclass."""

    def test_empty_deliberation(self):
        """Test creating an empty deliberation."""
        delib = Deliberation.empty("Test question?")
        assert delib.question == "Test question?"
        assert len(delib.perspectives) == 0
        assert delib.synthesis.content == ""
        assert delib.id is not None
        assert delib.session_id is not None

    def test_deliberation_has_unique_ids(self):
        """Test that each deliberation has unique IDs."""
        delib1 = Deliberation.empty("Question 1")
        delib2 = Deliberation.empty("Question 2")
        assert delib1.id != delib2.id
        assert delib1.session_id != delib2.session_id


class TestPerspective:
    """Tests for the Perspective dataclass."""

    def test_perspective_creation(self):
        """Test creating a perspective."""
        perspective = Perspective(
            member_id="phi",
            model="llama3.2:8b",
            character="Western analytical",
            content="This is my perspective on the matter.",
        )
        assert perspective.member_id == "phi"
        assert perspective.content == "This is my perspective on the matter."
        assert perspective.timestamp is not None


class TestCouncilOrchestrator:
    """Tests for the CouncilOrchestrator class."""

    @pytest.mark.asyncio
    async def test_deliberate_collects_perspectives(
        self,
        mock_gateway: MagicMock,
        council_config: CouncilConfig,
        degradation_config: DegradationConfig,
    ):
        """Test that deliberation collects perspectives from all members."""
        orchestrator = CouncilOrchestrator(
            gateway=mock_gateway,
            config=council_config,
            degradation=degradation_config,
        )

        # Mock different responses for each model
        responses = [
            InferenceResponse(content="Phi's perspective", model="llama3.2:8b"),
            InferenceResponse(content="Psi's perspective", model="mistral:7b"),
            InferenceResponse(content="Omega's perspective", model="qwen2.5:7b"),
            InferenceResponse(content="Review 1", model="llama3.2:8b"),
            InferenceResponse(content="Review 2", model="mistral:7b"),
            InferenceResponse(content="Review 3", model="qwen2.5:7b"),
            InferenceResponse(content="Chairman synthesis", model="llama3.2:70b"),
        ]
        mock_gateway.complete = AsyncMock(side_effect=responses)

        deliberation = await orchestrator.deliberate("What is the meaning of life?")

        assert len(deliberation.perspectives) == 3
        assert deliberation.question == "What is the meaning of life?"

    @pytest.mark.asyncio
    async def test_deliberate_fails_with_insufficient_perspectives(
        self,
        mock_gateway: MagicMock,
        council_config: CouncilConfig,
        degradation_config: DegradationConfig,
    ):
        """Test that deliberation fails when too few perspectives are gathered."""
        orchestrator = CouncilOrchestrator(
            gateway=mock_gateway,
            config=council_config,
            degradation=degradation_config,
        )

        # Mock only one successful response, rest fail
        mock_gateway.complete = AsyncMock(
            side_effect=[
                InferenceResponse(content="Only perspective", model="llama3.2:8b"),
                ModelUnavailableError("Model not found"),
                ModelUnavailableError("Model not found"),
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            await orchestrator.deliberate("Test question")
        assert "Insufficient council members" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_deliberate_warns_below_threshold(
        self,
        mock_gateway: MagicMock,
        council_config: CouncilConfig,
        degradation_config: DegradationConfig,
    ):
        """Test that deliberation warns when below threshold but continues."""
        orchestrator = CouncilOrchestrator(
            gateway=mock_gateway,
            config=council_config,
            degradation=degradation_config,
        )

        # Mock two successful responses (above minimum, below warn threshold)
        responses = [
            InferenceResponse(content="Phi's perspective", model="llama3.2:8b"),
            InferenceResponse(content="Psi's perspective", model="mistral:7b"),
            ModelUnavailableError("Model not found"),
            InferenceResponse(content="Review 1", model="llama3.2:8b"),
            InferenceResponse(content="Review 2", model="mistral:7b"),
            InferenceResponse(content="Chairman synthesis", model="llama3.2:70b"),
        ]
        mock_gateway.complete = AsyncMock(side_effect=responses)

        status_messages = []

        def capture_status(msg):
            status_messages.append(msg)

        deliberation = await orchestrator.deliberate(
            "Test question", on_status=capture_status
        )

        assert len(deliberation.perspectives) == 2
        assert any("Warning" in msg for msg in status_messages)

    @pytest.mark.asyncio
    async def test_deliberate_produces_synthesis(
        self,
        mock_gateway: MagicMock,
        council_config: CouncilConfig,
        degradation_config: DegradationConfig,
    ):
        """Test that deliberation produces a synthesis."""
        orchestrator = CouncilOrchestrator(
            gateway=mock_gateway,
            config=council_config,
            degradation=degradation_config,
        )

        responses = [
            InferenceResponse(content="Perspective 1", model="llama3.2:8b"),
            InferenceResponse(content="Perspective 2", model="mistral:7b"),
            InferenceResponse(content="Perspective 3", model="qwen2.5:7b"),
            InferenceResponse(content="Review 1", model="llama3.2:8b"),
            InferenceResponse(content="Review 2", model="mistral:7b"),
            InferenceResponse(content="Review 3", model="qwen2.5:7b"),
            InferenceResponse(
                content="The council has deliberated and reached a synthesis.",
                model="llama3.2:70b",
            ),
        ]
        mock_gateway.complete = AsyncMock(side_effect=responses)

        deliberation = await orchestrator.deliberate("What should I do?")

        assert "synthesis" in deliberation.synthesis.content.lower()


class TestDisagreementExtraction:
    """Tests for disagreement extraction."""

    def test_disagreement_creation(self):
        """Test creating a disagreement."""
        disagreement = Disagreement(
            topic="Risk assessment",
            positions={
                "phi": "Take the risk",
                "psi": "Avoid the risk",
            },
            description="Council members disagree on risk tolerance",
        )
        assert disagreement.topic == "Risk assessment"
        assert len(disagreement.positions) == 2


class TestMinorityReport:
    """Tests for minority reports."""

    def test_minority_report_creation(self):
        """Test creating a minority report."""
        report = MinorityReport(
            member_id="phi",
            position="The risk is worth taking",
            rationale="Opportunity cost of not trying outweighs potential loss",
        )
        assert report.member_id == "phi"
        assert "risk" in report.position.lower()


class TestSynthesis:
    """Tests for synthesis."""

    def test_synthesis_creation(self):
        """Test creating a synthesis."""
        synthesis = Synthesis(
            content="The council concludes...",
            consensus_points=["Point 1", "Point 2"],
            divisions=["Risk tolerance"],
            unique_insights=["Novel perspective from omega"],
        )
        assert len(synthesis.consensus_points) == 2
        assert len(synthesis.divisions) == 1
        assert len(synthesis.unique_insights) == 1

"""
Tests for the deliberation analysis module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.analysis import (
    DeliberationAnalyzer,
    DisagreementSeverity,
    AnalyzedDisagreement,
    ConfidenceAssessment,
)
from src.council import Perspective, Critique
from src.gateway import InferenceResponse


@pytest.fixture
def mock_gateway():
    """Create a mock gateway for analysis."""
    gateway = MagicMock()
    gateway.complete = AsyncMock()
    return gateway


@pytest.fixture
def sample_perspectives():
    """Create sample perspectives for testing."""
    return [
        Perspective(
            member_id="phi",
            model="llama3.2:8b",
            character="Western analytical",
            content="The risk-reward ratio suggests taking the opportunity.",
        ),
        Perspective(
            member_id="psi",
            model="mistral:7b",
            character="European regulatory",
            content="Financial security must be prioritized over speculation.",
        ),
        Perspective(
            member_id="omega",
            model="qwen2.5:7b",
            character="Eastern philosophical",
            content="Consider the timing - perhaps waiting is itself an answer.",
        ),
    ]


@pytest.fixture
def sample_critiques():
    """Create sample critiques for testing."""
    return [
        Critique(
            reviewer_id="phi",
            rankings=["psi", "omega"],
            comments={},
        ),
        Critique(
            reviewer_id="psi",
            rankings=["omega", "phi"],
            comments={},
        ),
    ]


class TestDeliberationAnalyzer:
    """Tests for the DeliberationAnalyzer class."""

    @pytest.mark.asyncio
    async def test_analyze_disagreements_parses_response(
        self, mock_gateway, sample_perspectives
    ):
        """Test that disagreement analysis parses LLM response correctly."""
        mock_gateway.complete.return_value = InferenceResponse(
            content="""DISAGREEMENT_COUNT: 1

DISAGREEMENT_1:
TOPIC: Risk tolerance
SEVERITY: FUNDAMENTAL
POSITIONS:
- phi: Take the risk for potential gains
- psi: Avoid risk for financial security
IMPLICATIONS: The user must decide their personal risk tolerance
""",
            model="llama3.2:8b",
        )

        analyzer = DeliberationAnalyzer(mock_gateway, "llama3.2:8b")
        disagreements = await analyzer.analyze_disagreements(
            "Should I invest?", sample_perspectives
        )

        assert len(disagreements) == 1
        assert disagreements[0].topic == "Risk tolerance"
        assert disagreements[0].severity == DisagreementSeverity.FUNDAMENTAL

    @pytest.mark.asyncio
    async def test_analyze_disagreements_handles_none(
        self, mock_gateway, sample_perspectives
    ):
        """Test that analysis handles no disagreements."""
        mock_gateway.complete.return_value = InferenceResponse(
            content="DISAGREEMENT_COUNT: 0\n\nNONE",
            model="llama3.2:8b",
        )

        analyzer = DeliberationAnalyzer(mock_gateway, "llama3.2:8b")
        disagreements = await analyzer.analyze_disagreements(
            "What is 2+2?", sample_perspectives
        )

        assert len(disagreements) == 0

    @pytest.mark.asyncio
    async def test_extract_minority_reports(
        self, mock_gateway, sample_perspectives, sample_critiques
    ):
        """Test minority report extraction."""
        mock_gateway.complete.return_value = InferenceResponse(
            content="""MINORITY_REPORTS: 1

REPORT_1:
MEMBER: phi
POSITION: Risk should be embraced for growth
RATIONALE: The synthesis focused on caution but phi's perspective on opportunity cost deserves attention
KEY_INSIGHT: Regret of inaction may exceed regret of failed action
""",
            model="llama3.2:8b",
        )

        analyzer = DeliberationAnalyzer(mock_gateway, "llama3.2:8b")
        reports = await analyzer.extract_minority_reports(
            "Should I take the risk?",
            sample_perspectives,
            "The council recommends caution.",
            sample_critiques,
        )

        assert len(reports) == 1
        assert reports[0].member_id == "phi"
        assert "risk" in reports[0].position.lower()

    @pytest.mark.asyncio
    async def test_assess_confidence(
        self, mock_gateway, sample_perspectives
    ):
        """Test confidence assessment."""
        mock_gateway.complete.return_value = InferenceResponse(
            content="""OVERALL_CONFIDENCE: 0.7
CONSENSUS_STRENGTH: 0.4
DISSENT_STRENGTH: 0.6
REASONING: Council shows moderate agreement with notable dissent on risk tolerance.
""",
            model="llama3.2:8b",
        )

        analyzer = DeliberationAnalyzer(mock_gateway, "llama3.2:8b")
        confidence = await analyzer.assess_confidence(
            "Test question",
            sample_perspectives,
            [],
            "Test synthesis",
        )

        assert confidence.overall == 0.7
        assert confidence.consensus_strength == 0.4
        assert confidence.dissent_strength == 0.6
        assert "risk" in confidence.reasoning.lower()

    @pytest.mark.asyncio
    async def test_confidence_clamps_values(self, mock_gateway, sample_perspectives):
        """Test that confidence values are clamped to 0.0-1.0 range."""
        mock_gateway.complete.return_value = InferenceResponse(
            content="""OVERALL_CONFIDENCE: 1.5
CONSENSUS_STRENGTH: -0.3
DISSENT_STRENGTH: 2.0
REASONING: Test
""",
            model="llama3.2:8b",
        )

        analyzer = DeliberationAnalyzer(mock_gateway, "llama3.2:8b")
        confidence = await analyzer.assess_confidence(
            "Test", sample_perspectives, [], "Test"
        )

        assert confidence.overall == 1.0  # Clamped from 1.5
        assert confidence.consensus_strength == 0.0  # Clamped from -0.3
        assert confidence.dissent_strength == 1.0  # Clamped from 2.0


class TestDisagreementSeverity:
    """Tests for DisagreementSeverity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert DisagreementSeverity.MINOR.value == "minor"
        assert DisagreementSeverity.MODERATE.value == "moderate"
        assert DisagreementSeverity.FUNDAMENTAL.value == "fundamental"

    def test_severity_comparison(self):
        """Test that severities can be compared."""
        severities = [
            DisagreementSeverity.MINOR,
            DisagreementSeverity.MODERATE,
            DisagreementSeverity.FUNDAMENTAL,
        ]
        assert len(set(severities)) == 3


class TestAnalyzedDisagreement:
    """Tests for AnalyzedDisagreement dataclass."""

    def test_creation(self):
        """Test creating an analyzed disagreement."""
        disagreement = AnalyzedDisagreement(
            topic="Test topic",
            positions={"a": "position a", "b": "position b"},
            description="Test description",
            severity=DisagreementSeverity.FUNDAMENTAL,
            implications="What this means",
        )
        assert disagreement.topic == "Test topic"
        assert disagreement.severity == DisagreementSeverity.FUNDAMENTAL
        assert disagreement.implications == "What this means"

    def test_default_severity(self):
        """Test default severity is MODERATE."""
        disagreement = AnalyzedDisagreement(
            topic="Test",
            positions={},
            description="Test",
        )
        assert disagreement.severity == DisagreementSeverity.MODERATE


class TestConfidenceAssessment:
    """Tests for ConfidenceAssessment dataclass."""

    def test_creation(self):
        """Test creating a confidence assessment."""
        assessment = ConfidenceAssessment(
            overall=0.8,
            consensus_strength=0.9,
            dissent_strength=0.2,
            reasoning="High consensus",
        )
        assert assessment.overall == 0.8
        assert assessment.consensus_strength == 0.9
        assert assessment.dissent_strength == 0.2

"""
Unit tests for LLM response parsers.
Zero LLM calls — all inputs are hardcoded strings.
Run with: pytest tests/test_parsing.py -v
"""

import pytest
from unittest.mock import MagicMock

from src.analysis import DeliberationAnalyzer
from src.council import _parse_synthesis_response


@pytest.fixture
def analyzer():
    return DeliberationAnalyzer(gateway=MagicMock(), analysis_model="test-model")


# ─── _parse_consensus_insights ────────────────────────────────────────────────

class TestParseConsensusInsights:

    def test_dash_bullets(self, analyzer):
        raw = (
            "CONSENSUS_POINTS:\n"
            "- Both agreed risk must be managed\n"
            "- Growth requires preparation\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "- Only Phi raised operational collapse risk\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert consensus == ["Both agreed risk must be managed", "Growth requires preparation"]
        assert insights == ["Only Phi raised operational collapse risk"]

    def test_bullet_char(self, analyzer):
        """Model outputs • (U+2022) instead of - — the primary bug this fixes."""
        raw = (
            "CONSENSUS_POINTS:\n"
            "• Both agreed risk must be managed\n"
            "• Growth requires preparation\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "• Only Phi raised operational collapse risk\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert len(consensus) == 2
        assert len(insights) == 1

    def test_none_value_excluded(self, analyzer):
        raw = (
            "CONSENSUS_POINTS:\n"
            "- Real point\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "- NONE\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert len(consensus) == 1
        assert len(insights) == 0

    def test_missing_headers_returns_empty(self, analyzer):
        raw = "The council discussed many things.\nPhi said one thing.\nPsi said another."
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert consensus == []
        assert insights == []

    def test_markdown_decorated_headers(self, analyzer):
        """Models sometimes bold or header-ify section names."""
        raw = (
            "**CONSENSUS_POINTS:**\n"
            "- Shared point\n"
            "\n"
            "**UNIQUE_INSIGHTS:**\n"
            "- Unique point\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert len(consensus) == 1
        assert len(insights) == 1

    def test_markdown_heading_mixed_case(self, analyzer):
        """Small models output ### Consensus Points: instead of CONSENSUS_POINTS:"""
        raw = (
            "### Consensus Points:\n"
            "• Both agreed risk must be managed\n"
            "• Growth requires preparation\n"
            "\n"
            "### Unique Insights:\n"
            "• Only Phi raised operational collapse risk\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert len(consensus) == 2
        assert len(insights) == 1

    def test_empty_response(self, analyzer):
        consensus, insights = analyzer._parse_consensus_insights("")
        assert consensus == []
        assert insights == []

    def test_mixed_bullet_styles(self, analyzer):
        raw = (
            "CONSENSUS_POINTS:\n"
            "- Dash bullet\n"
            "• Char bullet\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "- Another point\n"
        )
        consensus, insights = analyzer._parse_consensus_insights(raw)
        assert len(consensus) == 2
        assert len(insights) == 1


# ─── _parse_synthesis_response ────────────────────────────────────────────────

class TestParseSynthesisResponse:

    def test_strips_synthesis_header(self):
        raw = "Synthesis:\n\nThe council is divided on the matter."
        content, consensus, insights = _parse_synthesis_response(raw)
        assert not content.startswith("Synthesis:")
        assert "council is divided" in content

    def test_splits_sections(self):
        raw = (
            "The council reached several conclusions.\n"
            "\n"
            "CONSENSUS_POINTS:\n"
            "- Point one\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "- Insight one\n"
        )
        content, consensus, insights = _parse_synthesis_response(raw)
        assert "council reached" in content
        assert consensus == ["Point one"]
        assert insights == ["Insight one"]

    def test_no_sections_returns_full_text(self):
        raw = "The council discussed the matter at length without reaching consensus."
        content, consensus, insights = _parse_synthesis_response(raw)
        assert content == raw.strip()
        assert consensus == []
        assert insights == []

    def test_fallback_when_content_empty(self):
        """If markers appear before any prose, full raw is used as content."""
        raw = (
            "CONSENSUS_POINTS:\n"
            "- Point\n"
            "\n"
            "UNIQUE_INSIGHTS:\n"
            "- Insight\n"
        )
        content, consensus, insights = _parse_synthesis_response(raw)
        assert content  # not empty

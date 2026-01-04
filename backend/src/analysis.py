"""
Deliberation analysis for The Sovereign Council.

Uses the council's own models to analyze disagreements, extract minority reports,
and assess confidence. We use local LLMs for analysis to maintain privacy -
no external NLP services that might phone home.

Philosophy: The council understands itself through its own intelligence.
"""

from dataclasses import dataclass
from enum import Enum

from .config import Temperature
from .council import (
    Perspective,
    Critique,
    Disagreement,
    MinorityReport,
    format_perspectives_for_prompt,
)
from .gateway import InferenceGateway


# Utility functions
def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value to the specified range."""
    return max(min_val, min(max_val, value))


def extract_value(line: str) -> str:
    """Extract the value after the first colon in a line."""
    if ":" not in line:
        return line.strip()
    return line.split(":", 1)[1].strip()


class DisagreementSeverity(str, Enum):
    """How fundamental is the disagreement?"""

    MINOR = "minor"  # Different emphasis, same conclusion
    MODERATE = "moderate"  # Different reasoning, similar conclusions
    FUNDAMENTAL = "fundamental"  # Incompatible positions


@dataclass
class AnalyzedDisagreement(Disagreement):
    """A disagreement with additional analysis."""

    severity: DisagreementSeverity = DisagreementSeverity.MODERATE
    implications: str = ""  # What this disagreement means for the user


@dataclass
class ConfidenceAssessment:
    """Assessment of synthesis confidence."""

    overall: float  # 0.0 to 1.0
    consensus_strength: float  # How much agreement exists
    dissent_strength: float  # How strong the minority positions are
    reasoning: str


DISAGREEMENT_ANALYSIS_PROMPT = """You are analyzing a council deliberation to identify disagreements.

Given multiple perspectives on a question, identify:
1. Points where perspectives fundamentally conflict (not just different emphasis)
2. The nature of each disagreement (values, facts, reasoning, priorities)
3. The severity: MINOR (emphasis), MODERATE (reasoning differs), FUNDAMENTAL (incompatible)

Question: {question}

Perspectives:
{perspectives}

Respond in this exact format:
DISAGREEMENT_COUNT: <number>

DISAGREEMENT_1:
TOPIC: <brief topic>
SEVERITY: <MINOR|MODERATE|FUNDAMENTAL>
POSITIONS:
- [member_id]: <their position>
- [member_id]: <their position>
IMPLICATIONS: <what this means for the user>

(repeat for each disagreement, or write NONE if all perspectives agree)
"""

MINORITY_REPORT_PROMPT = """You are identifying minority positions that deserve attention.

In a council deliberation, the synthesis represents the majority/consensus view.
Your task is to identify perspectives that:
1. Were not fully represented in the synthesis
2. Contain valid points that should not be lost
3. Represent a coherent alternative viewpoint

Question: {question}

Individual Perspectives:
{perspectives}

Synthesis:
{synthesis}

Peer Review Rankings (who ranked whom highest):
{rankings}

Identify any perspective that deserves a "minority report" - a dissenting view worth preserving.

Respond in this exact format:
MINORITY_REPORTS: <number>

REPORT_1:
MEMBER: <member_id>
POSITION: <one sentence summary of their dissenting position>
RATIONALE: <why this perspective deserves attention despite not being the consensus>
KEY_INSIGHT: <the unique insight this perspective offers>

(or write NONE if the synthesis adequately represents all views)
"""

CONFIDENCE_ASSESSMENT_PROMPT = """Assess the confidence level of this council synthesis.

Question: {question}

Number of perspectives: {num_perspectives}
Number of disagreements: {num_disagreements}
Disagreement severities: {severities}

Synthesis:
{synthesis}

Assess:
1. OVERALL_CONFIDENCE: 0.0 to 1.0 (how confident should the user be in this synthesis?)
2. CONSENSUS_STRENGTH: 0.0 to 1.0 (how much did the council agree?)
3. DISSENT_STRENGTH: 0.0 to 1.0 (how strong are the minority positions?)
4. REASONING: One sentence explaining the confidence level

Respond in this exact format:
OVERALL_CONFIDENCE: <0.0-1.0>
CONSENSUS_STRENGTH: <0.0-1.0>
DISSENT_STRENGTH: <0.0-1.0>
REASONING: <explanation>
"""


class DeliberationAnalyzer:
    """
    Analyzes council deliberations to extract deeper insights.

    Uses the council's own models for analysis to maintain privacy.
    No external services, no data exfiltration.
    """

    def __init__(self, gateway: InferenceGateway, analysis_model: str):
        """
        Initialize the analyzer.

        Args:
            gateway: The inference gateway to use
            analysis_model: Model to use for analysis (typically a council member)
        """
        self.gateway = gateway
        self.analysis_model = analysis_model

    async def analyze_disagreements(
        self,
        question: str,
        perspectives: list[Perspective],
    ) -> list[AnalyzedDisagreement]:
        """
        Analyze perspectives to identify and characterize disagreements.

        Args:
            question: The original question
            perspectives: Council member perspectives

        Returns:
            List of analyzed disagreements
        """
        if len(perspectives) < 2:
            return []

        # Format perspectives for analysis
        perspectives_text = format_perspectives_for_prompt(perspectives)

        prompt = DISAGREEMENT_ANALYSIS_PROMPT.format(
            question=question,
            perspectives=perspectives_text,
        )

        response = await self.gateway.complete(
            model=self.analysis_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=Temperature.ANALYSIS,
        )

        return self._parse_disagreements(response.content, perspectives)

    async def extract_minority_reports(
        self,
        question: str,
        perspectives: list[Perspective],
        synthesis_content: str,
        critiques: list[Critique],
    ) -> list[MinorityReport]:
        """
        Extract minority reports for perspectives not well-represented in synthesis.

        Args:
            question: The original question
            perspectives: Council member perspectives
            synthesis_content: The chairman's synthesis
            critiques: Peer review critiques with rankings

        Returns:
            List of minority reports
        """
        if len(perspectives) < 2:
            return []

        # Format perspectives
        perspectives_text = format_perspectives_for_prompt(perspectives, include_character=False)

        # Format rankings
        rankings_text = "\n".join(
            f"- {c.reviewer_id} ranked: {' > '.join(c.rankings)}" for c in critiques
        )

        prompt = MINORITY_REPORT_PROMPT.format(
            question=question,
            perspectives=perspectives_text,
            synthesis=synthesis_content,
            rankings=rankings_text or "No rankings available",
        )

        response = await self.gateway.complete(
            model=self.analysis_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=Temperature.ANALYSIS,
        )

        return self._parse_minority_reports(response.content)

    async def assess_confidence(
        self,
        question: str,
        perspectives: list[Perspective],
        disagreements: list[Disagreement],
        synthesis_content: str,
    ) -> ConfidenceAssessment:
        """
        Assess the confidence level of the synthesis.

        Args:
            question: The original question
            perspectives: Council member perspectives
            disagreements: Identified disagreements
            synthesis_content: The chairman's synthesis

        Returns:
            Confidence assessment
        """
        severities = [
            d.severity if isinstance(d, AnalyzedDisagreement) else "UNKNOWN"
            for d in disagreements
        ]

        prompt = CONFIDENCE_ASSESSMENT_PROMPT.format(
            question=question,
            num_perspectives=len(perspectives),
            num_disagreements=len(disagreements),
            severities=", ".join(str(s) for s in severities) or "None",
            synthesis=synthesis_content,
        )

        response = await self.gateway.complete(
            model=self.analysis_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=Temperature.CONFIDENCE,
        )

        return self._parse_confidence(response.content)

    def _parse_disagreements(
        self, response: str, perspectives: list[Perspective]
    ) -> list[AnalyzedDisagreement]:
        """Parse disagreement analysis response."""
        disagreements = []

        # Get member IDs for reference
        member_ids = {p.member_id for p in perspectives}

        lines = response.strip().split("\n")
        current_disagreement = None
        current_positions = {}

        for line in lines:
            line = line.strip()

            if line.startswith("DISAGREEMENT_COUNT:"):
                continue
            elif line.startswith("DISAGREEMENT_"):
                if current_disagreement:
                    current_disagreement.positions = current_positions
                    disagreements.append(current_disagreement)
                current_disagreement = AnalyzedDisagreement(
                    topic="",
                    positions={},
                    description="",
                )
                current_positions = {}
            elif line.startswith("TOPIC:"):
                if current_disagreement:
                    current_disagreement.topic = extract_value(line)
            elif line.startswith("SEVERITY:"):
                if current_disagreement:
                    severity_str = extract_value(line).upper()
                    try:
                        current_disagreement.severity = DisagreementSeverity(
                            severity_str.lower()
                        )
                    except ValueError:
                        current_disagreement.severity = DisagreementSeverity.MODERATE
            elif line.startswith("IMPLICATIONS:"):
                if current_disagreement:
                    current_disagreement.implications = extract_value(line)
                    current_disagreement.description = current_disagreement.implications
            elif line.startswith("- "):
                # Position line: "- member_id: position"
                if ":" in line:
                    parts = line[2:].split(":", 1)
                    member_id = parts[0].strip()
                    position = parts[1].strip() if len(parts) > 1 else ""
                    # Try to match to actual member ID
                    for mid in member_ids:
                        if mid.lower() in member_id.lower():
                            current_positions[mid] = position
                            break
                    else:
                        current_positions[member_id] = position
            elif line == "NONE":
                return []

        # Don't forget the last one
        if current_disagreement and current_disagreement.topic:
            current_disagreement.positions = current_positions
            disagreements.append(current_disagreement)

        return disagreements

    def _parse_minority_reports(self, response: str) -> list[MinorityReport]:
        """Parse minority report extraction response."""
        reports = []

        if "NONE" in response.upper() and "MINORITY_REPORTS: 0" in response:
            return []

        lines = response.strip().split("\n")
        current_report = None

        for line in lines:
            line = line.strip()

            if line.startswith("REPORT_"):
                if current_report and current_report.member_id:
                    reports.append(current_report)
                current_report = MinorityReport(
                    member_id="",
                    position="",
                    rationale="",
                )
            elif line.startswith("MEMBER:"):
                if current_report:
                    current_report.member_id = extract_value(line)
            elif line.startswith("POSITION:"):
                if current_report:
                    current_report.position = extract_value(line)
            elif line.startswith("RATIONALE:"):
                if current_report:
                    current_report.rationale = extract_value(line)
            elif line.startswith("KEY_INSIGHT:"):
                if current_report:
                    # Append key insight to rationale
                    current_report.rationale += f" Key insight: {extract_value(line)}"

        # Don't forget the last one
        if current_report and current_report.member_id:
            reports.append(current_report)

        return reports

    def _parse_confidence(self, response: str) -> ConfidenceAssessment:
        """Parse confidence assessment response."""
        overall = 0.5
        consensus = 0.5
        dissent = 0.5
        reasoning = "Unable to assess confidence"

        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("OVERALL_CONFIDENCE:"):
                try:
                    overall = clamp(float(extract_value(line)))
                except ValueError:
                    pass
            elif line.startswith("CONSENSUS_STRENGTH:"):
                try:
                    consensus = clamp(float(extract_value(line)))
                except ValueError:
                    pass
            elif line.startswith("DISSENT_STRENGTH:"):
                try:
                    dissent = clamp(float(extract_value(line)))
                except ValueError:
                    pass
            elif line.startswith("REASONING:"):
                reasoning = extract_value(line)

        return ConfidenceAssessment(
            overall=overall,
            consensus_strength=consensus,
            dissent_strength=dissent,
            reasoning=reasoning,
        )

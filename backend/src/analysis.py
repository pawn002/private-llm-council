"""
Deliberation analysis for The Sovereign Council.

Uses the council's own models to analyze disagreements, extract minority reports,
and assess confidence. We use local LLMs for analysis to maintain privacy -
no external NLP services that might phone home.

Philosophy: The council understands itself through its own intelligence.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from .config import Temperature

logger = logging.getLogger(__name__)
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


def normalize_field_name(text: str) -> str:
    """
    Normalize field name for fuzzy matching.
    Converts to lowercase and removes spaces/underscores.

    Examples:
        "OVERALL_CONFIDENCE:" -> "overallconfidence"
        "Overall Confidence:" -> "overallconfidence"
        "overall confidence is" -> "overallconfidenceis"
    """
    return text.lower().replace("_", "").replace(" ", "").rstrip(":")


def matches_field(line: str, field_name: str) -> bool:
    """
    Check if line starts with the given field name (fuzzy match).

    Args:
        line: The line to check (e.g., "Overall Confidence: 0.8")
        field_name: Expected field name (e.g., "OVERALL_CONFIDENCE")

    Returns:
        True if line matches the field name
    """
    # Normalize both the line prefix and expected field name
    line_prefix = line.split(":")[0] if ":" in line else line
    normalized_line = normalize_field_name(line_prefix)
    normalized_field = normalize_field_name(field_name)

    return normalized_line.startswith(normalized_field)


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


DISAGREEMENT_ANALYSIS_PROMPT = """Read these perspectives and find cases where members give OPPOSITE recommendations.

A disagreement only counts when:
- One member recommends doing X
- Another member recommends NOT doing X, or recommends the opposite

If their advice could both be followed, or if they are on different topics, it is NOT a disagreement.
If you are not certain their positions are opposite, write DISAGREEMENT_COUNT: 0.

Severity:
- FUNDAMENTAL: following one member's advice makes it impossible to follow the other's
- MODERATE: the recommendations pull in opposite directions but are not mutually exclusive
- MINOR: same overall direction, meaningfully different emphasis

Members: {member_names}

Question: {question}

Perspectives:
{perspectives}

Format (use the actual member names from above, not the word "member_name"):
DISAGREEMENT_COUNT: <number>

DISAGREEMENT_1:
TOPIC: <what they disagree about, in 5 words or fewer>
SEVERITY: MINOR or MODERATE or FUNDAMENTAL
POSITIONS:
- <first member name>: <their specific recommendation>
- <second member name>: <their opposing recommendation>
IMPLICATIONS: <what this means for the person asking>

(only include disagreements where the positions are genuinely opposite)
"""

CONSENSUS_POINTS_PROMPT = """Read these perspectives and identify what all or most members agreed on.

Question: {question}

Perspectives:
{perspectives}

Write a bullet list of shared conclusions — ideas everyone or almost everyone expressed.
Do NOT include member names. Write the shared idea itself, not who said it.
Use "- " bullets. One sentence per bullet. Write "- NONE" if nothing was shared.
Only output the bullet list."""

UNIQUE_INSIGHTS_PROMPT = """Read these perspectives and identify ideas that only one member raised.

Question: {question}

Perspectives:
{perspectives}

Write a bullet list of distinctive ideas that appear in only one perspective.
Do NOT include member names. Write the distinctive idea itself, not who said it.
Use "- " bullets. One sentence per bullet. Write "- NONE" if there are no unique insights.
Only output the bullet list."""

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


def _parse_bullet_list(response: str) -> list[str]:
    """Extract bullet items from a response that contains only a bullet list.

    Accepts both '- ' and '• ' prefixes. Excludes NONE sentinels, member-name
    labels (short text ending with ':'), and blank items.
    """
    items = []
    for line in response.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("• "):
            text = stripped[2:].strip()
            if not text:
                continue
            if text.upper() == "NONE":
                continue
            # Skip labels like "Phi:" or "Member Name:" — model echoing group headers
            if text.endswith(":") or (len(text) <= 20 and ":" in text):
                continue
            items.append(text)
    return items


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
        member_names = " and ".join(p.member_id for p in perspectives)

        prompt = DISAGREEMENT_ANALYSIS_PROMPT.format(
            question=question,
            perspectives=perspectives_text,
            member_names=member_names,
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
                    # Only add if we have actual positions (not all placeholders)
                    if current_positions:
                        disagreements.append(current_disagreement)
                    elif current_disagreement.topic:
                        logger.warning(
                            f"Disagreement '{current_disagreement.topic}' had no valid positions (all were placeholders)"
                        )
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

                    # Validate position is not placeholder text
                    placeholder_indicators = [
                        "<their position>",
                        "<position>",
                        "<view>",
                        "<their view>",
                        "their position",
                        "their view",
                        "position here",
                        "view here",
                    ]
                    is_placeholder = any(
                        indicator in position.lower() for indicator in placeholder_indicators
                    )

                    if is_placeholder:
                        # Skip this position - it's placeholder text
                        logger.warning(
                            f"Disagreement analysis returned placeholder text for {member_id}: '{position}'"
                        )
                        continue

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
            if current_positions:
                disagreements.append(current_disagreement)
            else:
                logger.warning(
                    f"Disagreement '{current_disagreement.topic}' had no valid positions (all were placeholders)"
                )

        # Discard disagreements with fewer than 2 distinct member positions —
        # single-position "disagreements" are a model formatting failure, not real conflicts.
        valid = [d for d in disagreements if len(d.positions) >= 2]
        if len(valid) < len(disagreements):
            logger.warning(
                "Dropped %d disagreement(s) with fewer than 2 positions",
                len(disagreements) - len(valid),
            )
        return valid

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
                    value = extract_value(line)
                    # Reject bare numbers — small models sometimes echo the MINORITY_REPORTS count
                    if not value.isdigit():
                        current_report.member_id = value
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

    async def extract_consensus_and_insights(
        self,
        question: str,
        perspectives: list[Perspective],
        synthesis: str,
    ) -> tuple[list[str], list[str]]:
        """Extract consensus points and unique insights via a dedicated LLM call.

        Returns (consensus_points, unique_insights).
        """
        if not perspectives:
            return [], []

        perspectives_text = format_perspectives_for_prompt(perspectives, include_character=False)

        try:
            consensus_prompt = CONSENSUS_POINTS_PROMPT.format(
                question=question,
                perspectives=perspectives_text,
            )
            insights_prompt = UNIQUE_INSIGHTS_PROMPT.format(
                question=question,
                perspectives=perspectives_text,
            )

            consensus_resp, insights_resp = await asyncio.gather(
                self.gateway.complete(
                    model=self.analysis_model,
                    messages=[{"role": "user", "content": consensus_prompt}],
                    temperature=Temperature.ANALYSIS,
                ),
                self.gateway.complete(
                    model=self.analysis_model,
                    messages=[{"role": "user", "content": insights_prompt}],
                    temperature=Temperature.ANALYSIS,
                ),
            )

            logger.info("Consensus raw:\n%s", consensus_resp.content[:400])
            logger.info("Insights raw:\n%s", insights_resp.content[:400])

            consensus_points = _parse_bullet_list(consensus_resp.content)
            unique_insights = _parse_bullet_list(insights_resp.content)

            logger.info(
                "Consensus/insights extraction — %d consensus points, %d unique insights",
                len(consensus_points),
                len(unique_insights),
            )
            return consensus_points, unique_insights
        except Exception as e:
            logger.warning("Failed to extract consensus/insights: %s", e)
            return [], []

    def _parse_consensus_insights(self, response: str) -> tuple[list[str], list[str]]:
        """Parse CONSENSUS_POINTS and UNIQUE_INSIGHTS sections from a single response.

        Handles mixed-case and markdown-headed section labels produced by small models.
        """
        consensus_points: list[str] = []
        unique_insights: list[str] = []

        current_section: str | None = None

        for line in response.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Normalize header: lowercase, strip markdown decoration (#, *, _), collapse separators
            normalized = stripped.lower().lstrip("#*_ ").replace("_", " ")
            if normalized.startswith("consensus point"):
                current_section = "consensus"
            elif normalized.startswith("unique insight"):
                current_section = "insights"
            elif (stripped.startswith("- ") or stripped.startswith("• ")) and current_section:
                text = stripped[2:].strip()
                if text and text.upper() != "NONE":
                    if current_section == "consensus":
                        consensus_points.append(text)
                    elif current_section == "insights":
                        unique_insights.append(text)

        return consensus_points, unique_insights

    def _parse_confidence(self, response: str) -> ConfidenceAssessment:
        """Parse confidence assessment response."""
        overall = 0.5
        consensus = 0.5
        dissent = 0.5
        reasoning = "Unable to assess confidence"

        # Track what we successfully parsed
        parsed_fields = []

        # Log the raw response for debugging (first 500 chars to avoid log spam)
        logger.debug(f"Confidence assessment raw response: {response[:500]}...")

        for line in response.strip().split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check each field with fuzzy matching
            if matches_field(line, "OVERALL_CONFIDENCE"):
                try:
                    overall = clamp(float(extract_value(line)))
                    parsed_fields.append(f"overall={overall:.2f}")
                    logger.debug(f"Parsed OVERALL_CONFIDENCE: {overall}")
                except ValueError as e:
                    logger.warning(f"Failed to parse OVERALL_CONFIDENCE from '{line}': {e}")

            elif matches_field(line, "CONSENSUS_STRENGTH"):
                try:
                    consensus = clamp(float(extract_value(line)))
                    parsed_fields.append(f"consensus={consensus:.2f}")
                    logger.debug(f"Parsed CONSENSUS_STRENGTH: {consensus}")
                except ValueError as e:
                    logger.warning(f"Failed to parse CONSENSUS_STRENGTH from '{line}': {e}")

            elif matches_field(line, "DISSENT_STRENGTH"):
                try:
                    dissent = clamp(float(extract_value(line)))
                    parsed_fields.append(f"dissent={dissent:.2f}")
                    logger.debug(f"Parsed DISSENT_STRENGTH: {dissent}")
                except ValueError as e:
                    logger.warning(f"Failed to parse DISSENT_STRENGTH from '{line}': {e}")

            elif matches_field(line, "REASONING"):
                reasoning = extract_value(line)
                parsed_fields.append("reasoning")
                logger.debug(f"Parsed REASONING: {reasoning[:100]}...")

        # Log summary of what was parsed
        if parsed_fields:
            logger.debug(f"Successfully parsed fields: {', '.join(parsed_fields)}")
        else:
            logger.warning("No confidence fields parsed from response, using defaults (0.5)")

        # Log if any field is still at default value
        if overall == 0.5 and "overall" not in [f.split("=")[0] for f in parsed_fields]:
            logger.warning("OVERALL_CONFIDENCE not parsed, using default 0.5")
        if consensus == 0.5 and "consensus" not in [f.split("=")[0] for f in parsed_fields]:
            logger.warning("CONSENSUS_STRENGTH not parsed, using default 0.5")
        if dissent == 0.5 and "dissent" not in [f.split("=")[0] for f in parsed_fields]:
            logger.warning("DISSENT_STRENGTH not parsed, using default 0.5")

        return ConfidenceAssessment(
            overall=overall,
            consensus_strength=consensus,
            dissent_strength=dissent,
            reasoning=reasoning,
        )

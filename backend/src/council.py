"""
Council orchestration for The Sovereign Council.

Implements the three-stage deliberation process:
1. Collect: Gather independent perspectives from each council member
2. Review: Anonymized peer review and ranking
3. Synthesize: Chairman produces synthesis with preserved dissent
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .config import CouncilConfig, CouncilMember, DegradationConfig, Temperature
from .gateway import GatewayError, InferenceGateway, InferenceResponse, ModelUnavailableError


@dataclass
class Perspective:
    """A council member's perspective on the question."""

    member_id: str
    model: str
    character: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


def format_perspectives_for_prompt(
    perspectives: list[Perspective],
    include_character: bool = True
) -> str:
    """Format perspectives for LLM prompt consumption."""
    if include_character:
        return "\n\n".join(
            f"### {p.member_id} ({p.character})\n{p.content}"
            for p in perspectives
        )
    return "\n\n".join(
        f"### {p.member_id}\n{p.content}"
        for p in perspectives
    )


@dataclass
class Critique:
    """A council member's critique of other perspectives."""

    reviewer_id: str
    rankings: list[str]  # Member IDs in order of quality
    comments: dict[str, str]  # Member ID -> comment


@dataclass
class Disagreement:
    """A fundamental disagreement identified during deliberation."""

    topic: str
    positions: dict[str, str]  # Member ID -> their position
    description: str


@dataclass
class MinorityReport:
    """A dissenting view that was outvoted but preserved."""

    member_id: str
    position: str
    rationale: str


@dataclass
class ConfidenceScore:
    """Confidence assessment for the synthesis."""

    overall: float = 0.5  # 0.0 to 1.0
    consensus_strength: float = 0.5
    dissent_strength: float = 0.5
    reasoning: str = ""


@dataclass
class Synthesis:
    """The chairman's synthesis of the deliberation."""

    content: str
    consensus_points: list[str]
    divisions: list[str]
    unique_insights: list[str]
    confidence: ConfidenceScore | None = None


@dataclass
class Deliberation:
    """
    Complete record of a council deliberation.

    This object belongs entirely to you.
    It can be saved, deleted, encrypted, or forgotten - your choice.
    """

    id: str
    question: str
    perspectives: list[Perspective]
    critiques: list[Critique]
    synthesis: Synthesis
    disagreements: list[Disagreement]
    minority_reports: list[MinorityReport]
    timestamp: datetime
    session_id: str  # Random, not linked to identity

    @classmethod
    def empty(cls, question: str) -> "Deliberation":
        """Create an empty deliberation for a question."""
        return cls(
            id=str(uuid4()),
            question=question,
            perspectives=[],
            critiques=[],
            synthesis=Synthesis(
                content="",
                consensus_points=[],
                divisions=[],
                unique_insights=[],
                confidence=None,
            ),
            disagreements=[],
            minority_reports=[],
            timestamp=datetime.now(),
            session_id=str(uuid4()),
        )


class CouncilOrchestrator:
    """
    Orchestrates the council deliberation process.

    The council should argue, not agree. Dissent is preserved, not suppressed.
    """

    def __init__(
        self,
        gateway: InferenceGateway,
        config: CouncilConfig,
        degradation: DegradationConfig,
        enable_deep_analysis: bool = True,
    ):
        self.gateway = gateway
        self.config = config
        self.degradation = degradation
        self.enable_deep_analysis = enable_deep_analysis
        self._analyzer = None

    def _get_analyzer(self):
        """Lazy-load the analyzer to avoid circular imports."""
        if self._analyzer is None and self.enable_deep_analysis:
            from .analysis import DeliberationAnalyzer

            # Use chairman model for analysis (better suited for analytical tasks)
            # Falls back to first council member if chairman unavailable
            analysis_model = None
            if self.config.chairman:
                analysis_model = self.config.chairman.model
            elif self.config.members:
                analysis_model = self.config.members[0].model

            if analysis_model:
                self._analyzer = DeliberationAnalyzer(self.gateway, analysis_model)
        return self._analyzer

    async def deliberate(
        self,
        question: str,
        on_status: callable = None,
    ) -> Deliberation:
        """
        Conduct a full council deliberation on a question.

        Args:
            question: The user's question
            on_status: Optional callback for status updates

        Returns:
            Complete Deliberation record

        Raises:
            ValueError: If insufficient council members available
        """
        deliberation = Deliberation.empty(question)

        # Stage 1: Collect perspectives
        if on_status:
            on_status("Gathering perspectives from council members...")

        perspectives = await self._collect_perspectives(question)
        deliberation.perspectives = perspectives

        if len(perspectives) < self.degradation.minimum_council_size:
            raise ValueError(
                f"Insufficient council members responded "
                f"({len(perspectives)} < {self.degradation.minimum_council_size}). "
                f"Cannot proceed with meaningful deliberation."
            )

        if len(perspectives) < self.degradation.warn_below_size:
            if on_status:
                on_status(
                    f"Warning: Only {len(perspectives)} perspectives gathered. "
                    f"Epistemic diversity may be reduced."
                )

        # Stage 2: Peer review
        if on_status:
            on_status("Council members reviewing each other's perspectives...")

        critiques = await self._conduct_reviews(question, perspectives)
        deliberation.critiques = critiques

        # Extract disagreements (enhanced if analyzer available)
        analyzer = self._get_analyzer()
        if analyzer:
            if on_status:
                on_status("Analyzing disagreements between perspectives...")
            try:
                disagreements = await analyzer.analyze_disagreements(question, perspectives)
            except Exception:
                # Fall back to basic extraction on error
                disagreements = self._extract_disagreements(perspectives, critiques)
        else:
            disagreements = self._extract_disagreements(perspectives, critiques)
        deliberation.disagreements = disagreements

        # Stage 3: Chairman synthesis
        if on_status:
            on_status("Chairman synthesizing final response...")

        synthesis, minority_reports = await self._synthesize(
            question, perspectives, critiques, disagreements
        )
        deliberation.synthesis = synthesis

        # Enhanced minority report extraction if analyzer available
        if analyzer:
            if on_status:
                on_status("Extracting minority reports...")
            try:
                enhanced_reports = await analyzer.extract_minority_reports(
                    question, perspectives, synthesis.content, critiques
                )
                if enhanced_reports:
                    minority_reports = enhanced_reports
            except Exception:
                pass  # Keep basic minority reports on error

        deliberation.minority_reports = minority_reports

        # Assess confidence if analyzer available
        if analyzer:
            if on_status:
                on_status("Assessing synthesis confidence...")
            try:
                confidence = await analyzer.assess_confidence(
                    question, perspectives, disagreements, synthesis.content
                )
                deliberation.synthesis.confidence = ConfidenceScore(
                    overall=confidence.overall,
                    consensus_strength=confidence.consensus_strength,
                    dissent_strength=confidence.dissent_strength,
                    reasoning=confidence.reasoning,
                )
            except Exception:
                pass  # No confidence score on error

        return deliberation

    async def _collect_perspectives(self, question: str) -> list[Perspective]:
        """Collect perspectives from all council members in parallel."""
        tasks = []
        for member in self.config.members:
            tasks.append(self._get_perspective(member, question))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        perspectives = []
        for result in results:
            if isinstance(result, Perspective):
                perspectives.append(result)
            # Silently skip failed members (logged elsewhere)

        return perspectives

    async def _get_perspective(self, member: CouncilMember, question: str) -> Perspective:
        """Get a single council member's perspective."""
        system_prompt = f"""You are a member of a deliberation council. Your role is to provide your honest perspective on the question asked.

Your character and approach: {member.character}

Provide a thoughtful, well-reasoned response. Be specific and substantive. If you disagree with conventional wisdom, say so. Your perspective should reflect your unique viewpoint."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

        try:
            response = await self.gateway.complete(
                model=member.model,
                messages=messages,
                temperature=member.temperature,
            )
            return Perspective(
                member_id=member.id,
                model=member.model,
                character=member.character,
                content=response.content,
            )
        except ModelUnavailableError:
            raise
        except GatewayError as e:
            raise GatewayError(f"Failed to get perspective from {member.id}: {e}")

    async def _conduct_reviews(
        self, question: str, perspectives: list[Perspective]
    ) -> list[Critique]:
        """Have each council member review others' perspectives (anonymized)."""
        tasks = []
        for reviewer in self.config.members:
            # Only review if this member provided a perspective
            if any(p.member_id == reviewer.id for p in perspectives):
                other_perspectives = [p for p in perspectives if p.member_id != reviewer.id]
                if other_perspectives:
                    tasks.append(
                        self._get_critique(reviewer, question, other_perspectives)
                    )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        critiques = []
        for result in results:
            if isinstance(result, Critique):
                critiques.append(result)

        return critiques

    async def _get_critique(
        self,
        reviewer: CouncilMember,
        question: str,
        perspectives: list[Perspective],
    ) -> Critique:
        """Get a single council member's critique of other perspectives."""
        # Anonymize perspectives
        anonymized = []
        id_mapping = {}
        for i, p in enumerate(perspectives):
            anon_id = f"Response {chr(65 + i)}"  # A, B, C, ...
            id_mapping[anon_id] = p.member_id
            anonymized.append(f"### {anon_id}\n{p.content}")

        perspectives_text = "\n\n".join(anonymized)

        system_prompt = """You are reviewing other council members' responses. The responses are anonymized to prevent bias.

Evaluate each response for:
1. Accuracy and soundness of reasoning
2. Depth of insight
3. Unique perspectives offered
4. Potential blind spots

Rank the responses from best to worst and explain your reasoning briefly for each."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Question: {question}\n\nResponses to evaluate:\n\n{perspectives_text}",
            },
        ]

        try:
            response = await self.gateway.complete(
                model=reviewer.model,
                messages=messages,
                temperature=Temperature.ANALYSIS,
            )

            # Parse rankings from response (simplified - would need more robust parsing)
            rankings = list(id_mapping.values())  # Default order if parsing fails
            comments = {mid: "" for mid in id_mapping.values()}

            return Critique(
                reviewer_id=reviewer.id,
                rankings=rankings,
                comments=comments,
            )
        except (ModelUnavailableError, GatewayError) as e:
            raise GatewayError(f"Failed to get critique from {reviewer.id}: {e}")

    def _extract_disagreements(
        self, perspectives: list[Perspective], critiques: list[Critique]
    ) -> list[Disagreement]:
        """Extract fundamental disagreements from the perspectives."""
        # This is a simplified implementation
        # A full implementation would use NLP to identify semantic disagreements
        disagreements = []

        # Check if rankings significantly differ
        if len(critiques) >= 2:
            first_rankings = critiques[0].rankings
            for critique in critiques[1:]:
                if critique.rankings != first_rankings:
                    disagreements.append(
                        Disagreement(
                            topic="Response quality assessment",
                            positions={
                                critiques[0].reviewer_id: f"Top choice: {first_rankings[0]}",
                                critique.reviewer_id: f"Top choice: {critique.rankings[0]}",
                            },
                            description="Council members disagree on which perspective is strongest.",
                        )
                    )
                    break

        return disagreements

    async def _synthesize(
        self,
        question: str,
        perspectives: list[Perspective],
        critiques: list[Critique],
        disagreements: list[Disagreement],
    ) -> tuple[Synthesis, list[MinorityReport]]:
        """Have the chairman synthesize the deliberation."""
        if not self.config.chairman:
            # Fallback: use first available model
            chairman_model = self.config.members[0].model if self.config.members else None
            if not chairman_model:
                raise ValueError("No chairman or fallback model available")
        else:
            chairman_model = self.config.chairman.model

        # Prepare perspectives summary
        perspectives_text = format_perspectives_for_prompt(perspectives)

        # Prepare disagreements summary
        disagreements_text = ""
        if disagreements:
            disagreements_text = "\n\nIdentified disagreements:\n" + "\n".join(
                f"- {d.topic}: {d.description}" for d in disagreements
            )

        system_prompt = """You are the Chairman of a deliberation council. Your role is to synthesize multiple perspectives into a coherent final response.

Your responsibilities:
1. Identify points of consensus
2. Acknowledge and preserve disagreements - do not smooth them over
3. Highlight unique insights from individual perspectives
4. Produce a synthesis that respects the full range of views
5. Include a "minority report" section if any perspective was significantly outvoted

You are a synthesizer, not an arbiter of truth. If the council is divided, say so honestly."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""Question: {question}

Council Perspectives:
{perspectives_text}
{disagreements_text}

Please provide your synthesis.""",
            },
        ]

        try:
            response = await self.gateway.complete(
                model=chairman_model,
                messages=messages,
                temperature=self.config.chairman.temperature if self.config.chairman else 0.3,
            )

            synthesis = Synthesis(
                content=response.content,
                consensus_points=[],  # Would parse from response
                divisions=[d.topic for d in disagreements],
                unique_insights=[],  # Would parse from response
            )

            # Generate minority reports for outvoted perspectives
            minority_reports = []
            # This would be more sophisticated in practice

            return synthesis, minority_reports

        except ModelUnavailableError:
            # Fallback handling
            if self.config.members:
                fallback_model = self.config.members[0].model
                response = await self.gateway.complete(
                    model=fallback_model,
                    messages=messages,
                    temperature=Temperature.ANALYSIS,
                )
                synthesis = Synthesis(
                    content=f"[Synthesized by fallback model: {fallback_model}]\n\n{response.content}",
                    consensus_points=[],
                    divisions=[d.topic for d in disagreements],
                    unique_insights=[],
                )
                return synthesis, []
            raise

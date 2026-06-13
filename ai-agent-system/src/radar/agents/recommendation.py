from __future__ import annotations

from radar.schemas import NvidiaRecommendation, TechnicalGap
from radar.graph.state import RadarState


def generate_recommendations(state: RadarState) -> tuple[list[TechnicalGap], list[NvidiaRecommendation]]:
    validation = state.get("validation")
    if not validation or not validation.has_minimum_evidence:
        return [], []

    nvidia_context = state.get("nvidia_context", [])
    if not nvidia_context:
        return [], []

    gap = TechnicalGap(
        description="Startup may benefit from NVIDIA startup ecosystem support once AI usage is validated.",
        evidence_ids=validation.supporting_evidence_ids,
        severity="medium",
    )
    recommendation = NvidiaRecommendation(
        technology=nvidia_context[0].technology,
        target_gap=gap.description,
        technical_justification="Initial recommendation based on validated public AI evidence and NVIDIA startup program relevance.",
        business_justification="NVIDIA Inception may support startup nurturing, community access, and go-to-market alignment.",
        priority="medium",
        implementation_complexity="low",
        suggested_next_action="Manually review the evidence before outreach.",
        startup_evidence_ids=validation.supporting_evidence_ids,
        nvidia_knowledge_ids=[nvidia_context[0].id],
    )
    return [gap], [recommendation]

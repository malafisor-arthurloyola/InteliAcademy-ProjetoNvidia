from __future__ import annotations

from radar.schemas import ExecutiveBriefing
from radar.graph.state import RadarState


def generate_briefing(state: RadarState) -> ExecutiveBriefing:
    classification = state.get("classification")
    validation = state.get("validation")
    recommendations = state.get("recommendations", [])

    title = f"Briefing: {state.get('query', 'startup analysis')}"
    classification_label = classification.label if classification else "Inconclusive"
    caveats = []
    if validation and not validation.has_minimum_evidence:
        caveats.append("Insufficient validated public evidence for recommendations.")

    return ExecutiveBriefing(
        title=title,
        summary="Initial automated briefing generated from the current pipeline state.",
        classification=classification_label,
        evidence_ids=[claim.id for claim in state.get("claims", [])],
        recommendations=recommendations,
        caveats=caveats,
        suggested_approach="Review evidence coverage before commercial or technical outreach.",
    )

from __future__ import annotations

from radar.graph.retry_policy import MAX_COLLECTION_ATTEMPTS, has_collection_retry_limit_reached
from radar.graph.state import RadarState
from radar.schemas import ExecutiveBriefing


def generate_briefing(state: RadarState) -> ExecutiveBriefing:
    classification = state.get("classification")
    validation = state.get("validation")
    recommendations = state.get("recommendations", [])

    title = f"Briefing: {state.get('query', 'startup analysis')}"
    classification_label = classification.label if classification else "Inconclusive"
    caveats = []
    if validation and not validation.has_minimum_evidence:
        caveats.append("Insufficient validated public evidence for recommendations.")
    if has_collection_retry_limit_reached(state):
        caveats.append(
            f"Collection retry limit reached after {MAX_COLLECTION_ATTEMPTS} attempts."
        )
    caveats.extend(_collection_error_caveats(state))

    return ExecutiveBriefing(
        title=title,
        summary="Initial automated briefing generated from the current pipeline state.",
        classification=classification_label,
        evidence_ids=[claim.id for claim in state.get("claims", [])],
        recommendations=recommendations,
        caveats=caveats,
        suggested_approach="Review evidence coverage before commercial or technical outreach.",
    )


def _collection_error_caveats(state: RadarState) -> list[str]:
    caveats: list[str] = []
    for error in state.get("errors", []):
        if not error.step.startswith("scraper."):
            continue
        location = f" for {error.source_url}" if error.source_url else ""
        provider = f" via {error.provider}" if error.provider else ""
        caveats.append(
            f"Collection warning at {error.step}{location}{provider}: {error.message}"
        )
    return caveats

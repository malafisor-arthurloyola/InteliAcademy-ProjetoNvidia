from __future__ import annotations

from radar.graph.state import RadarState


MAX_COLLECTION_ATTEMPTS = 2


def route_after_validation(state: RadarState) -> str:
    validation = state.get("validation")
    attempts = state.get("collection_attempts", 0)

    if validation and validation.has_minimum_evidence:
        return "classifier"
    if attempts < MAX_COLLECTION_ATTEMPTS:
        return "scraper"
    return "briefing"


def route_after_classification(state: RadarState) -> str:
    classification = state.get("classification")
    if not classification or classification.label == "Non-AI":
        return "briefing"
    return "nvidia_rag"

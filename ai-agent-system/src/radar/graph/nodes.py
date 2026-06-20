from __future__ import annotations

from typing import Any

from radar.agents.briefing import generate_briefing
from radar.agents.classifier import classify_startup
from radar.agents.extractor import extract_startups_and_claims
from radar.agents.nvidia_rag import retrieve_nvidia_context
from radar.agents.recommendation import generate_recommendations
from radar.agents.scraper import collect_sources_with_errors
from radar.agents.search_planner import plan_search
from radar.agents.validator import validate_evidence
from radar.graph.state import RadarState


def search_planner_node(state: RadarState) -> dict[str, Any]:
    return {"search_plan": plan_search(state["query"])}


def scraper_node(state: RadarState) -> dict[str, Any]:
    new_sources, new_errors = collect_sources_with_errors(state)
    sources = [*state.get("sources", []), *new_sources]
    errors = [*state.get("errors", []), *new_errors]
    update: dict[str, Any] = {
        "sources": sources,
        "collection_attempts": state.get("collection_attempts", 0) + 1,
    }
    if errors:
        update["errors"] = errors
        update["review_required"] = True
    return update


def extractor_node(state: RadarState) -> dict[str, Any]:
    startups, claims = extract_startups_and_claims(state)
    return {"extracted_startups": startups, "claims": claims}


def validator_node(state: RadarState) -> dict[str, Any]:
    validation = validate_evidence(state)
    return {
        "validation": validation,
        "review_required": validation.requires_human_review,
    }


def classifier_node(state: RadarState) -> dict[str, Any]:
    return {"classification": classify_startup(state)}


def nvidia_rag_node(state: RadarState) -> dict[str, Any]:
    return {"nvidia_context": retrieve_nvidia_context(state)}


def recommendation_node(state: RadarState) -> dict[str, Any]:
    gaps, recommendations = generate_recommendations(state)
    return {"technical_gaps": gaps, "recommendations": recommendations}


def briefing_node(state: RadarState) -> dict[str, Any]:
    return {"briefing": generate_briefing(state)}

from __future__ import annotations

from radar.graph.state import RadarState
from radar.schemas import EvidenceClaim, StartupProfile


AI_MARKERS = ("ai", "ia", "llm", "machine learning", "agents", "automation")
TECH_MARKERS = ("pipeline", "production", "evaluation", "workflow", "data")


def extract_startups_and_claims(state: RadarState) -> tuple[list[StartupProfile], list[EvidenceClaim]]:
    sources = state.get("sources", [])
    claims: list[EvidenceClaim] = []

    for source in sources:
        if not source.text:
            continue

        claim_type = _infer_claim_type(source.text)
        confidence = _infer_claim_confidence(source.source_type, claim_type)
        claims.append(
            EvidenceClaim(
                source_document_id=source.id,
                text=source.text[:500],
                claim_type=claim_type,
                confidence=confidence,
            )
        )

    ai_claims = [claim for claim in claims if claim.claim_type == "ai_usage"]
    profile = StartupProfile(
        name=state.get("query", "Unknown startup"),
        description="MVP profile assembled from collected public evidence.",
        ai_usage_summary=_summarize_ai_usage(ai_claims),
        evidence_ids=[claim.id for claim in claims],
    )
    return [profile], claims


def _infer_claim_type(text: str) -> str:
    normalized_text = text.lower()
    if any(marker in normalized_text for marker in AI_MARKERS):
        return "ai_usage"
    if any(marker in normalized_text for marker in TECH_MARKERS):
        return "technology_signal"
    return "public_signal"


def _infer_claim_confidence(source_type: str, claim_type: str) -> float:
    base_confidence = {
        "official_site": 0.7,
        "blog": 0.6,
        "careers": 0.55,
        "news": 0.55,
        "startup_directory": 0.5,
        "nvidia_documentation": 0.35,
        "other": 0.3,
    }.get(source_type, 0.3)

    if claim_type == "ai_usage":
        return base_confidence
    if claim_type == "technology_signal":
        return max(base_confidence - 0.1, 0.0)
    return max(base_confidence - 0.2, 0.0)


def _summarize_ai_usage(ai_claims: list[EvidenceClaim]) -> str | None:
    if not ai_claims:
        return None
    return "Public evidence mentions AI usage; deeper AI-native dependency still requires validation."

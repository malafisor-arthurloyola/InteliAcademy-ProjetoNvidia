from __future__ import annotations

from radar.schemas import EvidenceClaim, StartupProfile
from radar.graph.state import RadarState


def extract_startups_and_claims(state: RadarState) -> tuple[list[StartupProfile], list[EvidenceClaim]]:
    sources = state.get("sources", [])
    claims: list[EvidenceClaim] = []

    for source in sources:
        if source.text:
            claims.append(
                EvidenceClaim(
                    source_document_id=source.id,
                    text=source.text[:500],
                    claim_type="public_signal",
                    confidence=0.35,
                )
            )

    profile = StartupProfile(
        name=state.get("query", "Unknown startup"),
        description="MVP profile assembled from collected public evidence.",
        evidence_ids=[claim.id for claim in claims],
    )
    return [profile], claims

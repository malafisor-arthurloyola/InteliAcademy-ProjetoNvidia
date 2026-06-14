from __future__ import annotations

from radar.graph.state import RadarState
from radar.schemas import EvidenceClaim, EvidenceValidationReport


MINIMUM_CLAIMS = 2
MINIMUM_AI_CLAIMS = 1
MINIMUM_CONFIDENCE = 0.5


def validate_evidence(state: RadarState) -> EvidenceValidationReport:
    claims = state.get("claims", [])
    sources = state.get("sources", [])
    source_by_id = {source.id: source for source in sources}
    supporting_claims = [
        claim
        for claim in claims
        if claim.confidence >= MINIMUM_CONFIDENCE and claim.source_document_id in source_by_id
    ]
    supporting_ids = [claim.id for claim in supporting_claims]
    supporting_urls = {str(source_by_id[claim.source_document_id].url) for claim in supporting_claims}
    ai_supporting_claims = [claim for claim in supporting_claims if claim.claim_type == "ai_usage"]
    has_minimum_evidence = (
        len(supporting_ids) >= MINIMUM_CLAIMS
        and len(supporting_urls) >= MINIMUM_CLAIMS
        and len(ai_supporting_claims) >= MINIMUM_AI_CLAIMS
    )

    return EvidenceValidationReport(
        has_minimum_evidence=has_minimum_evidence,
        source_quality="medium" if has_minimum_evidence else "weak",
        supporting_evidence_ids=supporting_ids,
        conflicts=[],
        caveats=_build_caveats(
            supporting_ids=supporting_ids,
            supporting_urls=supporting_urls,
            ai_supporting_claims=ai_supporting_claims,
        ),
        requires_human_review=not has_minimum_evidence,
    )


def _build_caveats(
    *,
    supporting_ids: list[str],
    supporting_urls: set[str],
    ai_supporting_claims: list[EvidenceClaim],
) -> list[str]:
    caveats: list[str] = []
    if len(supporting_ids) < MINIMUM_CLAIMS or len(supporting_urls) < MINIMUM_CLAIMS:
        caveats.append("Need at least two independent public evidence claims before recommendations.")
    if len(ai_supporting_claims) < MINIMUM_AI_CLAIMS:
        caveats.append("Need at least one validated AI usage claim before recommendations.")
    return caveats

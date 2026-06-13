from __future__ import annotations

from radar.schemas import EvidenceValidationReport
from radar.graph.state import RadarState


MINIMUM_CLAIMS = 2


def validate_evidence(state: RadarState) -> EvidenceValidationReport:
    claims = state.get("claims", [])
    sources = state.get("sources", [])
    source_by_id = {source.id: source for source in sources}
    supporting_ids = [claim.id for claim in claims if claim.confidence >= 0.3]
    supporting_urls = {
        str(source_by_id[claim.source_document_id].url)
        for claim in claims
        if claim.id in supporting_ids and claim.source_document_id in source_by_id
    }
    has_minimum_evidence = len(supporting_ids) >= MINIMUM_CLAIMS and len(supporting_urls) >= MINIMUM_CLAIMS

    return EvidenceValidationReport(
        has_minimum_evidence=has_minimum_evidence,
        source_quality="medium" if has_minimum_evidence else "weak",
        supporting_evidence_ids=supporting_ids,
        conflicts=[],
        caveats=[] if has_minimum_evidence else ["Need at least two public evidence claims before recommendations."],
        requires_human_review=not has_minimum_evidence,
    )

from radar.agents.briefing import generate_briefing
from radar.graph.retry_policy import MAX_COLLECTION_ATTEMPTS
from radar.schemas import EvidenceValidationReport, PipelineError


def test_briefing_includes_collection_error_caveats() -> None:
    briefing = generate_briefing(
        {
            "query": "startup brasileira validada com IA",
            "errors": [
                PipelineError(
                    step="scraper.fetch",
                    message="fixture missing",
                    recoverable=True,
                    source_url="https://example.com/missing",
                    provider="PageContentAdapter",
                    error_type="ValueError",
                )
            ],
        }
    )

    assert briefing.caveats == [
        (
            "Aviso de coleta em scraper.fetch em https://example.com/missing "
            "via PageContentAdapter: fixture missing"
        )
    ]


def test_briefing_includes_retry_limit_caveat() -> None:
    briefing = generate_briefing(
        {
            "query": "startup brasileira de IA",
            "collection_attempts": MAX_COLLECTION_ATTEMPTS,
            "validation": EvidenceValidationReport(
                has_minimum_evidence=False,
                source_quality="weak",
                supporting_evidence_ids=[],
                conflicts=[],
                caveats=[],
                requires_human_review=True,
            ),
        }
    )

    assert "Limite de tentativas de coleta atingido apos 2 tentativas." in briefing.caveats

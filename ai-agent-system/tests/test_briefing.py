from radar.agents.briefing import generate_briefing
from radar.schemas import PipelineError


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
            "Collection warning at scraper.fetch for https://example.com/missing "
            "via PageContentAdapter: fixture missing"
        )
    ]

import pytest

from radar.scraping.normalizers import normalize_source_payload


def test_normalizer_accepts_api_style_aliases() -> None:
    source = normalize_source_payload(
        {
            "source_url": "https://example.com/startup-ai-platform",
            "type": "official",
            "name": "Example AI Platform",
            "body": "Example startup uses AI agents to automate customer workflows.",
        },
        collection_method="unit_test",
    )

    assert str(source.url) == "https://example.com/startup-ai-platform"
    assert source.domain == "example.com"
    assert source.source_type == "official_site"
    assert source.title == "Example AI Platform"
    assert source.collection_method == "unit_test"


def test_normalizer_rejects_payload_without_traceable_url() -> None:
    with pytest.raises(ValueError, match="URL"):
        normalize_source_payload(
            {"content": "AI evidence without a source should not enter the pipeline."},
            collection_method="unit_test",
        )

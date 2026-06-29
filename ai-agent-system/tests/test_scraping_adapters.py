from __future__ import annotations

import json
from pathlib import Path

import pytest

from radar.schemas import PipelineError, SearchPlan
from radar.scraping.adapters import (
    HtmlPageContentAdapter,
    PageContentAdapter,
    SerpApiSearchAdapter,
    _infer_source_type_from_url,
)
from radar.graph.nodes import scraper_node
from radar.scraping.collectors import SearchBackedCollector


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_serpapi_adapter_normalizes_fixture_results() -> None:
    adapter = SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json"))

    candidates = adapter.search(_search_plan())

    assert len(candidates) == 2
    assert str(candidates[0].url) == "https://example.com/startup-ai-platform"
    assert candidates[0].provider == "serpapi"
    assert candidates[0].rank == 1
    assert candidates[1].source_type == "news"


def test_firecrawl_source_type_infers_official_company_domain() -> None:
    assert (
        _infer_source_type_from_url(
            "https://www.gupy.io/software-de-recrutamento-e-selecao",
            query="gupy",
        )
        == "official_site"
    )
    assert (
        _infer_source_type_from_url(
            "https://startups.com.br/noticias/gupy-ia",
            query="gupy",
        )
        == "news"
    )

def test_page_content_adapter_uses_candidate_metadata() -> None:
    search_adapter = SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json"))
    page_adapter = PageContentAdapter(_load_fixture("page_payloads_ai_startups.json"))
    candidate = search_adapter.search(_search_plan())[0]

    source = page_adapter.fetch(candidate)

    assert str(source.url) == "https://example.com/startup-ai-platform"
    assert source.domain == "example.com"
    assert source.source_type == "official_site"
    assert source.title == "Example AI Platform"
    assert "AI agents" in source.text
    assert source.collection_method == "fixture_page_content"


def test_html_page_content_adapter_extracts_readable_text_without_network() -> None:
    search_adapter = SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json"))
    candidate = search_adapter.search(_search_plan())[0]
    page_adapter = HtmlPageContentAdapter(
        {
            str(candidate.url): {
                "html": """
                <html>
                  <head>
                    <title>HTML Startup AI Platform</title>
                    <style>.hidden { display: none; }</style>
                    <script>window.secret = 'ignore me';</script>
                  </head>
                  <body>
                    <h1>AI agents for operations</h1>
                    <p>Startup uses proprietary workflows and AI automation.</p>
                  </body>
                </html>
                """,
            }
        }
    )

    source = page_adapter.fetch(candidate)

    assert str(source.url) == "https://example.com/startup-ai-platform"
    assert source.domain == "example.com"
    assert source.source_type == "official_site"
    assert source.title == "HTML Startup AI Platform"
    assert "AI agents for operations" in source.text
    assert "proprietary workflows" in source.text
    assert "ignore me" not in source.text
    assert source.collection_method == "offline_html_page"


def test_page_content_adapter_rejects_missing_page_fixture() -> None:
    search_adapter = SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json"))
    page_adapter = PageContentAdapter({})
    candidate = search_adapter.search(_search_plan())[0]

    with pytest.raises(ValueError, match="No fixture page payload"):
        page_adapter.fetch(candidate)


def test_html_page_content_adapter_rejects_payload_without_html() -> None:
    search_adapter = SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json"))
    candidate = search_adapter.search(_search_plan())[0]
    page_adapter = HtmlPageContentAdapter({str(candidate.url): {"title": "No HTML"}})

    with pytest.raises(ValueError, match="must include an html field"):
        page_adapter.fetch(candidate)


def test_search_backed_collector_composes_search_and_page_adapters() -> None:
    collector = SearchBackedCollector(
        search_provider=SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json")),
        page_provider=PageContentAdapter(
            _load_fixture("page_payloads_ai_startups.json")
        ),
    )

    sources = collector.collect(_search_plan())

    assert len(sources) == 2
    assert [source.source_type for source in sources] == ["official_site", "news"]
    assert all(source.text for source in sources)


def test_search_backed_collector_keeps_successes_when_one_page_fails() -> None:
    page_payloads = _load_fixture("page_payloads_ai_startups.json")
    page_payloads.pop("https://news.example.com/example-ai-platform")
    collector = SearchBackedCollector(
        search_provider=SerpApiSearchAdapter(_load_fixture("serpapi_ai_startups.json")),
        page_provider=PageContentAdapter(page_payloads),
    )

    sources, errors = collector.collect_with_errors(_search_plan())

    assert len(sources) == 1
    assert len(errors) == 1
    assert errors[0].step == "scraper.fetch"
    assert errors[0].source_url == "https://news.example.com/example-ai-platform"
    assert errors[0].provider == "PageContentAdapter"
    assert errors[0].recoverable is True


def test_scraper_node_records_collection_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_collect_sources_with_errors(state):
        return [], [
            PipelineError(
                step="scraper.fetch",
                message="fixture missing",
                recoverable=True,
                source_url="https://example.com/missing",
                provider="fixture",
                error_type="ValueError",
            )
        ]

    monkeypatch.setattr(
        "radar.graph.nodes.collect_sources_with_errors",
        fake_collect_sources_with_errors,
    )

    update = scraper_node({"search_plan": _search_plan(), "collection_attempts": 0})

    assert update["sources"] == []
    assert update["collection_attempts"] == 1
    assert update["review_required"] is True
    assert update["errors"][0].source_url == "https://example.com/missing"


def _search_plan() -> SearchPlan:
    return SearchPlan(
        query="startup brasileira validada com IA",
        keywords=["startup", "IA"],
        source_types=["official_site", "news"],
        collection_plan=["fixture search", "fixture page extraction"],
    )


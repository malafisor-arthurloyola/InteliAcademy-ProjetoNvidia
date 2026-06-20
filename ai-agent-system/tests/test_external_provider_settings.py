from __future__ import annotations

import pytest

from radar.schemas import SearchPlan
from radar.scraping.adapters import (
    ConfiguredFirecrawlPageAdapter,
    ConfiguredSerpApiSearchAdapter,
    ExternalProviderCredentialsError,
    ExternalProviderDisabledError,
    SerpApiSearchAdapter,
)
from radar.settings import RadarSettings


def test_external_providers_are_disabled_by_default() -> None:
    settings = RadarSettings()

    assert settings.enable_external_providers is False
    assert settings.provider_mode == "fixture"
    assert settings.search_provider == "fixture"
    assert settings.page_provider == "fixture"


def test_configured_serpapi_adapter_fails_closed_without_external_authorization() -> None:
    adapter = ConfiguredSerpApiSearchAdapter(settings=RadarSettings())

    with pytest.raises(ExternalProviderDisabledError, match="explicit authorization"):
        adapter.search(_search_plan())


def test_configured_firecrawl_adapter_fails_closed_without_external_authorization() -> None:
    candidate = SerpApiSearchAdapter(
        [{"url": "https://example.com", "title": "Example", "snippet": "AI startup"}]
    ).search(_search_plan())[0]
    adapter = ConfiguredFirecrawlPageAdapter(settings=RadarSettings())

    with pytest.raises(ExternalProviderDisabledError, match="explicit authorization"):
        adapter.fetch(candidate)


def test_enabled_external_provider_still_requires_credentials() -> None:
    settings = RadarSettings(enable_external_providers=True, search_provider="serpapi")
    adapter = ConfiguredSerpApiSearchAdapter(settings=settings)

    with pytest.raises(ExternalProviderCredentialsError, match="no API key"):
        adapter.search(_search_plan())


def _search_plan() -> SearchPlan:
    return SearchPlan(
        query="startup brasileira com IA",
        keywords=["startup", "IA"],
        source_types=["official_site"],
        collection_plan=["fixture only"],
    )
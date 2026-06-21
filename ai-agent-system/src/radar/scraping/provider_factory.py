from __future__ import annotations

from radar.scraping.adapters import (
    ConfiguredFirecrawlPageAdapter,
    ConfiguredSerpApiSearchAdapter,
)
from radar.scraping.collectors import SearchBackedCollector, StaticSeedCollector, WebCollector
from radar.settings import RadarSettings, get_settings


class ProviderSelectionError(ValueError):
    """Raised when provider settings describe an unsupported collector setup."""


def build_web_collector(settings: RadarSettings | None = None) -> WebCollector:
    """Build the collector selected by settings without performing network calls."""

    active_settings = settings or get_settings()
    if _uses_fixture_stack(active_settings):
        return StaticSeedCollector()

    if active_settings.search_provider == "serpapi" and active_settings.page_provider == "firecrawl":
        return SearchBackedCollector(
            search_provider=ConfiguredSerpApiSearchAdapter(settings=active_settings),
            page_provider=ConfiguredFirecrawlPageAdapter(settings=active_settings),
        )

    raise ProviderSelectionError(
        "Unsupported provider combination: "
        f"search_provider={active_settings.search_provider}, "
        f"page_provider={active_settings.page_provider}. "
        "Use fixture/fixture for offline tests or serpapi/firecrawl for external collection."
    )


def _uses_fixture_stack(settings: RadarSettings) -> bool:
    return settings.search_provider == "fixture" and settings.page_provider == "fixture"
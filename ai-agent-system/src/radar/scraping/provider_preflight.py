from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from radar.settings import RadarSettings, get_settings


ProviderPreflightStatus = Literal["ready", "blocked", "misconfigured"]


@dataclass(frozen=True)
class ProviderPreflight:
    """Offline diagnosis of the configured scraping provider stack."""

    status: ProviderPreflightStatus
    search_provider: str
    page_provider: str
    external_providers_enabled: bool
    network_required: bool
    missing_credentials: tuple[str, ...] = ()
    messages: tuple[str, ...] = ()

    @property
    def can_collect_without_network(self) -> bool:
        return self.status == "ready" and not self.network_required

    @property
    def requires_user_authorization(self) -> bool:
        return self.network_required and not self.external_providers_enabled


def inspect_provider_setup(settings: RadarSettings | None = None) -> ProviderPreflight:
    """Inspect provider configuration without instantiating clients or calling APIs."""

    active_settings = settings or get_settings()
    search_provider = active_settings.search_provider
    page_provider = active_settings.page_provider

    if search_provider == "fixture" and page_provider == "fixture":
        return ProviderPreflight(
            status="ready",
            search_provider=search_provider,
            page_provider=page_provider,
            external_providers_enabled=active_settings.enable_external_providers,
            network_required=False,
            messages=("Using deterministic fixture providers; no external API calls are required.",),
        )

    if search_provider in ("serpapi", "firecrawl") and page_provider in ("firecrawl", "playwright"):
        return _inspect_external_stack(active_settings)

    return ProviderPreflight(
        status="misconfigured",
        search_provider=search_provider,
        page_provider=page_provider,
        external_providers_enabled=active_settings.enable_external_providers,
        network_required=search_provider != "fixture" or page_provider != "fixture",
        messages=(
            "Unsupported provider combination. Use fixture/fixture for offline tests "
            "or firecrawl/playwright for the controlled external stack.",
        ),
    )


def _inspect_external_stack(settings: RadarSettings) -> ProviderPreflight:
    missing_credentials = _missing_external_credentials(settings, settings.search_provider, settings.page_provider)
    if not settings.enable_external_providers:
        return ProviderPreflight(
            status="blocked",
            search_provider=settings.search_provider,
            page_provider=settings.page_provider,
            external_providers_enabled=False,
            network_required=True,
            missing_credentials=missing_credentials,
            messages=(
                "External scraping providers are selected but blocked by "
                "RADAR_ENABLE_EXTERNAL_PROVIDERS=false.",
                "Do not enable external providers without explicit user authorization.",
            ),
        )

    if missing_credentials:
        return ProviderPreflight(
            status="misconfigured",
            search_provider=settings.search_provider,
            page_provider=settings.page_provider,
            external_providers_enabled=True,
            network_required=True,
            missing_credentials=missing_credentials,
            messages=("External providers are enabled but required API keys are missing.",),
        )

    return ProviderPreflight(
        status="ready",
        search_provider=settings.search_provider,
        page_provider=settings.page_provider,
        external_providers_enabled=True,
        network_required=True,
        messages=(
            "External provider configuration is complete. Running collection would use network/API calls.",
        ),
    )


def _missing_external_credentials(settings: RadarSettings, search_provider: str, page_provider: str) -> tuple[str, ...]:
    missing: list[str] = []
    if search_provider == "serpapi" and not settings.serpapi_api_key:
        missing.append("SERPAPI_API_KEY")
    if not settings.firecrawl_api_key and (search_provider == "firecrawl" or page_provider == "firecrawl"):
        missing.append("FIRECRAWL_API_KEY")
    if not _has_playwright_browser() and page_provider == "playwright":
        missing.append("CHROMIUM_BROWSER")
    return tuple(missing)


def _has_playwright_browser() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            _ = p.chromium.executable_path
            return True
    except Exception:
        return False

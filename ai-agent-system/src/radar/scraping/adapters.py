from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from bs4 import BeautifulSoup

from radar.schemas import SearchPlan, SourceCandidate, SourceDocument
from radar.scraping.normalizers import (
    normalize_collected_page_payload,
    normalize_search_result_payloads,
)
from radar.settings import RadarSettings, get_settings


class ExternalProviderDisabledError(RuntimeError):
    """Raised when code tries to use external providers while offline mode is active."""


class ExternalProviderCredentialsError(RuntimeError):
    """Raised when an enabled external provider has no configured credentials."""


class SerpApiSearchAdapter:
    """Adapt a SerpAPI-like response payload into source candidates.

    This class does not call SerpAPI. It only normalizes an already available
    payload, which keeps tests deterministic and avoids handling secrets here.
    """

    provider = "serpapi"

    def __init__(
        self, payload: Mapping[str, Any] | Sequence[Mapping[str, Any]]
    ) -> None:
        self._payload = payload

    def search(self, plan: SearchPlan) -> list[SourceCandidate]:
        results = _extract_search_results(self._payload)
        return normalize_search_result_payloads(results, provider=self.provider)


class PageContentAdapter:
    """Adapt collected page payloads into source documents."""

    def __init__(
        self,
        payloads_by_url: Mapping[str, Mapping[str, Any]],
        *,
        collection_method: str = "fixture_page_content",
    ) -> None:
        self._payloads_by_url = dict(payloads_by_url)
        self._collection_method = collection_method

    def fetch(self, candidate: SourceCandidate) -> SourceDocument:
        url = str(candidate.url)
        payload = self._payloads_by_url.get(url)
        if payload is None:
            raise ValueError(f"No fixture page payload found for URL: {url}")
        return normalize_collected_page_payload(
            payload,
            collection_method=self._collection_method,
            candidate=candidate,
        )


class HtmlPageContentAdapter:
    """Adapt locally available raw HTML into source documents without network calls."""

    def __init__(
        self,
        payloads_by_url: Mapping[str, Mapping[str, Any]],
        *,
        collection_method: str = "offline_html_page",
    ) -> None:
        self._payloads_by_url = dict(payloads_by_url)
        self._collection_method = collection_method

    def fetch(self, candidate: SourceCandidate) -> SourceDocument:
        url = str(candidate.url)
        payload = self._payloads_by_url.get(url)
        if payload is None:
            raise ValueError(f"No raw HTML page payload found for URL: {url}")

        html = _first_payload_text(payload, ("html", "raw_html", "content"))
        if html is None:
            raise ValueError("Raw HTML page payload must include an html field.")

        title, text = _extract_html_text(html)
        return normalize_collected_page_payload(
            {
                "url": url,
                "title": _first_payload_text(payload, ("title", "name", "headline"))
                or title,
                "text": text,
            },
            collection_method=self._collection_method,
            candidate=candidate,
        )


class ConfiguredSerpApiSearchAdapter:
    """Boundary for future SerpAPI calls, disabled unless explicitly configured."""

    provider = "serpapi"

    def __init__(self, settings: RadarSettings | None = None) -> None:
        self._settings = settings or get_settings()

    def search(self, plan: SearchPlan) -> list[SourceCandidate]:
        _ensure_external_provider_enabled(self._settings, self.provider)
        _ensure_api_key(self._settings.serpapi_api_key, self.provider)
        raise NotImplementedError(
            "SerpAPI network calls are intentionally not implemented until external "
            "API usage is explicitly authorized."
        )


class FirecrawlSearchAdapter:
    """Search the web via Firecrawl's search API."""

    provider = "firecrawl"

    def __init__(self, settings: RadarSettings | None = None) -> None:
        self._settings = settings or get_settings()

    def search(self, plan: SearchPlan) -> list[SourceCandidate]:
        _ensure_external_provider_enabled(self._settings, self.provider)
        _ensure_api_key(self._settings.firecrawl_api_key, self.provider)

        from firecrawl import Firecrawl

        client = Firecrawl(api_key=self._settings.firecrawl_api_key)
        response = client.search(
            query=plan.query,
            origin="api",
            limit=10,
        )

        raw_results = response.get("data", [])
        candidates = []
        for i, item in enumerate(raw_results):
            url = item.get("url") or item.get("link")
            if not url:
                continue
            candidates.append(
                _firecrawl_result_to_candidate(item, url, i + 1)
            )
        return normalize_search_result_payloads(
            [_candidate_to_payload(c) for c in candidates],
            provider=self.provider,
        )


class FirecrawlPageAdapter:
    """Fetch page content via Firecrawl's scrape API."""

    provider = "firecrawl"

    def __init__(self, settings: RadarSettings | None = None) -> None:
        self._settings = settings or get_settings()

    def fetch(self, candidate: SourceCandidate) -> SourceDocument:
        _ensure_external_provider_enabled(self._settings, self.provider)
        _ensure_api_key(self._settings.firecrawl_api_key, self.provider)

        from firecrawl import Firecrawl

        client = Firecrawl(api_key=self._settings.firecrawl_api_key)
        response = client.scrape_url(
            url=str(candidate.url),
            formats=["markdown", "rawHtml"],
            only_main_content=True,
        )

        data = response.get("data", {})
        markdown = data.get("markdown", "")
        raw_html = data.get("rawHtml", "")

        if not markdown and raw_html:
            _, text = _extract_html_text(raw_html)
        else:
            text = markdown or ""

        title = (
            data.get("metadata", {}).get("title")
            or data.get("title")
            or candidate.title
        )

        payload = {
            "url": str(candidate.url),
            "title": title,
            "text": text,
            "source_type": _infer_source_type(candidate),
        }
        return normalize_collected_page_payload(
            payload,
            collection_method="firecrawl_scrape",
            candidate=candidate,
        )


def _first_payload_text(
    payload: Mapping[str, Any], keys: tuple[str, ...]
) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_html_text(html: str) -> tuple[str | None, str]:
    soup = BeautifulSoup(html, "html.parser")
    for noisy_tag in soup(("script", "style", "noscript")):
        noisy_tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
    text = "\n".join(line for line in lines if line)
    if not text:
        raise ValueError("Raw HTML page payload must include readable text content.")
    return title, text


def _extract_search_results(
    payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        organic_results = payload.get("organic_results")
        if isinstance(organic_results, list):
            return [result for result in organic_results if isinstance(result, Mapping)]
        return [payload]
    return [result for result in payload if isinstance(result, Mapping)]


def _ensure_external_provider_enabled(settings: RadarSettings, provider: str) -> None:
    if not settings.enable_external_providers:
        raise ExternalProviderDisabledError(
            f"{provider} is disabled. Set RADAR_ENABLE_EXTERNAL_PROVIDERS=true only "
            "after explicit authorization to use external APIs."
        )


def _ensure_api_key(api_key: str | None, provider: str) -> None:
    if not api_key:
        raise ExternalProviderCredentialsError(
            f"{provider} is enabled but no API key was configured."
        )


def _firecrawl_result_to_candidate(item: dict, url: str, rank: int) -> dict:
    return {
        "url": url,
        "title": item.get("title", ""),
        "description": item.get("description", "") or item.get("snippet", ""),
        "source_type": _infer_source_type_from_url(url),
        "rank": rank,
    }


def _candidate_to_payload(candidate: dict) -> dict:
    return {
        "link": candidate["url"],
        "title": candidate["title"],
        "snippet": candidate["description"],
        "kind": candidate.get("source_type", "other"),
    }


def _infer_source_type(candidate: SourceCandidate) -> str:
    """Infer source type from candidate metadata."""
    raw = candidate.raw or {}
    return raw.get("source_type", "other")


def _infer_source_type_from_url(url: str) -> str:
    url_lower = url.lower()
    if any(d in url_lower for d in ("crunchbase", "pitchbook", "startupbase", "distrito")):
        return "startup_directory"
    if any(d in url_lower for d in ("linkedin", "glassdoor")):
        return "careers"
    if any(n in url_lower for n in ("g1.", "globo", "valor", "forbes", "infomoney", "startups")):
        return "news"
    if "nvidia" in url_lower:
        return "nvidia_documentation"
    if any(b in url_lower for b in ("blog.", "/blog", "medium.com")):
        return "blog"
    if any(j in url_lower for j in ("/sobre", "/about", "/quem-somos")):
        return "official_site"
    return "other"

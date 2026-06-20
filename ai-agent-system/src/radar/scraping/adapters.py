from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from radar.schemas import SearchPlan, SourceCandidate, SourceDocument
from radar.scraping.normalizers import (
    normalize_collected_page_payload,
    normalize_search_result_payloads,
)


class SerpApiSearchAdapter:
    """Adapt a SerpAPI-like response payload into source candidates.

    This class does not call SerpAPI. It only normalizes an already available
    payload, which keeps tests deterministic and avoids handling secrets here.
    """

    provider = "serpapi"

    def __init__(self, payload: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> None:
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


def _extract_search_results(
    payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        organic_results = payload.get("organic_results")
        if isinstance(organic_results, list):
            return [result for result in organic_results if isinstance(result, Mapping)]
        return [payload]
    return [result for result in payload if isinstance(result, Mapping)]

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

from radar.schemas import SourceDocument
from radar.schemas.evidence import SourceType


SOURCE_TYPE_ALIASES: dict[str, SourceType] = {
    "official": "official_site",
    "official_site": "official_site",
    "site": "official_site",
    "blog": "blog",
    "careers": "careers",
    "jobs": "careers",
    "founder": "founder_profile",
    "founder_profile": "founder_profile",
    "directory": "startup_directory",
    "startup_directory": "startup_directory",
    "news": "news",
    "nvidia": "nvidia_documentation",
    "nvidia_documentation": "nvidia_documentation",
}


def normalize_source_payload(
    payload: Mapping[str, Any],
    *,
    collection_method: str,
) -> SourceDocument:
    """Convert a raw collector/API payload into the pipeline SourceDocument contract."""

    url = _first_text(payload, ("url", "source_url", "link"))
    text = _first_text(payload, ("text", "content", "body", "markdown"))
    if not url:
        raise ValueError("Raw source payload must include a URL.")
    if not text:
        raise ValueError("Raw source payload must include text content.")

    domain = _first_text(payload, ("domain", "host")) or _domain_from_url(url)
    source_type = _normalize_source_type(_first_text(payload, ("source_type", "type", "kind")))

    return SourceDocument(
        url=url,
        domain=domain,
        source_type=source_type,
        title=_first_text(payload, ("title", "name", "headline")),
        text=text,
        collection_method=collection_method,
    )


def normalize_source_payloads(
    payloads: list[Mapping[str, Any]],
    *,
    collection_method: str,
) -> list[SourceDocument]:
    return [
        normalize_source_payload(payload, collection_method=collection_method)
        for payload in payloads
    ]


def _first_text(payload: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def _normalize_source_type(raw_type: str | None) -> SourceType:
    if not raw_type:
        return "other"
    return SOURCE_TYPE_ALIASES.get(raw_type.strip().lower(), "other")

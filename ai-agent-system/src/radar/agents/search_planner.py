from __future__ import annotations

from radar.schemas import SearchPlan


DEFAULT_SOURCE_TYPES = [
    "official_site",
    "blog",
    "careers",
    "startup_directory",
    "news",
]


def plan_search(query: str) -> SearchPlan:
    keywords = [term.strip() for term in query.replace(",", " ").split() if term.strip()]
    return SearchPlan(
        query=query,
        keywords=keywords or [query],
        source_types=DEFAULT_SOURCE_TYPES,
        collection_plan=[
            "Find official company pages and public startup directory entries.",
            "Collect news and blog pages that mention AI usage, product, customers, funding, or founders.",
            "Preserve URLs and retrieval metadata for every source.",
        ],
    )

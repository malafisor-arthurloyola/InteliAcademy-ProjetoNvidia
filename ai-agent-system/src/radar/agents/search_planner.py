from __future__ import annotations

from radar.schemas import SearchPlan

DEFAULT_SOURCE_TYPES = [
    "official_site",
    "blog",
    "careers",
    "startup_directory",
    "news",
]

_STARTUP_CONTEXT_SUFFIXES = (
    "startup",
    "Brasil startup",
    "empresa tecnologia",
)


def _expand_single_word(query: str) -> list[str]:
    base = query.strip()
    expansions = [base]
    for suffix in _STARTUP_CONTEXT_SUFFIXES:
        expansions.append(f"{base} {suffix}")
    expansions.append(f"{base} AI")
    expansions.append(f"{base} inteligência artificial")
    expansions.append(f"{base} funding founders product")
    return list(dict.fromkeys(expansions))


def plan_search(query: str) -> SearchPlan:
    raw_keywords = [term.strip() for term in query.replace(",", " ").split() if term.strip()]
    is_short = len(raw_keywords) <= 1 and len(query.split()) <= 2

    if is_short:
        keywords = _expand_single_word(query)
        collection_plan = [
            f"Query curta '{query}' — expandindo busca para capturar contexto de startup/IA.",
            "Buscar site oficial, perfil de founders, funding e notícias.",
            "Preservar URLs e metadados de cada fonte.",
        ]
    else:
        keywords = raw_keywords or [query]
        collection_plan = [
            "Find official company pages and public startup directory entries.",
            "Collect news and blog pages that mention AI usage, product, customers, funding, or founders.",
            "Preserve URLs and retrieval metadata for every source.",
        ]

    return SearchPlan(
        query=query,
        keywords=keywords,
        source_types=DEFAULT_SOURCE_TYPES,
        collection_plan=collection_plan,
    )

from __future__ import annotations

from radar.schemas import SearchPlan

DEFAULT_SOURCE_TYPES = [
    "official_site",
    "blog",
    "careers",
    "startup_directory",
    "news",
]


def _expand_single_word(query: str, startup_name: str | None = None) -> list[str]:
    base = query.strip()
    expansions = [base]

    expansions.append(f"{base} IA")
    expansions.append(f"{base} inteligência artificial")
    expansions.append(f"{base} startup")
    expansions.append(f"{base} empresa tecnologia")
    expansions.append(f"{base} AI")
    expansions.append(f"{base} funding founders product")

    if startup_name and startup_name.strip().lower() != base.lower():
        sn = startup_name.strip()
        expansions.append(f"{sn} IA")

    return list(dict.fromkeys(expansions))


def _meaningful_terms(text: str) -> list[str]:
    stopwords = {
        "a", "as", "com", "de", "do", "da", "das", "dos",
        "e", "em", "ia", "o", "os", "para", "que", "um", "uma",
        "startup", "startups", "empresa", "empresas",
    }
    terms = []
    for raw in text.lower().replace("-", " ").replace("_", " ").split():
        t = "".join(c for c in raw if c.isalnum())
        if len(t) >= 3 and t not in stopwords:
            terms.append(t)
    return terms


def _generate_name_queries(
    startup_name: str, query: str
) -> list[str]:
    sn = startup_name.strip()
    if not sn:
        return []

    queries: list[str] = []
    queries.append(sn)
    queries.append(f"{sn} IA")
    queries.append(f"{sn} inteligência artificial")

    terms = _meaningful_terms(query)
    seen_terms: set[str] = set()
    for t in terms:
        if t.lower() not in sn.lower() and t not in seen_terms:
            queries.append(f"{sn} {t}")
            seen_terms.add(t)

    return list(dict.fromkeys(queries))


def _generate_discovery_queries(query: str) -> list[str]:
    base = query.strip()
    if not base:
        base = "startup IA Brasil"

    queries: list[str] = []

    # ── 1. Broad (PT + EN) ──────────────────────────────────────────
    if base not in queries:
        queries.append(base)
    broad_terms = [
        "startups de IA Brasil",
        "AI startups Brazil",
        "inteligência artificial Brasil",
        "empresas IA Brasil",
        "startups brasileiras inteligência artificial",
    ]
    for t in broad_terms:
        if t not in queries:
            queries.append(t)

    # ── 2. Anos recentes ───────────────────────────────────────────
    year_terms = [
        f"{base} 2025",
        f"{base} 2026",
        "startups IA Brasil 2026",
        "AI startups Brazil 2026",
        "inteligência artificial Brasil 2026",
        "inteligência artificial Brasil 2025",
    ]
    for t in year_terms:
        if t not in queries:
            queries.append(t)

    # ── 3. Listas / Rankings ───────────────────────────────────────
    list_terms = [
        '"top 10" startups IA Brasil',
        '"melhores" empresas IA Brasil',
        '"lista" startups inteligência artificial Brasil',
        '"ranking" startups IA Brasil',
        '"top 10" AI startups Brazil',
        '"melhores" startups IA Brasil 2026',
        "maiores startups IA Brasil",
    ]
    for t in list_terms:
        if t not in queries:
            queries.append(t)

    # ── 4. Setores específicos ─────────────────────────────────────
    sector_queries = [
        "startups IA Brasil jurídico",
        "startups IA Brasil fintech",
        "startups IA Brasil saúde",
        "AI startups Brasil produtividade",
        "inteligência artificial Brasil legal",
        "startups IA Brasil education",
        "startups IA Brasil agro",
        "startups IA Brasil logística",
        "startups IA Brasil HR tech",
        "AI startups Brasil edtech",
        "inteligência artificial Brasil fintech",
        "AI startups Brasil healthtech",
    ]
    for t in sector_queries:
        if t not in queries:
            queries.append(t)

    # Detect sector hint from original query — append sector query early
    sector_hints_map = {
        "saude": "startups IA Brasil saúde",
        "saúde": "startups IA Brasil saúde",
        "health": "startups IA Brasil saúde",
        "fintech": "startups IA Brasil fintech",
        "juridico": "startups IA Brasil jurídico",
        "jurídico": "startups IA Brasil jurídico",
        "legal": "startups IA Brasil jurídico",
        "educacao": "startups IA Brasil education",
        "educação": "startups IA Brasil education",
        "edtech": "AI startups Brasil edtech",
        "agro": "startups IA Brasil agro",
        "logistica": "startups IA Brasil logística",
        "logística": "startups IA Brasil logística",
        "recrutamento": "startups IA Brasil HR tech",
        "hr": "startups IA Brasil HR tech",
        "produtividade": "AI startups Brasil produtividade",
    }
    for key, sector_query in sector_hints_map.items():
        if key in base.lower() and sector_query not in queries:
            queries.insert(1, sector_query)
            break

    # ── 5. Tech específica ─────────────────────────────────────────
    tech_queries = [
        "agentes IA Brasil autônomo",
        "LLM Brasil startup",
        "NLP jurídico Brasil",
        "generative AI Brasil",
        "NLP Brasil startup",
        "machine learning Brasil startup",
        "deep learning Brasil startup",
        "visão computacional Brasil startup",
        "processamento linguagem natural Brasil startup",
    ]
    for t in tech_queries:
        if t not in queries:
            queries.append(t)

    # ── 6. Funding / Valuation ─────────────────────────────────────
    funding_queries = [
        "unicórnio IA Brasil",
        "startup IA Brasil valuation",
        "startup IA Brasil R$500M",
        "startup IA Brasil Series B",
        "AI startup Brazil funding 2026",
        "startup IA Brasil investimento",
        "startup IA Brasil seed 2026",
        "startup IA Brasil rodada",
        "AI startup Brazil $1B",
    ]
    for t in funding_queries:
        if t not in queries:
            queries.append(t)

    # ── 7. Diretórios / Curadorias ─────────────────────────────────
    directory_queries = [
        f"site:crunchbase.com {base}",
        f"site:distrito.me {base}",
        f"site:startse.com.br {base} startup",
        f"site:cubo.network {base}",
        f"site:bossainvest.com.br {base}",
        f"site:openstartups.net {base}",
        f"site:latitud.com {base}",
        f"site:inovativa.com.br {base} startup",
        f"site:startupbase.com.br {base}",
        f"site:abstartups.com.br {base}",
    ]
    for t in directory_queries:
        if t not in queries:
            queries.append(t)

    # ── 8. Expansão relacionada ao termo original ──────────────────
    if base.lower() not in {"startup ia brasil", "startup", "ia"}:
        related = [
            f"{base} fundada funding",
            f"{base} inteligência artificial produto",
            f"{base} founders CEO",
            f"{base} startup IA",
        ]
        for t in related:
            if t not in queries:
                queries.append(t)

    return list(dict.fromkeys(queries))


def plan_search(query: str, startup_name: str | None = None, mode: str = "research") -> SearchPlan:
    raw_keywords = [term.strip() for term in query.replace(",", " ").split() if term.strip()]
    is_short = len(raw_keywords) <= 1 and len(query.split()) <= 2

    if mode == "discovery":
        keywords = _generate_discovery_queries(query)
        return SearchPlan(
            query=query,
            keywords=keywords,
            source_types=DEFAULT_SOURCE_TYPES,
            mode=mode,
            collection_plan=[
                f"Modo descoberta: '{query}' — buscando startups em diretórios, Crunchbase, Distrito, notícias.",
                "Extrair nomes, domínios e tecnologias de cada candidato encontrado.",
                "Preservar URLs e metadados de cada fonte para desambiguação posterior.",
            ],
        )

    name_queries = _generate_name_queries(startup_name, query) if startup_name else []

    if is_short:
        keywords = name_queries or _expand_single_word(query, startup_name)
        collection_plan = [
            f"Query curta '{query}' — expandindo busca para capturar contexto de startup/IA.",
            "Buscar site oficial, perfil de founders, funding e notícias.",
            "Preservar URLs e metadados de cada fonte.",
        ]
    else:
        keywords = raw_keywords or [query]
        if name_queries:
            keywords = name_queries + keywords
        collection_plan = [
            "Find official company pages and public startup directory entries.",
            "Collect news and blog pages that mention AI usage, product, customers, funding, or founders.",
            "Preserve URLs and retrieval metadata for every source.",
        ]

    return SearchPlan(
        query=query,
        keywords=keywords,
        source_types=DEFAULT_SOURCE_TYPES,
        mode=mode,
        collection_plan=collection_plan,
    )

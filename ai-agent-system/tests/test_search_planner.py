from __future__ import annotations

from radar.agents.search_planner import _generate_discovery_queries, plan_search
from radar.schemas import SearchPlan


def test_discovery_queries_returns_at_least_40_queries() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    assert len(queries) >= 40, f"Só {len(queries)} queries geradas"


def test_discovery_queries_no_duplicates() -> None:
    queries = _generate_discovery_queries("fintech IA Brasil")
    assert len(queries) == len(set(queries))


def test_discovery_queries_includes_broad_portuguese() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    assert any("startups de IA Brasil" in q for q in queries)


def test_discovery_queries_includes_broad_english() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    assert any("AI startups Brazil" in q for q in queries)


def test_discovery_queries_includes_recent_years() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    assert any("2026" in q for q in queries)
    assert any("2025" in q for q in queries)


def test_discovery_queries_includes_rankings() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    assert any('"top 10"' in q for q in queries)
    assert any('"ranking"' in q for q in queries)
    assert any('"melhores"' in q for q in queries)


def test_discovery_queries_includes_sectors() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    sector_terms = ["jurídico", "fintech", "saúde", "produtividade", "legal", "education", "edtech", "healthtech"]
    found = [t for t in sector_terms if any(t in q for q in queries)]
    assert len(found) >= 6, f"Só {len(found)} setores encontrados: {found}"


def test_discovery_queries_includes_tech_specific() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    tech_terms = ["agentes IA", "LLM", "NLP", "generative AI", "machine learning", "deep learning"]
    assert any(any(t in q for q in queries) for t in tech_terms)


def test_discovery_queries_includes_funding() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    funding_terms = ["unicórnio", "valuation", "Series B", "funding", "investimento", "seed"]
    assert sum(1 for t in funding_terms if any(t in q.lower() for q in queries)) >= 4


def test_discovery_queries_includes_directories() -> None:
    queries = _generate_discovery_queries("startup IA Brasil")
    directory_sites = ["crunchbase", "distrito", "startse", "cubo.network", "openstartups", "latitud"]
    assert any(any(s in q for q in queries) for s in directory_sites)


def test_discovery_queries_respects_sector_hint_saida() -> None:
    queries = _generate_discovery_queries("IA saude Brasil")
    assert any("saúde" in q or "health" in q for q in queries)


def test_discovery_queries_respects_sector_hint_juridico() -> None:
    queries = _generate_discovery_queries("IA jurídico Brasil")
    assert any("jurídico" in q or "legal" in q for q in queries)


def test_discovery_queries_respects_sector_hint_fintech() -> None:
    queries = _generate_discovery_queries("fintech IA Brasil")
    assert any("fintech" in q for q in queries)


def test_plan_search_discovery_includes_mode() -> None:
    plan = plan_search("startup IA Brasil", mode="discovery")
    assert plan.mode == "discovery"
    assert len(plan.keywords) >= 40


def test_plan_search_research_defaults_to_research_mode() -> None:
    plan = plan_search("startup brasileira de IA", startup_name="Enter")
    assert plan.mode == "research"
    assert len(plan.keywords) <= 15


def test_search_plan_mode_field_present() -> None:
    plan = SearchPlan(query="test", keywords=["test"], source_types=["news"], collection_plan=[])
    assert plan.mode == "research"

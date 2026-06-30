from __future__ import annotations

from typing import Any

from radar.agents.briefing import generate_briefing
from radar.agents.classifier import classify_startup
from radar.agents.extractor import extract_startups_and_claims
from radar.agents.nvidia_rag import retrieve_nvidia_context
from radar.agents.recommendation import generate_recommendations
from radar.agents.scraper import collect_sources_with_errors
from radar.agents.search_planner import plan_search
from radar.agents.validator import validate_evidence
from radar.graph.progress import get_tracker
from radar.graph.state import RadarState


def candidate_extractor_node(state: RadarState) -> dict[str, Any]:
    import re
    from urllib.parse import urlparse

    seen: set[str] = set()
    candidates_raw: list[dict[str, str | int]] = []
    query = state.get("query", "")

    # ── Patterns de extração ───────────────────────────────────────
    FUNDING_PATTERN = re.compile(
        r"(?:startup|empresa|plataforma)\s+([A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?)\s+(?:recebe|levanta|anuncia|fecha|conquista|lanca)"
    )
    FUNDING_SHORT_PATTERN = re.compile(
        r"([A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?)\s+(?:recebe|levanta|anuncia.*?funding|fecha.*?seed|recebe.*?R\$|recebe.*?\$|levanta.*?seed)"
    )
    CRUNCHBASE_PATTERN = re.compile(
        r"Crunchbase[:\s]+([A-Z][A-Za-z0-9]+(?:[-\s][A-Z][A-Za-z0-9]+)?)"
    )
    STARTUP_DIRECTORY_PATTERN = re.compile(
        r"(?:startup|empresa)[:\s]+([A-Z][A-Za-z0-9]+(?:[-\s][A-Z][A-Za-z0-9]+)?)"
    )
    ARTICLE_INTRO_PATTERN = re.compile(
        r"(?:Conheça|Conheca|conheça|conheca)\s+a\s+([A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?)"
    )
    RANKING_PATTERN = re.compile(
        r"(?:top|ranking|lista)[^.]*?(?:de\s+)?(?:startups|empresas)[^.]*?:\s*([A-Z][A-Za-z0-9]+)"
    )

    STARTUP_PATTERNS = [
        FUNDING_PATTERN,
        FUNDING_SHORT_PATTERN,
        CRUNCHBASE_PATTERN,
        STARTUP_DIRECTORY_PATTERN,
        ARTICLE_INTRO_PATTERN,
        RANKING_PATTERN,
    ]

    # ── Blacklist de palavras genéricas ────────────────────────────
    GENERIC_NAME_BLOCKLIST: set[str] = {
        "blog", "home", "contato", "sobre", "artigos", "notícias", "noticias",
        "pdf", "portfolio", "portfólio", "login", "signup", "cadastro",
        "download", "upload", "app", "mobile", "web", "saiba", "leia",
        "startupsummit", "startup", "empresa", "empresas", "plataforma",
        "solucao", "solução", "produto", "produtos", "servico", "serviço",
        "carreira", "carreiras", "trabalhe", "vagas", "index", "default",
        "newsletter", "blog", "categorias", "categoria", "tags", "autor",
        "下一页", "上一页", "page", "pages", "article", "articles",
        "privacy", "terms", "cookies", "politica", "política",
    }

    # ── Domínios blocklist (expandido) ─────────────────────────────
    DOMAIN_BLOCKLIST: set[str] = {
        "youtube", "instagram", "facebook", "twitter", "linkedin", "wikipedia",
        "reddit", "tiktok", "medium", "substack", "blogspot", "wordpress",
        "github", "gitlab", "bitbucket", "stackoverflow", "quora",
        "pinterest", "flickr", "vimeo", "dailymotion", "twitch",
        "amazon", "aws", "google", "microsoft", "apple", "netflix",
        "spotify", "dropbox", "notion", "miro", "figma", "canva",
        "whatsapp", "telegram", "discord", "slack", "teams",
    }

    for src in state.get("sources", []):
        title = getattr(src, "title", "") or str(getattr(src, "url", ""))
        snippet = getattr(src, "snippet", "") or ""
        body = getattr(src, "text", "") or ""
        source_url = str(getattr(src, "url", ""))
        combined = f"{title} {snippet} {body[:500]}"

        # Pattern-based extraction
        for pattern in STARTUP_PATTERNS:
            for match in pattern.finditer(combined):
                name = match.group(1).strip()
                name_lower = name.lower()
                if len(name) < 3:
                    continue
                if name_lower in GENERIC_NAME_BLOCKLIST:
                    continue
                if name_lower not in seen:
                    seen.add(name_lower)
                    candidates_raw.append({"startup_name": name, "query": name, "source": source_url, "score": 1})

        # Domain-based extraction
        domain = urlparse(source_url).netloc.lower().removeprefix("www.")
        domain_name = domain.split(".")[0]
        if (
            domain_name
            and domain_name not in DOMAIN_BLOCKLIST
            and domain_name not in GENERIC_NAME_BLOCKLIST
            and len(domain_name) >= 4
            and domain_name.lower() not in seen
        ):
            # Check if domain has a plausible company TLD
            parts = domain.split(".")
            has_company_tld = len(parts) >= 2 and parts[-1] in {
                "com", "com.br", "io", "ai", "co", "org", "net", "app", "tech",
                "br", "me", "dev", "cloud", "digital",
            }
            if has_company_tld:
                seen.add(domain_name.lower())
                candidates_raw.append({
                    "startup_name": domain_name.capitalize(),
                    "query": domain_name,
                    "source": source_url,
                    "score": 2,  # domain-based is stronger evidence
                })

    # ── Cross-reference scoring ────────────────────────────────────
    name_counts: dict[str, int] = {}
    name_sources: dict[str, list[str]] = {}
    for c in candidates_raw:
        name_lower = c["startup_name"].lower()
        name_counts[name_lower] = name_counts.get(name_lower, 0) + 1
        if name_lower not in name_sources:
            name_sources[name_lower] = []
        name_sources[name_lower].append(c["source"])

    # Remove low-quality candidates by score threshold
    MIN_SCORE = 2
    candidates_final: list[dict[str, str]] = []
    seen_final: set[str] = set()

    for c in candidates_raw:
        name_lower = c["startup_name"].lower()
        if name_lower in seen_final:
            continue

        base_score = c["score"]  # type: ignore
        cross_count = name_counts.get(name_lower, 0)
        total_score = base_score + cross_count
        has_directory_source = any(
            "crunchbase" in s or "distrito" in s or "pitchbook" in s or "startse" in s or "cubo" in s
            for s in name_sources.get(name_lower, [])
        )
        if has_directory_source:
            total_score += 2

        if total_score < MIN_SCORE:
            continue

        seen_final.add(name_lower)
        candidates_final.append({
            "startup_name": c["startup_name"],
            "query": c["query"],
            "source": c["source"],
            "score": str(total_score),
        })

    # Order by score descending
    candidates_final.sort(key=lambda x: int(x["score"]), reverse=True)

    if not candidates_final and query.strip():
        candidates_final.append({"startup_name": query.strip(), "query": query.strip(), "source": "query", "score": "0"})

    tracker = get_tracker()
    if tracker:
        names = [c["startup_name"] for c in candidates_final[:8]]
        tracker.set_detail("candidate_extractor", f"{len(candidates_final)} candidatos (filtrados de {len(candidates_raw)}): {', '.join(names)}...")

    return {"candidates": candidates_final}


def search_planner_node(state: RadarState) -> dict[str, Any]:
    plan = plan_search(state["query"], state.get("startup_name"), mode=state.get("mode", "research"))
    tracker = get_tracker()
    if tracker:
        kw = plan.keywords[:4]
        tracker.set_detail("search_planner", f"Planejadas {len(plan.keywords)} queries: {', '.join(kw)}...")
    return {"search_plan": plan}


def scraper_node(state: RadarState) -> dict[str, Any]:
    tracker = get_tracker()
    new_sources, new_errors = collect_sources_with_errors(state)
    sources = [*state.get("sources", []), *new_sources]
    errors = [*state.get("errors", []), *new_errors]
    if tracker:
        urls = [str(s.url) for s in new_sources[:3]]
        detail = f"Coletadas {len(new_sources)} fontes: {', '.join(urls)}..."
        if new_errors:
            detail += f" | {len(new_errors)} erro(s)"
        tracker.set_detail("scraper", detail)
    update: dict[str, Any] = {
        "sources": sources,
        "collection_attempts": state.get("collection_attempts", 0) + 1,
    }
    if errors:
        update["errors"] = errors
        update["review_required"] = True
    return update


def extractor_node(state: RadarState) -> dict[str, Any]:
    startups, claims = extract_startups_and_claims(state)
    tracker = get_tracker()
    if tracker:
        ai_claims = sum(1 for c in claims if c.claim_type == "ai_usage")
        techs = set()
        for c in claims:
            if c.claim_type == "ai_usage":
                for kw in ("llm", "agent", "nlp", "ml", "deep", "neural", "gpt", "openai"):
                    if kw in c.text.lower():
                        techs.add(kw)
        detail = f"{len(claims)} claims extraidas: {ai_claims} IA"
        if techs:
            detail += f" ({', '.join(sorted(techs)[:5])})"
        tracker.set_detail("extractor", detail)
    return {"extracted_startups": startups, "claims": claims}


def validator_node(state: RadarState) -> dict[str, Any]:
    validation = validate_evidence(state)
    tracker = get_tracker()
    if tracker:
        total = len(state.get("claims", []))
        aprovadas = len(validation.supporting_evidence_ids)
        rejeitadas = total - aprovadas
        detail = f"{aprovadas} aprovadas, {rejeitadas} rejeitadas | qualidade: {validation.source_quality}"
        tracker.set_detail("validator", detail)
    return {
        "validation": validation,
        "review_required": validation.requires_human_review,
    }


def classifier_node(state: RadarState) -> dict[str, Any]:
    classification = classify_startup(state)
    tracker = get_tracker()
    if tracker:
        detail = f"Classificacao: {classification.label} | Score: {classification.confidence:.2f}"
        tracker.set_detail("classifier", detail)
    return {"classification": classification}


def nvidia_rag_node(state: RadarState) -> dict[str, Any]:
    context = retrieve_nvidia_context(state)
    tracker = get_tracker()
    if tracker:
        techs = sorted(set(c.technology for c in context)) if context else []
        detail = f"{len(context)} chunks relevantes" + (f": {', '.join(techs[:5])}" if techs else "")
        tracker.set_detail("nvidia_rag", detail)
    return {"nvidia_context": context}


def recommendation_node(state: RadarState) -> dict[str, Any]:
    gaps, recommendations = generate_recommendations(state)
    tracker = get_tracker()
    if tracker:
        techs = [r.technology for r in recommendations[:4]]
        detail = f"{len(recommendations)} recomendacoes: {', '.join(techs)}..."
        tracker.set_detail("recommendation", detail)
    return {"technical_gaps": gaps, "recommendations": recommendations}


def briefing_node(state: RadarState) -> dict[str, Any]:
    briefing = generate_briefing(state)
    tracker = get_tracker()
    if tracker:
        tracker.set_detail("briefing", "Relatorio executivo gerado com sucesso")
    return {"briefing": briefing}

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
    candidates: list[dict[str, str]] = []
    query = state.get("query", "")

    STARTUP_PATTERNS = [
        re.compile(r"(?:startup|empresa|plataforma)\s+([A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?)\s+(?:recebe|levanta|anuncia|fecha|conquista|lanca)"),
        re.compile(r"([A-Z][A-Za-z0-9]+(?:\s[A-Z][A-Za-z0-9]+)?)\s+(?:recebe|levanta|anuncia\s+.*?funding|fecha\s+.*?seed)"),
        re.compile(r"Crunchbase[:\s]+([A-Z][A-Za-z0-9]+(?:[-\s][A-Z][A-Za-z0-9]+)?)"),
    ]
    DOMAIN_BLOCKLIST = {"youtube", "instagram", "facebook", "twitter", "linkedin", "wikipedia", "reddit"}

    for src in state.get("sources", []):
        title = getattr(src, "title", "") or str(getattr(src, "url", ""))
        snippet = getattr(src, "snippet", "") or ""
        body = getattr(src, "text", "") or ""
        combined = f"{title} {snippet} {body[:500]}"

        for pattern in STARTUP_PATTERNS:
            for match in pattern.finditer(combined):
                name = match.group(1).strip()
                if len(name) >= 3 and name.lower() not in seen:
                    seen.add(name.lower())
                    candidates.append({"startup_name": name, "query": name, "source": str(getattr(src, "url", ""))})

        domain = urlparse(str(getattr(src, "url", ""))).netloc.lower().removeprefix("www.")
        domain_name = domain.split(".")[0]
        if domain_name not in DOMAIN_BLOCKLIST and len(domain_name) >= 4 and domain_name.lower() not in seen:
            seen.add(domain_name.lower())
            candidates.append({"startup_name": domain_name.capitalize(), "query": domain_name, "source": str(getattr(src, "url", ""))})

    if not candidates and query.strip():
        candidates.append({"startup_name": query.strip(), "query": query.strip(), "source": "query"})

    tracker = get_tracker()
    if tracker:
        names = [c["startup_name"] for c in candidates[:8]]
        tracker.set_detail("candidate_extractor", f"{len(candidates)} candidatos: {', '.join(names)}...")

    return {"candidates": candidates}


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

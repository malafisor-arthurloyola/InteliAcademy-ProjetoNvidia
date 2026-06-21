from __future__ import annotations

from radar.graph.state import RadarState
from radar.rag.retriever import ensure_seeded, retrieve
from radar.schemas import NvidiaKnowledgeChunk


def retrieve_nvidia_context(state: RadarState) -> list[NvidiaKnowledgeChunk]:
    classification = state.get("classification")
    if not classification or classification.label == "Non-AI":
        return []

    validation = state.get("validation")
    if not validation or not validation.has_minimum_evidence:
        return []

    profiles = state.get("extracted_startups", [])
    if not profiles:
        return []

    profile = profiles[0]
    query_parts = []
    if profile.sector:
        query_parts.append(f"sector: {profile.sector}")
    if profile.product:
        query_parts.append(f"product: {profile.product}")
    if profile.cited_technologies:
        query_parts.append(f"technologies: {', '.join(profile.cited_technologies)}")
    if profile.ai_usage_summary:
        query_parts.append(f"ai_usage: {profile.ai_usage_summary}")

    supported_claims = [
        claim
        for claim in state.get("claims", [])
        if claim.id in (validation.supporting_evidence_ids if validation else [])
    ]
    if supported_claims:
        claim_text = " ".join(c.text for c in supported_claims)
        query_parts.append(f"evidence: {claim_text[:1000]}")

    query = " ".join(query_parts) if query_parts else profile.description or ""
    if not query:
        return []

    ensure_seeded()
    results = retrieve(query, top_k=5)

    chunks: list[NvidiaKnowledgeChunk] = []
    for r in results:
        score = r.get("score", 0.0)
        if score < 0.3:
            continue
        chunk_id = str(r.get("id", "")) if r.get("id") is not None else None
        chunks.append(
                NvidiaKnowledgeChunk(
                    id=chunk_id,
                    technology=r.get("technology", ""),
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    content=r.get("content", ""),
                    relevance_score=score,
                )
            )

    return chunks

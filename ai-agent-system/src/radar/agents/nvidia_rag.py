from __future__ import annotations

import unicodedata
from typing import Any, cast, get_args

from radar.graph.state import RadarState
from radar.rag.retriever import ensure_seeded, retrieve
from radar.schemas import NvidiaKnowledgeChunk
from radar.schemas.recommendation import NvidiaTechnology


NVIDIA_TECHNOLOGIES: set[str] = set(get_args(NvidiaTechnology))

QUERY_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("saude", "health", "healthcare", "medical", "medico", "clinica", "clinical"),
        "healthcare medical clinical NVIDIA Clara",
    ),
    (
        ("voz", "voice", "speech", "audio", "transcricao", "asr", "tts", "call center", "atendimento"),
        "voice speech ASR TTS transcription NVIDIA Riva",
    ),
    (
        ("llm", "generativa", "generative", "chatbot", "assistente", "assistant"),
        "generative AI LLM NVIDIA NIM NVIDIA NeMo TensorRT-LLM",
    ),
    (
        ("agente", "agents", "agent", "workflow", "guardrail", "governanca", "governance"),
        "AI agents workflow governance NeMo Guardrails",
    ),
    (
        ("latencia", "latency", "inferencia", "inference", "serving", "producao", "production"),
        "production inference serving latency Triton TensorRT-LLM",
    ),
    (
        ("dados", "data", "analytics", "tabular", "etl", "pipeline"),
        "data analytics dataframe ETL NVIDIA RAPIDS cuDF cuML",
    ),
    (
        ("robo", "robot", "robotica", "robotics", "simulacao", "simulation"),
        "robotics simulation autonomy NVIDIA Isaac NVIDIA Omniverse",
    ),
    (
        ("seguranca", "security", "cyber", "cybersecurity"),
        "cybersecurity threat detection NVIDIA Morpheus",
    ),
)


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
        if claim.id in validation.supporting_evidence_ids
    ]
    if supported_claims:
        claim_text = " ".join(c.text for c in supported_claims)
        query_parts.append(f"evidence: {claim_text[:1000]}")

    query = " ".join(query_parts) if query_parts else profile.description or ""
    hints = _build_query_hints(query)
    if hints:
        query = f"{query} retrieval_hints: {' '.join(hints)}"
    if not query:
        return []

    ensure_seeded()
    results = retrieve(query, top_k=5)

    chunks: list[NvidiaKnowledgeChunk] = []
    for result in results:
        score = _as_score(result.get("score"))
        if score < 0.3:
            continue

        technology = _as_nvidia_technology(result.get("technology"))
        if technology is None:
            continue

        chunks.append(
            NvidiaKnowledgeChunk(
                id=str(result.get("id", "")),
                technology=technology,
                title=_as_text(result.get("title")),
                url=_as_text(result.get("url")),
                content=_as_text(result.get("content")),
                relevance_score=score,
            )
        )

    return chunks


def _build_query_hints(text: str) -> list[str]:
    normalized = _normalize_for_hints(text)
    hints: list[str] = []
    for needles, hint in QUERY_HINTS:
        if any(needle in normalized for needle in needles):
            hints.append(hint)
    return hints


def _normalize_for_hints(text: str) -> str:
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


def _as_score(value: Any) -> float:
    if isinstance(value, int | float):
        return max(0.0, min(float(value), 1.0))
    return 0.0


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_nvidia_technology(value: Any) -> NvidiaTechnology | None:
    if isinstance(value, str) and value in NVIDIA_TECHNOLOGIES:
        return cast(NvidiaTechnology, value)
    return None
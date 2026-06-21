from __future__ import annotations

import re
from typing import Dict, Pattern

from radar.graph.state import RadarState
from radar.schemas import EvidenceClaim, SourceDocument, StartupProfile


SECTOR_PATTERNS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"sa[úu]de|health|healthcare|medical|cl[íi]nica", re.IGNORECASE), "Healthcare"),
    (re.compile(r"finan[cç]as|fintech|banking|pagamentos|finance", re.IGNORECASE), "Fintech"),
    (re.compile(r"agro|agricultura|farming|rural", re.IGNORECASE), "Agrotech"),
    (re.compile(r"educa[cç][ãa]o|learning|edtech|ensino|escola", re.IGNORECASE), "Edtech"),
    (re.compile(r"log[ií]stica|logistics|supply chain|frota", re.IGNORECASE), "Logistics"),
    (re.compile(r"vendas|sales|marketing|crm", re.IGNORECASE), "Sales & Marketing"),
    (re.compile(r"call.center|atendimento|customer.support|contact.center", re.IGNORECASE), "Customer Service"),
    (re.compile(r"jur[ií]dico|legal|law|advocacia", re.IGNORECASE), "Legal"),
    (re.compile(r"rob[oô]|robotics|automa[cç][ãa]o|autonomous", re.IGNORECASE), "Robotics"),
    (re.compile(r"voz|voice|speech|transcri[cç][ãa]o|asr|tts", re.IGNORECASE), "Voice AI"),
    (re.compile(r"data|analytics|business.intelligence|bi[^a-z]", re.IGNORECASE), "Data & Analytics"),
    (re.compile(r"seguran[cç]a|security|cyber|surveillance", re.IGNORECASE), "Cybersecurity"),
    (re.compile(r"jogos|gaming|game|entertainment|m[íi]dia", re.IGNORECASE), "Gaming & Media"),
]

FOUNDER_PATTERN = re.compile(
    r"(?:founder|ceo|cto|co-founder|fundador)[:\s]+([A-Z][a-zà-ú]+(?:\s+[A-Z][a-zà-ú]+){1,3})",
    re.IGNORECASE,
)

FUNDING_PATTERNS: list[Pattern[str]] = [
    re.compile(r"raised\s+\$?([\d,.]+)\s*(million|m|billion|b)?", re.IGNORECASE),
    re.compile(r"(?:seed|series\s*[a-z]|s[ée]rie\s*[a-z])\s*(?:round|funding)?", re.IGNORECASE),
    re.compile(r"(?:us\$|r\$)\s*[\d,]+(?:\s*(?:mi|bi|m|b))?", re.IGNORECASE),
]

TECHNOLOGY_KEYWORDS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"tensorrt|tensor-rt|tensor.rt", re.IGNORECASE), "TensorRT-LLM"),
    (re.compile(r"triton\s+inference", re.IGNORECASE), "Triton Inference Server"),
    (re.compile(r"nemo|nemotron", re.IGNORECASE), "NeMo"),
    (re.compile(r"rapids\s+|cudf|cuml", re.IGNORECASE), "RAPIDS"),
    (re.compile(r"\bcuda\b(?![\w])", re.IGNORECASE), "CUDA"),
    (re.compile(r"omniverse", re.IGNORECASE), "Omniverse"),
    (re.compile(r"isaac\s+(sim|robot)", re.IGNORECASE), "Isaac"),
    (re.compile(r"clara", re.IGNORECASE), "Clara"),
    (re.compile(r"morpheus", re.IGNORECASE), "Morpheus"),
    (re.compile(r"riva", re.IGNORECASE), "Riva"),
    (re.compile(r"nvidia\s+inception", re.IGNORECASE), "NVIDIA Inception"),
    (re.compile(r"ai\s+enterprise", re.IGNORECASE), "AI Enterprise"),
    (re.compile(r"\b(llm|llms)\b|large\s+language\s+model", re.IGNORECASE), "LLM"),
    (re.compile(r"langchain|langgraph", re.IGNORECASE), "LangChain/LangGraph"),
    (re.compile(r"rag|retrieval.augmented", re.IGNORECASE), "RAG"),
    (re.compile(r"vector\s+(database|store|db)|qdrant|chroma|pinecone", re.IGNORECASE), "Vector Database"),
    (re.compile(r"kubernetes|k8s|docker", re.IGNORECASE), "Container/Orch."),
    (re.compile(r"pytorch|tensorflow|jax", re.IGNORECASE), "ML Framework"),
    (re.compile(r"hugging.face|transformers", re.IGNORECASE), "Hugging Face"),
    (re.compile(r"on[ -]?prem(?:ise)?|edge\s+(?:deploy|infer)", re.IGNORECASE), "Edge/On-Prem"),
    (re.compile(r"gpu|inferencia|inference\s+(?:serv|optim)", re.IGNORECASE), "GPU Inference"),
]


def extract_startups_and_claims(state: RadarState) -> tuple[list[StartupProfile], list[EvidenceClaim]]:
    sources = state.get("sources", [])
    query = state.get("query", "Unknown startup")
    claims: list[EvidenceClaim] = []

    for source in sources:
        if not source.text:
            continue

        claim_type = _infer_claim_type(source.text)
        confidence = _infer_claim_confidence(source.source_type, claim_type)
        claims.append(
            EvidenceClaim(
                source_document_id=source.id,
                text=source.text[:500],
                claim_type=claim_type,
                confidence=confidence,
            )
        )

    profile = _build_profile(query, sources, claims)
    return [profile], claims


def _build_profile(
    query: str, sources: list[SourceDocument], claims: list[EvidenceClaim]
) -> StartupProfile:
    all_text = " ".join(s.text for s in sources if s.text)

    sector = _extract_sector(all_text)
    product = _extract_product(all_text)
    founders = _extract_founders(all_text)
    funding = _extract_funding(all_text)
    technologies = _extract_technologies(all_text)

    ai_claims = [c for c in claims if c.claim_type == "ai_usage"]
    usage_summary = _summarize_ai_usage(ai_claims, technologies, sector)

    return StartupProfile(
        name=query,
        sector=sector,
        product=product,
        description="Startup profile assembled from collected public evidence.",
        founders=founders,
        funding=funding,
        cited_technologies=technologies,
        ai_usage_summary=usage_summary,
        evidence_ids=[c.id for c in claims],
    )


def _extract_sector(text: str) -> str | None:
    for pattern, sector in SECTOR_PATTERNS:
        if pattern.search(text):
            return sector
    return None


def _extract_product(text: str) -> str | None:
    product_match = re.search(
        r"(?:product|platform|solution|ferramenta|solu[cç][ãa]o|produto)[:\s]+([A-Z][A-Za-z0-9\s\-]{2,40}?)(?:\s+(?:foi|[eé]|para|que|,|\.|$))",
        text,
    )
    return product_match.group(1).strip() if product_match else None


def _extract_founders(text: str) -> list[str]:
    return list({m.group(1).strip() for m in FOUNDER_PATTERN.finditer(text)})


def _extract_funding(text: str) -> str | None:
    for pattern in FUNDING_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0).strip()[:100]
    return None


def _extract_technologies(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pattern, tech_name in TECHNOLOGY_KEYWORDS:
        if pattern.search(text) and tech_name not in seen:
            found.append(tech_name)
            seen.add(tech_name)
    return found


AI_MARKERS = ("ai", "ia", "llm", "machine learning", "agents", "automation")
TECH_MARKERS = ("pipeline", "production", "evaluation", "workflow", "data")


def _infer_claim_type(text: str) -> str:
    normalized_text = text.lower()
    if any(marker in normalized_text for marker in AI_MARKERS):
        return "ai_usage"
    if any(marker in normalized_text for marker in TECH_MARKERS):
        return "technology_signal"
    return "public_signal"


def _infer_claim_confidence(source_type: str, claim_type: str) -> float:
    base_confidence: Dict[str, float] = {
        "official_site": 0.7,
        "blog": 0.6,
        "careers": 0.55,
        "news": 0.55,
        "startup_directory": 0.5,
        "nvidia_documentation": 0.35,
        "other": 0.3,
    }
    base = base_confidence.get(source_type, 0.3)
    if claim_type == "ai_usage":
        return base
    if claim_type == "technology_signal":
        return max(base - 0.1, 0.0)
    return max(base - 0.2, 0.0)


def _summarize_ai_usage(
    ai_claims: list[EvidenceClaim],
    technologies: list[str],
    sector: str | None,
) -> str | None:
    if not ai_claims:
        return None

    tech_count = len(technologies)
    sector_info = f" no setor de {sector}" if sector else ""

    if tech_count >= 3:
        return (
            f"Evidencias indicam uso intensivo de IA{sector_info}, com "
            f"{tech_count} tecnologias citadas. Potencial perfil AI-Native."
        )
    if tech_count >= 1:
        return (
            f"Public evidence mentions AI usage{sector_info}; "
            f"{tech_count} tecnologia(s) especifica(s) identificada(s)."
        )
    return (
        "Public evidence mentions AI usage{sector_info}; "
        "deeper AI-native dependency still requires validation."
    )

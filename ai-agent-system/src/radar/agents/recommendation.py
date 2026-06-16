from __future__ import annotations

from radar.graph.state import RadarState
from radar.schemas import NvidiaKnowledgeChunk, NvidiaRecommendation, TechnicalGap


TECHNOLOGY_GUIDANCE = {
    "NVIDIA Inception": {
        "gap": "Startup needs ecosystem validation and structured NVIDIA startup support.",
        "technical": "Inception can connect the startup to NVIDIA technical resources and ecosystem guidance while the AI stack matures.",
        "business": "The program supports startup nurturing, community access, and go-to-market alignment.",
        "priority": "medium",
        "complexity": "low",
        "action": "Review public evidence and evaluate fit for NVIDIA Inception outreach.",
    },
    "NVIDIA NIM": {
        "gap": "Validated LLM or agent workflow may need optimized deployment beyond generic API usage.",
        "technical": "NIM can package optimized inference microservices for generative AI workloads.",
        "business": "Optimized inference can reduce deployment friction and support scalable AI-native services.",
        "priority": "high",
        "complexity": "medium",
        "action": "Assess current model deployment path and benchmark NIM for the validated AI workflow.",
    },
    "NeMo Guardrails": {
        "gap": "Validated AI agent or customer workflow may need behavior control and governance.",
        "technical": "NeMo Guardrails can constrain assistant behavior and add policy controls around agent interactions.",
        "business": "Governed agents reduce operational risk for customer-facing or workflow-critical automation.",
        "priority": "high",
        "complexity": "medium",
        "action": "Identify risky agent flows and prototype guardrails for the highest-impact interaction.",
    },
    "NVIDIA Triton Inference Server": {
        "gap": "Production AI workflow may need scalable model serving and latency control.",
        "technical": "Triton standardizes production inference serving and supports scalable deployment patterns.",
        "business": "Better serving infrastructure can improve reliability, latency, and cost predictability.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Map production inference endpoints and evaluate Triton for serving standardization.",
    },
    "NVIDIA RAPIDS": {
        "gap": "Data-heavy AI workflow may need faster analytics or feature pipeline processing.",
        "technical": "RAPIDS accelerates data science and analytics pipelines on GPUs.",
        "business": "Faster data pipelines can shorten experimentation cycles and reduce processing bottlenecks.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Profile tabular or analytics workloads and identify a RAPIDS proof of concept.",
    },
    "NVIDIA Riva": {
        "gap": "Voice or transcription product may need production-grade speech AI capabilities.",
        "technical": "Riva supports speech AI workloads such as ASR, TTS, and voice applications.",
        "business": "Speech AI acceleration can improve user experience in call center, voice, or transcription workflows.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Validate speech workload requirements and evaluate Riva for ASR/TTS components.",
    },
    "NVIDIA Clara": {
        "gap": "Healthcare AI workflow may need domain-specific NVIDIA healthcare tooling.",
        "technical": "Clara supports healthcare and life sciences AI workflows.",
        "business": "Domain-aligned healthcare tooling can reduce adoption friction in regulated or clinical contexts.",
        "priority": "medium",
        "complexity": "high",
        "action": "Review healthcare use case, compliance needs, and potential Clara alignment.",
    },
}


def generate_recommendations(state: RadarState) -> tuple[list[TechnicalGap], list[NvidiaRecommendation]]:
    validation = state.get("validation")
    if not validation or not validation.has_minimum_evidence:
        return [], []

    nvidia_context = state.get("nvidia_context", [])
    if not nvidia_context:
        return [], []

    gaps: list[TechnicalGap] = []
    recommendations: list[NvidiaRecommendation] = []

    for chunk in nvidia_context:
        guidance = TECHNOLOGY_GUIDANCE.get(chunk.technology)
        if not guidance:
            continue

        gap = _build_gap(chunk, guidance["gap"], validation.supporting_evidence_ids)
        gaps.append(gap)
        recommendations.append(
            NvidiaRecommendation(
                technology=chunk.technology,
                target_gap=gap.description,
                technical_justification=guidance["technical"],
                business_justification=guidance["business"],
                priority=guidance["priority"],
                implementation_complexity=guidance["complexity"],
                suggested_next_action=guidance["action"],
                startup_evidence_ids=validation.supporting_evidence_ids,
                nvidia_knowledge_ids=[chunk.id],
            )
        )

    return gaps, recommendations


def _build_gap(
    chunk: NvidiaKnowledgeChunk,
    description: str,
    evidence_ids: list[str],
) -> TechnicalGap:
    severity = "high" if chunk.technology in {"NVIDIA NIM", "NeMo Guardrails"} else "medium"
    return TechnicalGap(
        description=description,
        evidence_ids=evidence_ids,
        severity=severity,
    )

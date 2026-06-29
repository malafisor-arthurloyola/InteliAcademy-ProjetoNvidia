from __future__ import annotations

import unicodedata

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
    "TensorRT-LLM": {
        "gap": "LLM workload may need lower latency and higher throughput inference optimization.",
        "technical": "TensorRT-LLM can optimize LLM inference performance with batching and low-latency serving techniques.",
        "business": "Optimized LLM inference can reduce serving cost and improve responsiveness for AI products.",
        "priority": "high",
        "complexity": "high",
        "action": "Benchmark representative LLM prompts against TensorRT-LLM optimization paths.",
    },
    "NVIDIA RAPIDS": {
        "gap": "Data-heavy AI workflow may need faster analytics or feature pipeline processing.",
        "technical": "RAPIDS accelerates data science and analytics pipelines on GPUs.",
        "business": "Faster data pipelines can shorten experimentation cycles and reduce processing bottlenecks.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Profile tabular or analytics workloads and identify a RAPIDS proof of concept.",
    },
    "cuDF": {
        "gap": "Tabular or dataframe-heavy workflow may need faster preprocessing.",
        "technical": "cuDF accelerates dataframe operations on GPUs and can reduce bottlenecks in tabular data preparation.",
        "business": "Faster dataframe processing can improve iteration speed for analytics-heavy AI products.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Identify dataframe-heavy jobs and compare pandas-style processing against cuDF.",
    },
    "cuML": {
        "gap": "Predictive machine learning workflow may need accelerated model training or experimentation.",
        "technical": "cuML accelerates classical machine learning algorithms on GPUs.",
        "business": "Accelerated model experimentation can shorten validation cycles for data-intensive startups.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Review predictive ML workloads and select one cuML-compatible benchmark.",
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
    "NVIDIA Omniverse": {
        "gap": "Simulation or digital twin workflow may need a stronger 3D collaboration and simulation layer.",
        "technical": "Omniverse supports simulation, 3D workflows, and digital twins for industrial environments.",
        "business": "Better simulation can reduce physical testing cost and speed up robotics or industrial validation.",
        "priority": "medium",
        "complexity": "high",
        "action": "Map simulation assets and evaluate where Omniverse could support digital twin workflows.",
    },
    "NVIDIA Isaac": {
        "gap": "Robotics or autonomy workflow may need NVIDIA tooling for simulation and deployment.",
        "technical": "Isaac supports robotics simulation, autonomy, and robot development workflows.",
        "business": "Robotics-specific tooling can improve validation speed and reduce deployment risk.",
        "priority": "medium",
        "complexity": "high",
        "action": "Review robotics autonomy stack and identify a simulation or deployment proof of concept with Isaac.",
    },
    "NVIDIA NeMo": {
        "gap": "Generative AI workflow may need a structured path for customization, evaluation, and deployment readiness.",
        "technical": "NeMo supports building, customizing, evaluating, and deploying generative AI models.",
        "business": "A stronger generative AI lifecycle can help AI-native startups reduce model risk and improve product differentiation.",
        "priority": "high",
        "complexity": "medium",
        "action": "Review the validated generative AI workflow and identify whether fine-tuning, evaluation, or model governance is the next bottleneck.",
    },
    "CUDA": {
        "gap": "GPU-heavy AI workload may need lower-level acceleration or optimization.",
        "technical": "CUDA is the foundation for NVIDIA GPU acceleration across AI, HPC, analytics, and simulation workloads.",
        "business": "GPU acceleration can improve performance and cost efficiency when workloads outgrow generic CPU-only execution.",
        "priority": "medium",
        "complexity": "high",
        "action": "Profile the validated workload and identify whether CUDA-backed libraries or custom kernels are warranted.",
    },
    "NVIDIA Morpheus": {
        "gap": "Cybersecurity AI workflow may need real-time threat detection or anomaly analysis.",
        "technical": "Morpheus supports GPU-accelerated cybersecurity pipelines for telemetry, anomaly detection, and threat response.",
        "business": "Real-time cybersecurity AI can improve detection speed and strengthen enterprise value propositions.",
        "priority": "medium",
        "complexity": "high",
        "action": "Map the cybersecurity data flow and evaluate whether Morpheus fits the validated detection workload.",
    },
    "NVIDIA AI Enterprise": {
        "gap": "Production AI workflow may need enterprise-grade support, security, and stable deployment infrastructure.",
        "technical": "NVIDIA AI Enterprise packages production AI software including NIM, Triton, RAPIDS, and enterprise support.",
        "business": "Enterprise-grade AI infrastructure can reduce operational risk for startups selling into regulated or large-company environments.",
        "priority": "medium",
        "complexity": "medium",
        "action": "Assess production, security, and support requirements for enterprise customers and evaluate AI Enterprise fit.",
    },
}



TECHNOLOGY_EVIDENCE_PATTERNS: dict[str, tuple[str, ...]] = {
    "NVIDIA Inception": ("ai", "ia", "startup", "empresa", "platform", "plataforma"),
    "NVIDIA NIM": ("llm", "generative", "generativa", "agent", "agente", "chatbot", "inference", "inferencia"),
    "NVIDIA NeMo": ("llm", "generative", "generativa", "fine tuning", "fine-tuning", "agent", "agente", "evaluation"),
    "NeMo Guardrails": ("agent", "agente", "assistant", "assistente", "governance", "governanca", "guardrail", "workflow"),
    "NVIDIA Triton Inference Server": ("inference", "inferencia", "serving", "latency", "latencia", "production", "producao"),
    "TensorRT-LLM": ("llm", "latency", "latencia", "throughput", "inference", "inferencia"),
    "NVIDIA RAPIDS": ("data", "dados", "analytics", "tabular", "etl", "dataframe"),
    "cuDF": ("dataframe", "tabular", "pandas", "etl", "dados"),
    "cuML": ("machine learning", "predictive", "preditivo", "tabular", "modelo"),
    "CUDA": ("gpu", "cuda", "performance", "aceleracao", "acceleration"),
    "NVIDIA Riva": ("voice", "voz", "speech", "audio", "transcricao", "transcription", "asr", "tts", "call center"),
    "NVIDIA Clara": ("healthcare", "saude", "medical", "clinica", "clinical", "life sciences"),
    "NVIDIA Omniverse": ("simulation", "simulacao", "digital twin", "3d", "industrial"),
    "NVIDIA Isaac": ("robot", "robotica", "robotics"),
    "NVIDIA Morpheus": ("cyber", "cybersecurity", "threat", "ameaca", "anomaly", "anomalia"),
    "NVIDIA AI Enterprise": ("production", "producao", "enterprise", "seguranca", "security", "governance", "governanca", "compliance"),
}

def generate_recommendations(state: RadarState) -> tuple[list[TechnicalGap], list[NvidiaRecommendation]]:
    validation = state.get("validation")
    if not validation or not validation.has_minimum_evidence:
        return [], []

    nvidia_context = state.get("nvidia_context", [])
    if not nvidia_context:
        return [], []

    evidence_text = _evidence_text(state, validation.supporting_evidence_ids)
    gaps: list[TechnicalGap] = []
    recommendations: list[NvidiaRecommendation] = []

    for chunk in nvidia_context:
        guidance = TECHNOLOGY_GUIDANCE.get(chunk.technology)
        if not guidance or not _technology_supported(chunk.technology, evidence_text):
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
    severity = "high" if chunk.technology in {"NVIDIA NIM", "NeMo Guardrails", "TensorRT-LLM"} else "medium"
    return TechnicalGap(
        description=description,
        evidence_ids=evidence_ids,
        severity=severity,
    )


def _evidence_text(state: RadarState, evidence_ids: list[str]) -> str:
    supported = [
        claim.text
        for claim in state.get("claims", [])
        if claim.id in evidence_ids
    ]
    profiles = state.get("extracted_startups", [])
    if profiles:
        profile = profiles[0]
        supported.extend(
            part for part in (
                profile.sector,
                profile.product,
                profile.ai_usage_summary,
                " ".join(profile.cited_technologies),
            ) if part
        )
    return _normalize("\n".join(supported))


def _technology_supported(technology: str, evidence_text: str) -> bool:
    patterns = TECHNOLOGY_EVIDENCE_PATTERNS.get(technology, ())
    if technology in {"NVIDIA Inception", "NVIDIA AI Enterprise"}:
        return bool(evidence_text) and any(pattern in evidence_text for pattern in patterns)
    return any(pattern in evidence_text for pattern in patterns)


def _normalize(text: str) -> str:
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )

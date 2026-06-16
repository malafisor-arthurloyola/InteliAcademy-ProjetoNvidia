from __future__ import annotations

from radar.graph.state import RadarState
from radar.schemas import NvidiaKnowledgeChunk


NVIDIA_KNOWLEDGE_BASE = [
    {
        "technology": "NVIDIA Inception",
        "title": "NVIDIA Inception startup program",
        "url": "https://www.nvidia.com/en-us/startups/",
        "content": "Startup program for technical resources, ecosystem support, and go-to-market support.",
        "keywords": ("startup", "ecosystem", "go-to-market", "community", "support"),
        "relevance_score": 0.55,
    },
    {
        "technology": "NVIDIA NIM",
        "title": "NVIDIA NIM for optimized AI inference services",
        "url": "https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/",
        "content": "NIM provides optimized inference microservices for deploying generative AI models.",
        "keywords": ("llm", "generative", "inference", "agents", "automation"),
        "relevance_score": 0.82,
    },
    {
        "technology": "NeMo Guardrails",
        "title": "NeMo Guardrails for safer AI agents",
        "url": "https://github.com/NVIDIA/NeMo-Guardrails",
        "content": "NeMo Guardrails helps control, constrain, and govern conversational assistants and AI agents.",
        "keywords": ("agents", "guardrails", "workflow", "customer", "automation"),
        "relevance_score": 0.78,
    },
    {
        "technology": "NVIDIA Triton Inference Server",
        "title": "Triton Inference Server for production serving",
        "url": "https://developer.nvidia.com/triton-inference-server",
        "content": "Triton standardizes scalable production model serving across frameworks.",
        "keywords": ("production", "serving", "latency", "inference", "pipeline"),
        "relevance_score": 0.76,
    },
    {
        "technology": "NVIDIA RAPIDS",
        "title": "NVIDIA RAPIDS for accelerated data pipelines",
        "url": "https://rapids.ai/",
        "content": "RAPIDS accelerates data science and analytics pipelines with GPUs.",
        "keywords": ("data", "tabular", "analytics", "pipeline", "dataframe"),
        "relevance_score": 0.72,
    },
    {
        "technology": "NVIDIA Riva",
        "title": "NVIDIA Riva for speech AI",
        "url": "https://developer.nvidia.com/riva",
        "content": "Riva supports speech AI use cases such as ASR, TTS, and voice applications.",
        "keywords": ("voice", "speech", "transcription", "asr", "tts", "call center"),
        "relevance_score": 0.72,
    },
    {
        "technology": "NVIDIA Clara",
        "title": "NVIDIA Clara for healthcare and life sciences",
        "url": "https://www.nvidia.com/en-us/clara/",
        "content": "Clara supports healthcare and life sciences AI workflows.",
        "keywords": ("health", "healthcare", "saude", "medical", "life sciences"),
        "relevance_score": 0.72,
    },
]


def retrieve_nvidia_context(state: RadarState) -> list[NvidiaKnowledgeChunk]:
    classification = state.get("classification")
    if not classification or classification.label == "Non-AI":
        return []

    validation = state.get("validation")
    if not validation or not validation.has_minimum_evidence:
        return []

    supported_claims = [
        claim
        for claim in state.get("claims", [])
        if claim.id in validation.supporting_evidence_ids
    ]
    signal_text = " ".join(claim.text.lower() for claim in supported_claims)

    chunks = [_build_chunk(NVIDIA_KNOWLEDGE_BASE[0])]
    for item in NVIDIA_KNOWLEDGE_BASE[1:]:
        if any(keyword in signal_text for keyword in item["keywords"]):
            chunks.append(_build_chunk(item))

    return chunks


def _build_chunk(item: dict[str, object]) -> NvidiaKnowledgeChunk:
    return NvidiaKnowledgeChunk(
        technology=item["technology"],
        title=item["title"],
        url=item["url"],
        content=item["content"],
        relevance_score=item["relevance_score"],
    )

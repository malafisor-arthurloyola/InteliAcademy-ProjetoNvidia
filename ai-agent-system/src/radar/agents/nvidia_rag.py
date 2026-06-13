from __future__ import annotations

from radar.schemas import NvidiaKnowledgeChunk
from radar.graph.state import RadarState


def retrieve_nvidia_context(state: RadarState) -> list[NvidiaKnowledgeChunk]:
    classification = state.get("classification")
    if not classification or classification.label == "Non-AI":
        return []

    return [
        NvidiaKnowledgeChunk(
            technology="NVIDIA Inception",
            title="NVIDIA Inception startup program",
            url="https://www.nvidia.com/en-us/startups/",
            content="Startup program for technical resources, ecosystem support, and go-to-market support.",
            relevance_score=0.5,
        )
    ]

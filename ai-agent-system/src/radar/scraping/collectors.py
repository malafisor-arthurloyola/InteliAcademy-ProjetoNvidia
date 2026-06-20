from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from radar.schemas import SearchPlan, SourceCandidate, SourceDocument
from radar.scraping.normalizers import normalize_source_payloads


class WebCollector(ABC):
    @abstractmethod
    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        """Collect public documents for a search plan."""

class SearchProvider(Protocol):
    def search(self, plan: SearchPlan) -> list[SourceCandidate]:
        """Return candidate URLs for a search plan."""


class PageProvider(Protocol):
    def fetch(self, candidate: SourceCandidate) -> SourceDocument:
        """Return a normalized source document for a candidate URL."""


class SearchBackedCollector(WebCollector):
    """Collector that composes a search adapter with a page-content adapter."""

    def __init__(self, search_provider: SearchProvider, page_provider: PageProvider) -> None:
        self._search_provider = search_provider
        self._page_provider = page_provider

    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        candidates = self._search_provider.search(plan)
        return [self._page_provider.fetch(candidate) for candidate in candidates]

class StaticSeedCollector(WebCollector):
    """Deterministic collector used until real web adapters are added."""

    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        query = plan.query or "startup"
        raw_payloads = [
            {
                "url": "https://www.nvidia.com/en-us/startups/",
                "source_type": "nvidia",
                "title": "NVIDIA Inception",
                "content": (
                    f"Seed evidence placeholder for {query}: public startup analysis "
                    "needs traceable sources."
                ),
            }
        ]

        if any(marker in query.lower() for marker in ("validada", "validated", "duas fontes")):
            raw_payloads.extend(_scenario_payloads(query))

        return normalize_source_payloads(raw_payloads, collection_method="static_seed")


def _scenario_payloads(query: str) -> list[dict[str, str]]:
    normalized_query = query.lower()
    if any(marker in normalized_query for marker in ("dados", "data", "tabular", "analytics")):
        return _data_payloads()
    if any(marker in normalized_query for marker in ("voz", "voice", "transcricao", "transcrição", "call center")):
        return _voice_payloads()
    if any(marker in normalized_query for marker in ("saude", "saúde", "health", "healthcare", "medical")):
        return _healthcare_payloads()
    if any(marker in normalized_query for marker in ("robot", "robotica", "robótica", "simulacao", "simulação")):
        return _robotics_payloads()
    if any(marker in normalized_query for marker in ("latencia", "latência", "inferencia", "inferência")):
        return _latency_payloads()
    return _llm_agent_payloads()


def _llm_agent_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-ai-platform",
            "type": "official",
            "name": "Example AI Platform",
            "body": (
                "Example startup uses AI agents and proprietary operational workflows "
                "to automate customer support."
            ),
        },
        {
            "link": "https://news.example.com/example-ai-platform",
            "kind": "news",
            "headline": "Example startup expands AI product",
            "markdown": (
                "The company reports LLM-based automation, evaluation pipelines, "
                "and production AI workflows."
            ),
        },
    ]


def _data_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-data-platform",
            "type": "official",
            "name": "Example Data Platform",
            "body": (
                "Example startup uses AI to process large tabular datasets, dataframe "
                "analytics, and predictive machine learning features."
            ),
        },
        {
            "link": "https://news.example.com/example-data-platform",
            "kind": "news",
            "headline": "Example startup scales tabular AI analytics",
            "markdown": (
                "The company reports analytics pipelines for high-volume dataframes "
                "and tabular machine learning workloads."
            ),
        },
    ]


def _voice_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-voice-ai",
            "type": "official",
            "name": "Example Voice AI",
            "body": (
                "Example startup uses AI voice assistants for call center automation, "
                "speech transcription, and customer support workflows."
            ),
        },
        {
            "link": "https://news.example.com/example-voice-ai",
            "kind": "news",
            "headline": "Example startup launches voice AI product",
            "markdown": (
                "The product combines ASR, TTS, and LLM summarization for voice and "
                "transcription workflows."
            ),
        },
    ]


def _healthcare_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-health-ai",
            "type": "official",
            "name": "Example Health AI",
            "body": (
                "Example startup uses AI for healthcare workflow automation, medical "
                "document review, and life sciences data analysis."
            ),
        },
        {
            "link": "https://news.example.com/example-health-ai",
            "kind": "news",
            "headline": "Example startup applies AI in healthcare",
            "markdown": (
                "The company reports clinical support workflows, patient data analysis, "
                "and governance needs for medical AI."
            ),
        },
    ]


def _robotics_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-robotics-ai",
            "type": "official",
            "name": "Example Robotics AI",
            "body": (
                "Example startup uses AI robotics, autonomy, simulation, and digital "
                "twins to test industrial robots."
            ),
        },
        {
            "link": "https://news.example.com/example-robotics-ai",
            "kind": "news",
            "headline": "Example startup expands robotics simulation",
            "markdown": (
                "The company reports AI-based 3D simulation workflows for autonomous "
                "robots and robotics deployment."
            ),
        },
    ]


def _latency_payloads() -> list[dict[str, str]]:
    return [
        {
            "source_url": "https://example.com/startup-inference-ai",
            "type": "official",
            "name": "Example Inference AI",
            "body": (
                "Example startup uses AI inference for LLM responses and reports "
                "latency constraints in production serving."
            ),
        },
        {
            "link": "https://news.example.com/example-inference-ai",
            "kind": "news",
            "headline": "Example startup optimizes LLM inference",
            "markdown": (
                "The company reports AI model batching, low-latency inference, and "
                "production model serving requirements."
            ),
        },
    ]



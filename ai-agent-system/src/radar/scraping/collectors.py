from __future__ import annotations

from abc import ABC, abstractmethod

from radar.schemas import SearchPlan, SourceDocument
from radar.scraping.normalizers import normalize_source_payloads


class WebCollector(ABC):
    @abstractmethod
    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        """Collect public documents for a search plan."""


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
            raw_payloads.extend(
                [
                    {
                        "source_url": "https://example.com/startup-ai-platform",
                        "type": "official",
                        "name": "Example AI Platform",
                        "body": (
                            "Example startup uses AI agents and proprietary operational "
                            "data to automate customer workflows."
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
            )

        return normalize_source_payloads(raw_payloads, collection_method="static_seed")

from __future__ import annotations

from abc import ABC, abstractmethod

from radar.schemas import SearchPlan, SourceDocument


class WebCollector(ABC):
    @abstractmethod
    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        """Collect public documents for a search plan."""


class StaticSeedCollector(WebCollector):
    """Deterministic collector used until real web adapters are added."""

    def collect(self, plan: SearchPlan) -> list[SourceDocument]:
        query = plan.query or "startup"
        return [
            SourceDocument(
                url="https://www.nvidia.com/en-us/startups/",
                domain="nvidia.com",
                source_type="nvidia_documentation",
                title="NVIDIA Inception",
                text=f"Seed evidence placeholder for {query}: public startup analysis needs traceable sources.",
                collection_method="static_seed",
            )
        ]

from __future__ import annotations

from radar.graph.state import RadarState
from radar.scraping.collectors import StaticSeedCollector
from radar.schemas import SourceDocument


def collect_sources(state: RadarState) -> list[SourceDocument]:
    plan = state["search_plan"]
    collector = StaticSeedCollector()
    return collector.collect(plan)

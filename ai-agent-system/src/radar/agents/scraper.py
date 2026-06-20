from __future__ import annotations

from radar.graph.state import RadarState
from radar.scraping.collectors import StaticSeedCollector, WebCollector
from radar.schemas import PipelineError, SourceDocument


def collect_sources(state: RadarState) -> list[SourceDocument]:
    plan = state["search_plan"]
    collector = StaticSeedCollector()
    return collector.collect(plan)


def collect_sources_with_errors(
    state: RadarState,
    collector: WebCollector | None = None,
) -> tuple[list[SourceDocument], list[PipelineError]]:
    plan = state["search_plan"]
    active_collector = collector or StaticSeedCollector()
    detailed_collect = getattr(active_collector, "collect_with_errors", None)
    if callable(detailed_collect):
        return detailed_collect(plan)

    try:
        return active_collector.collect(plan), []
    except Exception as exc:
        return [], [
            PipelineError(
                step="scraper.collect",
                message=str(exc),
                recoverable=True,
                provider=active_collector.__class__.__name__,
                error_type=type(exc).__name__,
            )
        ]

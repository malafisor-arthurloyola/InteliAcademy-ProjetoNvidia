from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langgraph.graph import END, StateGraph

from radar.graph.edges import route_after_classification, route_after_validation
from radar.graph.nodes import (
    briefing_node,
    classifier_node,
    extractor_node,
    nvidia_rag_node,
    recommendation_node,
    scraper_node,
    search_planner_node,
    validator_node,
)
from radar.graph.state import RadarState

ProgressCallback = Callable[[str, str, str | None], None]
NodeFunction = Callable[[RadarState], dict[str, Any]]


def _with_progress(
    step_key: str,
    node_fn: NodeFunction,
    progress_callback: ProgressCallback | None,
) -> NodeFunction:
    if progress_callback is None:
        return node_fn

    def wrapped(state: RadarState) -> dict[str, Any]:
        progress_callback(step_key, "running", None)
        try:
            result = node_fn(state)
        except Exception as exc:
            progress_callback(step_key, "failed", str(exc))
            raise
        progress_callback(step_key, "completed", None)
        return result

    return wrapped


def build_graph(progress_callback: ProgressCallback | None = None):
    graph = StateGraph(RadarState)

    graph.add_node(
        "search_planner",
        _with_progress("search_planner", search_planner_node, progress_callback),
    )
    graph.add_node("scraper", _with_progress("scraper", scraper_node, progress_callback))
    graph.add_node(
        "extractor", _with_progress("extractor", extractor_node, progress_callback)
    )
    graph.add_node(
        "validator", _with_progress("validator", validator_node, progress_callback)
    )
    graph.add_node(
        "classifier", _with_progress("classifier", classifier_node, progress_callback)
    )
    graph.add_node(
        "nvidia_rag", _with_progress("nvidia_rag", nvidia_rag_node, progress_callback)
    )
    graph.add_node(
        "recommendation",
        _with_progress("recommendation", recommendation_node, progress_callback),
    )
    graph.add_node("briefing", _with_progress("briefing", briefing_node, progress_callback))

    graph.set_entry_point("search_planner")
    graph.add_edge("search_planner", "scraper")
    graph.add_edge("scraper", "extractor")
    graph.add_edge("extractor", "validator")
    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "scraper": "scraper",
            "classifier": "classifier",
            "briefing": "briefing",
        },
    )
    graph.add_conditional_edges(
        "classifier",
        route_after_classification,
        {
            "nvidia_rag": "nvidia_rag",
            "briefing": "briefing",
        },
    )
    graph.add_edge("nvidia_rag", "recommendation")
    graph.add_edge("recommendation", "briefing")
    graph.add_edge("briefing", END)

    return graph.compile()
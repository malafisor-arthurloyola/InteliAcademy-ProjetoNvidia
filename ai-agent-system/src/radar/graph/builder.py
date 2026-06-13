from __future__ import annotations

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


def build_graph():
    graph = StateGraph(RadarState)

    graph.add_node("search_planner", search_planner_node)
    graph.add_node("scraper", scraper_node)
    graph.add_node("extractor", extractor_node)
    graph.add_node("validator", validator_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("nvidia_rag", nvidia_rag_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("briefing", briefing_node)

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

from radar.graph.builder import build_graph


def test_graph_generates_limited_briefing_when_evidence_is_weak() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup brasileira de IA", "collection_attempts": 0})

    assert result["briefing"].classification == "Inconclusive"
    assert result.get("recommendations", []) == []
    assert result["review_required"] is True


def test_graph_preserves_source_urls() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup brasileira de IA", "collection_attempts": 0})

    assert result["sources"]
    assert str(result["sources"][0].url) == "https://www.nvidia.com/en-us/startups/"

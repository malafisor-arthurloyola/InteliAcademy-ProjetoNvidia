from radar.graph.builder import build_graph


def test_graph_maps_llm_agent_signals_to_specific_nvidia_recommendations() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada com duas fontes de IA", "collection_attempts": 0})

    technologies = {recommendation.technology for recommendation in result["recommendations"]}

    assert "NVIDIA Inception" in technologies
    assert "NVIDIA NIM" in technologies
    assert "NeMo Guardrails" in technologies
    assert "NVIDIA Triton Inference Server" in technologies


def test_recommendations_keep_startup_and_nvidia_evidence_ids() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada com duas fontes de IA", "collection_attempts": 0})

    for recommendation in result["recommendations"]:
        assert recommendation.startup_evidence_ids == result["validation"].supporting_evidence_ids
        assert recommendation.nvidia_knowledge_ids


def test_weak_evidence_still_blocks_specific_nvidia_recommendations() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup brasileira de IA", "collection_attempts": 0})

    assert result.get("nvidia_context", []) == []
    assert result.get("recommendations", []) == []

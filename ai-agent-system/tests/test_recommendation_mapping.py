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


def test_graph_maps_tabular_data_signals_to_rapids_stack() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada de dados tabulares", "collection_attempts": 0})

    technologies = _recommendation_technologies(result)

    assert {"NVIDIA RAPIDS", "cuDF", "cuML"}.issubset(technologies)
    assert "NVIDIA Riva" not in technologies


def test_graph_maps_voice_signals_to_riva_and_nim() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada de voz e call center", "collection_attempts": 0})

    technologies = _recommendation_technologies(result)

    assert "NVIDIA Riva" in technologies
    assert "NVIDIA NIM" in technologies


def test_graph_maps_healthcare_signals_to_clara() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada de saude com IA", "collection_attempts": 0})

    technologies = _recommendation_technologies(result)

    assert "NVIDIA Clara" in technologies


def test_graph_maps_robotics_simulation_signals_to_isaac_and_omniverse() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada de robotica e simulacao", "collection_attempts": 0})

    technologies = _recommendation_technologies(result)

    assert "NVIDIA Isaac" in technologies
    assert "NVIDIA Omniverse" in technologies


def test_graph_maps_latency_signals_to_tensorrt_llm() -> None:
    graph = build_graph()

    result = graph.invoke({"query": "startup validada com latencia de inferencia", "collection_attempts": 0})

    technologies = _recommendation_technologies(result)

    assert "TensorRT-LLM" in technologies
    assert "NVIDIA Triton Inference Server" in technologies


def _recommendation_technologies(result: dict) -> set[str]:
    return {recommendation.technology for recommendation in result["recommendations"]}

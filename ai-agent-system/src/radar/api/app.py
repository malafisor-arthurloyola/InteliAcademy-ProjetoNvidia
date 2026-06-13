from __future__ import annotations

from fastapi import FastAPI

from radar.graph.builder import build_graph


app = FastAPI(title="NVIDIA Startup AI Radar")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs")
def run_analysis(payload: dict[str, str]) -> dict[str, object]:
    query = payload.get("query", "")
    graph = build_graph()
    return graph.invoke({"query": query, "collection_attempts": 0})

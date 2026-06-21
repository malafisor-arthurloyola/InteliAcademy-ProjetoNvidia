from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI

from radar.graph.builder import build_graph
from radar.scraping.provider_preflight import inspect_provider_setup


app = FastAPI(title="NVIDIA Startup AI Radar")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/providers/preflight")
def provider_preflight() -> dict[str, object]:
    return asdict(inspect_provider_setup())


@app.post("/runs")
def run_analysis(payload: dict[str, str]) -> dict[str, object]:
    query = payload.get("query", "")
    graph = build_graph()
    return graph.invoke({"query": query, "collection_attempts": 0})

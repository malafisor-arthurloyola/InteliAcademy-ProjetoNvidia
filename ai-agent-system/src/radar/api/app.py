from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from radar.database import (
    get_all_runs,
    get_all_source_documents,
    get_all_startups,
    get_run_by_id,
    get_run_evidence_claims,
    get_run_recommendations,
    get_run_source_documents,
    get_runs_by_startup,
    get_startup_by_id,
    init_db,
    save_evidence_claim,
    save_recommendation,
    save_run,
    save_source_document,
    save_startup,
    save_validation,
    update_run_startup,
    update_run_status,
)
from radar.graph.builder import build_graph
from radar.scraping.provider_preflight import inspect_provider_setup


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(title="NVIDIA Startup AI Radar", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    query: str


def _persist_run_result(run_id: int, result: dict[str, Any]) -> None:  # noqa: C901
    classification_data = result.get("classification")
    startup_data = (
        result.get("extracted_startups", [None])[0]
        if result.get("extracted_startups")
        else None
    )

    if startup_data:
        startup_dict: dict[str, Any] = {
            **startup_data.model_dump(),
            "classification_label": classification_data.label
            if classification_data
            else None,
            "classification_confidence": classification_data.confidence
            if classification_data
            else None,
            "classification_rationale": classification_data.rationale
            if classification_data
            else None,
        }
        startup_id = save_startup(startup_dict)
        update_run_startup(run_id, startup_id)
        update_run_status(run_id, "completed")

        for src in result.get("sources", []):
            save_source_document(run_id, src.model_dump())

        for claim in result.get("claims", []):
            save_evidence_claim(run_id, claim.model_dump())

        validation = result.get("validation")
        if validation:
            save_validation(run_id, validation.model_dump())

        for rec in result.get("recommendations", []):
            save_recommendation(run_id, rec.model_dump())
    else:
        update_run_status(run_id, "failed")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "NVIDIA Startup AI Radar",
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/providers/preflight")
def provider_preflight() -> dict[str, object]:
    return asdict(inspect_provider_setup())


@app.post("/runs")
def run_analysis(payload: RunRequest) -> dict[str, Any]:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    run_id = save_run(payload.query)
    try:
        graph = build_graph()
        result: dict[str, Any] = graph.invoke(
            {"query": payload.query, "collection_attempts": 0}
        )
        _persist_run_result(run_id, result)
        return jsonable_encoder(
            {"run_id": run_id, "status": "completed", "result": result}
        )
    except Exception as exc:
        update_run_status(run_id, "failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/runs")
def list_runs() -> list[dict[str, Any]]:
    return get_all_runs()


@app.get("/sources")
def list_sources() -> list[dict[str, Any]]:
    return get_all_source_documents()


@app.get("/runs/{run_id}/sources")
def get_run_sources(run_id: int) -> list[dict[str, Any]]:
    if not get_run_by_id(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return get_run_source_documents(run_id)


@app.get("/runs/{run_id}/claims")
def get_run_claims(run_id: int) -> list[dict[str, Any]]:
    if not get_run_by_id(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return get_run_evidence_claims(run_id)


@app.get("/runs/{run_id}")
def get_run(run_id: int) -> dict[str, Any]:
    run = get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run["recommendations"] = get_run_recommendations(run_id)
    return run


@app.get("/startups")
def list_startups() -> list[dict[str, Any]]:
    return get_all_startups()


@app.get("/startups/{startup_id}")
def get_startup(startup_id: str) -> dict[str, Any]:
    startup = get_startup_by_id(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup


@app.get("/startups/{startup_id}/runs")
def list_startup_runs(startup_id: str) -> list[dict[str, Any]]:
    if not get_startup_by_id(startup_id):
        raise HTTPException(status_code=404, detail="Startup not found")
    return get_runs_by_startup(startup_id)

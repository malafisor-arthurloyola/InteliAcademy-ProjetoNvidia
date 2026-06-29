from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from radar.database import (
    get_all_runs,
    get_all_source_documents,
    get_all_startups,
    get_run_by_id,
    get_run_evidence_claims,
    get_run_recommendations,
    get_run_source_documents,
    get_run_steps,
    get_run_validation,
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
from radar.database.connection import get_db_path
from radar.graph.builder import build_graph
from radar.graph.progress import PipelineTracker, set_tracker
from radar.scraping.provider_preflight import inspect_provider_setup


_DB_DIR = Path(__file__).resolve().parent.parent / "database"
_ALEMBIC_INI = _DB_DIR / "alembic.ini"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    if _ALEMBIC_INI.is_file():
        cfg = AlembicConfig(str(_ALEMBIC_INI))
        cfg.set_main_option(
            "script_location",
            str(_DB_DIR / "alembic"),
        )
        alembic_command.upgrade(cfg, "head")
    else:
        init_db()

    _prewarm_vector_store()
    yield


def _prewarm_vector_store() -> None:
    try:
        from radar.rag.retriever import ensure_seeded

        def _warm():
            import logging
            logging.getLogger("radar").info("Pre-warming vector store (sentence-transformers)...")
            ensure_seeded()
            logging.getLogger("radar").info("Vector store pre-warmed successfully.")

        t = threading.Thread(target=_warm, daemon=True)
        t.start()
    except Exception:
        pass


app = FastAPI(title="NVIDIA Startup AI Radar", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    query: str
    startup_name: str | None = None


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

        for src in result.get("sources", []):
            save_source_document(run_id, src.model_dump())

        for claim in result.get("claims", []):
            save_evidence_claim(run_id, claim.model_dump())

        validation = result.get("validation")
        if validation:
            save_validation(run_id, validation.model_dump())

        for rec in result.get("recommendations", []):
            save_recommendation(run_id, rec.model_dump())

        update_run_status(run_id, "completed")
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


@app.get("/health/db")
def health_db() -> dict[str, object]:
    import sqlite3

    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        conn.close()
        size = os.path.getsize(db_path) if os.path.isfile(db_path) else 0
        return {
            "status": "ok",
            "path": db_path,
            "tables": tables,
            "table_count": len(tables),
            "size_bytes": size,
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.get("/providers/preflight")
def provider_preflight() -> dict[str, object]:
    return asdict(inspect_provider_setup())


@app.post("/runs")
def run_analysis(payload: RunRequest) -> dict[str, Any]:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    run_id = save_run(query)
    update_run_status(run_id, "pending")

    tracker = PipelineTracker(run_id)
    tracker.ensure_steps_registered()

    threading.Thread(
        target=_run_pipeline_background,
        args=(run_id, query, tracker, payload.startup_name),
        daemon=True,
    ).start()

    return jsonable_encoder({"run_id": run_id, "status": "pending"})


def _run_pipeline_background(run_id: int, query: str, tracker: PipelineTracker, startup_name: str | None = None) -> None:
    update_run_status(run_id, "running")
    set_tracker(tracker)
    try:
        graph = build_graph()
        initial_state: dict[str, Any] = {"query": query, "collection_attempts": 0}
        if startup_name:
            initial_state["startup_name"] = startup_name
        result: dict[str, Any] = graph.invoke(initial_state)
        _persist_run_result(run_id, result)
    except Exception as exc:
        import logging
        logging.getLogger("radar").error("Pipeline run %d failed: %s", run_id, exc)
        update_run_status(run_id, "failed")
    finally:
        set_tracker(None)


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
    run["steps"] = get_run_steps(run_id)
    run["validation"] = get_run_validation(run_id)
    return run


@app.get("/runs/{run_id}/stream")
def stream_pipeline(run_id: int):
    if not get_run_by_id(run_id):
        raise HTTPException(status_code=404, detail="Run not found")

    def event_stream():
        last_data: Any = None
        while True:
            steps = get_run_steps(run_id)
            if steps != last_data:
                last_data = steps
                yield f"data: {json.dumps(steps)}\n\n"
            statuses = {s["status"] for s in steps}
            if statuses == {"completed"} or ("error" in statuses and not statuses - {"completed", "error"}):
                yield "event: done\ndata: {}\n\n"
                break
            time.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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



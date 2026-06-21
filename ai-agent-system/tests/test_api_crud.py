from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from radar.api.app import app
from radar.database.connection import get_db_path


@pytest.fixture(autouse=True)
def _clean_db() -> None:
    db_path = Path(get_db_path())
    if db_path.exists():
        db_path.unlink()
    from radar.database import init_db

    init_db()
    yield
    if db_path.exists():
        db_path.unlink()


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_points_to_docs_and_health() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["health"] == "/health"
    assert response.json()["docs"] == "/docs"


def test_local_frontend_cors_preflight() -> None:
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_provider_preflight_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/providers/preflight")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["search_provider"] == "fixture"


def test_list_runs_empty() -> None:
    client = TestClient(app)
    response = client.get("/runs")
    assert response.status_code == 200
    assert response.json() == []


def test_list_startups_empty() -> None:
    client = TestClient(app)
    response = client.get("/startups")
    assert response.status_code == 200
    assert response.json() == []


def test_list_sources_empty() -> None:
    client = TestClient(app)
    response = client.get("/sources")
    assert response.status_code == 200
    assert response.json() == []


def test_get_nonexistent_run() -> None:
    client = TestClient(app)
    response = client.get("/runs/999")
    assert response.status_code == 404


def test_get_nonexistent_startup() -> None:
    client = TestClient(app)
    response = client.get("/startups/nonexistent")
    assert response.status_code == 404


def test_run_analysis_with_empty_query_fails() -> None:
    client = TestClient(app)
    response = client.post("/runs", json={"query": ""})
    assert response.status_code == 400
    assert "query must not be empty" in response.text


def test_run_analysis_with_fixture_succeeds() -> None:
    client = TestClient(app)
    response = client.post("/runs", json={"query": "startup brasileira de IA"})
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "completed"


def test_run_analysis_can_be_queried_afterwards() -> None:
    client = TestClient(app)
    post_resp = client.post("/runs", json={"query": "startup brasileira de IA"})
    run_id = post_resp.json()["run_id"]

    get_resp = client.get(f"/runs/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["query"] == "startup brasileira de IA"
    assert get_resp.json()["status"] == "completed"


def test_run_analysis_exposes_sources_and_claims_afterwards() -> None:
    client = TestClient(app)
    post_resp = client.post("/runs", json={"query": "startup brasileira de IA"})
    run_id = post_resp.json()["run_id"]

    sources_resp = client.get(f"/runs/{run_id}/sources")
    claims_resp = client.get(f"/runs/{run_id}/claims")
    all_sources_resp = client.get("/sources")

    assert sources_resp.status_code == 200
    assert claims_resp.status_code == 200
    assert all_sources_resp.status_code == 200
    assert len(sources_resp.json()) >= 1
    assert len(claims_resp.json()) >= 1
    assert sources_resp.json()[0]["claim_count"] >= 1

from __future__ import annotations

from starlette.testclient import TestClient

from radar.api.app import app


def test_provider_preflight_endpoint_reports_default_fixture_stack() -> None:
    client = TestClient(app)

    response = client.get("/providers/preflight")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["search_provider"] == "fixture"
    assert payload["page_provider"] == "fixture"
    assert payload["external_providers_enabled"] is False
    assert payload["network_required"] is False
    assert payload["missing_credentials"] == []
    assert "fixture providers" in payload["messages"][0]

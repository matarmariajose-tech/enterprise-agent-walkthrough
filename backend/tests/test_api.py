from collections.abc import Iterator
from uuid import uuid4

import pytest
from conftest import Runtime
from fastapi.testclient import TestClient

from app.api.dependencies import orchestrator
from app.main import app


@pytest.fixture
def client(runtime: Runtime) -> Iterator[TestClient]:
    app.dependency_overrides[orchestrator] = runtime.agent
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_health_identifies_demo_mode(client: TestClient) -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "demo"}


def test_replay_preserves_proposal_but_uses_a_new_trace(client: TestClient) -> None:
    body = {"query": "Review payments", "region": "LATAM", "correlation_id": str(uuid4())}
    first = client.post("/v1/agent/requests", json=body)
    replay = client.post("/v1/agent/requests", json=body)
    assert first.status_code == replay.status_code == 200
    assert first.json()["action"]["id"] == replay.json()["action"]["id"]
    assert first.json()["trace_id"] != replay.json()["trace_id"]
    assert first.json()["trace_id"] == first.headers["X-Request-ID"]


def test_idempotency_conflict_is_http_409(client: TestClient) -> None:
    body = {"query": "Review payments", "region": "LATAM", "correlation_id": str(uuid4())}
    assert client.post("/v1/agent/requests", json=body).status_code == 200
    response = client.post("/v1/agent/requests", json={**body, "query": "Another question"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "idempotency_conflict"
    assert response.json()["error"]["trace_id"] == response.headers["X-Request-ID"]


def test_headers_cannot_grant_region_access(client: TestClient, runtime: Runtime) -> None:
    response = client.post(
        "/v1/agent/requests",
        json={"query": "Review payments", "region": "EU"},
        headers={
            "X-Tenant-ID": "EU",
            "X-Permissions": "payments:read",
            "X-Request-ID": "client-controlled",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"
    assert response.headers["X-Request-ID"] != "client-controlled"
    assert not runtime.retrieval.calls
    assert not runtime.payments.calls


def test_insufficient_evidence_has_a_safe_http_error(client: TestClient, runtime: Runtime) -> None:
    runtime.retrieval.evidence.clear()
    response = client.post(
        "/v1/agent/requests", json={"query": "Private example question", "region": "LATAM"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "insufficient_evidence"
    assert "Private example question" not in response.text
    assert not runtime.payments.calls


@pytest.mark.parametrize(
    "body",
    [
        {"query": "   ", "region": "LATAM"},
        {"query": "Review payments", "region": "unknown"},
        {"query": "Review payments", "region": "LATAM", "subject": "admin"},
    ],
)
def test_invalid_request_is_http_422(client: TestClient, body: dict[str, str]) -> None:
    assert client.post("/v1/agent/requests", json=body).status_code == 422

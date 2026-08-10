from pathlib import Path

import pytest
from export_api.app import create_app
from export_api.config import APIConfig
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    config = APIConfig(api_key="test-key-123", data_root=str(tmp_path))
    app = create_app(config)
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": "test-key-123"}


def test_health_no_auth(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "export-api"


def test_create_message_job(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/jobs/messages", json={
        "type": "messages",
        "guild_id": "guild_1",
        "params": {"channel": "general"},
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "messages"
    assert data["state"] == "QUEUED"
    assert data["job_id"].startswith("JOB-")


def test_create_member_job(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/jobs/members", json={
        "type": "members",
        "guild_id": "guild_2",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "members"
    assert data["state"] == "QUEUED"


def test_create_both_job(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/jobs/both", json={
        "guild_id": "guild_3",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "both"
    job_ids = data["job_ids"]
    assert len(job_ids) == 2


def test_create_both_order(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/jobs/both", json={
        "guild_id": "guild_order",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    job_ids = data["job_ids"]

    first = client.get(f"/jobs/{job_ids[0]}", headers=auth_headers)
    second = client.get(f"/jobs/{job_ids[1]}", headers=auth_headers)

    assert first.json()["type"] == "messages"
    assert first.json()["state"] == "QUEUED"
    assert second.json()["type"] == "members"
    assert second.json()["state"] == "CREATED"
    assert first.json()["chain_next"] == job_ids[1]


def test_list_jobs(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_1"},
                headers=auth_headers)
    client.post("/jobs/members", json={"type": "members", "guild_id": "g_2"},
                headers=auth_headers)

    resp = client.get("/jobs", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


def test_get_job(client: TestClient, auth_headers: dict[str, str]) -> None:
    create = client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_get"},
                         headers=auth_headers)
    job_id = create.json()["job_id"]

    resp = client.get(f"/jobs/{job_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["job_id"] == job_id


def test_get_job_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/jobs/JOB-20991231-nonono", headers=auth_headers)
    assert resp.status_code == 404


def test_cancel_queued_job(client: TestClient, auth_headers: dict[str, str]) -> None:
    create = client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_cancel"},
                         headers=auth_headers)
    job_id = create.json()["job_id"]

    resp = client.post(f"/jobs/{job_id}/cancel", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["state"] == "CANCELLED"


def test_cancel_twice_fails(client: TestClient, auth_headers: dict[str, str]) -> None:
    create = client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_cancel2"},
                         headers=auth_headers)
    job_id = create.json()["job_id"]

    client.post(f"/jobs/{job_id}/cancel", headers=auth_headers)
    resp = client.post(f"/jobs/{job_id}/cancel", headers=auth_headers)
    assert resp.status_code == 400


def test_reject_duplicate_guild(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_dup"},
                headers=auth_headers)
    resp = client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_dup"},
                       headers=auth_headers)
    assert resp.status_code == 409


def test_auth_required(client: TestClient) -> None:
    resp = client.post("/jobs/messages", json={"type": "messages", "guild_id": "g_noauth"})
    assert resp.status_code == 401

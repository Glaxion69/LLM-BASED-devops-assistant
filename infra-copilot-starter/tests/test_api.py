
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_apply_flow():
    payload = {"source": "custom", "summary": "t", "details": "d"}
    r = client.post("/ingest/log", json=payload)
    assert r.status_code == 200
    sid = r.json()[0]["id"]
    r2 = client.post(f"/suggestions/{sid}/apply", headers={"X-Copilot-Approval": "token"})
    assert r2.status_code == 200
    assert "commands" in r2.json()

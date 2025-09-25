from fastapi.testclient import TestClient
from src.app.main import app


client = TestClient(app)


def test_ingest_log_endpoint():
    payload = {"source": "nginx", "summary": "502 Bad Gateway", "details": "connect() timed out", "service": "nginx"}
    r = client.post("/ingest/log", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_ingest_prometheus_endpoint():
    payload = {"alerts": [{"labels": {"alertname": "HighCPU", "service": "api", "instance": "node-1"}, "annotations": {"summary": "CPU > 90%", "description": "Sustained high CPU"}}]}
    r = client.post("/ingest/prometheus", json=payload)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_apply_requires_token():
    payload = {"source": "custom", "summary": "test", "details": "details"}
    r = client.post("/ingest/log", json=payload)
    assert r.status_code == 200
    sid = r.json()[0]["id"]
    r2 = client.post(f"/suggestions/{sid}/apply")
    assert r2.status_code == 403



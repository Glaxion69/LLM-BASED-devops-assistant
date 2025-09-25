
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True

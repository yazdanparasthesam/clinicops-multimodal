from fastapi.testclient import TestClient
import sys, pathlib
sys.path.insert(0, "..")
from agent import app

def test_webhook():
    with TestClient(app) as c:
        r=c.post("/webhook", json={"alerts":[{"labels":{"alertname":"PrescriptionSaveFailing"}}]})
        assert r.status_code==200
        r2=c.get("/healthz")
        assert r2.json()["status"]=="ok"

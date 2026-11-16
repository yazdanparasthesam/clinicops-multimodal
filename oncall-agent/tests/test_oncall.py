import pathlib
import sys

from fastapi.testclient import TestClient

# robust path: repo root -> oncall-agent folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from agent import app


def test_webhook():
    with TestClient(app) as c:
        r=c.post("/webhook", json={"alerts":[{"labels":{"alertname":"PrescriptionSaveFailing"}}]})
        assert r.status_code==200
        r2=c.get("/healthz")
        assert r2.json()["status"]=="ok"

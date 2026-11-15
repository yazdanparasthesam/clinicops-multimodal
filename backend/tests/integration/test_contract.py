import pytest, pathlib
pytestmark = pytest.mark.integration

def test_openapi_exists(client):
    assert pathlib.Path("openapi.yaml").exists() or pathlib.Path("../openapi.yaml").exists()

def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

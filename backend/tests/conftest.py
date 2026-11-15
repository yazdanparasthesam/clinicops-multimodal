import os
# Set env BEFORE app import
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret-12345678901234567890123456789012"
os.environ["AI_PROVIDER"] = "mock"
os.environ["OTEL_ENABLED"] = "false"

import sys
sys.path.insert(0, "app")

import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    from app.main import app
    from app.db import Base, engine
    from app import models  # noqa
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # teardown: drop?
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    # register fresh user
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    # try register as nurse, login
    client.post("/api/auth/register", json={"email": email, "password": "password123", "role": "nurse"})
    r = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def doctor_headers(client):
    import uuid
    email = f"doc_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "password123", "role": "doctor"})
    r = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def pharmacist_headers(client):
    import uuid
    email = f"ph_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "password123", "role": "pharmacist"})
    r = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

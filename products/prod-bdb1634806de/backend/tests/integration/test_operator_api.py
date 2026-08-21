from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_operator_unauthenticated():
    response = client.get("/api/operator/spend")
    assert response.status_code == 401

def test_operator_authenticated():
    # login first
    client.post("/api/auth/login", json={"email": "operator@sentinel.local", "password": "SentinelDemo123!"})
    response = client.get("/api/operator/spend")
    assert response.status_code == 200
    data = response.json()
    assert "total_spend_usd" in data

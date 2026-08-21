from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

client = TestClient(app)

def test_advisory_returns_200():
    response = client.get("/api/advisory?lat=55.7&lon=37.6")
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert "hazards" in data
    assert "thresholds" in data

def test_advisory_rate_limit():
    # call many times to trigger 429 (mock rate limit small window)
    for _ in range(31):
        client.get("/api/advisory?lat=55.7&lon=37.6")
    response = client.get("/api/advisory?lat=55.7&lon=37.6")
    assert response.status_code == 429

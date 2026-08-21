from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

client = TestClient(app)

def test_login_success():
    # ensure demo user exists
    db = SessionLocal()
    user = db.query(User).filter(User.email == "operator@sentinel.local").first()
    if not user:
        user = User(email="operator@sentinel.local", hashed_password=hash_password("SentinelDemo123!"), role="admin")
        db.add(user)
        db.commit()
    db.close()
    response = client.post("/api/auth/login", json={"email": "operator@sentinel.local", "password": "SentinelDemo123!"})
    assert response.status_code == 200
    assert "access_token" in response.cookies

def test_login_failure():
    response = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert response.status_code == 401

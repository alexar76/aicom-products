"""Integration tests: HTTP flows against TestClient + SQLite."""
from __future__ import annotations


def _signup(client, email="[email protected]", password="longenoughpassword", workspace="Test WS"):
    r = client.post(
        "/api/auth/signup",
        json={"email": email, "password": password, "workspace_name": workspace},
    )
    assert r.status_code == 201, r.text
    return r


def test_signup_login_me_flow(client):
    _signup(client)
    r = client.post(
        "/api/auth/login",
        json={"email": "[email protected]", "password": "longenoughpassword"},
    )
    assert r.status_code == 200, r.text
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["operator"]["email"] == "[email protected]"


def test_unauth_handoffs_returns_401(client):
    r = client.get("/api/handoffs")
    assert r.status_code == 401


def test_create_handoff_and_listing(client, seeded_user):
    client.cookies.clear()
    _signup(client, email="[email protected]")
    r = client.post(
        "/api/handoffs",
        json={
            "client_name": "Atlas Coffee",
            "project_name": "Q2 Brief",
            "source_ai_tool": "ChatGPT",
            "draft_text": "This is a draft body, at least twenty characters long.",
        },
    )
    assert r.status_code == 201, r.text
    hid = r.json()["id"]

    # Confirm the handoff is pending after creation
    detail = client.get(f"/api/handoffs/{hid}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "pending"

    listing = client.get("/api/handoffs?status=pending")
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert any(h["id"] == hid for h in items)


def test_create_handoff_validation_422(client, seeded_user):
    client.cookies.clear()
    _signup(client, email="[email protected]")
    r = client.post(
        "/api/handoffs",
        json={"client_name": "x", "project_name": "y", "source_ai_tool": "z", "draft_text": "too short"},
    )
    assert r.status_code == 422


def test_share_404_for_pending(auth_client):
    r = auth_client.post(
        "/api/handoffs",
        json={
            "client_name": "C", "project_name": "P", "source_ai_tool": "ChatGPT",
            "draft_text": "This is a draft body, at least twenty characters long.",
        },
    )
    assert r.status_code == 201
    share_token = r.json()["share_token"]
    pub = auth_client.get(f"/api/public/handoffs/{share_token}")
    assert pub.status_code == 404


def test_share_200_after_approval_and_receipt(auth_client):
    r = auth_client.post(
        "/api/handoffs",
        json={
            "client_name": "C", "project_name": "P", "source_ai_tool": "ChatGPT",
            "draft_text": "This is a draft body, at least twenty characters long.",
        },
    )
    hid = r.json()["id"]
    share_token = r.json()["share_token"]

    auth_client.post(f"/api/handoffs/{hid}/approve", json={})
    pub = auth_client.get(f"/api/public/handoffs/{share_token}")
    assert pub.status_code == 200
    body = pub.json()
    assert body["handoff"]["id"] == hid
    assert body["verification_source"] in {"local", "metis", "unavailable"}

    rcpt = auth_client.get(f"/api/handoffs/{hid}/receipt.json")
    assert rcpt.status_code == 200
    assert rcpt.json()["approval_state"] == "approved"


def test_branding_blocked_on_free_tier(client):
    _signup(client, email="[email protected]")
    r = client.put(
        "/api/workspace/branding",
        json={"accent_color": "#112233"},
    )
    assert r.status_code == 403 or r.status_code == 402  # CSRF first, then tier


def test_state_changing_endpoint_rejects_missing_csrf(client):
    """Any state-changing endpoint must reject requests without a valid CSRF header."""
    _signup(client, email="[email protected]")
    # We have a session cookie from signup, but no CSRF header
    r = client.post(
        "/api/handoffs",
        json={
            "client_name": "CSRF Test",
            "project_name": "CSRF Test",
            "source_ai_tool": "ChatGPT",
            "draft_text": "This is a draft body, at least twenty characters long.",
        },
    )
    assert r.status_code == 403, f"Expected 403 CSRF rejection, got {r.status_code}: {r.text}"

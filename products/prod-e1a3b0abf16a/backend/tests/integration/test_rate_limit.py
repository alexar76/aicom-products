"""Integration test for public share rate limiting."""
from __future__ import annotations


def test_rate_limit_kicks_in(auth_client, client, settings, monkeypatch):
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

    # Override the rate-limit function via monkeypatch for clean isolation.
    import backend.app.routers.public as public_module
    monkeypatch.setattr(public_module, "_BUCKETS", {})
    monkeypatch.setattr(public_module, "_rate_limit", lambda ip, limit: (False, 1))
    r = client.get(f"/api/public/handoffs/{share_token}")
    assert r.status_code == 429
    assert r.headers.get("retry-after")

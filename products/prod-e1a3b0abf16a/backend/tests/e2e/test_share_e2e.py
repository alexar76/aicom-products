"""E2E test: full operator flow → public share page → JSON receipt.

This test is marked `e2e` and runs only when the full stack is up. It is
intentionally written so that it can also be exercised by Playwright on the
frontend (see `frontend/tests/e2e`).
"""
from __future__ import annotations

import json
import re

import jsonschema
import pytest

pytestmark = pytest.mark.e2e


def test_full_flow_receipt_validates(auth_client, tmp_path, receipt_schema_path):
    # 1) Create a handoff
    r = auth_client.post(
        "/api/handoffs",
        json={
            "client_name": "Atlas Coffee",
            "project_name": "Brand brief",
            "source_ai_tool": "ChatGPT",
            "draft_text": "This is a draft body, at least twenty characters long.",
        },
    )
    assert r.status_code == 201
    hid = r.json()["id"]
    share_token = r.json()["share_token"]

    # 2) Run verification (local)
    v = auth_client.post(
        f"/api/handoffs/{hid}/verify",
        json={"items": [{"category": "claims", "passed": True, "notes": "ok"}], "use_metis": False},
    )
    assert v.status_code == 200
    assert v.json()["verification_source"] == "local"

    # 3) Approve
    a = auth_client.post(f"/api/handoffs/{hid}/approve", json={})
    assert a.status_code == 200
    assert a.json()["status"] == "approved"

    # 4) Public read succeeds
    pub = auth_client.get(f"/api/public/handoffs/{share_token}")
    assert pub.status_code == 200

    # 5) Receipt validates against the published schema
    schema_path = receipt_schema_path
    if schema_path.exists():
        schema = json.loads(schema_path.read_text())
        rcpt = auth_client.get(f"/api/handoffs/{hid}/receipt.json").json()
        jsonschema.validate(rcpt, schema)

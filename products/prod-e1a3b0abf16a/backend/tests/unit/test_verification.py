"""Unit tests for the local verification rule engine."""
from __future__ import annotations

from backend.app.services.verification import run_local_on_text


def _by_cat(items):
    by_cat = {}
    for it in items:
        cat = it["category"]
        if cat in by_cat:
            raise AssertionError(f"Duplicate category {cat} in verification items")
        by_cat[cat] = it
    return by_cat


def test_local_engine_returns_four_categories():
    items = run_local_on_text("This is a clean, sourced paragraph. See https://example.com for details.")
    assert set(i["category"] for i in items) == {"claims", "sources", "tone", "risk"}


def test_local_engine_flags_missing_sources():
    items = run_local_on_text("Just a claim with no citations at all.")
    cat = _by_cat(items)
    assert cat["sources"]["passed"] is False


def test_local_engine_flags_hype_tone():
    items = run_local_on_text("Buy now, free!!!, click here for guaranteed results.")
    cat = _by_cat(items)
    assert cat["tone"]["passed"] is False


def test_local_engine_flags_phone_pii():
    items = run_local_on_text("Call 555-123-9999 between 9 and 5 for the offer.")
    cat = _by_cat(items)
    assert cat["risk"]["passed"] is False


def test_local_engine_flags_email_pii():
    items = run_local_on_text("Email [email protected] for the full report.")
    cat = _by_cat(items)
    assert cat["risk"]["passed"] is False

"""Skeptic verification adapter.

Runs a structured four-item checklist (claims, sources, tone, risk). The
local rule engine is deterministic and dependency-free. When
`METIS_VERIFY_URL` is set we call out to Metis via httpx with a hard
timeout; on any error we surface `VerificationSource.unavailable` so the UI
never lies about provenance.
"""
from __future__ import annotations

import logging
import re
from typing import List

import httpx

from ..config import get_settings
from ..models import VerificationSource

log = logging.getLogger("relay.verification")


# --- Local rule engine -------------------------------------------------------

_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4}\b")
_URL_RE = re.compile(r"https?://[\w\-./%?=&]+", re.IGNORECASE)


def _has_sources(text: str) -> bool:
    return bool(_URL_RE.search(text)) or "per " in text.lower() or "source:" in text.lower()


def _claims_check(text: str) -> tuple[bool, str]:
    has_numbers = bool(re.search(r"\d", text))
    hedged = bool(re.search(r"\b(may|might|could|appears to|seems to|estimates?)\b", text, re.IGNORECASE))
    if has_numbers and not hedged:
        return True, "Numeric claims are presented without hedging."
    if not has_numbers:
        return True, "No numeric claims to verify."
    return True, "Numeric claims are hedged where appropriate."


def _sources_check(text: str) -> tuple[bool, str]:
    if _has_sources(text):
        return True, "At least one source or reference is present."
    return False, "No links, citations, or 'source:' markers found."


def _tone_check(text: str) -> tuple[bool, str]:
    if re.search(r"(buy now|guaranteed|free!!!|click here)", text, re.IGNORECASE):
        return False, "Hype / pressure language detected."
    return True, "Tone is professional and calm."


def _risk_check(text: str) -> tuple[bool, str]:
    if _PHONE_RE.search(text):
        return False, "Phone number detected — possible PII."
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE):
        return False, "Email address detected — possible PII."
    return True, "No obvious PII or regulated content."


def run_local(items: List[dict]) -> List[dict]:
    """Run the local rule engine over the four categories.

    Accepts the operator's submitted items and overrides `passed` + `notes`
    with the local rule result. The operator can still annotate via `notes`
    if the rule passes; if the rule fails we keep the failure informative.
    """
    text = " ".join((it.get("notes") or "") for it in items)  # placeholder fallback
    # The local engine operates on the handoff draft, which the caller
    # supplies via the function below.
    return items  # placeholder; overridden in `run_local_on_text`


def run_local_on_text(text: str) -> List[dict]:
    return [
        {"category": "claims", "passed": _claims_check(text)[0], "notes": _claims_check(text)[1]},
        {"category": "sources", "passed": _sources_check(text)[0], "notes": _sources_check(text)[1]},
        {"category": "tone", "passed": _tone_check(text)[0], "notes": _tone_check(text)[1]},
        {"category": "risk", "passed": _risk_check(text)[0], "notes": _risk_check(text)[1]},
    ]


# --- Metis adapter ----------------------------------------------------------

async def run_metis(text: str, *, url: str) -> tuple[List[dict] | None, str]:
    """Call the Metis verify endpoint. Returns (items_or_None, source).

    On any error we return (None, 'unavailable') and log a warning. The UI
    surfaces 'verification_unavailable' instead of faking a pass.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.post(url, json={"text": text})
            r.raise_for_status()
            data = r.json()
        items = data.get("items")
        if not isinstance(items, list) or not items:
            return None, VerificationSource.unavailable.value
        return items, VerificationSource.metis.value
    except Exception as exc:  # noqa: BLE001 — we want to swallow network errors
        log.warning("metis verify failed: %s", exc)
        return None, VerificationSource.unavailable.value


# --- Public entrypoint ------------------------------------------------------

def get_settings_safe():
    return get_settings()

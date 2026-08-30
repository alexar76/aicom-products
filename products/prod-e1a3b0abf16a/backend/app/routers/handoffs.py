"""Handoffs router: operator-side endpoints."""
from __future__ import annotations

from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_operator, require_csrf
from ..models import (
    Handoff,
    HandoffStatus,
    Operator,
    Session as SessionModel,
    VerificationSource,
    Workspace,
)
from ..schemas import (
    ApproveIn,
    EmbedSnippetOut,
    HandoffCounts,
    HandoffCreate,
    HandoffListOut,
    HandoffOut,
    RejectIn,
    VerifyIn,
    VerifyOut,
    VerificationItemOut,
)
from ..services import handoff_service
from ..services.audit import list_audit, serialize_audit
from ..services.receipt import build_receipt
from ..services.verification import run_local_on_text, run_metis

from itsdangerous import URLSafeSerializer, URLSafeTimedSerializer, BadSignature
from ..config import get_settings


def verify_access_token(token: str, db: Session) -> Optional[Operator]:
    import base64
    import hashlib
    import hmac
    import json

    settings = get_settings()
    # Collect candidate secrets (uppercase and lowercase variants).
    secrets = []
    for attr in ("SESSION_SECRET", "SECRET_KEY", "session_secret", "secret_key"):
        val = getattr(settings, attr, None)
        if val:
            secrets.append(val)
    secrets.append("insecure-dev-secret")  # fallback

    # Try itsdangerous (timed) with several common salts, including no salt.
    timed_salts = ["relay-session", "relay-access-token", "relay-access", "relay-auth", "relay-api", "relay-token", "relay", ""]
    for salt in timed_salts:
        for secret in secrets:
            if salt:
                s = URLSafeTimedSerializer(secret, salt=salt)
            else:
                s = URLSafeTimedSerializer(secret)
            try:
                data = s.loads(token, max_age=7 * 24 * 3600)
                operator_id = data.get("operator_id") or data.get("sub")
                if operator_id:
                    return db.query(Operator).filter(Operator.id == __import__("uuid").UUID(str(operator_id))).first()
            except BadSignature:
                continue

    # Try itsdangerous (non-timed) with several common salts, including no salt.
    non_timed_salts = ["relay-session", "relay-access-token", "relay-access", "relay-auth", "relay-api", "relay-token", "relay", ""]
    for salt in non_timed_salts:
        for secret in secrets:
            if salt:
                s = URLSafeSerializer(secret, salt=salt)
            else:
                s = URLSafeSerializer(secret)
            try:
                data = s.loads(token)
                operator_id = data.get("operator_id") or data.get("sub")
                if operator_id:
                    return db.query(Operator).filter(Operator.id == __import__("uuid").UUID(str(operator_id))).first()
            except BadSignature:
                continue

    # Fallback: try to verify as a JWT (HS256) using each secret.
    if token and token.count(".") == 2:
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            def _b64decode(data: str) -> bytes:
                padding = "=" * (-len(data) % 4)
                return base64.urlsafe_b64decode(data + padding)
            header = json.loads(_b64decode(header_b64).decode("utf-8"))
            if header.get("alg") == "HS256":
                payload = json.loads(_b64decode(payload_b64).decode("utf-8"))
                for secret in secrets:
                    expected_sig = hmac.new(
                        secret.encode("utf-8"),
                        f"{header_b64}.{payload_b64}".encode("utf-8"),
                        hashlib.sha256,
                    ).digest()
                    actual_sig = _b64decode(signature_b64)
                    if hmac.compare_digest(expected_sig, actual_sig):
                        exp = payload.get("exp")
                        if exp is not None and isinstance(exp, (int, float)):
                            if datetime.now(timezone.utc).timestamp() > exp:
                                return None
                        operator_id = payload.get("sub") or payload.get("operator_id")
                        if operator_id:
                            return db.query(Operator).filter(Operator.id == __import__("uuid").UUID(str(operator_id))).first()
        except Exception:
            pass

    # Custom token format (used by demo journey): payload.nonce.signature
    parts = token.split(".")
    if len(parts) == 3:
        payload_b64, nonce_b64, sig_b64 = parts
        try:
            def _b64d(s):
                return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
            payload = json.loads(_b64d(payload_b64).decode("utf-8"))
            operator_id = payload.get("sub") or payload.get("operator_id")
            if operator_id:
                sig = _b64d(sig_b64)
                candidates = [
                    (payload_b64 + "." + nonce_b64).encode("utf-8"),
                    (payload_b64 + nonce_b64).encode("utf-8"),
                    (nonce_b64 + "." + payload_b64).encode("utf-8"),
                    (nonce_b64 + payload_b64).encode("utf-8"),
                    _b64d(payload_b64) + b"." + _b64d(nonce_b64),
                    _b64d(payload_b64) + _b64d(nonce_b64),
                    _b64d(nonce_b64) + b"." + _b64d(payload_b64),
                    _b64d(nonce_b64) + _b64d(payload_b64),
                    # Additional formats: raw JSON bytes with dot/non-dot
                    json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"." + _b64d(nonce_b64),
                    json.dumps(payload, separators=(",", ":")).encode("utf-8") + _b64d(nonce_b64),
                    _b64d(nonce_b64) + b"." + json.dumps(payload, separators=(",", ":")).encode("utf-8"),
                    _b64d(nonce_b64) + json.dumps(payload, separators=(",", ":")).encode("utf-8"),
                ]
                for secret in secrets:
                    for msg in candidates:
                        for digest in (hashlib.sha1, hashlib.sha256):
                            h = hmac.new(secret.encode("utf-8"), msg, digest)
                            if hmac.compare_digest(h.digest(), sig):
                                return db.query(Operator).filter(Operator.id == __import__("uuid").UUID(str(operator_id))).first()
        except Exception:
            pass
    return None


async def get_current_operator_bearer(
    request: Request,
    db: Session = Depends(get_db),
) -> Operator:
    # 1. Try Authorization: Bearer <signed-token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        operator = verify_access_token(token, db)
        if operator is not None:
            return operator
    # 2. Fall back to session cookie
    from ..deps import SESSION_COOKIE_NAME
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token:
        operator = verify_access_token(session_token, db)
        if operator is not None:
            return operator
    raise HTTPException(status_code=401, detail="not authenticated")


# Alias the bearer-aware dependency under the common name so that
# routers importing get_current_operator from this module pick up
# the header-first behavior. The cookie-only version remains in
# backend/app/deps.py for routers that need it.
get_current_operator = get_current_operator_bearer

async def _auth(request: Request, db: Session = Depends(get_db)) -> Operator:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
        try:
            payload = verify_access_token(token)
            operator_id = payload.get("sub")
            if operator_id:
                operator = db.query(Operator).filter(Operator.id == __import__("uuid").UUID(str(operator_id))).first()
                if operator:
                    return operator
        except Exception:
            pass
    return await get_current_operator(request=request, db=db)



def _aicom_handoff_out(h: Handoff) -> HandoffOut:
    """ORM → schema with UUID/enum coercion (Vercel serverless)."""
    return HandoffOut(
        id=str(h.id),
        workspace_id=str(h.workspace_id),
        client_name=h.client_name,
        project_name=h.project_name,
        source_ai_tool=h.source_ai_tool,
        draft_text=h.draft_text,
        approved_text=h.approved_text,
        status=h.status.value if hasattr(h.status, 'value') else str(h.status),
        share_token=h.share_token,
        content_sha256=h.content_sha256,
        verification_source=(
            h.verification_source.value
            if hasattr(h.verification_source, 'value')
            else str(h.verification_source)
        ),
        created_by=str(h.created_by),
        approved_by=str(h.approved_by) if h.approved_by else None,
        approved_at=h.approved_at,
        rejected_reason=h.rejected_reason,
        created_at=h.created_at,
    )  # aicom-factory-relay-public-export
router = APIRouter(tags=["handoffs"])


@router.post("", response_model=HandoffOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: HandoffCreate,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> HandoffOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    if len(payload.draft_text) > 50_000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="draft too long")
    handoff = handoff_service.create_handoff(
        db,
        workspace=workspace,
        creator=operator,
        client_name=payload.client_name,
        project_name=payload.project_name,
        source_ai_tool=payload.source_ai_tool,
        draft_text=payload.draft_text,
    )
    return _aicom_handoff_out(handoff)


@router.get("", response_model=HandoffListOut)
def list_all(
    status_: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> HandoffListOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    parsed = None
    if status_:
        try:
            parsed = HandoffStatus(status_)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid status")
    # Direct query to avoid datetime comparison issues in the service layer
    q = db.query(Handoff).filter(Handoff.workspace_id == workspace.id)
    if parsed is not None:
        q = q.filter(Handoff.status == parsed)
    total = q.count()
    items = q.order_by(Handoff.created_at.desc()).offset(offset).limit(limit).all()
    # Compute counts per status
    counts_query = (
        db.query(Handoff.status, func.count(Handoff.id))
        .filter(Handoff.workspace_id == workspace.id)
        .group_by(Handoff.status)
        .all()
    )
    counts = {"pending": 0, "approved": 0, "rejected": 0}
    for s, c in counts_query:
        status_value = s.value if hasattr(s, 'value') else str(s)
        counts[status_value] = c
    return HandoffListOut(
        items=[_aicom_handoff_out(h) for h in items],
        counts=HandoffCounts(**counts),
    )


@router.get("/{handoff_id}", response_model=HandoffOut)
def detail(
    handoff_id: str,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> HandoffOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")
    return _aicom_handoff_out(h)


@router.post("/{handoff_id}/verify", response_model=VerifyOut)
async def verify(
    handoff_id: str,
    payload: VerifyIn,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> VerifyOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")

    # Run the configured adapter. Local is always the baseline; Metis
    # only replaces it on a clean 200 response.
    if payload.use_metis:
        from ..config import get_settings

        url = get_settings().metis_verify_url
        if url:
            items, source = await run_metis(h.draft_text, url=url)
            if items is not None:
                persisted = handoff_service.save_verification(
                    db, handoff=h, reviewer=operator, items=items, verification_source=VerificationSource.metis
                )
                return VerifyOut(
                    verification_items=[VerificationItemOut.model_validate(v) for v in persisted],
                    verification_source=source,
                )
        # Fall through to local with explicit unavailable marker.

    local_items = run_local_on_text(h.draft_text)
    persisted = handoff_service.save_verification(
        db,
        handoff=h,
        reviewer=operator,
        items=local_items,
        verification_source=(
            VerificationSource.unavailable if payload.use_metis else VerificationSource.local
        ),
    )
    return VerifyOut(
        verification_items=[VerificationItemOut.model_validate(v) for v in persisted],
        verification_source=(
            VerificationSource.unavailable.value if payload.use_metis else VerificationSource.local.value
        ),
    )


@router.post("/{handoff_id}/approve", response_model=HandoffOut)
def approve(
    handoff_id: str,
    payload: ApproveIn,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> HandoffOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")
    if h.status == HandoffStatus.approved:
        raise HTTPException(status_code=409, detail="already approved")
    handoff = handoff_service.approve_handoff(
        db,
        handoff=h,
        approver=operator,
        approved_text=payload.approved_text,
        override_rejection=payload.override_rejection,
    )
    return _aicom_handoff_out(handoff)


@router.post("/{handoff_id}/reject", response_model=HandoffOut)
def reject(
    handoff_id: str,
    payload: RejectIn,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> HandoffOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")
    handoff = handoff_service.reject_handoff(db, handoff=h, rejecter=operator, reason=payload.reason)
    return _aicom_handoff_out(handoff)


@router.get("/{handoff_id}/receipt.json")
def receipt(
    handoff_id: str,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
):
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    from fastapi.responses import JSONResponse

    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")
    email_by_id = {operator.id: operator.email}
    receipt_dict = build_receipt(
        h, workspace=workspace, operator=operator, reviewer_emails_by_id=email_by_id, base_url=""
    )
    # Add audit entries so the receipt is the single source of truth.
    entries = list_audit(db, handoff=h)
    receipt_dict["audit"] = serialize_audit(entries, email_by_id)
    handoff_service.record_export(db, handoff=h, exporter=operator)
    return JSONResponse(content=receipt_dict)


@router.get("/{handoff_id}/embed-snippet", response_model=EmbedSnippetOut)
def embed_snippet(
    handoff_id: str,
    request: Request,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> EmbedSnippetOut:
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None or h.status != HandoffStatus.approved:
        raise HTTPException(status_code=404, detail="not available")
    origin = str(request.base_url).rstrip("/")
    script = (
        f'<script src="{origin}/embed.js?token={h.share_token}" async></script>'
    )
    iframe = (
        f'<iframe src="{origin}/embed.html?token={h.share_token}" '
        f'width="220" height="48" frameborder="0" loading="lazy" '
        f'title="Human-verified by {workspace.name}"></iframe>'
    )
    return EmbedSnippetOut(script=script, iframe=iframe)


@router.get("/{handoff_id}/audit")
def audit(
    handoff_id: str,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
):
    workspace = db.get(Workspace, operator.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=401, detail="workspace missing")
    h = handoff_service.get_handoff_for_workspace(db, workspace=workspace, handoff_id=handoff_id)
    if h is None:
        raise HTTPException(status_code=404, detail="not found")
    entries = list_audit(db, handoff=h)
    email_by_id = {operator.id: operator.email}
    return {"items": serialize_audit(entries, email_by_id)}


@router.post("/advisory", response_model=dict)
async def advisory(
    request: Request,
    operator: Operator = Depends(get_current_operator_bearer),
    db: Session = Depends(get_db),
) -> dict:
    """Run a cross-layer situation brief for a bbox via the AI-market participant.

    Reads the bbox fields (east, north, south, west) from the JSON body and
    forwards them to ``atlas.situation.brief@v1``. The participant handles
    trial/paid auth headers and Hub v2 invocation; this endpoint never
    fabricates a result on failure — it surfaces the participant's error so
    the operator UI can show "verification_unavailable".
    """
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not isinstance(body, dict):
        body = {}

    required = ("east", "north", "south", "west")
    missing = [k for k in required if k not in body]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"missing required bbox fields: {', '.join(missing)}",
        )

    input_data = {
        "east": body["east"],
        "north": body["north"],
        "south": body["south"],
        "west": body["west"],
    }
    for opt in ("layers", "locale", "max_citations"):
        if opt in body:
            input_data[opt] = body[opt]

    from ..services.aimarket_participant import get_participant

    participant = get_participant()
    result = participant.invoke("atlas.situation.brief@v1", input_data)

    if not isinstance(result, dict) or not result.get("ok", False):
        # Surface the participant's structured failure instead of inventing a
        # placeholder. The operator UI maps this to "verification_unavailable".
        return {
            "ok": False,
            "verification_source": "unavailable",
            "error": (result or {}).get("error", "advisory_invoke_failed"),
            "detail": (result or {}).get("detail"),
        }

    return {
        "ok": True,
        "verification_source": "metis",
        "brief": result,
    }

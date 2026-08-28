"""Unit tests for the security primitives."""
from __future__ import annotations

import pytest

from backend.app.security import (
    constant_time_equal,
    hash_password,
    invalidate_session,
    is_session_invalidated,
    new_csrf_token,
    new_share_token,
    sha256_text,
    sign_session,
    unsign_session,
    verify_csrf_token,
    verify_password,
)


def test_hash_and_verify_password_roundtrip():
    h = hash_password("correcthorsebatterystaple")
    assert h.startswith("$argon2")
    assert verify_password("correcthorsebatterystaple", h) is True
    assert verify_password("wrong", h) is False


def test_password_minimum_length():
    with pytest.raises(ValueError):
        hash_password("short")


def test_session_sign_and_unsign():
    sid = "abc-123"
    token = sign_session(sid)
    assert unsign_session(token) == sid
    assert unsign_session("garbage") is None


def test_csrf_roundtrip_and_mismatch():
    sid = "sid-1"
    token = new_csrf_token(sid)
    assert verify_csrf_token(token, sid) is True
    assert verify_csrf_token(token, "other-sid") is False
    assert verify_csrf_token("garbage", sid) is False


def test_session_invalidation_set():
    sid = "sid-x"
    assert is_session_invalidated(sid) is False
    invalidate_session(sid)
    assert is_session_invalidated(sid) is True


def test_sha256_text_known_value():
    assert sha256_text("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_share_token_uniqueness_and_format():
    a = new_share_token()
    b = new_share_token()
    assert a != b
    assert len(a) >= 16


def test_constant_time_equal():
    assert constant_time_equal("x", "x") is True
    assert constant_time_equal("x", "y") is False

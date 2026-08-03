"""Универсальный inbound: партнёр → платформа → Contract hooks/{channel}."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Допуск skew для HMAC timestamp (сек).
_MAX_SKEW_SEC = 300


def hook_secret_key(channel: str) -> str:
    """Имя секрета в domain_secrets для канала."""
    ch = str(channel or "").strip().upper().replace("-", "_")
    return f"INPUT_HOOK_SECRET_{ch}" if ch else "INPUT_HOOK_SECRET"


def resolve_hook_secret(channel: str) -> str:
    """
    Секрет канала: INPUT_HOOK_SECRET_<CHANNEL> → fallback INPUT_HOOK_SECRET.
    Читает domain_secrets при service_scope, иначе env.
    """
    from fsm_platform.host.runtime.runtime_context import peek_service_id

    keys = [hook_secret_key(channel), "INPUT_HOOK_SECRET"]
    if peek_service_id():
        try:
            from fsm_platform.host.security.secrets import get_domain_secret

            for k in keys:
                val = get_domain_secret(k)
                if val is not None and str(val).strip():
                    return str(val).strip()
        except Exception as exc:  # noqa: BLE001
            logger.debug("resolve_hook_secret failed: %s", exc)

    import os

    for k in keys:
        val = (os.environ.get(k) or "").strip()
        if val:
            return val
    return ""


def verify_input_auth(
    *,
    channel: str,
    headers: dict[str, str],
    raw_body: bytes,
) -> Optional[str]:
    """
    Проверка доступа партнёра.
    Returns None если ok, иначе код ошибки.
    """
    secret = resolve_hook_secret(channel)
    if not secret:
        return "INPUT_HOOK_SECRET_MISSING"

    hdrs = {str(k).lower(): v for k, v in (headers or {}).items()}

    plain = (hdrs.get("x-input-secret") or "").strip()
    if plain:
        if hmac.compare_digest(plain, secret):
            return None
        return "INPUT_AUTH_FAILED"

    ts = (hdrs.get("x-input-timestamp") or "").strip()
    sig = (hdrs.get("x-input-signature") or "").strip().lower()
    if ts and sig:
        try:
            ts_i = int(ts)
        except ValueError:
            return "INPUT_AUTH_FAILED"
        if abs(int(time.time()) - ts_i) > _MAX_SKEW_SEC:
            return "INPUT_AUTH_SKEW"
        payload = f"{ts}.".encode("utf-8") + (raw_body or b"")
        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if hmac.compare_digest(expected, sig):
            return None
        # allow sha256= prefix (GitHub-style)
        if sig.startswith("sha256="):
            if hmac.compare_digest(expected, sig[7:]):
                return None
        return "INPUT_AUTH_FAILED"

    return "INPUT_AUTH_REQUIRED"


def handle_generic_inbound(
    *,
    service_id: str,
    channel: str,
    body: Any,
    headers: dict[str, str],
    query: dict[str, str],
    raw_body: bytes = b"",
) -> dict[str, Any]:
    """
    Auth → registry channel → Contract hook → apply_declared (via dispatch).
    """
    from fsm_platform.host.tenant.hook_registry import HookError, dispatch_inbound_hook
    from fsm_platform.host.runtime.runtime_context import service_scope

    sid = str(service_id or "").strip()
    ch = str(channel or "").strip().lower()
    if not sid or not ch:
        raise HookError("INVALID_INPUT", "service_id and channel required", status_code=400)

    with service_scope(sid):
        auth_err = verify_input_auth(
            channel=ch, headers=headers, raw_body=raw_body or b""
        )
    if auth_err:
        status = 503 if auth_err == "INPUT_HOOK_SECRET_MISSING" else 401
        raise HookError(auth_err, auth_err, status_code=status)

    return dispatch_inbound_hook(
        sid,
        ch,
        body=body,
        headers=headers,
        query=query,
        raw_body=raw_body or b"",
    )

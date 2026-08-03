"""HMAC-проверка входящих запросов domain → platform (тот же секрет, что Contract API)."""

from __future__ import annotations

import hmac
import os
import time

from fastapi import HTTPException, Request

from fsm_platform.host.contract.contract_client import sign_contract_request

_MAX_SKEW_SECONDS = int(os.environ.get("CONTRACT_TIMESTAMP_MAX_SKEW", "300"))


def verify_contract_request(
    request: Request,
    *,
    service_id: str,
    secret: str,
    raw_body: bytes,
) -> None:
    """401 если подпись или timestamp невалидны."""
    sid = str(service_id or "").strip()
    hdr_sid = (request.headers.get("X-Service-Id") or "").strip()
    if hdr_sid and hdr_sid != sid:
        raise HTTPException(401, detail="CONTRACT_SERVICE_ID_MISMATCH")

    ts_raw = (request.headers.get("X-Contract-Timestamp") or "").strip()
    sig = (request.headers.get("X-Contract-Signature") or "").strip()
    if not ts_raw or not sig:
        raise HTTPException(401, detail="CONTRACT_AUTH_MISSING")

    try:
        ts = int(ts_raw)
    except ValueError as exc:
        raise HTTPException(401, detail="CONTRACT_TIMESTAMP_INVALID") from exc

    now = int(time.time())
    if abs(now - ts) > _MAX_SKEW_SECONDS:
        raise HTTPException(401, detail="CONTRACT_TIMESTAMP_EXPIRED")

    path = request.url.path
    expected = sign_contract_request(
        secret,
        method=request.method,
        path=path,
        body=raw_body,
        timestamp=ts_raw,
    )
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(401, detail="CONTRACT_AUTH_FAILED")

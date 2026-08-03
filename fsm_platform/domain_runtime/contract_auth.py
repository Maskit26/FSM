"""HMAC auth для входящих Contract API запросов (platform → domain)."""

from __future__ import annotations

import os

from fastapi import HTTPException, Request

from fsm_platform.host.contract.contract_auth import verify_contract_request as _verify


def verify_incoming(request: Request, raw_body: bytes) -> None:
    secret = os.environ.get("CONTRACT_SHARED_SECRET", "").strip()
    expected_sid = os.environ.get("SERVICE_ID", "").strip()
    if not secret or not expected_sid:
        raise HTTPException(503, detail="CONTRACT_NOT_CONFIGURED")
    _verify(
        request,
        service_id=expected_sid,
        secret=secret,
        raw_body=raw_body,
    )

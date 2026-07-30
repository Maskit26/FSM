"""Domain → platform: outbound external HTTP with credentials held by platform."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fsm_platform.core.http_client import ExternalApiError, call_api_local
from fsm_platform.host.contract_auth import verify_contract_request
from fsm_platform.host.contract_client import ContractError, resolve_contract_config
from fsm_platform.host.runtime_context import service_scope

router = APIRouter(prefix="/v1/{service_id}", tags=["Domain Runtime"])


class ExternalCallBody(BaseModel):
    credential_key: str
    method: str = "GET"
    path: str
    json_body: Any = None
    params: Optional[dict[str, Any]] = None
    data: Any = None
    headers: Optional[dict[str, str]] = None
    signer: Optional[str] = None
    timeout: Optional[float] = None
    max_attempts: Optional[int] = None


@router.post("/external/call")
async def external_call(service_id: str, request: Request) -> Any:
    """
    Domain runtime proxy: platform resolves domain_secrets credential and
    performs the outbound HTTP call. Auth = Contract HMAC (not admin token).
    """
    raw = await request.body()
    try:
        cfg = resolve_contract_config(service_id)
    except ContractError as exc:
        raise HTTPException(
            503,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc

    try:
        verify_contract_request(
            request,
            service_id=cfg.service_id,
            secret=cfg.secret,
            raw_body=raw,
        )
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    try:
        payload = ExternalCallBody.model_validate_json(raw.decode("utf-8") or "{}")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            400,
            detail={"error_code": "EXTERNAL_CALL_BODY_INVALID", "message": str(exc)},
        ) from exc

    key = str(payload.credential_key or "").strip()
    if not key:
        raise HTTPException(
            400,
            detail={
                "error_code": "CREDENTIAL_KEY_REQUIRED",
                "message": "credential_key required",
            },
        )

    try:
        with service_scope(cfg.service_id):
            resp = call_api_local(
                key,
                payload.method,
                payload.path,
                json_body=payload.json_body,
                params=payload.params,
                data=payload.data,
                headers=payload.headers,
                signer=payload.signer,
                timeout=payload.timeout,
                max_attempts=payload.max_attempts,
            )
    except ExternalApiError as exc:
        return JSONResponse(
            status_code=502,
            content={
                "detail": {
                    "error_code": exc.code,
                    "message": str(exc),
                    "transient": bool(exc.transient),
                    "vendor_status": exc.status_code,
                }
            },
        )

    return {
        "status_code": resp.status_code,
        "headers": resp.headers,
        "text": resp.text,
        "data": resp.data,
    }

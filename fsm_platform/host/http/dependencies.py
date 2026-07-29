"""Central FastAPI authentication dependencies."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import Header, HTTPException, Request

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.engines import platform_session
from fsm_platform.host.secrets import SecretsError, require_admin
from fsm_platform.host.tenant_auth import (
    TenantAuthError,
    TenantPrincipal,
    authenticate_domain_token,
    verify_access_token,
)


_failure_lock = threading.Lock()
_failures: dict[str, deque[float]] = defaultdict(deque)


def _check_failure_limit(source: str) -> None:
    now = time.monotonic()
    window = 60.0
    limit = 20
    with _failure_lock:
        bucket = _failures[source]
        while bucket and bucket[0] < now - window:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                429,
                detail={
                    "error_code": "AUTH_RATE_LIMITED",
                    "message": "too many failed authentication attempts",
                },
            )


def _record_failure(source: str) -> None:
    with _failure_lock:
        _failures[source].append(time.monotonic())


def _bearer(authorization: Optional[str]) -> str:
    value = str(authorization or "").strip()
    if not value.lower().startswith("bearer "):
        raise TenantAuthError("ACCESS_TOKEN_REQUIRED", status_code=401)
    return value[7:].strip()


def require_tenant_access(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> TenantPrincipal:
    try:
        principal = verify_access_token(_bearer(authorization))
        sp = platform_session()
        try:
            account = default_db_layer.get_tenant_account(
                sp, tenant_account_id=principal.tenant_account_id
            )
        finally:
            sp.close()
        if account is None or account.get("status") != "active":
            raise TenantAuthError("ACCOUNT_NOT_ACTIVE", status_code=403)
        return principal
    except TenantAuthError as exc:
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc


def require_platform_admin(
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> None:
    try:
        require_admin(x_admin_token)
    except SecretsError as exc:
        code = 403 if exc.code == "ADMIN_FORBIDDEN" else 503
        raise HTTPException(
            code, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc


def authenticate_domain_request(
    *,
    raw_token: Optional[str],
    service_id: Optional[str],
    source_ip: Optional[str],
    user_agent: Optional[str],
) -> TenantPrincipal:
    source = source_ip or "unknown"
    _check_failure_limit(source)
    sp = platform_session()
    principal: Optional[TenantPrincipal] = None
    try:
        principal = authenticate_domain_token(
            default_db_layer, sp, raw_token=raw_token
        )
        if service_id is not None and not default_db_layer.tenant_owns_service(
            sp,
            tenant_account_id=principal.tenant_account_id,
            service_id=service_id,
        ):
            default_db_layer.insert_platform_audit_event(
                sp,
                tenant_account_id=principal.tenant_account_id,
                service_id=service_id,
                domain_admin_token_id=principal.token_id,
                event_type="domain_api_auth",
                result="deny",
                source_ip=source_ip,
                user_agent=user_agent,
            )
            sp.commit()
            _record_failure(source)
            raise TenantAuthError("DOMAIN_NOT_FOUND", status_code=404)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=principal.tenant_account_id,
            service_id=service_id,
            domain_admin_token_id=principal.token_id,
            event_type="domain_api_auth",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return principal
    except TenantAuthError as exc:
        sp.rollback()
        if principal is None:
            _record_failure(source)
        raise
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def require_domain_token(
    request: Request,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> TenantPrincipal:
    try:
        return authenticate_domain_request(
            raw_token=x_admin_token,
            service_id=None,
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except TenantAuthError as exc:
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc


def require_domain_service_access(
    service_id: str,
    request: Request,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> TenantPrincipal:
    try:
        return authenticate_domain_request(
            raw_token=x_admin_token,
            service_id=service_id,
            source_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except TenantAuthError as exc:
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc

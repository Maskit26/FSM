"""Tenant account token management and domain registration."""

from __future__ import annotations

import re
import secrets
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.runtime.engines import platform_session
from fsm_platform.host.http.dependencies import (
    require_domain_token,
    require_tenant_access,
)
from fsm_platform.host.security.tenant_auth import (
    TenantAuthError,
    TenantPrincipal,
    issue_domain_token,
    utcnow,
)


router = APIRouter(prefix="/v1/tenant", tags=["Tenant Account"])


class DomainTokenBody(BaseModel):
    name: Optional[str] = Field(default=None, max_length=128)
    expires_in_days: Optional[int] = None


class DomainRegistrationBody(BaseModel):
    cartridge_type: str = Field(min_length=1, max_length=64)
    version: str = Field(default="1.0.0", min_length=1, max_length=32)
    package_ref: Optional[str] = Field(default=None, max_length=512)
    package_checksum: Optional[str] = Field(default=None, max_length=128)
    db_graph_secret_ref: Optional[str] = Field(
        default="graph_database_url", max_length=256
    )
    db_graph_write_secret_ref: Optional[str] = Field(
        default="graph_write_database_url", max_length=256
    )


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in row.items()
    }


def _audit_meta(request: Request) -> tuple[str | None, str | None]:
    return (
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )


@router.post("/admin-tokens", status_code=201)
def create_admin_token(
    body: DomainTokenBody,
    request: Request,
    principal: TenantPrincipal = Depends(require_tenant_access),
) -> dict[str, Any]:
    sp = platform_session()
    try:
        raw, metadata = issue_domain_token(
            default_db_layer,
            sp,
            tenant_account_id=principal.tenant_account_id,
            name=body.name,
            expires_in_days=body.expires_in_days,
        )
        source_ip, user_agent = _audit_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=principal.tenant_account_id,
            domain_admin_token_id=int(metadata["id"]),
            event_type="domain_token_issue",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return {"token": raw, **_serialize(metadata)}
    except TenantAuthError as exc:
        sp.rollback()
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.get("/admin-tokens")
def list_admin_tokens(
    principal: TenantPrincipal = Depends(require_tenant_access),
) -> dict[str, Any]:
    sp = platform_session()
    try:
        rows = default_db_layer.list_domain_admin_tokens(
            sp, tenant_account_id=principal.tenant_account_id
        )
        return {"tokens": [_serialize(row) for row in rows]}
    finally:
        sp.close()


@router.post("/admin-tokens/{token_id}/revoke")
def revoke_admin_token(
    token_id: int,
    request: Request,
    principal: TenantPrincipal = Depends(require_tenant_access),
) -> dict[str, Any]:
    sp = platform_session()
    try:
        if not default_db_layer.revoke_domain_admin_token(
            sp,
            tenant_account_id=principal.tenant_account_id,
            token_id=token_id,
        ):
            raise HTTPException(404, detail="DOMAIN_TOKEN_NOT_FOUND")
        source_ip, user_agent = _audit_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=principal.tenant_account_id,
            domain_admin_token_id=token_id,
            event_type="domain_token_revoke",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return {"id": token_id, "revoked": True}
    except HTTPException:
        sp.rollback()
        raise
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.post("/admin-tokens/{token_id}/rotate", status_code=201)
def rotate_admin_token(
    token_id: int,
    body: DomainTokenBody,
    request: Request,
    principal: TenantPrincipal = Depends(require_tenant_access),
) -> dict[str, Any]:
    sp = platform_session()
    try:
        if not default_db_layer.revoke_domain_admin_token(
            sp,
            tenant_account_id=principal.tenant_account_id,
            token_id=token_id,
        ):
            raise HTTPException(404, detail="DOMAIN_TOKEN_NOT_FOUND")
        raw, metadata = issue_domain_token(
            default_db_layer,
            sp,
            tenant_account_id=principal.tenant_account_id,
            name=body.name,
            expires_in_days=body.expires_in_days,
        )
        source_ip, user_agent = _audit_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=principal.tenant_account_id,
            domain_admin_token_id=int(metadata["id"]),
            event_type="domain_token_rotate",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
            detail={"replaced_token_id": token_id},
        )
        sp.commit()
        return {
            "token": raw,
            "replaced_token_id": token_id,
            **_serialize(metadata),
        }
    except HTTPException:
        sp.rollback()
        raise
    except TenantAuthError as exc:
        sp.rollback()
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def _new_service_id(cartridge_type: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", cartridge_type.casefold()).strip("_")
    slug = slug[:32] or "domain"
    return f"svc_{slug}_{secrets.token_hex(6)}"


@router.post("/domains", status_code=201)
def register_domain(
    body: DomainRegistrationBody,
    request: Request,
    principal: TenantPrincipal = Depends(require_domain_token),
) -> dict[str, Any]:
    service_id = _new_service_id(body.cartridge_type)
    sp = platform_session()
    try:
        default_db_layer.create_domain_service(
            sp,
            service_id=service_id,
            tenant_account_id=principal.tenant_account_id,
            cartridge_type=body.cartridge_type.strip(),
            version=body.version.strip(),
            package_ref=body.package_ref,
            package_checksum=body.package_checksum,
            db_secret_ref="unused",
            db_graph_secret_ref=body.db_graph_secret_ref,
            db_graph_write_secret_ref=body.db_graph_write_secret_ref,
        )
        source_ip, user_agent = _audit_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=principal.tenant_account_id,
            service_id=service_id,
            domain_admin_token_id=principal.token_id,
            event_type="domain_register",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return {
            "service_id": service_id,
            "status": "pending_configuration",
            "created_at": utcnow().isoformat(),
        }
    except IntegrityError as exc:
        sp.rollback()
        raise HTTPException(409, detail="SERVICE_ID_CONFLICT") from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()

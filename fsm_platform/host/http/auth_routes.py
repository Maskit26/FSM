"""Public tenant registration and session routes."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.runtime.engines import platform_session
from fsm_platform.host.security.tenant_auth import (
    TenantAuthError,
    hash_opaque_token,
    hash_password,
    issue_access_token,
    issue_refresh,
    issue_verification,
    normalize_email,
    utcnow,
    verify_password,
)


router = APIRouter(prefix="/v1/auth", tags=["Public Auth"])


class RegisterBody(BaseModel):
    email: str
    password: str


class VerifyEmailBody(BaseModel):
    token: str


class LoginBody(BaseModel):
    email: str
    password: str


class RefreshBody(BaseModel):
    refresh_token: str


def _request_meta(request: Request) -> tuple[str | None, str | None]:
    return (
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )


def _deliver_verification(email: str, raw_token: str) -> bool:
    """Send SMTP mail; return True when dev response may expose the raw token."""
    expose = str(os.environ.get("TENANT_AUTH_EXPOSE_TOKENS") or "").lower() in {
        "1",
        "true",
        "yes",
    }
    host = str(os.environ.get("TENANT_SMTP_HOST") or "").strip()
    if not host:
        if expose:
            return True
        raise TenantAuthError(
            "EMAIL_DELIVERY_DISABLED",
            "configure TENANT_SMTP_HOST or TENANT_AUTH_EXPOSE_TOKENS=1",
            status_code=503,
        )
    message = EmailMessage()
    message["Subject"] = "Verify your FSM Platform account"
    message["From"] = os.environ.get("TENANT_SMTP_FROM", "noreply@localhost")
    message["To"] = email
    verify_base = str(
        os.environ.get("TENANT_VERIFY_URL") or "http://localhost:8000/verify-email"
    ).rstrip("/")
    message.set_content(f"Verify your account: {verify_base}?token={raw_token}\n")
    port = int(os.environ.get("TENANT_SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if str(os.environ.get("TENANT_SMTP_STARTTLS", "1")).lower() not in {
            "0",
            "false",
            "no",
        }:
            smtp.starttls()
        username = str(os.environ.get("TENANT_SMTP_USERNAME") or "")
        if username:
            smtp.login(username, str(os.environ.get("TENANT_SMTP_PASSWORD") or ""))
        smtp.send_message(message)
    return expose


def _auth_error(exc: TenantAuthError) -> HTTPException:
    return HTTPException(
        exc.status_code,
        detail={"error_code": exc.code, "message": str(exc)},
    )


@router.post("/register", status_code=201)
def register(body: RegisterBody, request: Request) -> dict[str, Any]:
    try:
        email = normalize_email(body.email)
        password_hash = hash_password(body.password)
    except TenantAuthError as exc:
        raise _auth_error(exc) from exc
    sp = platform_session()
    try:
        account_id = default_db_layer.create_tenant_account(
            sp, email=email, password_hash=password_hash
        )
        raw_verification = issue_verification(
            default_db_layer, sp, tenant_account_id=account_id
        )
        expose = _deliver_verification(email, raw_verification)
        source_ip, user_agent = _request_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=account_id,
            event_type="tenant_register",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        response: dict[str, Any] = {
            "status": "pending_verification",
            "message": "verification instructions sent",
        }
        if expose:
            response["verification_token"] = raw_verification
        return response
    except IntegrityError as exc:
        sp.rollback()
        raise HTTPException(
            409,
            detail={
                "error_code": "ACCOUNT_EXISTS",
                "message": "account already exists",
            },
        ) from exc
    except TenantAuthError as exc:
        sp.rollback()
        raise _auth_error(exc) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.post("/verify-email")
def verify_email(body: VerifyEmailBody, request: Request) -> dict[str, Any]:
    sp = platform_session()
    try:
        account_id = default_db_layer.consume_email_verification(
            sp, token_hash=hash_opaque_token(body.token)
        )
        if account_id is None:
            raise TenantAuthError(
                "VERIFICATION_TOKEN_INVALID",
                "verification token is invalid or expired",
                status_code=400,
            )
        source_ip, user_agent = _request_meta(request)
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=account_id,
            event_type="tenant_email_verified",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return {"status": "active"}
    except TenantAuthError as exc:
        sp.rollback()
        raise _auth_error(exc) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.post("/login")
def login(body: LoginBody, request: Request) -> dict[str, Any]:
    try:
        email = normalize_email(body.email)
    except TenantAuthError as exc:
        raise _auth_error(exc) from exc
    sp = platform_session()
    source_ip, user_agent = _request_meta(request)
    try:
        account = default_db_layer.get_tenant_account_by_email(sp, email=email)
        valid = bool(account) and verify_password(
            str(account["password_hash"]), body.password
        )
        if not valid:
            if account:
                default_db_layer.record_tenant_login_failure(
                    sp, tenant_account_id=int(account["id"])
                )
            default_db_layer.insert_platform_audit_event(
                sp,
                tenant_account_id=int(account["id"]) if account else None,
                event_type="tenant_login",
                result="deny",
                source_ip=source_ip,
                user_agent=user_agent,
            )
            sp.commit()
            raise TenantAuthError(
                "LOGIN_INVALID", "invalid email or password", status_code=401
            )
        locked_until = account.get("locked_until")
        if locked_until is not None and locked_until > utcnow():
            raise TenantAuthError(
                "LOGIN_LOCKED", "account temporarily locked", status_code=429
            )
        if account.get("status") != "active":
            raise TenantAuthError(
                "ACCOUNT_NOT_ACTIVE", "email verification required", status_code=403
            )
        account_id = int(account["id"])
        access_token, access_ttl = issue_access_token(account_id)
        refresh_token, _, _ = issue_refresh(
            default_db_layer,
            sp,
            tenant_account_id=account_id,
            source_ip=source_ip,
            user_agent=user_agent,
        )
        default_db_layer.record_tenant_login_success(
            sp, tenant_account_id=account_id
        )
        default_db_layer.insert_platform_audit_event(
            sp,
            tenant_account_id=account_id,
            event_type="tenant_login",
            result="ok",
            source_ip=source_ip,
            user_agent=user_agent,
        )
        sp.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_ttl,
            "refresh_token": refresh_token,
        }
    except TenantAuthError as exc:
        sp.rollback()
        raise _auth_error(exc) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.post("/refresh")
def refresh(body: RefreshBody, request: Request) -> dict[str, Any]:
    sp = platform_session()
    source_ip, user_agent = _request_meta(request)
    try:
        row = default_db_layer.get_refresh_token_for_update(
            sp, token_hash=hash_opaque_token(body.refresh_token)
        )
        if row is None:
            raise TenantAuthError("REFRESH_TOKEN_INVALID", status_code=401)
        if row.get("revoked_at") is not None:
            default_db_layer.revoke_refresh_family(sp, family_id=str(row["family_id"]))
            sp.commit()
            raise TenantAuthError("REFRESH_TOKEN_REUSED", status_code=401)
        if row["expires_at"] <= utcnow():
            default_db_layer.revoke_refresh_family(sp, family_id=str(row["family_id"]))
            sp.commit()
            raise TenantAuthError("REFRESH_TOKEN_EXPIRED", status_code=401)
        account = default_db_layer.get_tenant_account(
            sp, tenant_account_id=int(row["tenant_account_id"])
        )
        if account is None or account.get("status") != "active":
            raise TenantAuthError("ACCOUNT_NOT_ACTIVE", status_code=403)
        new_refresh, new_id, _ = issue_refresh(
            default_db_layer,
            sp,
            tenant_account_id=int(row["tenant_account_id"]),
            source_ip=source_ip,
            user_agent=user_agent,
            family_id=str(row["family_id"]),
        )
        if not default_db_layer.rotate_refresh_token(
            sp, old_token_id=int(row["id"]), new_token_id=new_id
        ):
            raise TenantAuthError("REFRESH_TOKEN_REUSED", status_code=401)
        access_token, access_ttl = issue_access_token(int(row["tenant_account_id"]))
        sp.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_ttl,
            "refresh_token": new_refresh,
        }
    except TenantAuthError as exc:
        sp.rollback()
        raise _auth_error(exc) from exc
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@router.post("/logout", status_code=204)
def logout(body: RefreshBody) -> None:
    sp = platform_session()
    try:
        row = default_db_layer.get_refresh_token_for_update(
            sp, token_hash=hash_opaque_token(body.refresh_token)
        )
        if row is not None:
            default_db_layer.revoke_refresh_family(sp, family_id=str(row["family_id"]))
        sp.commit()
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()

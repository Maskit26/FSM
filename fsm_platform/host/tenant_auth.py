"""Tenant account, session and DOMAIN_ADMIN_TOKEN primitives."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from fsm_platform.core.db_layer import FsmDbLayer, SessionLike


_password_hasher = PasswordHasher()


def utcnow() -> datetime:
    """Naive UTC for MySQL DATETIME columns."""
    return datetime.now(UTC).replace(tzinfo=None)


class TenantAuthError(Exception):
    def __init__(self, code: str, message: str = "", *, status_code: int = 401) -> None:
        self.code = code
        self.status_code = status_code
        super().__init__(message or code)


@dataclass(frozen=True)
class TenantPrincipal:
    tenant_account_id: int
    token_id: Optional[int] = None


def normalize_email(value: str) -> str:
    email = str(value or "").strip().casefold()
    if len(email) > 255 or "@" not in email:
        raise TenantAuthError("EMAIL_INVALID", "valid email required", status_code=400)
    local, _, domain = email.partition("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise TenantAuthError("EMAIL_INVALID", "valid email required", status_code=400)
    return email


def validate_password(value: str) -> str:
    password = str(value or "")
    if len(password) < 12 or len(password) > 256:
        raise TenantAuthError(
            "PASSWORD_POLICY",
            "password must contain 12 to 256 characters",
            status_code=400,
        )
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise TenantAuthError(
            "PASSWORD_POLICY",
            "password must contain letters and digits",
            status_code=400,
        )
    return password


def hash_password(password: str) -> str:
    return _password_hasher.hash(validate_password(password))


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return bool(_password_hasher.verify(password_hash, password))
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def hash_opaque_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def new_opaque_token(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _access_secret() -> bytes:
    value = str(os.environ.get("TENANT_AUTH_SECRET") or "").strip()
    if len(value) < 32:
        raise TenantAuthError(
            "TENANT_AUTH_DISABLED",
            "TENANT_AUTH_SECRET must contain at least 32 characters",
            status_code=503,
        )
    return value.encode("utf-8")


def issue_access_token(tenant_account_id: int) -> tuple[str, int]:
    ttl = max(60, int(os.environ.get("TENANT_ACCESS_TOKEN_TTL_SECONDS", "900")))
    now = int(time.time())
    header = _b64encode(b'{"alg":"HS256","typ":"JWT"}')
    payload = _b64encode(
        json.dumps(
            {
                "sub": str(int(tenant_account_id)),
                "iat": now,
                "exp": now + ttl,
                "purpose": "tenant_access",
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    signing_input = f"{header}.{payload}".encode("ascii")
    signature = _b64encode(hmac.new(_access_secret(), signing_input, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}", ttl


def verify_access_token(raw_token: str) -> TenantPrincipal:
    try:
        header, payload, signature = raw_token.split(".")
        signing_input = f"{header}.{payload}".encode("ascii")
        expected = _b64encode(
            hmac.new(_access_secret(), signing_input, hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        claims = json.loads(_b64decode(payload))
        if claims.get("purpose") != "tenant_access":
            raise ValueError("purpose")
        if int(claims["exp"]) <= int(time.time()):
            raise TenantAuthError("ACCESS_TOKEN_EXPIRED", status_code=401)
        return TenantPrincipal(tenant_account_id=int(claims["sub"]))
    except TenantAuthError:
        raise
    except Exception as exc:
        raise TenantAuthError("ACCESS_TOKEN_INVALID", status_code=401) from exc


def issue_verification(
    db: FsmDbLayer,
    session: SessionLike,
    *,
    tenant_account_id: int,
) -> str:
    raw = new_opaque_token("tverify")
    ttl = max(300, int(os.environ.get("TENANT_EMAIL_TOKEN_TTL_SECONDS", "86400")))
    db.create_email_verification(
        session,
        tenant_account_id=tenant_account_id,
        token_hash=hash_opaque_token(raw),
        expires_at=utcnow() + timedelta(seconds=ttl),
    )
    return raw


def issue_refresh(
    db: FsmDbLayer,
    session: SessionLike,
    *,
    tenant_account_id: int,
    source_ip: Optional[str],
    user_agent: Optional[str],
    family_id: Optional[str] = None,
) -> tuple[str, int, str]:
    raw = new_opaque_token("trefresh")
    family = family_id or str(uuid4())
    ttl = max(3600, int(os.environ.get("TENANT_REFRESH_TOKEN_TTL_SECONDS", "2592000")))
    token_id = db.create_refresh_token(
        session,
        tenant_account_id=tenant_account_id,
        token_hash=hash_opaque_token(raw),
        family_id=family,
        expires_at=utcnow() + timedelta(seconds=ttl),
        source_ip=source_ip,
        user_agent=user_agent,
    )
    return raw, token_id, family


def issue_domain_token(
    db: FsmDbLayer,
    session: SessionLike,
    *,
    tenant_account_id: int,
    name: Optional[str],
    expires_in_days: Optional[int],
) -> tuple[str, dict[str, Any]]:
    raw = new_opaque_token("dadmin")
    expires_at = None
    if expires_in_days is not None:
        if expires_in_days < 1 or expires_in_days > 3650:
            raise TenantAuthError(
                "TOKEN_EXPIRY_INVALID",
                "expires_in_days must be between 1 and 3650",
                status_code=400,
            )
        expires_at = utcnow() + timedelta(days=expires_in_days)
    token_id = db.create_domain_admin_token(
        session,
        tenant_account_id=tenant_account_id,
        token_hash=hash_opaque_token(raw),
        token_prefix=raw[:16],
        name=(str(name).strip()[:128] or None) if name is not None else None,
        expires_at=expires_at,
    )
    return raw, {
        "id": token_id,
        "prefix": raw[:16],
        "name": (str(name).strip()[:128] or None) if name is not None else None,
        "expires_at": expires_at,
    }


def authenticate_domain_token(
    db: FsmDbLayer,
    session: SessionLike,
    *,
    raw_token: Optional[str],
) -> TenantPrincipal:
    token = str(raw_token or "").strip()
    if not token.startswith("dadmin_"):
        raise TenantAuthError("DOMAIN_TOKEN_INVALID", status_code=401)
    digest = hash_opaque_token(token)
    row = db.get_domain_admin_token(session, token_hash=digest)
    if row is None:
        raise TenantAuthError("DOMAIN_TOKEN_INVALID", status_code=401)
    if not hmac.compare_digest(str(row["token_hash"]), digest):
        raise TenantAuthError("DOMAIN_TOKEN_INVALID", status_code=401)
    if row.get("revoked_at") is not None:
        raise TenantAuthError("DOMAIN_TOKEN_REVOKED", status_code=401)
    expires_at = row.get("expires_at")
    if expires_at is not None and expires_at <= utcnow():
        raise TenantAuthError("DOMAIN_TOKEN_EXPIRED", status_code=401)
    db.touch_domain_admin_token(session, token_id=int(row["id"]))
    return TenantPrincipal(
        tenant_account_id=int(row["tenant_account_id"]),
        token_id=int(row["id"]),
    )

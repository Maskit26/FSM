"""End-user Domain API tokens (не DOMAIN_ADMIN_TOKEN).

Подпись — per-tenant секрет в domain_secrets (`end_user_token_secret`),
не PLATFORM_*.env. Выпускает бэкенд арендатора после login домена.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Optional

from fsm_platform.host.runtime.runtime_context import service_scope
from fsm_platform.host.security.secrets import (
    SecretsError,
    get_domain_secret,
    set_domain_secret,
)

SECRET_KEY = "end_user_token_secret"
_PREFIX = "eut1"


class EndUserTokenError(Exception):
    def __init__(self, code: str, message: str = "", *, status_code: int = 401) -> None:
        self.code = code
        self.status_code = status_code
        super().__init__(message or code)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def _load_or_create_signing_secret(service_id: str, *, create: bool) -> str:
    sid = str(service_id or "").strip()
    if not sid:
        raise EndUserTokenError("SERVICE_ID_REQUIRED", status_code=400)
    try:
        with service_scope(sid):
            existing = get_domain_secret(SECRET_KEY)
            if existing and str(existing).strip():
                return str(existing).strip()
            if not create:
                raise EndUserTokenError(
                    "END_USER_TOKENS_DISABLED",
                    f"domain secret {SECRET_KEY!r} not set for this service",
                    status_code=503,
                )
            raw = secrets.token_urlsafe(32)
            set_domain_secret(SECRET_KEY, raw)
            return raw
    except EndUserTokenError:
        raise
    except SecretsError as exc:
        raise EndUserTokenError(
            exc.code,
            str(exc),
            status_code=503 if exc.code in {"ADMIN_DISABLED", "DEK_MISSING"} else 500,
        ) from exc


def issue_end_user_token(
    *,
    service_id: str,
    actor_type: str,
    actor_id: str,
    roles: Optional[list[str]] = None,
    ttl_seconds: int = 86400,
) -> dict[str, Any]:
    secret = _load_or_create_signing_secret(service_id, create=True)
    sid = str(service_id or "").strip()
    at = str(actor_type or "user").strip() or "user"
    aid = str(actor_id or "").strip()
    if not aid:
        raise EndUserTokenError("ACTOR_ID_REQUIRED", status_code=400)
    ttl = int(ttl_seconds)
    if ttl < 60:
        ttl = 60
    if ttl > 30 * 86400:
        ttl = 30 * 86400
    now = int(time.time())
    role_list = [str(r).strip() for r in (roles or []) if str(r).strip()]
    if at and at not in role_list:
        role_list = [at, *role_list]
    payload = {
        "v": 1,
        "purpose": "domain_end_user",
        "sid": sid,
        "at": at,
        "aid": aid,
        "roles": role_list,
        "iat": now,
        "exp": now + ttl,
    }
    body = _b64url(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    sig = hmac.new(
        secret.encode("utf-8"), f"{_PREFIX}.{body}".encode("utf-8"), hashlib.sha256
    ).hexdigest()[:32]
    token = f"{_PREFIX}.{body}.{sig}"
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": ttl,
        "expires_at": now + ttl,
        "service_id": sid,
        "actor_type": at,
        "actor_id": aid,
        "roles": role_list,
    }


def verify_end_user_token(
    raw_token: str,
    *,
    service_id: str,
) -> dict[str, Any]:
    secret = _load_or_create_signing_secret(service_id, create=False)
    token = str(raw_token or "").strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != _PREFIX:
        raise EndUserTokenError("END_USER_TOKEN_INVALID", status_code=401)
    body, sig = parts[1], parts[2]
    expected = hmac.new(
        secret.encode("utf-8"), f"{_PREFIX}.{body}".encode("utf-8"), hashlib.sha256
    ).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        raise EndUserTokenError("END_USER_TOKEN_INVALID", status_code=401)
    try:
        claims = json.loads(_b64url_decode(body))
    except Exception as exc:
        raise EndUserTokenError("END_USER_TOKEN_INVALID", status_code=401) from exc
    if claims.get("purpose") != "domain_end_user" or int(claims.get("v") or 0) != 1:
        raise EndUserTokenError("END_USER_TOKEN_INVALID", status_code=401)
    if int(claims.get("exp") or 0) <= int(time.time()):
        raise EndUserTokenError("END_USER_TOKEN_EXPIRED", status_code=401)
    sid = str(claims.get("sid") or "").strip()
    if sid != str(service_id or "").strip():
        raise EndUserTokenError("END_USER_TOKEN_SERVICE_MISMATCH", status_code=403)
    aid = str(claims.get("aid") or "").strip()
    if not aid:
        raise EndUserTokenError("END_USER_TOKEN_INVALID", status_code=401)
    at = str(claims.get("at") or "user").strip() or "user"
    roles_raw = claims.get("roles") or []
    roles = (
        [str(r).strip() for r in roles_raw if str(r).strip()]
        if isinstance(roles_raw, list)
        else []
    )
    return {
        "actor_type": at,
        "actor_id": aid,
        "channel": "api",
        "roles": roles,
        "service_id": sid,
    }


def looks_like_end_user_token(raw: str) -> bool:
    text = str(raw or "").strip()
    return text.startswith(f"{_PREFIX}.") and text.count(".") == 2

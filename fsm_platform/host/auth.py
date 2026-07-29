"""
Аутентификация Public API.

Режим off (dev): PLATFORM_AUTH_SECRET не задан — actor из тела как раньше.
Режим on: Authorization: Bearer <actor_type>:<actor_id>:<sig>
  sig = HMAC-SHA256(secret, "{actor_type}:{actor_id}").hexdigest()[:24]
Тело actor игнорируется для identity — подставляется из заранее выданного
actor token. Tenant account access token и DOMAIN_ADMIN_TOKEN — отдельные
контуры и здесь не проверяются.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any, Optional


class AuthError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def auth_enabled() -> bool:
    return bool((os.environ.get("PLATFORM_AUTH_SECRET") or "").strip())


def _secret() -> str:
    return (os.environ.get("PLATFORM_AUTH_SECRET") or "").strip()


def make_token(*, actor_type: str = "user", actor_id: str) -> str:
    """Собирает Bearer token для actor."""
    secret = _secret()
    if not secret:
        raise AuthError("AUTH_DISABLED", "PLATFORM_AUTH_SECRET not set")
    at = str(actor_type or "user").strip() or "user"
    aid = str(actor_id).strip()
    if not aid:
        raise AuthError("ACTOR_ID_REQUIRED")
    raw = f"{at}:{aid}"
    sig = hmac.new(
        secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:24]
    return f"{raw}:{sig}"


def verify_bearer(authorization: Optional[str]) -> dict[str, str]:
    """
    Парсит Authorization: Bearer … → {actor_type, actor_id, channel}.
    channel всегда api (WS передаёт свой).
    """
    if not auth_enabled():
        raise AuthError("AUTH_DISABLED")
    header = (authorization or "").strip()
    if not header.lower().startswith("bearer "):
        raise AuthError("AUTH_REQUIRED", "Authorization: Bearer required")
    token = header[7:].strip()
    parts = token.split(":")
    if len(parts) != 3:
        raise AuthError("AUTH_INVALID", "token format actor_type:actor_id:sig")
    actor_type, actor_id, sig = parts[0], parts[1], parts[2]
    expected = make_token(actor_type=actor_type, actor_id=actor_id)
    expected_sig = expected.rsplit(":", 1)[-1]
    if not hmac.compare_digest(sig, expected_sig):
        raise AuthError("AUTH_INVALID", "bad signature")
    return {
        "actor_type": actor_type,
        "actor_id": actor_id,
        "channel": "api",
    }


def resolve_actor(
    *,
    authorization: Optional[str],
    body_actor: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """
    Если auth включён — actor только из Bearer.
    Если выключен — actor из body (dev).
    """
    if not auth_enabled():
        if not body_actor or body_actor.get("actor_id") in (None, ""):
            raise AuthError("ACTOR_REQUIRED", "actor.actor_id required")
        return {
            "actor_type": str(body_actor.get("actor_type") or "user"),
            "actor_id": str(body_actor["actor_id"]),
            "channel": str(body_actor.get("channel") or "api"),
        }
    return verify_bearer(authorization)

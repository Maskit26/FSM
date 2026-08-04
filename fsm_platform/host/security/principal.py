"""End-user Principal for Domain API (не DOMAIN_ADMIN_TOKEN)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class Principal:
    """
    Кто смотрит/действует в домене.
    Минимум: user_id + roles (из actor_type и/или явного roles).
    """

    user_id: str
    roles: tuple[str, ...] = ()
    actor_type: str = "user"
    channel: str = "api"

    def has_role(self, *names: str) -> bool:
        wanted = {str(n).strip().lower() for n in names if str(n).strip()}
        have = {r.strip().lower() for r in self.roles if str(r).strip()}
        at = (self.actor_type or "").strip().lower()
        if at:
            have.add(at)
        return bool(wanted & have)

    def to_dict(self) -> dict[str, Any]:
        return {
            "userId": self.user_id,
            "user_id": self.user_id,
            "roles": list(self.roles),
            "actor_type": self.actor_type,
            "channel": self.channel,
            "actor_id": self.user_id,
        }

    def as_actor(self) -> dict[str, Any]:
        return {
            "actor_type": self.actor_type,
            "actor_id": self.user_id,
            "channel": self.channel,
            "roles": list(self.roles),
        }


def principal_from_actor(actor: dict[str, Any]) -> Principal:
    """Собирает Principal из resolve_actor / body actor."""
    raw = actor or {}
    uid = str(raw.get("actor_id") or raw.get("userId") or raw.get("user_id") or "").strip()
    if not uid:
        raise ValueError("principal.user_id required")
    at = str(raw.get("actor_type") or "user").strip() or "user"
    roles_raw = raw.get("roles")
    roles: list[str] = []
    if isinstance(roles_raw, (list, tuple)):
        roles = [str(r).strip() for r in roles_raw if str(r).strip()]
    elif isinstance(roles_raw, str) and roles_raw.strip():
        roles = [p.strip() for p in roles_raw.split(",") if p.strip()]
    if at and at not in roles:
        roles = [at, *roles]
    channel = str(raw.get("channel") or "api").strip() or "api"
    return Principal(
        user_id=uid,
        roles=tuple(roles),
        actor_type=at,
        channel=channel,
    )


def try_principal_from_actor(actor: Optional[dict[str, Any]]) -> Optional[Principal]:
    if not actor:
        return None
    try:
        return principal_from_actor(actor)
    except ValueError:
        return None

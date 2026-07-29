"""
Inbound hook registry + dispatch через Domain Contract API.

Домен объявляет channels в catalog; platform проксирует HTTP → domain service.
"""

from __future__ import annotations

import base64
from typing import Any, Optional


class WebhookRegistry:
    """(service_id, channel) → declared. Handler живёт только в domain service."""

    def __init__(self) -> None:
        self._channels: set[tuple[str, str]] = set()

    def register_channel(self, service_id: str, channel: str) -> None:
        sid = str(service_id or "").strip()
        ch = str(channel or "").strip().lower()
        if not sid or not ch:
            raise ValueError("service_id and channel required")
        self._channels.add((sid, ch))

    def has(self, service_id: str, channel: str) -> bool:
        return (
            str(service_id).strip(),
            str(channel or "").strip().lower(),
        ) in self._channels

    def list_channels(self, service_id: str) -> list[str]:
        sid = str(service_id).strip()
        return sorted(ch for (s, ch) in self._channels if s == sid)

    def clear(self) -> None:
        self._channels.clear()

    def unregister(self, service_id: str) -> None:
        sid = str(service_id).strip()
        self._channels = {(s, ch) for (s, ch) in self._channels if s != sid}


default_webhook_registry = WebhookRegistry()


class HookError(Exception):
    """Отказ inbound hook → HTTP status."""

    def __init__(
        self,
        code: str,
        message: str = "",
        *,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.status_code = int(status_code)
        super().__init__(message or code)


def dispatch_inbound_hook(
    service_id: str,
    channel: str,
    *,
    body: Any,
    headers: dict[str, str],
    query: dict[str, str],
    raw_body: bytes = b"",
) -> dict[str, Any]:
    """Проксирует inbound hook в domain service (Contract API)."""
    from fsm_platform.host.contract_client import ContractError, get_contract_client
    from fsm_platform.host.contract_side_effects import apply_declared
    from fsm_platform.host.domain_bootstrap import is_domain_ready
    from fsm_platform.host.engines import platform_session
    from fsm_platform.host.runtime_context import service_scope

    ch = str(channel or "").strip().lower()
    if not default_webhook_registry.has(service_id, ch):
        raise HookError(
            "UNKNOWN_HOOK_CHANNEL",
            f"no inbound hook for channel={ch!r}",
            status_code=404,
        )
    if not is_domain_ready(service_id):
        raise HookError(
            "DOMAIN_NOT_READY",
            "domain service catalog not loaded",
            status_code=503,
        )

    raw_b64 = base64.b64encode(raw_body).decode("ascii") if raw_body else None
    try:
        with service_scope(service_id):
            result = get_contract_client(service_id).call_hook(
                ch,
                body=body,
                headers=headers,
                query=query,
                raw_body_b64=raw_b64,
            )
    except ContractError as exc:
        status = 503 if exc.transient else (exc.status_code or 502)
        if status == 404:
            status = 404
        raise HookError(exc.code, exc.message, status_code=int(status)) from exc

    sp = platform_session()
    try:
        with service_scope(service_id):
            apply_declared(sp, service_id=service_id, data=result)
        sp.commit()
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()

    if result is None:
        return {"ok": True, "service_id": service_id, "channel": ch}
    if isinstance(result, dict):
        return result
    return {"ok": True, "service_id": service_id, "channel": ch, "data": result}

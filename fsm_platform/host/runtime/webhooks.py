"""Webhook subscriptions: register + fan-out platform_events → platform_outbox."""

from __future__ import annotations

import json
from typing import Any, Optional

from fsm_platform.core.db_layer import SessionLike, default_db_layer
from fsm_platform.host.runtime import side_effects


def _event_types_match(raw: Any, event_type: str) -> bool:
    """event_types JSON: null / ['*'] / ['fsm.instance.completed', …]."""
    if raw is None or raw == "" or raw == "*":
        return True
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip() in ("*", event_type)
    if isinstance(raw, list):
        if not raw or "*" in raw:
            return True
        return event_type in {str(x) for x in raw}
    return False


def fanout_webhooks(
    session_platform: SessionLike,
    *,
    service_id: str,
    event_type: str,
    event_id: int,
    instance_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    payload: Optional[dict[str, Any]] = None,
) -> int:
    """
    Для каждой active webhook_subscriptions → notify(channel=webhook).
    Возвращает число поставленных outbox-строк (0 если нет подписок / дубликаты).
    """
    subs = default_db_layer.list_webhook_subscriptions(
        session_platform, service_id=service_id, active_only=True
    )
    n = 0
    body = {
        "event_id": int(event_id),
        "event_type": event_type,
        "service_id": service_id,
        "instance_id": instance_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload or {},
    }
    for sub in subs:
        if not _event_types_match(sub.get("event_types"), event_type):
            continue
        sub_id = int(sub["id"])
        dest = str(sub.get("url") or "").strip()
        if not dest:
            continue
        oid = side_effects.notify(
            session_platform,
            service_id=service_id,
            channel="webhook",
            destination=dest,
            event_type=event_type,
            payload={
                **body,
                "subscription_id": sub_id,
            },
            idempotency_key=f"webhook:{sub_id}:event:{int(event_id)}",
        )
        if oid:
            n += 1
    return n


def emit_event_with_webhooks(
    session_platform: SessionLike,
    *,
    service_id: str,
    event_type: str,
    instance_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    payload: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    client_request_id: Optional[str] = None,
) -> int:
    """emit_event + fan-out webhooks (platform COMPLETED/FAILED hook)."""
    event_id = side_effects.emit_event(
        session_platform,
        service_id=service_id,
        event_type=event_type,
        instance_id=instance_id,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        correlation_id=correlation_id,
        client_request_id=client_request_id,
    )
    fanout_webhooks(
        session_platform,
        service_id=service_id,
        event_type=event_type,
        event_id=event_id,
        instance_id=instance_id,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    )
    return event_id

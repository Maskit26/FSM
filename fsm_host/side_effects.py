"""Official domain → platform write API (§4.13). No raw SQL from domains."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text

from fsm_platform.db_layer import SessionLike
from fsm_platform.timers import schedule_timer as _schedule_timer


def schedule_timer(
    session_platform: SessionLike,
    *,
    service_id: str,
    entity_type: str,
    entity_id: int,
    process_name: str,
    fire_at: datetime,
    payload: Optional[dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> int:
    return _schedule_timer(
        session_platform,
        service_id=service_id,
        entity_type=entity_type,
        entity_id=entity_id,
        process_name=process_name,
        fire_at=fire_at,
        payload=payload,
        idempotency_key=idempotency_key,
    )


def notify(
    session_platform: SessionLike,
    *,
    service_id: str,
    channel: str,
    destination: str,
    event_type: str,
    payload: Optional[dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> int:
    """INSERT platform_outbox (PENDING). HTTP only after commit via outbox_worker."""
    result = session_platform.execute(
        text(
            """
            INSERT INTO platform_outbox
                (service_id, channel, destination, event_type, payload_json,
                 status, attempts, next_attempt_at, idempotency_key, created_at)
            VALUES
                (:service_id, :channel, :destination, :event_type, :payload_json,
                 'PENDING', 0, UTC_TIMESTAMP(), :idempotency_key, UTC_TIMESTAMP())
            """
        ),
        {
            "service_id": service_id,
            "channel": channel,
            "destination": destination,
            "event_type": event_type,
            "payload_json": json.dumps(payload or {}),
            "idempotency_key": idempotency_key,
        },
    )
    return int(result.lastrowid)


def emit_event(
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
    """Sole writer of platform_events."""
    result = session_platform.execute(
        text(
            """
            INSERT INTO platform_events
                (service_id, event_type, instance_id, entity_type, entity_id,
                 payload_json, correlation_id, client_request_id, created_at)
            VALUES
                (:service_id, :event_type, :instance_id, :entity_type, :entity_id,
                 :payload_json, :correlation_id, :client_request_id, UTC_TIMESTAMP())
            """
        ),
        {
            "service_id": service_id,
            "event_type": event_type,
            "instance_id": instance_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload_json": json.dumps(payload or {}),
            "correlation_id": correlation_id,
            "client_request_id": client_request_id,
        },
    )
    return int(result.lastrowid)

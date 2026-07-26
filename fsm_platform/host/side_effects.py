"""Официальный API домена → platform side-effects. Без raw SQL."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fsm_platform.core.db_layer import SessionLike, default_db_layer
from fsm_platform.core.timers import schedule_timer as _schedule_timer


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
    owner: str = "domain",
) -> int:
    """Планирует таймер FSM на platform. owner=domain|platform."""
    return _schedule_timer(
        session_platform,
        service_id=service_id,
        entity_type=entity_type,
        entity_id=entity_id,
        process_name=process_name,
        fire_at=fire_at,
        payload=payload,
        idempotency_key=idempotency_key,
        owner=owner,
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
    """
    Кладёт уведомление в platform_outbox (PENDING).
    Реальная отправка HTTP — только после commit, outbox-worker’ом.
    """
    return default_db_layer.insert_outbox(
        session_platform,
        service_id=service_id,
        channel=channel,
        destination=destination,
        event_type=event_type,
        payload=payload,
        idempotency_key=idempotency_key,
    )


def start_saga(
    session_platform: SessionLike,
    *,
    service_id: str,
    children: list[dict[str, Any]],
    on_success: Optional[dict[str, Any]] = None,
    on_fail: Optional[dict[str, Any]] = None,
    fail_policy: str = "fail_fast",
    payload: Optional[dict[str, Any]] = None,
    actor_id: Optional[int] = None,
) -> tuple[int, list[int]]:
    """Старт async-саги: children instances + fan-in on_success/on_fail."""
    from fsm_platform.core.sagas import start_saga as _start_saga

    return _start_saga(
        session_platform,
        service_id=service_id,
        children=children,
        on_success=on_success,
        on_fail=on_fail,
        fail_policy=fail_policy,
        payload=payload,
        actor_id=actor_id,
    )


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
    """
    Пишет доменное/платформенное событие в platform_events.
    Единая точка записи событий для SSE/аудита.
    """
    return default_db_layer.insert_event(
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

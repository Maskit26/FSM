"""Schedule / cancel fsm_timers via db_layer. Does not poll or fire timers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer


def schedule_timer(
    session: SessionLike,
    *,
    service_id: str,
    entity_type: str,
    entity_id: int,
    process_name: str,
    fire_at: datetime,
    payload: Optional[dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
    db_layer: FsmDbLayer | None = None,
) -> int:
    db = db_layer or default_db_layer
    return db.insert_timer(
        session,
        service_id=service_id,
        entity_type=entity_type,
        entity_id=entity_id,
        process_name=process_name,
        fire_at=fire_at,
        payload=payload,
        idempotency_key=idempotency_key,
    )


def cancel_timer(
    session: SessionLike,
    timer_id: int,
    db: Any = None,
    db_layer: FsmDbLayer | None = None,
) -> None:
    layer = db_layer or default_db_layer
    layer.cancel_timer(session, timer_id)

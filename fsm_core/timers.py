from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


def schedule_timer(
    session: Any,
    db: Any,
    *,
    service: str,
    entity_type: str,
    entity_id: int,
    process_name: str,
    fire_at: datetime,
    payload: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> int:
    """Create an FSM timer when the database migration is installed."""

    return db.create_fsm_timer(
        session=session,
        service=service,
        entity_type=entity_type,
        entity_id=entity_id,
        process_name=process_name,
        fire_at=fire_at,
        payload=payload,
        idempotency_key=idempotency_key,
    )


def cancel_timer(session: Any, db: Any, timer_id: int) -> None:
    db.cancel_fsm_timer(session=session, timer_id=timer_id)

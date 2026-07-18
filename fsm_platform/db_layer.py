"""SQL against platform DB only. Sessions are owned by worker / Request Runtime."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


SessionLike = Session | Connection


class FsmDbLayer:
    """Platform persistence: entity_fsm_state, fsm_transition_logs, fsm_timers, helpers."""

    # --- entity_fsm_state ---

    def get_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
    ) -> Optional[str]:
        row = session.execute(
            text(
                """
                SELECT current_state
                FROM entity_fsm_state
                WHERE service_id = :service_id
                  AND entity_type = :entity_type
                  AND entity_id = :entity_id
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
            },
        ).mappings().first()
        return None if row is None else str(row["current_state"])

    def upsert_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        session.execute(
            text(
                """
                INSERT INTO entity_fsm_state
                    (service_id, entity_type, entity_id, current_state, updated_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :current_state, UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    current_state = VALUES(current_state),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
            },
        )

    def insert_entity_state_initial(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        session.execute(
            text(
                """
                INSERT INTO entity_fsm_state
                    (service_id, entity_type, entity_id, current_state, updated_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :current_state, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
            },
        )

    # --- fsm_transition_logs ---

    def insert_transition_log(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        from_state: str,
        to_state: str,
        event_name: str,
        transition_id: int,
        instance_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        session.execute(
            text(
                """
                INSERT INTO fsm_transition_logs
                    (service_id, entity_type, entity_id, from_state, to_state,
                     event_name, transition_id, instance_id, user_id, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :from_state, :to_state,
                     :event_name, :transition_id, :instance_id, :user_id, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "instance_id": instance_id,
                "user_id": user_id,
            },
        )

    def insert_transition_log_idempotent(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        from_state: str,
        to_state: str,
        event_name: str,
        transition_id: int,
        instance_id: int,
        user_id: Optional[int] = None,
    ) -> bool:
        """INSERT ignore duplicate (instance_id, transition_id). Returns True if inserted."""
        result = session.execute(
            text(
                """
                INSERT IGNORE INTO fsm_transition_logs
                    (service_id, entity_type, entity_id, from_state, to_state,
                     event_name, transition_id, instance_id, user_id, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :from_state, :to_state,
                     :event_name, :transition_id, :instance_id, :user_id, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "instance_id": instance_id,
                "user_id": user_id,
            },
        )
        return bool(result.rowcount and result.rowcount > 0)

    # --- fsm_timers ---

    def insert_timer(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        process_name: str,
        fire_at: datetime,
        payload: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO fsm_timers
                    (service_id, entity_type, entity_id, process_name, fire_at,
                     status, payload_json, idempotency_key, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :process_name, :fire_at,
                     'SCHEDULED', :payload_json, :idempotency_key, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "process_name": process_name,
                "fire_at": fire_at,
                "payload_json": json.dumps(payload) if payload is not None else None,
                "idempotency_key": idempotency_key,
            },
        )
        return int(result.lastrowid)

    def cancel_timer(self, session: SessionLike, timer_id: int) -> None:
        session.execute(
            text(
                """
                UPDATE fsm_timers
                SET status = 'CANCELLED', cancelled_at = UTC_TIMESTAMP()
                WHERE id = :timer_id AND status = 'SCHEDULED'
                """
            ),
            {"timer_id": timer_id},
        )


default_db_layer = FsmDbLayer()

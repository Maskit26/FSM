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

    # --- server_fsm_instances ---

    def insert_fsm_instance(
        self,
        session: SessionLike,
        *,
        service_id: str,
        process_name: str,
        entity_type: str,
        entity_id: int,
        payload: Optional[dict[str, Any]] = None,
        requested_by_user_id: Optional[int] = None,
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO server_fsm_instances
                    (service_id, process_name, entity_type, entity_id, status,
                     attempts, payload_json, requested_by_user_id,
                     created_at, updated_at)
                VALUES
                    (:service_id, :process_name, :entity_type, :entity_id, 'PENDING',
                     0, :payload_json, :uid, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "process_name": process_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payload_json": json.dumps(payload or {}),
                "uid": requested_by_user_id,
            },
        )
        return int(result.lastrowid)

    def get_fsm_instance(
        self,
        session: SessionLike,
        service_id: str,
        instance_id: int,
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, last_error, payload_json,
                       created_at, started_at, finished_at
                FROM server_fsm_instances
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {"id": instance_id, "service_id": service_id},
        ).mappings().first()
        return dict(row) if row else None

    def claim_pending_instance(
        self, session: SessionLike
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, payload_json, requested_by_user_id
                FROM server_fsm_instances
                WHERE status = 'PENDING'
                ORDER BY id ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
                """
            )
        ).mappings().first()
        if row is None:
            return None
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'PROCESSING',
                    started_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": row["id"]},
        )
        return dict(row)

    def mark_instance_completed(
        self, session: SessionLike, instance_id: int
    ) -> None:
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'COMPLETED', finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP(), last_error = NULL
                WHERE id = :id
                """
            ),
            {"id": instance_id},
        )

    def mark_instance_failed(
        self, session: SessionLike, instance_id: int, last_error: str
    ) -> None:
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'FAILED', last_error = :err,
                    finished_at = UTC_TIMESTAMP(), updated_at = UTC_TIMESTAMP(),
                    attempts = attempts + 1
                WHERE id = :id
                """
            ),
            {"id": instance_id, "err": (last_error or "")[:2000]},
        )

    # --- platform_reconcile_queue ---

    def enqueue_reconcile(
        self,
        session: SessionLike,
        *,
        service_id: str,
        instance_id: int,
        entity_type: Optional[str],
        entity_id: Optional[int],
        from_state: Optional[str],
        to_state: Optional[str],
        event_name: Optional[str],
        transition_id: Optional[int],
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        session.execute(
            text(
                """
                INSERT INTO platform_reconcile_queue
                    (service_id, instance_id, entity_type, entity_id,
                     from_state, to_state, event_name, transition_id,
                     payload_json, status, attempts, created_at, updated_at)
                VALUES
                    (:service_id, :instance_id, :entity_type, :entity_id,
                     :from_state, :to_state, :event_name, :transition_id,
                     :payload_json, 'PENDING', 0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    status = IF(status = 'DONE', status, 'PENDING'),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": service_id,
                "instance_id": instance_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "payload_json": json.dumps(payload or {}),
            },
        )

    # --- platform_outbox / platform_events ---

    def insert_outbox(
        self,
        session: SessionLike,
        *,
        service_id: str,
        channel: str,
        destination: str,
        event_type: str,
        payload: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> int:
        result = session.execute(
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

    def insert_event(
        self,
        session: SessionLike,
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
        result = session.execute(
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

    # --- domain_services (boot) ---

    def list_active_domain_services(
        self, session: SessionLike
    ) -> list[dict[str, Any]]:
        rows = session.execute(
            text(
                """
                SELECT service_id, db_secret_ref, status
                FROM domain_services
                WHERE status = 'active'
                """
            )
        ).mappings().all()
        return [dict(r) for r in rows]


default_db_layer = FsmDbLayer()

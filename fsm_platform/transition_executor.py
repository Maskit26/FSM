"""Apply one transition: entity_fsm_state + fsm_transition_logs (platform only)."""

from __future__ import annotations

from typing import Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer
from .errors import FsmErrorCodes
from .types import TransitionDef


class TransitionApplyError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


class TransitionExecutor:
    def __init__(self, db_layer: FsmDbLayer | None = None) -> None:
        self._db = db_layer or default_db_layer

    def apply(
        self,
        session_platform: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        transition: TransitionDef,
        event_name: str,
        user_id: Optional[int] = None,
        instance_id: Optional[int] = None,
        allow_idempotent: bool = False,
    ) -> None:
        """
        1) Check current_state == from_state (or already to_state if allow_idempotent)
        2) UPSERT current_state = to_state
        3) INSERT fsm_transition_logs
        """
        current = self._db.get_entity_state(
            session_platform, service_id, entity_type, entity_id
        )
        if current is None:
            raise TransitionApplyError(
                FsmErrorCodes.ENTITY_STATE_NOT_FOUND,
                f"{entity_type}/{entity_id}",
            )

        if current == transition.to_state and allow_idempotent:
            if instance_id is not None:
                self._db.insert_transition_log_idempotent(
                    session_platform,
                    service_id=service_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    from_state=transition.from_state,
                    to_state=transition.to_state,
                    event_name=event_name,
                    transition_id=transition.id,
                    instance_id=instance_id,
                    user_id=user_id,
                )
            return

        if current != transition.from_state:
            raise TransitionApplyError(
                FsmErrorCodes.STATE_MISMATCH,
                f"expected={transition.from_state} actual={current}",
            )

        self._db.upsert_entity_state(
            session_platform,
            service_id,
            entity_type,
            entity_id,
            transition.to_state,
        )

        if instance_id is not None and allow_idempotent:
            self._db.insert_transition_log_idempotent(
                session_platform,
                service_id=service_id,
                entity_type=entity_type,
                entity_id=entity_id,
                from_state=transition.from_state,
                to_state=transition.to_state,
                event_name=event_name,
                transition_id=transition.id,
                instance_id=instance_id,
                user_id=user_id,
            )
        else:
            self._db.insert_transition_log(
                session_platform,
                service_id=service_id,
                entity_type=entity_type,
                entity_id=entity_id,
                from_state=transition.from_state,
                to_state=transition.to_state,
                event_name=event_name,
                transition_id=transition.id,
                instance_id=instance_id,
                user_id=user_id,
            )

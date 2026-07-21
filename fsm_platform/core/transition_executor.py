"""Применение одного перехода: entity_fsm_state и fsm_transition_logs только в платформенной БД."""

from __future__ import annotations

from typing import Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer
from .errors import FsmErrorCodes
from .types import TransitionDef


class TransitionApplyError(Exception):
    """Ошибка применения перехода с нормативным кодом FsmErrorCodes. Пробрасывается TransitionRunner и преобразуется в FsmResult FAILED."""

    def __init__(self, code: str, message: str = "") -> None:
        """Сохраняет code и формирует сообщение исключения. code используется в last_error экземпляра."""
        self.code = code
        super().__init__(message or code)


class TransitionExecutor:
    """Атомарно обновляет состояние сущности и пишет лог перехода в платформенной БД. Не выполняет guards и effects."""

    def __init__(self, db_layer: FsmDbLayer | None = None) -> None:
        """Принимает слой БД или использует default_db_layer. Позволяет подменить персистентность в тестах."""
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
        """Проверяет from_state, upsert to_state и вставляет fsm_transition_logs. При allow_idempotent допускает повторное применение уже достигнутого to_state."""
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

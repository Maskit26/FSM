"""API состояния сущности FSM поверх платформенного db_layer."""

from __future__ import annotations

from typing import Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer


class EntityStateStore:
    """Тонкая обёртка над entity_fsm_state для чтения и записи текущего состояния. Изолирует runner от прямых SQL-вызовов."""

    def __init__(self, db_layer: FsmDbLayer | None = None) -> None:
        """Принимает FsmDbLayer или использует default_db_layer. Упрощает подмену слоя в тестах."""
        self._db = db_layer or default_db_layer

    def get(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
    ) -> Optional[str]:
        """Возвращает текущее состояние сущности или None, если запись не найдена. Вызывается перед выбором кандидатов перехода."""
        return self._db.get_entity_state(session, service_id, entity_type, entity_id)

    def set(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        """Upsert текущего состояния сущности в платформенной БД. Используется при инициализации и ручной установке состояния."""
        self._db.upsert_entity_state(
            session, service_id, entity_type, entity_id, current_state
        )

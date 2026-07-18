"""Entity FSM-state API over platform db_layer."""

from __future__ import annotations

from typing import Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer


class EntityStateStore:
    def __init__(self, db_layer: FsmDbLayer | None = None) -> None:
        self._db = db_layer or default_db_layer

    def get(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
    ) -> Optional[str]:
        return self._db.get_entity_state(session, service_id, entity_type, entity_id)

    def set(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        self._db.upsert_entity_state(
            session, service_id, entity_type, entity_id, current_state
        )

"""Чтение кандидатов переходов из FSM-графа доменной БД."""

from __future__ import annotations

from sqlalchemy import text

from .db_layer import SessionLike
from .types import TransitionDef


class TransitionRepository:
    """Загружает transitions из доменной БД. Поддерживает схему fsm_events и legacy fsm_actions."""

    def list_candidates(
        self,
        session_domain: SessionLike,
        entity_type: str,
        from_state: str,
        event_name: str,
    ) -> list[TransitionDef]:
        """Возвращает кандидаты переходов, отсортированные по priority. TransitionRunner перебирает их и применяет guards."""
        if self._has_table(session_domain, "fsm_events"):
            sql = """
                SELECT
                    t.id,
                    t.entity_type,
                    fs.name AS from_state,
                    ts.name AS to_state,
                    e.name AS event_name,
                    t.guard_name,
                    t.guard_params,
                    t.priority,
                    t.effect_name,
                    t.effect_params
                FROM fsm_transitions t
                JOIN fsm_states fs ON fs.id = t.from_state_id
                JOIN fsm_states ts ON ts.id = t.to_state_id
                JOIN fsm_events e ON e.id = t.event_id
                WHERE t.entity_type = :entity_type
                  AND fs.name = :from_state
                  AND e.name = :event_name
                ORDER BY t.priority ASC, t.id ASC
            """
        else:
            # Legacy: fsm_actions / action_id
            sql = """
                SELECT
                    t.id,
                    t.entity_type,
                    fs.name AS from_state,
                    ts.name AS to_state,
                    a.name AS event_name,
                    t.guard_name,
                    t.guard_params,
                    t.priority,
                    t.effect_name,
                    t.effect_params
                FROM fsm_transitions t
                JOIN fsm_states fs ON fs.id = t.from_state_id
                JOIN fsm_states ts ON ts.id = t.to_state_id
                JOIN fsm_actions a ON a.id = t.action_id
                WHERE t.entity_type = :entity_type
                  AND fs.name = :from_state
                  AND a.name = :event_name
                ORDER BY t.priority ASC, t.id ASC
            """

        rows = session_domain.execute(
            text(sql),
            {
                "entity_type": entity_type,
                "from_state": from_state,
                "event_name": event_name,
            },
        ).mappings().all()
        return [TransitionDef.from_row(dict(r)) for r in rows]

    def get_initial_state(
        self,
        session_domain: SessionLike,
        entity_type: str,
    ) -> list[str]:
        """Возвращает имена начальных состояний из fsm_states. Для legacy-графа без is_initial возвращает пустой список."""
        if not self._has_column(session_domain, "fsm_states", "is_initial"):
            return []
        if self._has_column(session_domain, "fsm_states", "entity_type"):
            sql = """
                SELECT name FROM fsm_states
                WHERE entity_type = :entity_type AND is_initial = 1
                ORDER BY id ASC
            """
            params = {"entity_type": entity_type}
        else:
            sql = """
                SELECT name FROM fsm_states
                WHERE is_initial = 1
                ORDER BY id ASC
            """
            params = {}
        rows = session_domain.execute(text(sql), params).mappings().all()
        return [str(r["name"]) for r in rows]

    @staticmethod
    def _has_table(session: SessionLike, table: str) -> bool:
        """Проверяет наличие таблицы в текущей схеме БД. Выбирает SQL-запрос для fsm_events или legacy fsm_actions."""
        row = session.execute(
            text(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = :t
                LIMIT 1
                """
            ),
            {"t": table},
        ).first()
        return row is not None

    @staticmethod
    def _has_column(session: SessionLike, table: str, column: str) -> bool:
        """Проверяет наличие колонки в таблице через information_schema. Нужна для совместимости со старыми схемами графа."""
        row = session.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = :t AND column_name = :c
                LIMIT 1
                """
            ),
            {"t": table, "c": column},
        ).first()
        return row is not None

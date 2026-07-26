"""Чтение кандидатов переходов из FSM-графа доменной БД."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text

from .db_layer import SessionLike
from .types import TransitionDef


class TransitionRepository:
    """Загружает transitions из доменной БД. Поддерживает схему fsm_events и legacy fsm_actions."""

    def current_graph_version(self, session_domain: SessionLike) -> Optional[int]:
        """Текущая published-версия графа или None, если версионирование выключено."""
        if not self._has_column(session_domain, "fsm_transitions", "graph_version"):
            return None
        if self._has_table(session_domain, "fsm_graph_meta"):
            row = session_domain.execute(
                text(
                    "SELECT current_version FROM fsm_graph_meta WHERE id = 1 LIMIT 1"
                )
            ).mappings().first()
            if row is not None:
                try:
                    return max(1, int(row["current_version"]))
                except (TypeError, ValueError):
                    return 1
        return 1

    def list_candidates(
        self,
        session_domain: SessionLike,
        entity_type: str,
        from_state: str,
        event_name: str,
        graph_version: Optional[int] = None,
    ) -> list[TransitionDef]:
        """Возвращает кандидаты переходов, отсортированные по priority. TransitionRunner перебирает их и применяет guards."""
        ver_sql = ""
        params: dict = {
            "entity_type": entity_type,
            "from_state": from_state,
            "event_name": event_name,
        }
        if (
            graph_version is not None
            and self._has_column(session_domain, "fsm_transitions", "graph_version")
        ):
            ver_sql = " AND t.graph_version = :graph_version"
            params["graph_version"] = int(graph_version)

        if self._has_table(session_domain, "fsm_events"):
            sql = f"""
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
                  {ver_sql}
                ORDER BY t.priority ASC, t.id ASC
            """
        else:
            # Legacy: fsm_actions / action_id
            sql = f"""
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
                  {ver_sql}
                ORDER BY t.priority ASC, t.id ASC
            """

        rows = session_domain.execute(text(sql), params).mappings().all()
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

    def list_state_names(
        self, session_domain: SessionLike, entity_type: Optional[str] = None
    ) -> list[str]:
        """Имена состояний из fsm_states (опционально по entity_type)."""
        if not self._has_table(session_domain, "fsm_states"):
            return []
        if entity_type and self._has_column(session_domain, "fsm_states", "entity_type"):
            rows = session_domain.execute(
                text(
                    """
                    SELECT name FROM fsm_states
                    WHERE entity_type = :entity_type
                    ORDER BY id ASC
                    """
                ),
                {"entity_type": entity_type},
            ).mappings().all()
        else:
            rows = session_domain.execute(
                text("SELECT name FROM fsm_states ORDER BY id ASC")
            ).mappings().all()
        return [str(r["name"]) for r in rows]

    def list_outgoing(
        self,
        session_domain: SessionLike,
        entity_type: str,
        from_state: str,
        graph_version: Optional[int] = None,
    ) -> list[TransitionDef]:
        """Все рёбра из from_state (без фильтра event) — для available actions."""
        ver_sql = ""
        params: dict = {"entity_type": entity_type, "from_state": from_state}
        if (
            graph_version is not None
            and self._has_column(session_domain, "fsm_transitions", "graph_version")
        ):
            ver_sql = " AND t.graph_version = :graph_version"
            params["graph_version"] = int(graph_version)

        if self._has_table(session_domain, "fsm_events"):
            sql = f"""
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
                  {ver_sql}
                ORDER BY e.name ASC, t.priority ASC, t.id ASC
            """
        else:
            sql = f"""
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
                  {ver_sql}
                ORDER BY a.name ASC, t.priority ASC, t.id ASC
            """
        rows = session_domain.execute(text(sql), params).mappings().all()
        return [TransitionDef.from_row(dict(r)) for r in rows]

    def get_state_timeout(
        self,
        session_domain: SessionLike,
        entity_type: str,
        state_name: str,
    ) -> Optional[dict]:
        """
        Декларативный таймаут состояния из fsm_states (если колонки есть).
        {timeout_seconds, timeout_event, timeout_owner} или None.
        """
        if not self._has_table(session_domain, "fsm_states"):
            return None
        if not self._has_column(session_domain, "fsm_states", "timeout_seconds"):
            return None
        has_etype = self._has_column(session_domain, "fsm_states", "entity_type")
        has_owner = self._has_column(session_domain, "fsm_states", "timeout_owner")
        has_event = self._has_column(session_domain, "fsm_states", "timeout_event")
        if not has_event:
            return None
        cols = "timeout_seconds, timeout_event"
        if has_owner:
            cols += ", timeout_owner"
        if has_etype:
            sql = f"""
                SELECT {cols} FROM fsm_states
                WHERE name = :name AND entity_type = :entity_type
                LIMIT 1
            """
            params = {"name": state_name, "entity_type": entity_type}
        else:
            sql = f"SELECT {cols} FROM fsm_states WHERE name = :name LIMIT 1"
            params = {"name": state_name}
        row = session_domain.execute(text(sql), params).mappings().fetchone()
        if row is None:
            return None
        data = dict(row)
        seconds = data.get("timeout_seconds")
        event = data.get("timeout_event")
        if seconds is None or not event:
            return None
        try:
            sec = int(seconds)
        except (TypeError, ValueError):
            return None
        if sec <= 0:
            return None
        owner = str(data.get("timeout_owner") or "domain").strip().lower()
        if owner not in ("domain", "platform"):
            owner = "domain"
        return {
            "timeout_seconds": sec,
            "timeout_event": str(event).strip(),
            "timeout_owner": owner,
        }

    def list_transitions_for_event(
        self,
        session_domain: SessionLike,
        entity_type: str,
        event_name: str,
    ) -> list[dict]:
        """
        Все рёбра графа для (entity_type, event_name) — без фильтра from_state.
        Нужен Domain Validator (candidates / guard-effect names).
        """
        if self._has_table(session_domain, "fsm_events"):
            sql = """
                SELECT
                    t.id,
                    t.entity_type,
                    fs.name AS from_state,
                    ts.name AS to_state,
                    e.name AS event_name,
                    t.guard_name,
                    t.priority,
                    t.effect_name
                FROM fsm_transitions t
                JOIN fsm_states fs ON fs.id = t.from_state_id
                JOIN fsm_states ts ON ts.id = t.to_state_id
                JOIN fsm_events e ON e.id = t.event_id
                WHERE t.entity_type = :entity_type
                  AND e.name = :event_name
                ORDER BY fs.name ASC, t.priority ASC, t.id ASC
            """
        else:
            sql = """
                SELECT
                    t.id,
                    t.entity_type,
                    fs.name AS from_state,
                    ts.name AS to_state,
                    a.name AS event_name,
                    t.guard_name,
                    t.priority,
                    t.effect_name
                FROM fsm_transitions t
                JOIN fsm_states fs ON fs.id = t.from_state_id
                JOIN fsm_states ts ON ts.id = t.to_state_id
                JOIN fsm_actions a ON a.id = t.action_id
                WHERE t.entity_type = :entity_type
                  AND a.name = :event_name
                ORDER BY fs.name ASC, t.priority ASC, t.id ASC
            """
        rows = session_domain.execute(
            text(sql),
            {"entity_type": entity_type, "event_name": event_name},
        ).mappings().all()
        return [dict(r) for r in rows]

    def list_guard_effect_names(
        self,
        session_domain: SessionLike,
        *,
        entity_type: Optional[str] = None,
        event_name: Optional[str] = None,
    ) -> tuple[set[str], set[str]]:
        """
        Множества непустых guard_name / effect_name из fsm_transitions.
        Если заданы entity_type+event_name — только рёбра процесса; иначе весь граф.
        """
        if not self._has_table(session_domain, "fsm_transitions"):
            return set(), set()

        if entity_type and event_name:
            rows = self.list_transitions_for_event(
                session_domain, entity_type, event_name
            )
        else:
            rows = session_domain.execute(
                text(
                    """
                    SELECT guard_name, effect_name
                    FROM fsm_transitions
                    """
                )
            ).mappings().all()
            rows = [dict(r) for r in rows]

        guards: set[str] = set()
        effects: set[str] = set()
        for r in rows:
            g = r.get("guard_name")
            e = r.get("effect_name")
            if g is not None and str(g).strip():
                guards.add(str(g).strip())
            if e is not None and str(e).strip():
                effects.add(str(e).strip())
        return guards, effects

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

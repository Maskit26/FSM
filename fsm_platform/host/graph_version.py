"""Domain graph versioning: pin on enqueue, filter candidates by pinned version."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text

from fsm_platform.core.db_layer import SessionLike
from fsm_platform.core.transition_repository import TransitionRepository


_repo = TransitionRepository()


def graph_versioning_enabled(session_domain: SessionLike) -> bool:
    return _repo._has_column(session_domain, "fsm_transitions", "graph_version")


def current_graph_version(session_domain: SessionLike) -> int:
    """Текущая опубликованная версия графа (fsm_graph_meta) или 1."""
    ver = _repo.current_graph_version(session_domain)
    return int(ver) if ver is not None else 1


def resolve_graph_version(
    session_domain: Optional[SessionLike],
    explicit: Optional[int] = None,
) -> Optional[int]:
    """
    Версия для pin на instance.
    None — фича выключена (колонки нет) → instance.graph_version остаётся NULL.
    """
    if session_domain is None:
        return explicit
    if not graph_versioning_enabled(session_domain):
        return None
    if explicit is not None:
        return int(explicit)
    return current_graph_version(session_domain)


def publish_graph_version(session_domain: SessionLike) -> int:
    """
    Копирует все transitions current → current+1 и поднимает meta.
    Правьте копию новой версии; летящие инстансы остаются на старой.
    """
    if not graph_versioning_enabled(session_domain):
        raise RuntimeError("GRAPH_VERSIONING_DISABLED")
    cur = current_graph_version(session_domain)
    nxt = cur + 1

    # legacy: action_id; new template: event_id
    has_event = _repo._has_column(session_domain, "fsm_transitions", "event_id")
    has_action = _repo._has_column(session_domain, "fsm_transitions", "action_id")
    if has_event:
        link_col = "event_id"
    elif has_action:
        link_col = "action_id"
    else:
        raise RuntimeError("fsm_transitions missing event_id/action_id")

    session_domain.execute(
        text(
            f"""
            INSERT INTO fsm_transitions (
                entity_type, from_state_id, to_state_id, {link_col},
                guard_name, guard_params, priority, effect_name, effect_params,
                graph_version
            )
            SELECT
                entity_type, from_state_id, to_state_id, {link_col},
                guard_name, guard_params, priority, effect_name, effect_params,
                :nxt
            FROM fsm_transitions
            WHERE graph_version = :cur
            """
        ),
        {"cur": cur, "nxt": nxt},
    )
    if not _repo._has_table(session_domain, "fsm_graph_meta"):
        session_domain.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS fsm_graph_meta (
                    id TINYINT NOT NULL PRIMARY KEY DEFAULT 1,
                    current_version INT NOT NULL DEFAULT 1,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP
                )
                """
            )
        )
    session_domain.execute(
        text(
            """
            INSERT INTO fsm_graph_meta (id, current_version)
            VALUES (1, :nxt)
            ON DUPLICATE KEY UPDATE current_version = :nxt
            """
        ),
        {"nxt": nxt},
    )
    return nxt

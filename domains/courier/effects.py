from __future__ import annotations

from typing import Any, Dict

from fsm_core.types import EffectResult


def noop_effect(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    """Пустой effect: SQL transition уже выполнен, побочных действий нет."""
    return EffectResult(ok=True)


def release_orders_on_reservation_cancel(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    """После SQL-перехода отмены резерва — вернуть заказы в пул направления."""
    reservation_id = instance.get("entity_id")
    if reservation_id is None:
        return EffectResult(ok=False, error="MISSING_ENTITY_ID")

    released_count = db.release_orders_from_reservation(session, reservation_id)
    return EffectResult(
        ok=True,
        payload={"released_count": released_count},
    )

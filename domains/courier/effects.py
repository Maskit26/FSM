"""Effects домена: действия после успешного применения FSM-перехода."""

from __future__ import annotations

from fsm_platform.types import EffectResult

from domains.courier import db_layer


def sync_order_status(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Копирует to_state перехода в колонку orders.status.
    Если целевой статус не передан — пропускает обновление без ошибки.
    """
    order_id = int(instance["entity_id"])
    to_state = (effect_params or {}).get("to_state") or (context or {}).get("to_state")
    if not to_state:
        to_state = (instance.get("payload_json") or {}).get("expected_to_state")
    if not to_state:
        order = db_layer.get_order(session_domain, order_id)
        if order is None:
            return EffectResult(ok=False, error="ORDER_NOT_FOUND")
        return EffectResult(ok=True, payload={"skipped": True, "reason": "no_to_state"})

    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(ok=True, payload={"order_id": order_id, "status": to_state})


def assign_courier1_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Effect назначения courier1: выставляет orders.status = order_courier1_assigned.
    Вызывается после успешного FSM-перехода order_assign_courier1.
    """
    order_id = int(instance["entity_id"])
    db_layer.update_order_status(session_domain, order_id, "order_courier1_assigned")
    return EffectResult(
        ok=True,
        payload={"order_id": order_id, "status": "order_courier1_assigned"},
    )

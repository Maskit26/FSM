"""Effects домена: действия после успешного применения FSM-перехода."""

from __future__ import annotations

import json
from typing import Any

from fsm_platform.core.types import EffectResult

from domains.courier import db_layer


def _payload_dict(instance: dict[str, Any]) -> dict[str, Any]:
    """Достаёт payload инстанса как dict (из JSON-строки или уже dict)."""
    raw = instance.get("payload_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def sync_order_status(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Копирует to_state перехода в колонку orders.status.
    Если целевой статус не передан — пропускает обновление без ошибки.
    """
    order_id = int(instance["entity_id"])
    to_state = (effect_params or {}).get("to_state") or (context or {}).get("to_state")
    if not to_state:
        to_state = _payload_dict(instance).get("expected_to_state")
    if not to_state:
        order = db_layer.get_order(session_domain, order_id)
        if order is None:
            return EffectResult(ok=False, error="ORDER_NOT_FOUND")
        return EffectResult(ok=True, payload={"skipped": True, "reason": "no_to_state"})

    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(ok=True, payload={"order_id": order_id, "status": to_state})


def assign_courier1_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    После успешного apply: занимает stage_orders.pickup и пишет orders.status.
    Если слот уже занят другим — effect падает (ALREADY_TAKEN).
    """
    _ = db, context, effect_params
    order_id = int(instance["entity_id"])
    payload = _payload_dict(instance)
    courier_raw = payload.get("courier_user_id") or instance.get("actor_id")
    if not courier_raw:
        return EffectResult(ok=False, error="COURIER_ID_REQUIRED")
    courier_id = int(courier_raw)

    claimed = db_layer.claim_stage_order(
        session_domain, order_id, "pickup", courier_id
    )
    if not claimed:
        return EffectResult(ok=False, error="ALREADY_TAKEN")

    db_layer.update_order_status(session_domain, order_id, "order_courier1_assigned")
    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "status": "order_courier1_assigned",
            "courier_user_id": courier_id,
        },
    )

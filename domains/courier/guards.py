"""Guards домена courier: только read-only проверки перед FSM-переходом."""

from __future__ import annotations

import json
from typing import Any, Optional

from fsm_platform.types import GuardResult

from domains.courier import db_layer


def _payload_dict(instance: dict[str, Any]) -> dict[str, Any]:
    """Достаёт payload инстанса как dict."""
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


def _courier_id_from_instance(instance: dict[str, Any]) -> Optional[int]:
    """Id курьера из payload или platform actor_id (инициатор invoke)."""
    payload = _payload_dict(instance)
    raw = payload.get("courier_user_id") or instance.get("actor_id")
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


def can_assign_courier1(
    session_domain, db, context, instance, guard_params
) -> GuardResult:
    """
    Разрешает назначение courier1 на заказ с биржи pickup.
    Проверяет роль/город курьера, статус и тип заказа, свободный слот и совпадение города постамата.
    """
    _ = db, context, guard_params
    order_id = int(instance["entity_id"])
    courier_id = _courier_id_from_instance(instance)
    if not courier_id:
        return GuardResult(ok=False, reason="COURIER_ID_REQUIRED")

    user = db_layer.get_user(session_domain, courier_id)
    if user is None:
        return GuardResult(ok=False, reason="USER_NOT_FOUND")
    if str(user.get("role_name") or "") != "courier":
        return GuardResult(ok=False, reason="NOT_A_COURIER")
    courier_city = str(user.get("city") or "").strip()
    if not courier_city:
        return GuardResult(ok=False, reason="COURIER_CITY_REQUIRED")

    order = db_layer.get_order(session_domain, order_id)
    if order is None:
        return GuardResult(ok=False, reason="ORDER_NOT_FOUND")
    if str(order.get("status") or "") != "order_created":
        return GuardResult(ok=False, reason=f"ORDER_NOT_AVAILABLE:{order.get('status')}")
    if str(order.get("pickup_type") or "") != "courier":
        return GuardResult(ok=False, reason="NOT_COURIER_PICKUP")

    source_cell_id = order.get("source_cell_id")
    if not source_cell_id:
        return GuardResult(ok=False, reason="CELL_MISSING")

    locker_city = db_layer.get_locker_city_by_cell(session_domain, int(source_cell_id))
    if not locker_city or locker_city != courier_city:
        return GuardResult(
            ok=False,
            reason=f"CITY_MISMATCH:{courier_city}->{locker_city}",
        )

    if not db_layer.is_stage_slot_free(session_domain, order_id, "pickup"):
        return GuardResult(ok=False, reason="ALREADY_TAKEN")

    return GuardResult(ok=True)

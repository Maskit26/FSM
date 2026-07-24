"""Effects домена: действия после успешного применения FSM-перехода."""

from __future__ import annotations

import json
from typing import Any, Optional

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


def _executor_id(instance: dict[str, Any]) -> Optional[int]:
    """Id исполнителя из payload или actor_id."""
    payload = _payload_dict(instance)
    raw = (
        payload.get("executor_user_id")
        or payload.get("courier_user_id")
        or instance.get("actor_id")
    )
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


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


def confirm_courier2_delivery_effect(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """sync_order_status + пометить PIN получателя USED."""
    result = sync_order_status(
        session_domain, db, context, instance, effect_params
    )
    if not result.ok:
        return result
    order_id = int(instance["entity_id"])
    db_layer.mark_courier2_delivery_code_used(session_domain, order_id)
    payload = dict(result.payload or {})
    payload["delivery_code_used"] = True
    return EffectResult(ok=True, payload=payload)


def assign_executor_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Общий effect назначения исполнителя на order.
    leg из payload / effect_params / context; to_state — из перехода.
    """
    _ = db
    order_id = int(instance["entity_id"])
    payload = _payload_dict(instance)
    params = effect_params or {}
    ctx = context or {}
    leg = str(
        payload.get("leg") or params.get("leg") or ctx.get("leg") or "pickup"
    ).strip().lower()
    if leg not in ("pickup", "delivery"):
        return EffectResult(ok=False, error=f"INVALID_LEG:{leg}")

    executor_id = ctx.get("executor_id") or _executor_id(instance)
    if not executor_id:
        return EffectResult(ok=False, error="EXECUTOR_ID_REQUIRED")

    claimed = db_layer.claim_stage_order(
        session_domain, order_id, leg, int(executor_id)
    )
    if not claimed:
        return EffectResult(ok=False, error="ALREADY_TAKEN")

    to_state = ctx.get("to_state") or params.get("to_state")
    if not to_state:
        to_state = (
            "order_courier1_assigned" if leg == "pickup" else "order_courier2_assigned"
        )
    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "leg": leg,
            "status": to_state,
            "executor_user_id": int(executor_id),
        },
    )


def remove_executor_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Снимает исполнителя со stage_orders и пишет orders.status = to_state перехода.
    Курьер снова видит заказ на бирже (для pickup → order_created).
    """
    _ = db
    order_id = int(instance["entity_id"])
    payload = _payload_dict(instance)
    params = effect_params or {}
    ctx = context or {}
    leg = str(
        payload.get("leg") or params.get("leg") or ctx.get("leg") or "pickup"
    ).strip().lower()
    if leg not in ("pickup", "delivery"):
        return EffectResult(ok=False, error=f"INVALID_LEG:{leg}")

    executor_id = ctx.get("executor_id") or _executor_id(instance)
    if not executor_id:
        return EffectResult(ok=False, error="EXECUTOR_ID_REQUIRED")

    cleared = db_layer.clear_stage_courier(
        session_domain,
        order_id,
        leg,
        expected_courier_id=int(executor_id),
    )
    if not cleared:
        return EffectResult(ok=False, error="CLEAR_STAGE_FAILED")

    to_state = ctx.get("to_state") or params.get("to_state")
    if not to_state:
        to_state = "order_created" if leg == "pickup" else "order_arrived_at_post2"
    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "leg": leg,
            "status": to_state,
            "executor_user_id": int(executor_id),
        },
    )


def open_cell_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Primary effect open_cell: только orders.status = to_state.
    Ячейку двигает companion locker_open_locker (+ sync_locker_cell_status).
    """
    _ = db
    order_id = int(instance["entity_id"])
    payload = _payload_dict(instance)
    params = effect_params or {}
    ctx = context or {}
    leg = str(
        payload.get("leg") or params.get("leg") or ctx.get("leg") or "pickup"
    ).strip().lower()
    if leg not in ("pickup", "delivery"):
        return EffectResult(ok=False, error=f"INVALID_LEG:{leg}")

    to_state = ctx.get("to_state") or params.get("to_state")
    if not to_state:
        return EffectResult(ok=False, error="TO_STATE_REQUIRED")
    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "leg": leg,
            "cell_id": ctx.get("cell_id"),
            "status": to_state,
        },
    )


def close_cell_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Primary effect close_cell: orders.status = to_state.
    После order_parcel_confirmed (pickup confirm) — bind к directions
    (как старый bind_order_to_trip).
    Ячейку двигает companion locker_close_* (+ sync_locker_cell_status).
    """
    result = open_cell_effect(session_domain, db, context, instance, effect_params)
    if not result.ok:
        return result

    to_state = str((result.payload or {}).get("status") or "")
    if to_state != "order_parcel_confirmed":
        return result

    order_id = int(instance["entity_id"])
    direction_id, err = db_layer.bind_order_to_direction(session_domain, order_id)
    if err:
        return EffectResult(ok=False, error=f"BIND_DIRECTION:{err}")

    payload = dict(result.payload or {})
    payload["direction_id"] = direction_id
    return EffectResult(ok=True, payload=payload)


def sync_locker_cell_status(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """
    Companion effect: зеркало locker_cells.status = to_state перехода locker.
    """
    _ = db
    _ = instance
    _ = effect_params
    ctx = context or {}
    cell_id = ctx.get("applied_entity_id") or ctx.get("cell_id")
    to_state = ctx.get("to_state")
    if not cell_id:
        return EffectResult(ok=False, error="CELL_MISSING")
    if not to_state:
        return EffectResult(ok=False, error="TO_STATE_REQUIRED")
    ok = db_layer.set_cell_status(session_domain, int(cell_id), str(to_state))
    if not ok:
        return EffectResult(ok=False, error="SYNC_LOCKER_STATUS_FAILED")
    return EffectResult(
        ok=True,
        payload={"cell_id": int(cell_id), "cell_status": str(to_state)},
    )


def reserve_locker_cell_effect(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """
    Effect locker_reserve_cell: CAS free→reserved + bind current_order_id.
    order_id из context (payload create_order).
    """
    _ = db
    _ = effect_params
    ctx = context or {}
    cell_id = int(
        ctx.get("applied_entity_id") or ctx.get("cell_id") or instance["entity_id"]
    )
    order_id = ctx.get("order_id")
    if order_id is None:
        order_id = _payload_dict(instance).get("order_id")
    if not order_id:
        return EffectResult(ok=False, error="ORDER_ID_REQUIRED")

    ok = db_layer.reserve_cell_for_order(
        session_domain, cell_id, int(order_id)
    )
    if not ok:
        return EffectResult(ok=False, error="RESERVE_CELL_FAILED")
    return EffectResult(
        ok=True,
        payload={
            "cell_id": cell_id,
            "order_id": int(order_id),
            "cell_status": "locker_reserved",
        },
    )


def sync_reservation_status(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """Зеркало driver_reservations.status = to_state после FSM apply."""
    _ = db
    ctx = context or {}
    params = effect_params or {}
    reservation_id = int(
        ctx.get("applied_entity_id")
        or ctx.get("reservation_id")
        or instance["entity_id"]
    )
    to_state = ctx.get("to_state") or params.get("to_state")
    if not to_state:
        return EffectResult(ok=False, error="TO_STATE_REQUIRED")
    ok = db_layer.set_reservation_status(
        session_domain, reservation_id, str(to_state)
    )
    if not ok:
        return EffectResult(ok=False, error="SYNC_RESERVATION_STATUS_FAILED")
    return EffectResult(
        ok=True,
        payload={
            "reservation_id": reservation_id,
            "status": str(to_state),
            "direction_id": ctx.get("direction_id"),
        },
    )


def cancel_reservation_effect(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """
    Отмена резерва: заказы обратно в пул направления (stage_orders),
    затем mirror status → reservation_cancelled.
    orders.status / platform order state не меняются (остаются parcel_confirmed).
    """
    _ = db
    _ = effect_params
    ctx = context or {}
    reservation_id = int(
        ctx.get("applied_entity_id")
        or ctx.get("reservation_id")
        or instance["entity_id"]
    )
    to_state = ctx.get("to_state") or "reservation_cancelled"

    try:
        released = db_layer.release_orders_from_reservation(
            session_domain, reservation_id
        )
    except ValueError as exc:
        return EffectResult(ok=False, error=str(exc))

    ok = db_layer.set_reservation_status(
        session_domain, reservation_id, str(to_state)
    )
    if not ok:
        return EffectResult(ok=False, error="SYNC_RESERVATION_STATUS_FAILED")

    return EffectResult(
        ok=True,
        payload={
            "reservation_id": reservation_id,
            "status": str(to_state),
            "released_count": released,
            "direction_id": ctx.get("direction_id"),
        },
    )


def sync_trip_status(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """Зеркало trips.status = to_state после FSM apply."""
    _ = db
    ctx = context or {}
    params = effect_params or {}
    trip_id = int(
        ctx.get("applied_entity_id")
        or ctx.get("trip_id")
        or instance["entity_id"]
    )
    to_state = ctx.get("to_state") or params.get("to_state")
    if not to_state:
        return EffectResult(ok=False, error="TO_STATE_REQUIRED")
    ok = db_layer.set_trip_status(session_domain, trip_id, str(to_state))
    if not ok:
        return EffectResult(ok=False, error="SYNC_TRIP_STATUS_FAILED")
    return EffectResult(
        ok=True,
        payload={"trip_id": trip_id, "status": str(to_state)},
    )

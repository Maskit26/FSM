"""Effects домена: действия после успешного применения FSM-перехода."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fsm_platform.core.types import EffectResult

from domains.courier import db_layer
from domains.courier.notifications import enqueue_order_progress_notifications

logger = logging.getLogger(__name__)


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


def _service_id(instance: dict[str, Any]) -> str:
    return str(instance.get("service_id") or "svc_courier_01")


def _enqueue_core(
    db,
    *,
    op: str,
    payload: dict[str, Any],
    idempotency_key: str,
    service_id: str,
) -> Optional[str]:
    """None = ok; иначе error code если нет platform session."""
    from domains.courier.core.enqueue import enqueue_core

    try:
        enqueue_core(
            db,
            op=op,
            payload=payload,
            idempotency_key=idempotency_key,
            service_id=service_id,
        )
    except ValueError as exc:
        logger.error("core enqueue failed: %s", exc)
        return "PLATFORM_SESSION_REQUIRED_FOR_CORE"
    except Exception:
        logger.exception("core enqueue failed op=%s", op)
        return f"CORE_ENQUEUE_FAILED:{op}"
    return None


def _core_role_for_leg(leg: str) -> str:
    return "courier1" if leg == "pickup" else "courier2"


def _cas_order_status(
    session_domain, order_id: int, to_state: str, context: Optional[dict[str, Any]]
) -> Optional[str]:
    """CAS orders.status. None = ok, иначе error code."""
    expected = (context or {}).get("from_state")
    ok = db_layer.update_order_status(
        session_domain,
        order_id,
        str(to_state),
        expected_from=str(expected) if expected is not None else None,
    )
    if not ok:
        return "ORDER_STATUS_CAS_FAILED"
    return None


def _notify_order_progress(
    session_domain,
    db,
    instance: dict[str, Any],
    *,
    order_id: int,
    to_state: str,
    courier_user_id: Optional[int] = None,
) -> None:
    """Best-effort enqueue TG; ошибки не валят effect."""
    try:
        enqueue_order_progress_notifications(
            session_domain,
            db,
            order_id=int(order_id),
            to_state=str(to_state),
            service_id=_service_id(instance),
            instance_id=int(instance["id"]) if instance.get("id") else None,
            courier_user_id=courier_user_id,
        )
    except Exception:
        logger.exception(
            "order progress notify failed order_id=%s state=%s",
            order_id,
            to_state,
        )


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

    cas_err = _cas_order_status(session_domain, order_id, str(to_state), context)
    if cas_err:
        return EffectResult(ok=False, error=cas_err)
    _notify_order_progress(
        session_domain,
        db,
        instance,
        order_id=order_id,
        to_state=str(to_state),
        courier_user_id=_executor_id(instance),
    )
    return EffectResult(ok=True, payload={"order_id": order_id, "status": to_state})


def confirm_courier2_delivery_effect(
    session_domain, db, context, instance, effect_params
) -> EffectResult:
    """sync_order_status + пометить PIN получателя USED + Core complete courier2+main."""
    result = sync_order_status(
        session_domain, db, context, instance, effect_params
    )
    if not result.ok:
        return result
    order_id = int(instance["entity_id"])
    db_layer.mark_courier2_delivery_code_used(session_domain, order_id)

    executor_id = _executor_id(instance)
    sid = _service_id(instance)
    if executor_id:
        err = _enqueue_core(
            db,
            op="complete_suborder",
            payload={
                "local_order_id": order_id,
                "performer_local_user_id": int(executor_id),
                "role": "courier2",
            },
            idempotency_key=f"core:complete_sub:{order_id}:courier2",
            service_id=sid,
        )
        if err:
            return EffectResult(ok=False, error=err)
    err = _enqueue_core(
        db,
        op="complete_main",
        payload={"local_order_id": order_id},
        idempotency_key=f"core:complete_main:{order_id}",
        service_id=sid,
    )
    if err:
        return EffectResult(ok=False, error=err)

    payload = dict(result.payload or {})
    payload["delivery_code_used"] = True
    payload["core_enqueued"] = True
    return EffectResult(ok=True, payload=payload)


def assign_executor_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Общий effect назначения исполнителя на order.
    leg из payload / effect_params / context; to_state — из перехода.
    """
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
    cas_err = _cas_order_status(session_domain, order_id, str(to_state), ctx)
    if cas_err:
        return EffectResult(ok=False, error=cas_err)

    role = _core_role_for_leg(leg)
    err = _enqueue_core(
        db,
        op="assign_executor",
        payload={
            "local_order_id": order_id,
            "performer_local_user_id": int(executor_id),
            "role": role,
        },
        idempotency_key=f"core:assign:{order_id}:{role}:{int(executor_id)}",
        service_id=_service_id(instance),
    )
    if err:
        return EffectResult(ok=False, error=err)

    _notify_order_progress(
        session_domain,
        db,
        instance,
        order_id=order_id,
        to_state=str(to_state),
        courier_user_id=int(executor_id),
    )
    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "leg": leg,
            "status": to_state,
            "executor_user_id": int(executor_id),
            "core_enqueued": True,
        },
    )


def remove_executor_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """
    Снимает исполнителя со stage_orders и пишет orders.status = to_state перехода.
    Курьер снова видит заказ на бирже (для pickup → order_created).
    """
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
    cas_err = _cas_order_status(session_domain, order_id, str(to_state), ctx)
    if cas_err:
        return EffectResult(ok=False, error=cas_err)

    role = _core_role_for_leg(leg)
    err = _enqueue_core(
        db,
        op="remove_performer",
        payload={
            "local_order_id": order_id,
            "performer_local_user_id": int(executor_id),
            "role": role,
        },
        idempotency_key=f"core:remove:{order_id}:{role}:{int(executor_id)}",
        service_id=_service_id(instance),
    )
    if err:
        return EffectResult(ok=False, error=err)

    return EffectResult(
        ok=True,
        payload={
            "order_id": order_id,
            "leg": leg,
            "status": to_state,
            "executor_user_id": int(executor_id),
            "core_enqueued": True,
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
    cas_err = _cas_order_status(session_domain, order_id, str(to_state), ctx)
    if cas_err:
        return EffectResult(ok=False, error=cas_err)
    _notify_order_progress(
        session_domain,
        db,
        instance,
        order_id=order_id,
        to_state=str(to_state),
        courier_user_id=_executor_id(instance),
    )
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
    (как старый bind_order_to_trip) + Core complete courier1 suborder.
    Ячейку двигает companion locker_close_* (+ sync_locker_cell_status).
    """
    result = open_cell_effect(session_domain, db, context, instance, effect_params)
    if not result.ok:
        return result

    to_state = str((result.payload or {}).get("status") or "")
    order_id = int(instance["entity_id"])
    executor_id = _executor_id(instance)

    if to_state == "order_parcel_confirmed" and executor_id:
        err = _enqueue_core(
            db,
            op="complete_suborder",
            payload={
                "local_order_id": order_id,
                "performer_local_user_id": int(executor_id),
                "role": "courier1",
            },
            idempotency_key=f"core:complete_sub:{order_id}:courier1",
            service_id=_service_id(instance),
        )
        if err:
            return EffectResult(ok=False, error=err)

    if to_state != "order_parcel_confirmed":
        return result

    direction_id, err_bind = db_layer.bind_order_to_direction(session_domain, order_id)
    if err_bind:
        return EffectResult(ok=False, error=f"BIND_DIRECTION:{err_bind}")

    payload = dict(result.payload or {})
    payload["direction_id"] = direction_id
    payload["core_enqueued"] = bool(executor_id)
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
    from_state = ctx.get("from_state")
    if not cell_id:
        return EffectResult(ok=False, error="CELL_MISSING")
    if not to_state:
        return EffectResult(ok=False, error="TO_STATE_REQUIRED")
    ok = db_layer.set_cell_status(
        session_domain,
        int(cell_id),
        str(to_state),
        expected_from=str(from_state) if from_state is not None else None,
    )
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
    Effect locker_reserve_cell: CAS free→reserved + current_request_id.
    request_id = order_requests.id.
    """
    _ = db
    _ = effect_params
    ctx = context or {}
    payload = _payload_dict(instance)
    cell_id = int(
        ctx.get("applied_entity_id") or ctx.get("cell_id") or instance["entity_id"]
    )

    request_id = ctx.get("request_id")
    if request_id is None:
        request_id = payload.get("request_id")
    if not request_id:
        return EffectResult(ok=False, error="REQUEST_ID_REQUIRED")

    ok = db_layer.reserve_cell_for_request(
        session_domain, cell_id, int(request_id)
    )
    if not ok:
        return EffectResult(ok=False, error="RESERVE_CELL_FAILED")
    return EffectResult(
        ok=True,
        payload={
            "cell_id": cell_id,
            "request_id": int(request_id),
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
    """Зеркало trips.status = to_state после FSM apply + Core driver ops."""
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

    driver_id = (
        ctx.get("executor_id")
        or _executor_id(instance)
        or (_payload_dict(instance).get("driver_user_id"))
    )
    order_ids = list(ctx.get("order_ids") or [])
    if not order_ids:
        try:
            order_ids = db_layer.list_trip_order_ids(session_domain, trip_id)
        except Exception:
            order_ids = []

    sid = _service_id(instance)
    if driver_id and order_ids:
        if str(to_state) == "trip_in_progress":
            for oid in order_ids:
                err = _enqueue_core(
                    db,
                    op="assign_executor",
                    payload={
                        "local_order_id": int(oid),
                        "performer_local_user_id": int(driver_id),
                        "role": "driver",
                    },
                    idempotency_key=f"core:assign:{oid}:driver:{int(driver_id)}",
                    service_id=sid,
                )
                if err:
                    return EffectResult(ok=False, error=err)
        elif str(to_state) == "trip_completed":
            for oid in order_ids:
                err = _enqueue_core(
                    db,
                    op="complete_suborder",
                    payload={
                        "local_order_id": int(oid),
                        "performer_local_user_id": int(driver_id),
                        "role": "driver",
                    },
                    idempotency_key=f"core:complete_sub:{oid}:driver",
                    service_id=sid,
                )
                if err:
                    return EffectResult(ok=False, error=err)

    return EffectResult(
        ok=True,
        payload={"trip_id": trip_id, "status": str(to_state)},
    )

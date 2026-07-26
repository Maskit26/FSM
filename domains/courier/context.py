"""Сборка context для guards/effects процесса заказа."""

from __future__ import annotations

import json
from typing import Any, Optional

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


def build_order_context(session_domain, db, runtime_ctx, instance) -> dict[str, Any]:
    """
    Один раз собирает данные заказа и исполнителя для guards/effects.

    Guard дальше только читает context (и guard_params), не парсит payload
    и по возможности не ходит в БД повторно.
    """
    _ = db
    order_id = int(instance["entity_id"])
    payload = _payload_dict(instance)

    leg = str(
        payload.get("leg") or "pickup"
    ).strip().lower()

    executor_raw = (
        payload.get("executor_user_id")
        or payload.get("courier_user_id")
        or instance.get("actor_id")
    )
    executor_id: Optional[int] = None
    if executor_raw is not None and str(executor_raw).strip() != "":
        executor_id = int(executor_raw)

    order = db_layer.get_order(session_domain, order_id)
    executor = (
        db_layer.get_user(session_domain, executor_id) if executor_id else None
    )

    cell_id = None
    if order is not None:
        if leg == "delivery":
            cell_id = order.get("dest_cell_id")
        else:
            cell_id = order.get("source_cell_id")

    locker_city = (
        db_layer.get_locker_city_by_cell(session_domain, int(cell_id))
        if cell_id
        else None
    )
    executor_city = str((executor or {}).get("city") or "").strip() or None
    stage_courier_id = (
        db_layer.get_stage_courier(session_domain, order_id, leg)
        if leg in ("pickup", "delivery")
        else None
    )
    stage = (
        db_layer.get_stage_row(session_domain, order_id, leg)
        if leg in ("pickup", "delivery")
        else None
    )
    reserved_by_driver_id = None
    reservation_id = None
    if stage is not None:
        if stage.get("reserved_by_driver_id") is not None:
            reserved_by_driver_id = int(stage["reserved_by_driver_id"])
        if stage.get("reservation_id") is not None:
            reservation_id = int(stage["reservation_id"])
    cell_status = (
        db_layer.get_cell_status(session_domain, int(cell_id)) if cell_id else None
    )
    pin_raw = payload.get("pin")
    pin = str(pin_raw).strip() if pin_raw is not None and str(pin_raw).strip() else None

    return {
        "order": order,
        "order_id": order_id,
        "leg": leg,
        "payload": payload,
        "executor_id": executor_id,
        "executor": executor,
        "executor_city": executor_city,
        "cell_id": int(cell_id) if cell_id else None,
        "cell_status": cell_status,
        "locker_city": locker_city,
        "stage_courier_id": stage_courier_id,
        "stage": stage,
        "reserved_by_driver_id": reserved_by_driver_id,
        "reservation_id": reservation_id,
        "pin": pin,
        "runtime_ctx": runtime_ctx,
    }


def build_reservation_context(session_domain, db, runtime_ctx, instance) -> dict[str, Any]:
    """Context для процессов driver_reservations (start/complete loading)."""
    _ = db
    reservation_id = int(instance["entity_id"])
    payload = _payload_dict(instance)

    executor_raw = (
        payload.get("executor_user_id")
        or payload.get("driver_user_id")
        or instance.get("actor_id")
    )
    executor_id: Optional[int] = None
    if executor_raw is not None and str(executor_raw).strip() != "":
        executor_id = int(executor_raw)

    reservation = db_layer.get_driver_reservation(session_domain, reservation_id)
    executor = (
        db_layer.get_user(session_domain, executor_id) if executor_id else None
    )
    direction_id = None
    if reservation is not None and reservation.get("direction_id") is not None:
        direction_id = int(reservation["direction_id"])

    return {
        "reservation": reservation,
        "reservation_id": reservation_id,
        "direction_id": direction_id,
        "payload": payload,
        "executor_id": executor_id,
        "executor": executor,
        "runtime_ctx": runtime_ctx,
    }


def build_invoke_order_context(
    session_domain,
    *,
    order_id: int,
    actor_id: int,
    payload: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Context для sync invoke: тот же builder, что у FSM.
    payload — любые поля запроса (leg, pin, …); actor → executor_user_id.
    Не привязан к конкретной операции.
    """
    merged: dict[str, Any] = dict(payload or {})
    merged.setdefault("executor_user_id", actor_id)
    merged.setdefault("courier_user_id", actor_id)
    if not str(merged.get("leg") or "").strip():
        merged["leg"] = "pickup"

    instance: dict[str, Any] = {
        "entity_id": order_id,
        "actor_id": actor_id,
        "payload_json": merged,
    }
    ctx = build_order_context(session_domain, None, {}, instance)
    return ctx, instance


def build_locker_context(session_domain, db, runtime_ctx, instance) -> dict[str, Any]:
    """
    Context для процессов entity_type=locker (резерв ячейки и т.п.).
    entity_id инстанса = cell_id; request_id из payload → order_requests.
    """
    _ = db
    _ = runtime_ctx
    cell_id = int(instance["entity_id"])
    payload = _payload_dict(instance)

    request_id_raw = payload.get("request_id")
    request_id: Optional[int] = None
    if request_id_raw is not None and str(request_id_raw).strip() != "":
        request_id = int(request_id_raw)
    order_request = (
        db_layer.get_order_request(session_domain, request_id) if request_id else None
    )

    cell_status = db_layer.get_cell_status(session_domain, cell_id)
    locker_city = db_layer.get_locker_city_by_cell(session_domain, cell_id)

    src = (order_request or {}).get("source_cell_id")
    dst = (order_request or {}).get("dest_cell_id")

    return {
        "cell_id": cell_id,
        "cell_status": cell_status,
        "locker_city": locker_city,
        "request_id": request_id,
        "order_request": order_request,
        "cell_role": payload.get("cell_role"),
        "source_cell_id": src,
        "dest_cell_id": dst,
    }


def build_trip_context(session_domain, db, runtime_ctx, instance) -> dict[str, Any]:
    """Context для процессов entity_type=trip."""
    _ = db
    trip_id = int(instance["entity_id"])
    payload = _payload_dict(instance)

    executor_raw = (
        payload.get("executor_user_id")
        or payload.get("driver_user_id")
        or instance.get("actor_id")
    )
    executor_id: Optional[int] = None
    if executor_raw is not None and str(executor_raw).strip() != "":
        executor_id = int(executor_raw)

    trip = db_layer.get_trip(session_domain, trip_id)
    executor = (
        db_layer.get_user(session_domain, executor_id) if executor_id else None
    )
    order_ids = db_layer.list_trip_order_ids(session_domain, trip_id)
    order_rows = db_layer.list_trip_order_statuses(session_domain, trip_id)
    undelivered = [
        int(r["order_id"])
        for r in order_rows
        if str(r.get("status") or "") != "order_parcel_confirmed_post2"
    ]
    open_delivery_cells = db_layer.list_open_delivery_cells_for_trip(
        session_domain, trip_id
    )
    delivery_stops = db_layer.list_delivery_stops_for_trip(session_domain, trip_id)

    return {
        "trip": trip,
        "trip_id": trip_id,
        "order_ids": order_ids,
        "order_statuses": order_rows,
        "undelivered_order_ids": undelivered,
        "open_delivery_cells": open_delivery_cells,
        "delivery_stops": delivery_stops,
        "payload": payload,
        "executor_id": executor_id,
        "executor": executor,
        "runtime_ctx": runtime_ctx,
    }


def build_invoke_trip_context(
    session_domain,
    *,
    trip_id: int,
    actor_id: int,
    payload: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Context для sync invoke trip-команд (тот же builder, что у FSM)."""
    merged: dict[str, Any] = dict(payload or {})
    merged.setdefault("executor_user_id", actor_id)
    merged.setdefault("driver_user_id", actor_id)
    instance: dict[str, Any] = {
        "entity_id": trip_id,
        "actor_id": actor_id,
        "payload_json": merged,
    }
    ctx = build_trip_context(session_domain, None, {}, instance)
    return ctx, instance


def build_invoke_direction_context(
    session_domain,
    *,
    actor_id: int,
    capacity: int,
    direction_id: Optional[int] = None,
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Context для sync reserve_direction_slot (коридор или legacy direction_id)."""
    executor = db_layer.get_user(session_domain, actor_id)
    direction = None
    resolved_from = str(from_city or "").strip() or None
    resolved_to = str(to_city or "").strip() or None
    anchor_direction_id = int(direction_id) if direction_id else 0

    if anchor_direction_id:
        direction = db_layer.get_direction(session_domain, anchor_direction_id)
        if direction is not None:
            resolved_from = str(direction.get("from_city") or "").strip() or None
            resolved_to = str(direction.get("to_city") or "").strip() or None
    elif resolved_from and resolved_to:
        # synthetic corridor marker for guard (presence check)
        direction = {
            "from_city": resolved_from,
            "to_city": resolved_to,
            "id": None,
        }

    available_count = 0
    active_slots = 0
    if resolved_from and resolved_to:
        available_count = db_layer.count_available_orders_on_corridor(
            session_domain, resolved_from, resolved_to
        )
        active_slots = db_layer.count_active_driver_slots_on_corridor(
            session_domain, resolved_from, resolved_to, actor_id
        )

    instance: dict[str, Any] = {
        "entity_id": anchor_direction_id or 0,
        "actor_id": actor_id,
        "payload_json": {
            "executor_user_id": actor_id,
            "driver_user_id": actor_id,
            "capacity": capacity,
            "direction_id": anchor_direction_id or None,
            "from_city": resolved_from,
            "to_city": resolved_to,
        },
    }
    ctx: dict[str, Any] = {
        "direction": direction,
        "direction_id": anchor_direction_id or None,
        "from_city": resolved_from,
        "to_city": resolved_to,
        "capacity": capacity,
        "available_count": available_count,
        "active_slots": active_slots,
        "executor_id": actor_id,
        "executor": executor,
        "executor_city": str((executor or {}).get("city") or "").strip() or None,
        "payload": instance["payload_json"],
    }
    return ctx, instance


def build_invoke_create_trip_context(
    session_domain,
    *,
    actor_id: int,
    direction_id: Optional[int] = None,
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Context для sync части complete_loading: создание trip.
    Коридор: from_city/to_city (или legacy direction_id → города).
    """
    executor = db_layer.get_user(session_domain, actor_id)
    direction = None
    resolved_from = str(from_city or "").strip() or None
    resolved_to = str(to_city or "").strip() or None
    anchor_direction_id = int(direction_id) if direction_id else 0

    if anchor_direction_id:
        direction = db_layer.get_direction(session_domain, anchor_direction_id)
        if direction is not None:
            resolved_from = str(direction.get("from_city") or "").strip() or None
            resolved_to = str(direction.get("to_city") or "").strip() or None
    elif resolved_from and resolved_to:
        direction = {
            "from_city": resolved_from,
            "to_city": resolved_to,
            "id": None,
        }

    open_cells: list[int] = []
    reservation_ids: list[int] = []
    loading_ids: list[int] = []
    picked_order_ids: list[int] = []
    unbindable_order_ids: list[int] = []

    if resolved_from and resolved_to:
        reservation_ids = db_layer.get_driver_loading_reservations_for_corridor(
            session_domain, resolved_from, resolved_to, actor_id
        )
        for rid in reservation_ids:
            row = db_layer.get_driver_reservation(session_domain, rid) or {}
            if str(row.get("status") or "") == "reservation_loading":
                loading_ids.append(rid)
        if loading_ids:
            open_cells = db_layer.list_open_cells_for_reservations(
                session_domain, loading_ids
            )
            picked_order_ids = db_layer.get_picked_orders_by_reservations(
                session_domain, loading_ids
            )
            if picked_order_ids:
                unbindable_order_ids = db_layer.list_orders_missing_trip_legs(
                    session_domain, picked_order_ids
                )
            if not anchor_direction_id and loading_ids:
                anchor = db_layer.get_driver_reservation(
                    session_domain, loading_ids[0]
                )
                if anchor and anchor.get("direction_id") is not None:
                    anchor_direction_id = int(anchor["direction_id"])

    instance: dict[str, Any] = {
        "entity_id": anchor_direction_id or 0,
        "actor_id": actor_id,
        "payload_json": {
            "executor_user_id": actor_id,
            "driver_user_id": actor_id,
            "direction_id": anchor_direction_id or None,
            "from_city": resolved_from,
            "to_city": resolved_to,
        },
    }
    ctx: dict[str, Any] = {
        "direction": direction,
        "direction_id": anchor_direction_id or None,
        "from_city": resolved_from,
        "to_city": resolved_to,
        "open_cells": open_cells,
        "reservation_ids": reservation_ids,
        "loading_reservation_ids": loading_ids,
        "picked_order_ids": picked_order_ids,
        "unbindable_order_ids": unbindable_order_ids,
        "executor_id": actor_id,
        "executor": executor,
        "payload": instance["payload_json"],
    }
    return ctx, instance


def build_invoke_reservation_context(
    session_domain,
    *,
    reservation_id: int,
    actor_id: int,
    payload: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Context для sync invoke reservation-команд."""
    merged: dict[str, Any] = dict(payload or {})
    merged.setdefault("executor_user_id", actor_id)
    merged.setdefault("driver_user_id", actor_id)
    instance: dict[str, Any] = {
        "entity_id": reservation_id,
        "actor_id": actor_id,
        "payload_json": merged,
    }
    ctx = build_reservation_context(session_domain, None, {}, instance)
    return ctx, instance

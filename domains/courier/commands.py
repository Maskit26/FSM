"""Синхронные Command-обработчики домена courier (без SQL — только db_layer)."""

from __future__ import annotations

from typing import Any, Optional

from domains.courier import db_layer
from domains.courier.errors import DomainError


def _require_str(params: dict[str, Any], key: str) -> str:
    """Проверяет, что параметр есть и не пустой. Возвращает строку без пробелов по краям."""
    value = params.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"{key} required")
    return str(value).strip()


def _delivery_to_type(raw: Any, *, field: str) -> str:
    """Переводит sender/recipient_delivery в ENUM заказа. Ровно 'self' → self, иначе courier."""
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"{field} required")
    return "self" if str(raw).strip() == "self" else "courier"


def _opt_float(params: dict[str, Any], key: str) -> Optional[float]:
    """Читает необязательную координату из params. Пустое значение даёт None."""
    raw = params.get(key)
    if raw is None or str(raw).strip() == "":
        return None
    return float(raw)


def create_order_request(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Шаг 1: найти свободные ячейки, создать order_requests (PENDING, без orders),
    enqueue FSM locker_reserve под request_id.
    """
    try:
        client_user_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not client_user_id:
        raise ValueError("actor.actor_id required")

    from_address = _require_str(params, "from_address")
    to_address = _require_str(params, "to_address")
    cell_size = db_layer.normalize_cell_size(domain_session, params.get("cell_size"))
    parcel_type = _require_str(params, "parcel_type")
    pickup_type = _delivery_to_type(params.get("sender_delivery"), field="sender_delivery")
    delivery_type = _delivery_to_type(
        params.get("recipient_delivery"), field="recipient_delivery"
    )

    recipient_user_id: Optional[int] = None
    if params.get("recipient_user_id") not in (None, ""):
        recipient_user_id = int(params["recipient_user_id"])

    from_lat = _opt_float(params, "from_lat")
    from_lng = _opt_float(params, "from_lng")
    to_lat = _opt_float(params, "to_lat")
    to_lng = _opt_float(params, "to_lng")

    source = db_layer.find_nearest_free_cell(
        domain_session,
        address=from_address,
        cell_size=cell_size,
        lat=from_lat,
        lng=from_lng,
    )
    if source is None:
        raise DomainError("NO_FREE_CELLS", "Ячейки не найдены (откуда)")

    dest = db_layer.find_nearest_free_cell(
        domain_session,
        address=to_address,
        cell_size=cell_size,
        lat=to_lat,
        lng=to_lng,
        exclude_cell_id=int(source["cell_id"]),
    )
    if dest is None:
        raise DomainError("NO_FREE_CELLS", "Ячейки не найдены (куда)")

    src_id = int(source["cell_id"])
    dst_id = int(dest["cell_id"])

    request_id = db_layer.insert_order_request(
        domain_session,
        client_user_id=client_user_id,
        source_cell_id=src_id,
        dest_cell_id=dst_id,
        from_address=from_address,
        to_address=to_address,
        cell_size=cell_size,
        parcel_type=parcel_type,
        pickup_type=pickup_type,
        delivery_type=delivery_type,
        recipient_user_id=recipient_user_id,
    )

    return {
        "entity_type": "order_request",
        "entity_id": request_id,
        "initial_state": "PENDING",
        "related_entities": [
            {
                "entity_type": "locker",
                "entity_id": src_id,
                "initial_state": "locker_free",
            },
            {
                "entity_type": "locker",
                "entity_id": dst_id,
                "initial_state": "locker_free",
            },
        ],
        "enqueues": [
            {
                "entity_type": "locker",
                "entity_id": src_id,
                "process_name": "locker_reserve",
                "payload": {
                    "request_id": request_id,
                    "cell_role": "source",
                    "source": "create_order_request",
                },
            },
            {
                "entity_type": "locker",
                "entity_id": dst_id,
                "process_name": "locker_reserve",
                "payload": {
                    "request_id": request_id,
                    "cell_role": "dest",
                    "source": "create_order_request",
                },
            },
        ],
        "data": {
            "request_id": request_id,
            "status": "PENDING",
            "from_address": from_address,
            "to_address": to_address,
            "source_cell_id": src_id,
            "dest_cell_id": dst_id,
            "source_locker_id": int(source["locker_id"]),
            "dest_locker_id": int(dest["locker_id"]),
            "source_city": source.get("city"),
            "dest_city": dest.get("city"),
            "pickup_type": pickup_type,
            "delivery_type": delivery_type,
        },
    }


def create_order(
    domain_session,
    params: dict[str, Any],
    actor: dict[str, Any],
    platform_session=None,
) -> dict[str, Any]:
    """
    Шаг 2: создать заказ по готовому request_id (order_requests.id).

    Ячейки уже locker_reserved через FSM; здесь bind
    (current_request_id → current_order_id). Нет заявки / не ready →
    DomainError, order_id клиенту не отдаём.
    """
    try:
        client_user_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not client_user_id:
        raise ValueError("actor.actor_id required")

    raw = params.get("request_id")
    if raw in (None, ""):
        raise DomainError(
            "REQUEST_ID_REQUIRED",
            "Сначала create_order_request, затем create_order(request_id)",
        )
    request_id = int(raw)

    req = db_layer.get_order_request(domain_session, request_id)
    if req is None:
        raise DomainError("REQUEST_NOT_FOUND", f"order_request {request_id} not found")
    if int(req.get("client_user_id") or 0) != client_user_id:
        raise DomainError("REQUEST_NOT_OWNER", "заявка принадлежит другому клиенту")

    status = str(req.get("status") or "")
    if status == "COMPLETED":
        raise DomainError(
            "REQUEST_ALREADY_USED", f"request {request_id} уже COMPLETED"
        )
    if status == "FAILED":
        raise DomainError("REQUEST_FAILED", f"request {request_id} FAILED")
    if db_layer.is_request_expired(req):
        released = db_layer.abort_order_request(
            domain_session,
            request_id,
            error_code="REQUEST_EXPIRED",
            error_message="request expired",
        )
        raise DomainError(
            "REQUEST_EXPIRED",
            f"request {request_id} истёк; освобождено ячеек: {len(released)}",
        )
    if status != "PENDING":
        raise DomainError("REQUEST_INVALID", f"request status={status}")
    if not db_layer.request_cells_ready(domain_session, request_id):
        raise DomainError(
            "REQUEST_NOT_READY",
            "Ячейки ещё не зарезервированы (дождитесь locker_reserve)",
        )

    src_id = int(req["source_cell_id"])
    dst_id = int(req["dest_cell_id"])
    from_address = str(req["from_address"])
    to_address = str(req["to_address"])
    cell_size = str(req["cell_size"])
    parcel_type = str(req["parcel_type"])
    pickup_type = str(req["pickup_type"])
    delivery_type = str(req["delivery_type"])
    recipient_user_id = req.get("recipient_user_id")
    if recipient_user_id is not None:
        recipient_user_id = int(recipient_user_id)

    description = f"{parcel_type} ({cell_size})"
    order_id = db_layer.insert_order(
        domain_session,
        description=description,
        client_user_id=client_user_id,
        recipient_user_id=recipient_user_id,
        delivery_type=delivery_type,
        pickup_type=pickup_type,
        parcel_type=parcel_type,
        from_address=from_address,
        to_address=to_address,
        source_cell_id=src_id,
        dest_cell_id=dst_id,
    )

    if not db_layer.bind_request_cells_to_order(domain_session, request_id, order_id):
        raise DomainError(
            "BIND_REQUEST_FAILED",
            f"Не удалось привязать ячейки request #{request_id} к заказу",
        )
    if not db_layer.mark_request_completed(domain_session, request_id, order_id):
        raise DomainError(
            "REQUEST_COMPLETE_FAILED", f"request {request_id} COMPLETED failed"
        )

    db_layer.create_stage_order(domain_session, order_id, "pickup")
    db_layer.create_stage_order(domain_session, order_id, "delivery")

    if platform_session is not None:
        from domains.courier.notifications import enqueue_order_progress_notifications

        enqueue_order_progress_notifications(
            domain_session,
            {"platform": platform_session},
            order_id=order_id,
            to_state="order_created",
            platform_session=platform_session,
        )

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "initial_state": "order_created",
        "related_entities": [
            {
                "entity_type": "locker",
                "entity_id": src_id,
                "initial_state": "locker_reserved",
            },
            {
                "entity_type": "locker",
                "entity_id": dst_id,
                "initial_state": "locker_reserved",
            },
            {
                "entity_type": "order_request",
                "entity_id": request_id,
                "initial_state": "COMPLETED",
            },
        ],
        "data": {
            "order_id": order_id,
            "request_id": request_id,
            "status": "order_created",
            "from_address": from_address,
            "to_address": to_address,
            "source_cell_id": src_id,
            "dest_cell_id": dst_id,
            "pickup_type": pickup_type,
            "delivery_type": delivery_type,
        },
    }



def take_courier_order(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    UX-обёртка «взять с биржи»: enqueue общего процесса assign_executor.
    Цепочку (courier1 / courier2) выбирают guards по leg и текущему state.
    """
    return assign_executor(domain_session, params, actor)


def assign_executor(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Общее назначение исполнителя (как старый assign_executor).
    Для order: params.order_id + params.leg (pickup|delivery).
    Дальше FSM-процесс assign_executor + guards/effects.
    """
    _ = domain_session
    try:
        executor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not executor_id:
        raise ValueError("actor.actor_id required")

    entity_type = str(params.get("entity_type") or "order").strip().lower()
    if entity_type != "order":
        raise ValueError("entity_type=trip (driver) not implemented yet")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    leg = str(params.get("leg") or "pickup").strip().lower()
    if leg not in ("pickup", "delivery"):
        raise ValueError("leg must be pickup or delivery")

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "enqueue": {
            "process_name": "assign_executor",
            "payload": {
                "leg": leg,
                "executor_user_id": executor_id,
                "courier_user_id": executor_id,
                "source": "assign_executor",
            },
        },
        "data": {
            "order_id": order_id,
            "leg": leg,
            "executor_user_id": executor_id,
            "status": "pending_fsm",
        },
    }


def cancel_courier_order(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """UX: курьер отказался → remove_executor (заказ снова на бирже)."""
    return remove_executor(domain_session, params, actor)


def remove_executor(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Снятие исполнителя с заказа (как старый remove_executor).
    params: order_id, leg; опционально executor_user_id (кого снять).
    По умолчанию снимается actor (самоотказ курьера).
    """
    _ = domain_session
    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not actor_id:
        raise ValueError("actor.actor_id required")

    entity_type = str(params.get("entity_type") or "order").strip().lower()
    if entity_type != "order":
        raise ValueError("entity_type=trip (driver) not implemented yet")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    leg = str(params.get("leg") or "pickup").strip().lower()
    if leg not in ("pickup", "delivery"):
        raise ValueError("leg must be pickup or delivery")

    # кого снимаем: явно из params или сам actor (отказ курьера)
    raw_target = params.get("executor_user_id") or params.get("courier_user_id")
    if raw_target is not None and str(raw_target).strip() != "":
        executor_id = int(raw_target)
    else:
        executor_id = actor_id

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "enqueue": {
            "process_name": "remove_executor",
            "payload": {
                "leg": leg,
                "executor_user_id": executor_id,
                "courier_user_id": executor_id,
                "source": "remove_executor",
            },
        },
        "data": {
            "order_id": order_id,
            "leg": leg,
            "executor_user_id": executor_id,
            "status": "pending_fsm",
        },
    }


def open_cell(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Открытие ячейки (как старый open_cell).
    params: order_id, leg, pin.
    Цепочку (client / courier pickup|delivery) выбирают guards.
    related_entities: bootstrap entity_fsm_state ячейки для companion.
    """
    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not actor_id:
        raise ValueError("actor.actor_id required")

    entity_type = str(params.get("entity_type") or "order").strip().lower()
    if entity_type != "order":
        raise ValueError("entity_type=locker (driver) not implemented yet")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    leg = str(params.get("leg") or "pickup").strip().lower()
    if leg not in ("pickup", "delivery"):
        raise ValueError("leg must be pickup or delivery")

    pin = params.get("pin")
    if pin is None or str(pin).strip() == "":
        raise ValueError("pin required")
    pin = str(pin).strip()

    order = db_layer.get_order(domain_session, order_id)
    if order is None:
        raise DomainError("ORDER_NOT_FOUND", f"order {order_id} not found")
    cell_id = (
        order.get("dest_cell_id") if leg == "delivery" else order.get("source_cell_id")
    )
    if not cell_id:
        raise DomainError("CELL_MISSING", f"no cell for order {order_id} leg={leg}")
    cell_id = int(cell_id)
    cell_status = db_layer.get_cell_status(domain_session, cell_id) or "locker_reserved"

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "related_entities": [
            {
                "entity_type": "locker",
                "entity_id": cell_id,
                "initial_state": str(cell_status),
            }
        ],
        "enqueue": {
            "process_name": "open_cell",
            "payload": {
                "leg": leg,
                "pin": pin,
                "executor_user_id": actor_id,
                "courier_user_id": actor_id,
                "source": "open_cell",
            },
        },
        "data": {
            "order_id": order_id,
            "leg": leg,
            "cell_id": cell_id,
            "status": "pending_fsm",
        },
    }


def close_cell(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Закрытие ячейки (как старый close_cell).
    params: order_id, leg. PIN не нужен.
    Цепочку (client / courier pickup|delivery) выбирают guards.
    """
    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not actor_id:
        raise ValueError("actor.actor_id required")

    entity_type = str(params.get("entity_type") or "order").strip().lower()
    if entity_type != "order":
        raise ValueError("entity_type=locker (driver) not implemented yet")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    leg = str(params.get("leg") or "pickup").strip().lower()
    if leg not in ("pickup", "delivery"):
        raise ValueError("leg must be pickup or delivery")

    order = db_layer.get_order(domain_session, order_id)
    if order is None:
        raise DomainError("ORDER_NOT_FOUND", f"order {order_id} not found")
    cell_id = (
        order.get("dest_cell_id") if leg == "delivery" else order.get("source_cell_id")
    )
    if not cell_id:
        raise DomainError("CELL_MISSING", f"no cell for order {order_id} leg={leg}")
    cell_id = int(cell_id)
    cell_status = db_layer.get_cell_status(domain_session, cell_id) or "locker_opened"

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "related_entities": [
            {
                "entity_type": "locker",
                "entity_id": cell_id,
                "initial_state": str(cell_status),
            }
        ],
        "enqueue": {
            "process_name": "close_cell",
            "payload": {
                "leg": leg,
                "executor_user_id": actor_id,
                "courier_user_id": actor_id,
                "source": "close_cell",
            },
        },
        "data": {
            "order_id": order_id,
            "leg": leg,
            "cell_id": cell_id,
            "status": "pending_fsm",
        },
    }


def request_locker_access_code(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    «Получить PIN»: context → guard-rules → INSERT cell_access_tokens.
    """
    from domains.courier.context import build_invoke_order_context
    from domains.courier.guards import can_request_locker_access_code

    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not actor_id:
        raise ValueError("actor.actor_id required")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    leg = str(params.get("leg") or "pickup").strip().lower()
    if leg not in ("pickup", "delivery"):
        raise ValueError("leg must be pickup or delivery")
    expires_minutes = int(params.get("expires_minutes") or 15)

    ctx, instance = build_invoke_order_context(
        domain_session,
        order_id=order_id,
        actor_id=actor_id,
        payload={"leg": leg},
    )
    gate = can_request_locker_access_code(
        domain_session, None, ctx, instance, None
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_AUTHORIZED", gate.reason or "denied")

    cell_id = int(ctx["cell_id"])
    recent = db_layer.count_recent_access_code_requests(
        domain_session, order_id, leg, minutes=15
    )
    if recent >= 3:
        raise DomainError("TOO_MANY_CODE_REQUESTS", "too many PIN requests")

    pin, token_id, expires_at = db_layer.generate_and_store_access_token(
        domain_session,
        order_id,
        leg,
        cell_id,
        actor_id,
        expires_minutes=expires_minutes,
    )

    return {
        "data": {
            "order_id": order_id,
            "leg": leg,
            "cell_id": cell_id,
            "token_id": token_id,
            "expires_at": expires_at.isoformat() + "Z",
            "status": "issued",
            "pin": pin,
        }
    }


def reserve_direction_slot(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Водитель резервирует до capacity заказов по коридору (город→город).
    params: from_city + to_city + capacity
    (legacy: direction_id → резолвится в коридор).
    """
    from domains.courier.context import build_invoke_direction_context
    from domains.courier.guards import can_reserve_direction_slot

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    raw_dir = params.get("direction_id") or params.get("entity_id")
    direction_id = int(raw_dir) if raw_dir not in (None, "") else 0
    from_city = str(params.get("from_city") or "").strip() or None
    to_city = str(params.get("to_city") or "").strip() or None
    if not direction_id and (not from_city or not to_city):
        raise ValueError("from_city+to_city (or direction_id) required")

    try:
        capacity = int(params.get("capacity") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("capacity required") from exc

    ctx, _instance = build_invoke_direction_context(
        domain_session,
        actor_id=driver_id,
        capacity=capacity,
        direction_id=direction_id or None,
        from_city=from_city,
        to_city=to_city,
    )
    gate = can_reserve_direction_slot(
        domain_session, None, ctx, _instance, {"user_role": "driver"}
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    resolved_from = str(ctx.get("from_city") or "")
    resolved_to = str(ctx.get("to_city") or "")
    try:
        reservation_id, reserved_count, expires_at, order_ids = (
            db_layer.reserve_orders_for_corridor(
                domain_session,
                resolved_from,
                resolved_to,
                driver_id,
                capacity,
            )
        )
    except ValueError as exc:
        code = str(exc)
        raise DomainError(code, code) from exc

    pickup_stops = db_layer.list_pickup_stops_for_reservation(
        domain_session, reservation_id
    )
    anchor_direction_id = int(ctx.get("direction_id") or 0)
    if not anchor_direction_id:
        reservation = db_layer.get_driver_reservation(
            domain_session, reservation_id
        )
        if reservation and reservation.get("direction_id") is not None:
            anchor_direction_id = int(reservation["direction_id"])

    expire_key = f"expire_reservation:{reservation_id}"
    return {
        "entity_type": "driver_reservations",
        "entity_id": reservation_id,
        "initial_state": "reservation_active",
        "timers": [
            {
                "entity_type": "driver_reservations",
                "entity_id": reservation_id,
                "process_name": "expire_reservation",
                "fire_at": expires_at,
                "idempotency_key": expire_key,
                "payload": {
                    "direction_id": anchor_direction_id or None,
                    "from_city": resolved_from,
                    "to_city": resolved_to,
                    "executor_user_id": driver_id,
                    "driver_user_id": driver_id,
                    "source": "expire_timer",
                },
            }
        ],
        "data": {
            "reservation_id": reservation_id,
            "direction_id": anchor_direction_id or None,
            "from_city": resolved_from,
            "to_city": resolved_to,
            "driver_user_id": driver_id,
            "requested_count": capacity,
            "reserved_count": reserved_count,
            "order_ids": order_ids,
            "pickup_stops": pickup_stops,
            "expires_at": expires_at.isoformat() + "Z",
            "status": "reservation_active",
        },
    }


def start_loading(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Водитель начинает погрузку: context → can_start_loading → enqueue FSM.
    params: reservation_id.
    """
    from domains.courier.context import build_invoke_reservation_context
    from domains.courier.guards import can_start_loading

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    reservation_id = int(
        params.get("reservation_id") or params.get("entity_id") or 0
    )
    if not reservation_id:
        raise ValueError("reservation_id required")

    ctx, _instance = build_invoke_reservation_context(
        domain_session,
        reservation_id=reservation_id,
        actor_id=driver_id,
    )
    gate = can_start_loading(
        domain_session,
        None,
        ctx,
        _instance,
        {"user_role": "driver", "required_status": "reservation_active"},
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    direction_id = int(ctx.get("direction_id") or 0)
    pickup_stops = db_layer.list_pickup_stops_for_reservation(
        domain_session, reservation_id
    )
    return {
        "entity_type": "driver_reservations",
        "entity_id": reservation_id,
        "initial_state": "reservation_active",
        "cancel_timers": [
            {"idempotency_key": f"expire_reservation:{reservation_id}"}
        ],
        "enqueue": {
            "process_name": "start_loading",
            "payload": {
                "direction_id": direction_id,
                "executor_user_id": driver_id,
                "driver_user_id": driver_id,
                "source": "start_loading",
            },
        },
        "data": {
            "reservation_id": reservation_id,
            "direction_id": direction_id,
            "driver_user_id": driver_id,
            "pickup_stops": pickup_stops,
            "status": "pending_fsm",
        },
    }


def cancel_reservation(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Водитель отменяет резерв: context → can_cancel_reservation → enqueue FSM.
    params: reservation_id.
    """
    from domains.courier.context import build_invoke_reservation_context
    from domains.courier.guards import can_cancel_reservation

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    reservation_id = int(
        params.get("reservation_id") or params.get("entity_id") or 0
    )
    if not reservation_id:
        raise ValueError("reservation_id required")

    ctx, _instance = build_invoke_reservation_context(
        domain_session,
        reservation_id=reservation_id,
        actor_id=driver_id,
    )
    reservation = ctx.get("reservation") or {}
    status = str(reservation.get("status") or "")
    # Edge pick: active|loading — same as FSM graph.
    required = (
        status
        if status in ("reservation_active", "reservation_loading")
        else "reservation_active"
    )
    gate = can_cancel_reservation(
        domain_session,
        None,
        ctx,
        _instance,
        {"user_role": "driver", "required_status": required},
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    direction_id = int(ctx.get("direction_id") or 0)
    return {
        "entity_type": "driver_reservations",
        "entity_id": reservation_id,
        "initial_state": status,
        "cancel_timers": [
            {"idempotency_key": f"expire_reservation:{reservation_id}"}
        ],
        "enqueue": {
            "process_name": "cancel_reservation",
            "payload": {
                "direction_id": direction_id,
                "executor_user_id": driver_id,
                "driver_user_id": driver_id,
                "source": "cancel_reservation",
            },
        },
        "data": {
            "reservation_id": reservation_id,
            "direction_id": direction_id,
            "driver_user_id": driver_id,
            "status": "pending_fsm",
        },
    }


def complete_loading(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Завершить погрузку по коридору:
    context → can_create_trip → release unpicked + INSERT trip + bootstrap,
    затем enqueues[] complete_loading на каждый резерв (FSM).
    params: from_city + to_city (legacy: direction_id).
    """
    from domains.courier.context import build_invoke_create_trip_context
    from domains.courier.guards import can_create_trip

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    raw_dir = params.get("direction_id") or params.get("entity_id")
    direction_id = int(raw_dir) if raw_dir not in (None, "") else 0
    from_city = str(params.get("from_city") or "").strip() or None
    to_city = str(params.get("to_city") or "").strip() or None
    if not direction_id and (not from_city or not to_city):
        raise ValueError("from_city+to_city (or direction_id) required")

    ctx, _instance = build_invoke_create_trip_context(
        domain_session,
        actor_id=driver_id,
        direction_id=direction_id or None,
        from_city=from_city,
        to_city=to_city,
    )
    gate = can_create_trip(
        domain_session, None, ctx, _instance, {"user_role": "driver"}
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    loading_ids = list(ctx["loading_reservation_ids"])
    picked = list(ctx["picked_order_ids"])
    resolved_from = str(ctx.get("from_city") or "")
    resolved_to = str(ctx.get("to_city") or "")
    anchor_direction_id = int(ctx.get("direction_id") or 0)
    if not anchor_direction_id:
        raise DomainError("DIRECTION_NOT_FOUND", "DIRECTION_NOT_FOUND")

    released = db_layer.release_unpicked_orders_by_reservations(
        domain_session, loading_ids, picked
    )

    try:
        trip_id = db_layer.create_trip_with_orders(
            domain_session,
            direction_id=anchor_direction_id,
            driver_user_id=driver_id,
            order_ids=picked,
            from_city=resolved_from,
            to_city=resolved_to,
        )
    except ValueError as exc:
        raise DomainError(str(exc), str(exc)) from exc

    return {
        "entity_type": "driver_reservations",
        "entity_id": loading_ids[0],
        "related_entities": [
            {
                "entity_type": "trip",
                "entity_id": trip_id,
                "initial_state": "trip_assigned",
            }
        ],
        "enqueues": [
            {
                "entity_type": "driver_reservations",
                "entity_id": rid,
                "process_name": "complete_loading",
                "payload": {
                    "direction_id": anchor_direction_id,
                    "from_city": resolved_from,
                    "to_city": resolved_to,
                    "executor_user_id": driver_id,
                    "driver_user_id": driver_id,
                    "source": "complete_loading",
                },
            }
            for rid in loading_ids
        ],
        "cancel_timers": [
            {"idempotency_key": f"expire_reservation:{rid}"}
            for rid in loading_ids
        ],
        "data": {
            "direction_id": anchor_direction_id,
            "from_city": resolved_from,
            "to_city": resolved_to,
            "driver_user_id": driver_id,
            "reservation_ids": loading_ids,
            "picked_order_ids": picked,
            "released_rows": released,
            "trip_id": trip_id,
            "trip_status": "trip_assigned",
            "status": "pending_fsm",
        },
    }


def start_trip(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Старт рейса: context → can_start_trip → saga
    (orders transit → then trip assigned→in_progress).
    params: trip_id.
    """
    from domains.courier.context import build_invoke_trip_context
    from domains.courier.guards import can_start_trip

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    trip_id = int(params.get("trip_id") or params.get("entity_id") or 0)
    if not trip_id:
        raise ValueError("trip_id required")

    ctx, _instance = build_invoke_trip_context(
        domain_session,
        trip_id=trip_id,
        actor_id=driver_id,
    )
    gate = can_start_trip(
        domain_session,
        None,
        ctx,
        _instance,
        {"user_role": "driver", "required_status": "trip_assigned"},
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    order_ids = list(ctx.get("order_ids") or [])
    trip_payload = {
        "executor_user_id": driver_id,
        "driver_user_id": driver_id,
        "source": "start_trip",
    }

    return {
        "entity_type": "trip",
        "entity_id": trip_id,
        "initial_state": "trip_assigned",
        "saga": {
            "fail_policy": "fail_fast",
            "children": [
                {
                    "entity_type": "order",
                    "entity_id": oid,
                    "initial_state": "order_picked_up_from_post1",
                    "process_name": "start_order_transit",
                    "payload": {
                        "trip_id": trip_id,
                        "executor_user_id": driver_id,
                        "driver_user_id": driver_id,
                        "source": "start_trip",
                    },
                }
                for oid in order_ids
            ],
            "on_success": {
                "entity_type": "trip",
                "entity_id": trip_id,
                "initial_state": "trip_assigned",
                "process_name": "start_trip",
                "payload": trip_payload,
            },
            "on_fail": None,
        },
        "data": {
            "trip_id": trip_id,
            "driver_user_id": driver_id,
            "order_ids": order_ids,
            "status": "saga_pending",
        },
    }


def complete_trip(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Завершение рейса после разгрузки всех заказов в post2:
    context → can_complete_trip → enqueue FSM trip_in_progress→trip_completed.
    params: trip_id.
    """
    from domains.courier.context import build_invoke_trip_context
    from domains.courier.guards import can_complete_trip

    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    trip_id = int(params.get("trip_id") or params.get("entity_id") or 0)
    if not trip_id:
        raise ValueError("trip_id required")

    ctx, _instance = build_invoke_trip_context(
        domain_session,
        trip_id=trip_id,
        actor_id=driver_id,
    )
    gate = can_complete_trip(
        domain_session,
        None,
        ctx,
        _instance,
        {"user_role": "driver", "required_status": "trip_in_progress"},
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    return {
        "entity_type": "trip",
        "entity_id": trip_id,
        "initial_state": "trip_in_progress",
        "enqueue": {
            "process_name": "complete_trip",
            "payload": {
                "executor_user_id": driver_id,
                "driver_user_id": driver_id,
                "source": "complete_trip",
            },
        },
        "data": {
            "trip_id": trip_id,
            "driver_user_id": driver_id,
            "order_ids": list(ctx.get("order_ids") or []),
            "delivery_stops": list(ctx.get("delivery_stops") or []),
            "status": "pending_fsm",
        },
    }


def confirm_courier2_delivery(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Курьер2 подтверждает доставку кодом получателя.
    params: order_id, pin.
    FSM: order_courier2_parcel_delivered → order_completed.
    """
    from domains.courier.context import build_invoke_order_context
    from domains.courier.guards import can_confirm_courier2_delivery

    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not actor_id:
        raise ValueError("actor.actor_id required")

    order_id = int(params.get("order_id") or params.get("entity_id") or 0)
    if not order_id:
        raise ValueError("order_id required")

    pin = params.get("pin")
    if pin is None or str(pin).strip() == "":
        raise ValueError("pin required")
    pin = str(pin).strip()

    ctx, _instance = build_invoke_order_context(
        domain_session,
        order_id=order_id,
        actor_id=actor_id,
        payload={"leg": "delivery", "pin": pin},
    )
    gate = can_confirm_courier2_delivery(
        domain_session,
        None,
        ctx,
        _instance,
        {
            "leg": "delivery",
            "user_role": "courier",
            "required_status": "order_courier2_parcel_delivered",
            "type_field": "delivery_type",
            "type_value": "courier",
            "stage_must_be": "owned",
            "require_pin": True,
        },
    )
    if not gate.ok:
        raise DomainError(gate.reason or "NOT_ALLOWED", gate.reason or "denied")

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "initial_state": "order_courier2_parcel_delivered",
        "enqueue": {
            "process_name": "confirm_courier2_delivery",
            "payload": {
                "leg": "delivery",
                "pin": pin,
                "executor_user_id": actor_id,
                "courier_user_id": actor_id,
                "source": "confirm_courier2_delivery",
            },
        },
        "data": {
            "order_id": order_id,
            "leg": "delivery",
            "status": "pending_fsm",
        },
    }

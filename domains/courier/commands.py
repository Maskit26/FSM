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


def create_order(domain_session, params: dict[str, Any], actor: dict[str, Any]) -> dict[str, Any]:
    """
    Создаёт заказ: ищет свободные ячейки, пишет orders и stage_orders.
    Резерв ячеек — FSM process locker_reserve (locker_free → locker_reserved).
    Клиент берётся из actor.actor_id.
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

    db_layer.create_stage_order(domain_session, order_id, "pickup")
    db_layer.create_stage_order(domain_session, order_id, "delivery")

    # Ячейки резервирует FSM locker_reserve_cell (effect), не SQL в command.
    locker_bootstrap = [
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
    ]
    reserve_jobs = [
        {
            "entity_type": "locker",
            "entity_id": src_id,
            "initial_state": "locker_free",
            "process_name": "locker_reserve",
            "payload": {
                "order_id": order_id,
                "cell_role": "source",
                "source": "create_order",
            },
        },
        {
            "entity_type": "locker",
            "entity_id": dst_id,
            "initial_state": "locker_free",
            "process_name": "locker_reserve",
            "payload": {
                "order_id": order_id,
                "cell_role": "dest",
                "source": "create_order",
            },
        },
    ]

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "initial_state": "order_created",
        "related_entities": locker_bootstrap,
        "enqueues": reserve_jobs,
        "data": {
            "order_id": order_id,
            "status": "order_created",
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
    Водитель резервирует до capacity заказов из направления
    (old direction_reserve_slot / reserve_orders_for_direction).
    Sync: создаёт driver_reservations, без enqueue FSM.
    params: direction_id, capacity.
    """
    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, driver_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"user {driver_id} not found")
    if str(user.get("role_name") or "") != "driver":
        raise DomainError("ROLE_NOT_ALLOWED", "only driver can reserve direction slot")

    direction_id = int(params.get("direction_id") or params.get("entity_id") or 0)
    if not direction_id:
        raise ValueError("direction_id required")
    try:
        capacity = int(params.get("capacity") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("capacity required") from exc
    if capacity <= 0:
        raise DomainError("INVALID_CAPACITY", "capacity must be > 0")

    direction = db_layer.get_direction(domain_session, direction_id)
    if direction is None:
        raise DomainError("DIRECTION_NOT_FOUND", f"direction {direction_id} not found")

    driver_city = str(user.get("city") or "").strip()
    from_city = str(direction.get("from_city") or "").strip()
    if driver_city and from_city and driver_city != from_city:
        raise DomainError(
            "CITY_MISMATCH",
            f"{driver_city}->{from_city}",
        )

    try:
        reservation_id, reserved_count, expires_at = (
            db_layer.reserve_orders_for_direction(
                domain_session, direction_id, driver_id, capacity
            )
        )
    except ValueError as exc:
        code = str(exc)
        raise DomainError(code, code) from exc

    return {
        "entity_type": "driver_reservations",
        "entity_id": reservation_id,
        "initial_state": "reservation_active",
        "data": {
            "reservation_id": reservation_id,
            "direction_id": direction_id,
            "driver_user_id": driver_id,
            "requested_count": capacity,
            "reserved_count": reserved_count,
            "expires_at": expires_at.isoformat() + "Z",
            "status": "reservation_active",
        },
    }


def start_loading(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Водитель начинает погрузку: enqueue FSM start_loading на driver_reservations.
    params: reservation_id.
    """
    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, driver_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"user {driver_id} not found")
    if str(user.get("role_name") or "") != "driver":
        raise DomainError("ROLE_NOT_ALLOWED", "only driver can start loading")

    reservation_id = int(
        params.get("reservation_id") or params.get("entity_id") or 0
    )
    if not reservation_id:
        raise ValueError("reservation_id required")

    reservation = db_layer.get_driver_reservation(domain_session, reservation_id)
    if reservation is None:
        raise DomainError("RESERVATION_NOT_FOUND", f"reservation {reservation_id}")
    if int(reservation["driver_user_id"]) != driver_id:
        raise DomainError("NOT_RESERVATION_OWNER", "reservation belongs to another driver")
    if str(reservation.get("status") or "") != "reservation_active":
        raise DomainError(
            "INVALID_RESERVATION_STATUS",
            f"status={reservation.get('status')}",
        )

    return {
        "entity_type": "driver_reservations",
        "entity_id": reservation_id,
        "initial_state": "reservation_active",
        "enqueue": {
            "process_name": "start_loading",
            "payload": {
                "direction_id": int(reservation["direction_id"]),
                "executor_user_id": driver_id,
                "driver_user_id": driver_id,
                "source": "start_loading",
            },
        },
        "data": {
            "reservation_id": reservation_id,
            "direction_id": int(reservation["direction_id"]),
            "driver_user_id": driver_id,
            "status": "pending_fsm",
        },
    }


def complete_loading(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Завершить погрузку по направлению: проверки + release unpicked sync,
    затем enqueues[] complete_loading на каждый резерв (FSM + логи).
    params: direction_id.
    """
    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, driver_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"user {driver_id} not found")
    if str(user.get("role_name") or "") != "driver":
        raise DomainError("ROLE_NOT_ALLOWED", "only driver can complete loading")

    direction_id = int(params.get("direction_id") or params.get("entity_id") or 0)
    if not direction_id:
        raise ValueError("direction_id required")

    direction = db_layer.get_direction(domain_session, direction_id)
    if direction is None:
        raise DomainError("DIRECTION_NOT_FOUND", f"direction {direction_id}")

    open_cells = db_layer.list_open_cells_for_driver_direction(
        domain_session, direction_id, driver_id
    )
    if open_cells:
        raise DomainError(
            "OPEN_CELLS_DETECTED",
            f"cells still open: {open_cells}",
        )

    reservation_ids = db_layer.get_driver_loading_reservations(
        domain_session, direction_id, driver_id
    )
    # complete FSM edge is from reservation_loading only
    loading_ids = [
        rid
        for rid in reservation_ids
        if str(
            (db_layer.get_driver_reservation(domain_session, rid) or {}).get("status")
            or ""
        )
        == "reservation_loading"
    ]
    if not loading_ids:
        raise DomainError(
            "NO_LOADING_RESERVATIONS",
            "no reservations in reservation_loading",
        )

    picked = db_layer.get_picked_orders_by_driver_and_direction(
        domain_session, direction_id, driver_id
    )
    if not picked:
        raise DomainError("NO_PICKED_ORDERS", "no orders picked up from post1")

    released = db_layer.release_unpicked_orders_by_driver_and_direction(
        domain_session, direction_id, driver_id, picked
    )

    return {
        "entity_type": "driver_reservations",
        "entity_id": loading_ids[0],
        "enqueues": [
            {
                "entity_type": "driver_reservations",
                "entity_id": rid,
                "process_name": "complete_loading",
                "payload": {
                    "direction_id": direction_id,
                    "executor_user_id": driver_id,
                    "driver_user_id": driver_id,
                    "source": "complete_loading",
                },
            }
            for rid in loading_ids
        ],
        "data": {
            "direction_id": direction_id,
            "driver_user_id": driver_id,
            "reservation_ids": loading_ids,
            "picked_order_ids": picked,
            "released_rows": released,
            "status": "pending_fsm",
        },
    }

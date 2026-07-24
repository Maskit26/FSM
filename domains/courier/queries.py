"""Query-обработчики домена courier: только чтение через db_layer."""

from __future__ import annotations

from typing import Any

from domains.courier import db_layer
from domains.courier.errors import DomainError


def list_client_orders(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Возвращает список заказов клиента.
    Id клиента берётся из params или из actor.actor_id.
    """
    client_user_id = int(
        params.get("client_user_id")
        or (actor or {}).get("actor_id")
        or 0
    )
    if not client_user_id:
        raise ValueError("client_user_id required")
    limit = int(params.get("limit") or 20)
    rows = db_layer.list_orders_for_client(domain_session, client_user_id, limit=limit)
    return {"data": rows}


def list_courier_exchange(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Биржа курьера: свободные заказы в городе курьера (pickup и delivery).
    Курьер определяется по actor.actor_id; на фронте фильтруют по полю leg.
    """
    try:
        courier_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not courier_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, courier_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"User {courier_id} not found")
    if str(user.get("role_name") or "") != "courier":
        raise DomainError("NOT_A_COURIER", "User is not a courier")

    city = str(user.get("city") or "").strip()
    if not city:
        raise DomainError("COURIER_CITY_REQUIRED", "У курьера не указан город")

    exchange = db_layer.list_courier_exchange(domain_session, city)
    return {
        "data": {
            "courier_id": courier_id,
            "city": city,
            "orders": exchange["all"],
        }
    }


def list_courier_orders(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Заказы, которые курьер уже взял с биржи (по stage_orders).
    params.filter: active | archive | all (по умолчанию all); на фронте — вкладки.
    """
    try:
        courier_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not courier_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, courier_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"User {courier_id} not found")
    if str(user.get("role_name") or "") != "courier":
        raise DomainError("NOT_A_COURIER", "User is not a courier")

    status_filter = str(params.get("filter") or "all").strip().lower()
    limit = int(params.get("limit") or 50)
    orders = db_layer.list_orders_for_courier(
        domain_session,
        courier_id,
        status_filter=status_filter,
        limit=limit,
    )
    return {
        "data": {
            "courier_id": courier_id,
            "filter": status_filter,
            "orders": orders,
        }
    }


def view_locker_access_code(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    «Посмотреть PIN»: context → те же guard-rules → pin_encrypted.
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

    pin = db_layer.get_access_token_pin(domain_session, order_id, leg, actor_id)
    if not pin:
        raise DomainError(
            "CODE_NOT_FOUND_OR_EXPIRED",
            "active PIN not found or expired",
        )

    return {
        "data": {
            "order_id": order_id,
            "leg": leg,
            "pin": pin,
        }
    }


def list_driver_exchange(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Биржа водителя: коридоры из выбранного города (params.city).
    Город задаёт фронт/актёр; users.city водителя не используется.
    В directions[].pairs — разбивка по парам постаматов.
    """
    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, driver_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"User {driver_id} not found")
    if str(user.get("role_name") or "") != "driver":
        raise DomainError("NOT_A_DRIVER", "User is not a driver")

    city = str((params or {}).get("city") or "").strip()
    if not city:
        raise ValueError("city required")

    directions = db_layer.list_directions_for_driver_exchange(domain_session, city)
    return {
        "data": {
            "driver_id": driver_id,
            "city": city,
            "directions": directions,
        }
    }


def list_driver_trips(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
    """
    Рейсы водителя (по умолчанию trip_assigned + trip_in_progress).
    params.status — опционально один статус-фильтр.
    """
    try:
        driver_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not driver_id:
        raise ValueError("actor.actor_id required")

    user = db_layer.get_user(domain_session, driver_id)
    if user is None:
        raise DomainError("USER_NOT_FOUND", f"User {driver_id} not found")
    if str(user.get("role_name") or "") != "driver":
        raise DomainError("NOT_A_DRIVER", "User is not a driver")

    statuses: list[str] | None = None
    raw = params.get("status")
    if raw is not None and str(raw).strip() != "":
        statuses = [str(raw).strip()]

    trips = db_layer.list_driver_trips(
        domain_session, driver_id, statuses=statuses
    )
    return {
        "data": {
            "driver_id": driver_id,
            "trips": trips,
            "active_trip_id": trips[0]["id"] if trips else None,
        }
    }

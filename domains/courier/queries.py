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

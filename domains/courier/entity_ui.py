"""Entity access policy + Snapshot builders для courier."""

from __future__ import annotations

from typing import Any

from domains.courier import db_layer
from domains.courier.errors import DomainError


def _uid(principal: dict[str, Any]) -> int:
    raw = principal.get("userId") or principal.get("user_id") or principal.get("actor_id")
    try:
        return int(raw or 0)
    except (TypeError, ValueError):
        return 0


def _roles(principal: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    at = str(principal.get("actor_type") or "").strip().lower()
    if at:
        out.add(at)
    roles = principal.get("roles") or []
    if isinstance(roles, (list, tuple)):
        out.update(str(r).strip().lower() for r in roles if str(r).strip())
    return out


def can_access_order(
    domain_session,
    *,
    entity_id: int,
    principal: dict[str, Any],
    params: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """
    Дверь к order: admin/system, клиент/получатель заказа, назначенный курьер.
    """
    uid = _uid(principal)
    if not uid:
        return {"allowed": False, "reason": "ACTOR_REQUIRED"}

    roles = _roles(principal)
    if "admin" in roles or "system" in roles:
        return {"allowed": True, "reason": None}

    order = db_layer.get_order(domain_session, int(entity_id))
    if order is None:
        return {"allowed": False, "reason": "ORDER_NOT_FOUND"}

    client_id = int(order.get("client_user_id") or 0)
    recipient_id = int(order.get("recipient_user_id") or 0)
    if uid in {client_id, recipient_id}:
        return {"allowed": True, "reason": None}

    for leg in ("pickup", "delivery"):
        courier_id = db_layer.get_stage_courier(domain_session, int(entity_id), leg)
        if courier_id is not None and int(courier_id) == uid:
            return {"allowed": True, "reason": None}

    return {"allowed": False, "reason": "NOT_ORDER_PARTY"}


def snapshot_order(
    domain_session,
    *,
    entity_id: int,
    principal: dict[str, Any],
    params: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Карточка order для UI (поля; availableActions добавляет platform)."""
    order = db_layer.get_order(domain_session, int(entity_id))
    if order is None:
        raise DomainError("ORDER_NOT_FOUND", f"order {entity_id} not found")

    oid = int(order["id"])
    stages: dict[str, Any] = {}
    for leg in ("pickup", "delivery"):
        row = db_layer.get_stage_row(domain_session, oid, leg)
        if row:
            stages[leg] = {
                "courier_user_id": row.get("courier_user_id"),
                "trip_id": row.get("trip_id"),
                "direction_id": row.get("direction_id"),
            }

    source_cell = None
    dest_cell = None
    if order.get("source_cell_id"):
        source_cell = db_layer.get_cell_display(
            domain_session, int(order["source_cell_id"])
        )
    if order.get("dest_cell_id"):
        dest_cell = db_layer.get_cell_display(
            domain_session, int(order["dest_cell_id"])
        )

    return {
        "entityType": "order",
        "id": oid,
        "state": order.get("status"),
        "description": order.get("description"),
        "delivery_type": order.get("delivery_type"),
        "pickup_type": order.get("pickup_type"),
        "parcel_type": order.get("parcel_type"),
        "from_address": order.get("from_address"),
        "to_address": order.get("to_address"),
        "client_user_id": order.get("client_user_id"),
        "recipient_user_id": order.get("recipient_user_id"),
        "source_cell_id": order.get("source_cell_id"),
        "dest_cell_id": order.get("dest_cell_id"),
        "source_cell": source_cell,
        "dest_cell": dest_cell,
        "stages": stages,
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
    }

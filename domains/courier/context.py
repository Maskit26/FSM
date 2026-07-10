from __future__ import annotations

from typing import Any, Dict


def build_courier_context(
    session: Any,
    db: Any,
    runtime_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> Dict[str, Any]:
    """Собрать domain context для guards/effects courier-домена."""
    entity_type = instance.get("entity_type")
    if entity_type == "order_request":
        return _build_order_request_context(session, db, instance)
    return {}


def _build_order_request_context(
    session: Any,
    db: Any,
    instance: Dict[str, Any],
) -> Dict[str, Any]:
    request_id = instance.get("entity_id")
    if request_id is None:
        return {"request": None}

    request = db.get_order_request(session, request_id)
    if not request:
        return {"request": None, "request_id": request_id}

    pickup_type = "self" if request.get("sender_delivery") == "self" else "courier"
    delivery_type = "self" if request.get("recipient_delivery") == "self" else "courier"

    return {
        "request_id": request_id,
        "request": request,
        "client_user_id": request.get("client_user_id"),
        "recipient_user_id": request.get("recipient_user_id"),
        "client_city": request.get("from_city"),
        "recipient_city": request.get("to_city"),
        "from_city": request.get("from_city"),
        "to_city": request.get("to_city"),
        "parcel_type": request.get("parcel_type"),
        "cell_size": request.get("cell_size"),
        "pickup_type": pickup_type,
        "delivery_type": delivery_type,
        "description": f"{request.get('parcel_type')} ({request.get('cell_size')})",
    }

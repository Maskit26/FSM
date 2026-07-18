"""Sync Command handlers — no SQL here, only db_layer."""

from __future__ import annotations

from typing import Any

from domains.courier import db_layer


def create_order(domain_session, params: dict[str, Any], actor: dict[str, Any]) -> dict[str, Any]:
    """
    Create order row in domain DB.
    Request Runtime bootstraps entity_fsm_state + enqueue after return.
    """
    client_user_id = int(
        params.get("client_user_id")
        or (actor or {}).get("actor_id")
        or 0
    )
    if not client_user_id:
        raise ValueError("client_user_id required")

    description = str(params.get("description") or "Order")
    order_id = db_layer.insert_order(
        domain_session,
        description=description,
        client_user_id=client_user_id,
        delivery_type=str(params.get("delivery_type") or "courier"),
        pickup_type=str(params.get("pickup_type") or "courier"),
        parcel_type=params.get("parcel_type"),
    )
    return {
        "entity_type": "order",
        "entity_id": order_id,
        "initial_state": "order_created",
        "enqueue": {
            "process_name": "order_assign_courier1",
            "payload": {"source": "create_order"},
        },
        "data": {"order_id": order_id, "status": "order_created"},
    }

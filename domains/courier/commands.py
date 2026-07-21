"""Sync Command handlers — no SQL here, only db_layer.

create_order (frontend contract):
  - actor.actor_id → client_user_id (auth; not a form field)
  - from_address / to_address → nearest lockers + cell reserve; stored for routing
  - cell_size, parcel_type, sender_delivery, recipient_delivery
  - recipient_user_id optional (not a create form field)
"""

from __future__ import annotations

from typing import Any, Optional

from domains.courier import db_layer
from domains.courier.errors import DomainError

_VALID_CELL_SIZES = frozenset({"S", "M", "L", "P"})


def _require_str(params: dict[str, Any], key: str) -> str:
    value = params.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"{key} required")
    return str(value).strip()


def _delivery_to_type(raw: Any, *, field: str) -> str:
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"{field} required")
    return "self" if str(raw).strip() == "self" else "courier"


def _opt_float(params: dict[str, Any], key: str) -> Optional[float]:
    raw = params.get(key)
    if raw is None or str(raw).strip() == "":
        return None
    return float(raw)


def create_order(domain_session, params: dict[str, Any], actor: dict[str, Any]) -> dict[str, Any]:
    # Auth identity — not a frontend form field
    try:
        client_user_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("actor.actor_id required") from exc
    if not client_user_id:
        raise ValueError("actor.actor_id required")

    from_address = _require_str(params, "from_address")
    to_address = _require_str(params, "to_address")

    cell_size = _require_str(params, "cell_size").upper()
    if cell_size not in _VALID_CELL_SIZES:
        raise ValueError(f"cell_size must be one of {sorted(_VALID_CELL_SIZES)}")

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
    db_layer.reserve_and_bind_cells(domain_session, order_id, src_id, dst_id)

    return {
        "entity_type": "order",
        "entity_id": order_id,
        "initial_state": "order_created",
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

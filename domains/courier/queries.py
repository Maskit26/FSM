"""Query handlers — no SQL."""

from __future__ import annotations

from typing import Any

from domains.courier import db_layer


def list_client_orders(
    domain_session, params: dict[str, Any], actor: dict[str, Any]
) -> dict[str, Any]:
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

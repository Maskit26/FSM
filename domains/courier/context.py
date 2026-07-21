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

    return {
        "order": order,
        "order_id": order_id,
        "leg": leg,
        "payload": payload,
        "executor_id": executor_id,
        "executor": executor,
        "executor_city": executor_city,
        "cell_id": int(cell_id) if cell_id else None,
        "locker_city": locker_city,
        "stage_courier_id": stage_courier_id,
        "runtime_ctx": runtime_ctx,
    }

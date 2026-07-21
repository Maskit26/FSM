"""Сборка context для guards/effects процесса заказа."""

from __future__ import annotations

from typing import Any

from domains.courier import db_layer


def build_order_context(session_domain, db, runtime_ctx, instance) -> dict[str, Any]:
    """
    Готовит context по entity_id инстанса (заказ).
    Guards и effects читают из него данные заказа, не делая лишних запросов сами.
    """
    order_id = int(instance["entity_id"])
    order = db_layer.get_order(session_domain, order_id)
    return {
        "order": order,
        "order_id": order_id,
        "runtime_ctx": runtime_ctx,
    }

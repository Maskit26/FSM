"""Мапперы заказов Delivery ↔ Core drive API."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def to_core_drive_payload(
    start_address: str,
    dest_address: str,
    start_city: str,
    dest_city: str,
    b_options: Optional[dict[str, Any]] = None,
    kind: int = 1,
    upper: Optional[int] = None,
) -> dict[str, Any]:
    _ = start_city
    _ = dest_city
    payload: dict[str, Any] = {
        "b_start_address": start_address,
        "b_destination_address": dest_address,
        "b_payment_way": 2,
        "b_start_datetime": "any",
        "b_passengers_count": 1,
        "b_luggage_count": 0,
        "b_options": b_options or {},
        "kind": kind,
    }
    if upper is not None:
        payload["upper"] = upper
    return payload


def to_core_suborder_payload(
    start_address: str,
    dest_address: str,
    kind: int,
    upper: int,
) -> dict[str, Any]:
    return {
        "b_start_address": start_address,
        "b_destination_address": dest_address,
        "b_payment_way": 2,
        "b_start_datetime": "any",
        "kind": kind,
        "upper": upper,
    }


def from_core_order_response(
    response: dict[str, Any], core_order_id: int
) -> dict[str, Any]:
    data = response.get("data", {})
    booking_data: dict[str, Any] = {}

    if isinstance(data, dict):
        booking = data.get("booking", {})
        if isinstance(booking, dict):
            booking_data = booking.get(str(core_order_id), {}) or {}
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and str(item.get("b_id")) == str(core_order_id):
                booking_data = item
                break

    b_state = int(booking_data.get("b_state", 1))
    return {
        "b_state": b_state,
        "kind": booking_data.get("kind"),
        "upper": booking_data.get("upper"),
    }

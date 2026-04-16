# mappers/order.py

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def to_core_order_data(
    start_address: str,
    dest_address: str,
    start_city: str,
    dest_city: str,
    payment_way: int = 2,
    start_datetime: str = "any",
    passengers_count: int = 1,
    luggage_count: int = 0,
    b_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Преобразует данные заказа в формат Core API (/api/v1/drive).
    """
    data = {
        "b_start_address": start_address,
        "b_destination_address": dest_address,
        #"city_start": start_city,
        #"city_destination": dest_city,
        "b_payment_way": payment_way,
        "b_start_datetime": start_datetime,
        "b_passengers_count": passengers_count,
        "b_luggage_count": luggage_count,
    }
    if b_options:
        data["b_options"] = b_options
    return data

def to_core_drive_payload(
    start_address: str,
    dest_address: str,
    start_city: str,
    dest_city: str,
    b_options: Optional[Dict[str, Any]] = None,
    kind: int = 1,
    upper: Optional[int] = None,
) -> Dict[str, Any]:
    payload = {
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
) -> Dict[str, Any]:
    return {
        "b_start_address": start_address,
        "b_destination_address": dest_address,
        "b_payment_way": 2,
        "b_start_datetime": "any",
        "kind": kind,
        "upper": upper,
    }

def from_core_order_response(response: Dict[str, Any], core_order_id: int) -> Dict[str, Any]:
    """
    Извлекает b_state, kind, upper из ответа Core.
    Работает как с ответом от POST /drive (создание), так и с GET /drive/get/{id}.
    """
    data = response.get("data", {})
    logger.debug("from_core_order_response: data type=%s, content=%s", type(data), data)
    booking_data = {}

    if isinstance(data, dict):
        booking = data.get("booking", {})
        if isinstance(booking, dict):
            booking_data = booking.get(str(core_order_id), {})
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and str(item.get("b_id")) == str(core_order_id):
                booking_data = item
                break
    logger.info("Extracted booking_data for %s: %s", core_order_id, booking_data)
    b_state = int(booking_data.get("b_state", 1))
    kind = booking_data.get("kind")
    upper = booking_data.get("upper")
    return {"b_state": b_state, "kind": kind, "upper": upper}
# mappers/order.py

import json
from typing import Dict, Any, Optional

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
    only_offer: bool = False,
) -> Dict[str, Any]:
    """
    Преобразует данные заказа в формат Core API (/api/v1/drive).
    Если only_offer=True, то заказ создаётся в статусе 6 (предлагается водителям).
    """
    payload = {
        "b_start_address": start_address,
        "b_destination_address": dest_address,
        "b_payment_way": 2,
        "b_start_datetime": "any",
        "b_passengers_count": 1,
        "b_luggage_count": 0,
    }
    if only_offer:
        payload["b_only_offer"] = 1
    return payload
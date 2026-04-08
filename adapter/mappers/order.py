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
) -> Dict[str, Any]:
    """
    Обёртка над to_core_order_data для создания заказа в Core.
    """
    return to_core_order_data(
        start_address=start_address,
        dest_address=dest_address,
        start_city=start_city,
        dest_city=dest_city,
        payment_way=2,
        start_datetime="any",
        passengers_count=1,
        luggage_count=0,
        b_options=b_options,
    )
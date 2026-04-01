"""
Маппинг данных пользователей между Delivery и Core.
"""

import json
from typing import Dict, Any, Optional, List


# Маппинг ролей Delivery → Core
ROLE_TO_CORE = {
    "client": 1,
    "recipient": 1,
    "driver": 2,
    "courier": 2,  # Все исполнители role=2
    "admin": 3,
}


def to_core_register(
    local_user_id: int,
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    role_name: str = "client",
    performer_type: Optional[str] = None,
    transport_type: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Подготовка данных для регистрации в Core.
    
    Для исполнителей (driver/courier):
    - u_role = 2 (всегда)
    - u_details.performer.type = "driver" | "courier"
    
    Для клиентов:
    - u_role = 1
    - u_details без performer
    """
    
    # Определяем Core роль
    if role_name in ["driver", "courier"]:
        core_role = 2  # Все исполнители
        
        u_details = {
            "performer": {
                "type": performer_type or ("courier" if role_name == "courier" else "driver"),
                "transport": {
                    "type": transport_type or ("car" if role_name == "driver" else "bike"),
                },
                "capabilities": capabilities or ["delivery"],
            },
            "local_user_id": local_user_id,
            "source": "delivery_backend"
        }
    elif role_name == "admin":
        core_role = 3
        u_details = {"local_user_id": local_user_id}
    else:  # client, recipient
        core_role = 1
        u_details = {"local_user_id": local_user_id}
    
    data = {
        "u_name": name,
        "u_role": core_role,
        "data": json.dumps({"u_details": u_details}),
    }
    
    if phone:
        data["u_phone"] = phone
    if email:
        data["u_email"] = email
    
    return data


def from_core_register(core_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Разбор ответа после регистрации.
    """
    data = core_response.get("data", {})
    u_details = json.loads(data.get("u_details", "{}"))
    performer = u_details.get("performer", {})
    transport = performer.get("transport", {})
    
    return {
        "core_u_id": data.get("u_id"),
        "core_role": data.get("u_role"),
        "performer_type": performer.get("type", "client" if data.get("u_role") == 1 else "driver"),
        "transport_type": transport.get("type"),
        "capabilities": performer.get("capabilities", []),
        "token": data.get("token"),
        "u_hash": data.get("u_hash"),
    }


def get_performer_type_from_core(core_user: Dict[str, Any]) -> Optional[str]:
    """
    Извлечь performer_type из данных пользователя Core.
    """
    u_details = json.loads(core_user.get("u_details", "{}"))
    performer = u_details.get("performer", {})
    return performer.get("type")
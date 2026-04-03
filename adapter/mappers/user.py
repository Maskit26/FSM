"""
Мапперы данных пользователей между Delivery и Core.
"""
import json
from typing import Dict, Any, Optional, List
import logging
from ..exceptions import CoreMappingError, CoreValidationError

logger = logging.getLogger(__name__)

ROLE_TO_CORE = {
    "client": 1,
    "recipient": 1,
    "driver": 2,
    "courier": 2,
    "operator": 3,
    "admin": 4,
}

def to_core_register(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Преобразует данные в формат Core для регистрации (form-data)."""
    role_name = user_data.get("role_name", "client")
    core_role = ROLE_TO_CORE.get(role_name, 1)

    payload = {
        "u_name": user_data.get("name", "User"),
        "u_role": core_role,
        "st": 1,  
    }

    if user_data.get("phone"):
        payload["u_phone"] = user_data["phone"]
    if user_data.get("email"):
        payload["u_email"] = user_data["email"]

    u_details = {"source": "fsm_backend"}
    if core_role == 2:
        u_details["performer"] = {
            "type": user_data.get("performer_type", "driver"),
            "transport": {"type": user_data.get("transport_type", "car")},
            "capabilities": user_data.get("capabilities", ["delivery"]),
        }
    
    # Core принимает `data` как JSON-строку внутри form-data
    payload["data"] = json.dumps({"u_details": u_details})
    
    logger.debug("to_core_register: role=%s → core_role=%s", role_name, core_role)
    return payload


def from_core_register(core_response: Any) -> Dict[str, Any]:
    """Парсит ответ Core после регистрации."""
    if isinstance(core_response, list):
        core_response = core_response[0] if core_response else {}
        
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Core вернул неожиданный тип: {type(core_response)}")

    if core_response.get("status") == "error":
        raise CoreValidationError(f"Core error: {core_response.get('message')}")

    if core_response.get("code") and str(core_response.get("code")).startswith("4"):
        raise CoreValidationError(f"Core error {core_response.get('code')}: {core_response.get('message')}")

    data = core_response.get("data", {})
    if isinstance(data, str):
        data = json.loads(data)

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
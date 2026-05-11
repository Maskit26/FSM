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
    data_obj = {"u_details": u_details}
    if user_data.get("password"):
        data_obj["password"] = user_data["password"]

    payload["data"] = json.dumps(data_obj)
    logger.debug("to_core_register: role=%s → core_role=%s", role_name, core_role)
    return payload

def from_core_register(core_response: Any) -> Dict[str, Any]:
    if isinstance(core_response, list):
        core_response = core_response[0] if core_response else {}
    if not isinstance(core_response, dict):
        logger.error("Неожиданный тип ответа Core: %s", type(core_response))
        raise CoreMappingError(f"Неожиданный тип ответа: {type(core_response)}")

    if core_response.get("status") == "error":
        error_msg = core_response.get("message", "Unknown error")
        logger.error("Core вернул ошибку: %s", error_msg)
        raise CoreValidationError(f"Ошибка Core: {error_msg}")

    data = core_response.get("data", {})
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error("Ошибка парсинга data JSON: %s", e)
            raise CoreMappingError(f"Невалидный JSON в data: {e}")

    result = {
        "core_u_id": data.get("u_id"),
        "core_role": data.get("u_role"),
        "token": data.get("token"),
        "u_hash": data.get("u_hash"),
    }
    logger.debug("Парсинг регистрации успешен: core_u_id=%s", result["core_u_id"])
    return result

# ========================= Авторизация ===============================

def to_core_login(login: str, password: str, type: str = "phone") -> Dict[str, Any]:
    """Подготовка данных для авторизации в Core."""
    return {"login": login, "password": password, "type": type}

def from_core_login(core_response: Any) -> Dict[str, Any]:
    """Парсинг ответа Core после авторизации."""
    if isinstance(core_response, list):
        core_response = core_response[0] if core_response else {}
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Core вернул неожиданный тип: {type(core_response)}")

    if core_response.get("status") == "error":
        raise CoreValidationError(f"Core auth error: {core_response.get('message')}")
    if core_response.get("code") and str(core_response.get("code")).startswith("4"):
        raise CoreValidationError(f"Core auth error {core_response.get('code')}: {core_response.get('message')}")

    auth_user = core_response.get("auth_user", {})
    return {
        "core_u_id": auth_user.get("u_id"),
        "auth_hash": core_response.get("auth_hash"),
        "core_role": auth_user.get("u_role"),
        "user_name": auth_user.get("u_name"),
        "phone": auth_user.get("u_phone"),
    }

# =================== Создание авто ===================
def to_core_car_payload(
    registration_plate: str,
    car_type: str,
    seats: int = 1,
    custom_body_ru: Optional[str] = None,
    custom_body_en: Optional[str] = None,
    custom_make_ru: Optional[str] = None,
    custom_make_en: Optional[str] = None,
    custom_model_ru: Optional[str] = None,
    custom_model_en: Optional[str] = None,
    custom_model_year: Optional[int] = None,
    custom_model_doors: Optional[int] = None,
) -> Dict[str, Any]:
    cc_id = 4 if car_type == 'courier' else 5
    car_data = {
        "registration_plate": registration_plate,
        "seats": seats,
        "cc_id": cc_id,
        "cm_id": None,        
    }
    details = {}
    if custom_body_ru or custom_body_en:
        details["car_bodies"] = {
            "ru": custom_body_ru or "",
            "en": custom_body_en or "",
        }
    if custom_make_ru or custom_make_en:
        details["car_makes"] = {
            "ru": custom_make_ru or "",
            "en": custom_make_en or "",
        }
    if custom_model_ru or custom_model_en:
        model_details = {
            "ru": custom_model_ru or "",
            "en": custom_model_en or "",
        }
        if custom_model_year:
            model_details["year"] = custom_model_year
        if custom_model_doors is not None:
            model_details["door"] = custom_model_doors
        details["car_models"] = model_details

    if details:
        car_data["details"] = details
    return car_data

# =============== верификация пользователя =============
def to_core_user_update_payload(u_check_state: int) -> Dict[str, Any]:
    """Создать payload только с u_check_state."""
    return {"u_check_state": u_check_state}

def from_core_user_update_response(core_response: Dict[str, Any]) -> Dict[str, Any]:
    """Распарсить ответ Core после обновления пользователя."""
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Unexpected response type: {type(core_response)}")
    if core_response.get("status") != "success":
        raise CoreValidationError(f"Core error: {core_response.get('message', 'Unknown')}")
    data = core_response.get("data", {})
    return {
        "affected_fields": data.get("affected_fields", []),
        "forbidden_fields": data.get("forbidden_fields", []),
    }
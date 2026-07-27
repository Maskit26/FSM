"""Мапперы пользователей Delivery ↔ Core."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from domains.courier.core.exceptions import CoreMappingError, CoreValidationError

logger = logging.getLogger(__name__)

ROLE_TO_CORE = {
    "client": 1,
    "recipient": 1,
    "driver": 2,
    "courier": 2,
    "operator": 3,
    "admin": 4,
}


def to_core_register(user_data: dict[str, Any]) -> dict[str, Any]:
    role_name = user_data.get("role_name", "client")
    core_role = ROLE_TO_CORE.get(role_name, 1)

    payload: dict[str, Any] = {
        "u_name": user_data.get("name", "User"),
        "u_role": core_role,
        "st": 1,
    }
    if user_data.get("phone"):
        payload["u_phone"] = user_data["phone"]
    if user_data.get("email"):
        payload["u_email"] = user_data["email"]
    if user_data.get("city"):
        payload["u_city"] = user_data["city"]

    data_obj: dict[str, Any] = {"u_details": {"source": "fsm_platform"}}
    if user_data.get("password"):
        data_obj["password"] = user_data["password"]
    payload["data"] = json.dumps(data_obj, ensure_ascii=False)
    return payload


def from_core_register(core_response: Any) -> dict[str, Any]:
    if isinstance(core_response, list):
        core_response = core_response[0] if core_response else {}
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Unexpected response type: {type(core_response)}")

    if core_response.get("status") == "error":
        raise CoreValidationError(str(core_response.get("message") or "Core error"))

    data = core_response.get("data", {})
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise CoreMappingError(f"Invalid data JSON: {exc}") from exc

    return {
        "core_u_id": data.get("u_id"),
        "core_role": data.get("u_role"),
        "token": data.get("token"),
        "u_hash": data.get("u_hash"),
    }


def to_core_login(login: str, password: str, type: str = "phone") -> dict[str, Any]:
    return {"login": login, "password": password, "type": type}


def from_core_login(core_response: Any) -> dict[str, Any]:
    if isinstance(core_response, list):
        core_response = core_response[0] if core_response else {}
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Unexpected response type: {type(core_response)}")

    if core_response.get("status") == "error":
        raise CoreValidationError(str(core_response.get("message") or "auth error"))
    code = core_response.get("code")
    if code and str(code).startswith("4"):
        raise CoreValidationError(
            f"Core auth {code}: {core_response.get('message')}"
        )

    auth_user = core_response.get("auth_user", {}) or {}
    return {
        "core_u_id": auth_user.get("u_id"),
        "auth_hash": core_response.get("auth_hash"),
        "core_role": auth_user.get("u_role"),
        "user_name": auth_user.get("u_name"),
        "phone": auth_user.get("u_phone"),
        "city": auth_user.get("u_city"),
    }


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
) -> dict[str, Any]:
    cc_id = 4 if car_type == "courier" else 5
    car_data: dict[str, Any] = {
        "registration_plate": registration_plate,
        "seats": seats,
        "cc_id": cc_id,
        "cm_id": None,
    }
    details: dict[str, Any] = {}
    if custom_body_ru or custom_body_en:
        details["car_bodies"] = {"ru": custom_body_ru or "", "en": custom_body_en or ""}
    if custom_make_ru or custom_make_en:
        details["car_makes"] = {"ru": custom_make_ru or "", "en": custom_make_en or ""}
    if custom_model_ru or custom_model_en:
        model_details: dict[str, Any] = {
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


def to_core_user_update_payload(u_check_state: int) -> dict[str, Any]:
    return {"u_check_state": u_check_state}


def from_core_user_update_response(core_response: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(core_response, dict):
        raise CoreMappingError(f"Unexpected response type: {type(core_response)}")
    if core_response.get("status") != "success":
        raise CoreValidationError(
            str(core_response.get("message") or "Unknown")
        )
    data = core_response.get("data", {}) or {}
    return {
        "affected_fields": data.get("affected_fields", []),
        "forbidden_fields": data.get("forbidden_fields", []),
    }

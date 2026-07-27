"""Sync user flows: register / login / logout / create_car."""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from domains.courier import db_layer
from domains.courier.core import client as core_client
from domains.courier.core.exceptions import (
    CoreAuthError,
    CoreError,
    CoreMappingError,
    CoreValidationError,
)
from domains.courier.core.mappers.user import (
    ROLE_TO_CORE,
    from_core_login,
    from_core_register,
    to_core_car_payload,
    to_core_login,
    to_core_register,
)

logger = logging.getLogger(__name__)


def _resolve_city_name(city_id: Any) -> Optional[str]:
    if city_id is None or str(city_id).strip() == "":
        return None
    cities = core_client.get_cache_cities()
    info = cities.get(str(city_id))
    if isinstance(info, dict):
        name = info.get("1")
        if name:
            return str(name)
    return str(city_id)


def register_user(session: Session, user_data: dict[str, Any]) -> dict[str, Any]:
    """Core register → local user → core_user_mapping (+ tokens)."""
    role_name = str(user_data.get("role_name") or "client")
    payload = to_core_register(user_data)
    response = core_client.register(payload)
    parsed = from_core_register(response)
    core_u_id = parsed.get("core_u_id")
    if not core_u_id:
        raise CoreValidationError("Core register did not return u_id")

    local_user_id = db_layer.create_user_record(
        session,
        phone=str(user_data["phone"]),
        name=str(user_data.get("name") or "User"),
        role_name=role_name,
        city=user_data.get("city"),
    )
    core_role = 2 if role_name in ("courier", "driver") else int(
        ROLE_TO_CORE.get(role_name, 1)
    )
    db_layer.create_user_core_mapping(
        session,
        user_id=local_user_id,
        core_u_id=int(core_u_id),
        core_role=core_role,
    )
    token, u_hash = parsed.get("token"), parsed.get("u_hash")
    if token and u_hash:
        db_layer.update_user_core_tokens(session, int(core_u_id), str(token), str(u_hash))

    return {
        "local_user_id": local_user_id,
        "core_u_id": int(core_u_id),
        "role_name": role_name,
    }


def _get_or_create_local(
    session: Session, core_u_id: int, auth_data: dict[str, Any]
) -> int:
    existing = db_layer.get_local_user_id_by_core_u_id(session, core_u_id)
    if existing:
        return existing

    core_role = int(auth_data.get("core_role") or 1)
    if core_role == 2:
        local_role = "driver"
    elif core_role == 3:
        local_role = "operator"
    else:
        local_role = "client"

    city_name = _resolve_city_name(auth_data.get("city")) or "Неизвестен"
    local_user_id = db_layer.create_user_record(
        session,
        phone=str(auth_data.get("phone") or auth_data.get("login") or ""),
        name=str(auth_data.get("user_name") or f"User_{core_u_id}"),
        role_name=local_role,
        city=city_name,
    )
    db_layer.create_user_core_mapping(
        session,
        user_id=local_user_id,
        core_u_id=core_u_id,
        core_role=core_role,
    )
    return local_user_id


def login_user(
    session: Session,
    *,
    login: str,
    password: str,
    type: str = "phone",
) -> dict[str, Any]:
    auth_data = from_core_login(core_client.auth(to_core_login(login, password, type)))
    core_u_id = int(auth_data["core_u_id"])
    auth_hash = auth_data.get("auth_hash")
    if not auth_hash:
        raise CoreAuthError("Missing auth_hash")

    token_data = core_client.get_token(str(auth_hash))
    if token_data.get("status") != "success":
        raise CoreAuthError(str(token_data.get("message") or "get_token failed"))
    data = token_data.get("data") or {}
    if isinstance(data, list):
        data = data[0] if data else {}
    token = data.get("token")
    u_hash = data.get("u_hash")
    if not token or not u_hash:
        raise CoreAuthError("Missing token/u_hash")

    local_user_id = _get_or_create_local(session, core_u_id, auth_data)
    db_layer.update_user_core_tokens(session, core_u_id, str(token), str(u_hash))

    car_ids = core_client.list_user_cars(core_u_id, str(token), str(u_hash))
    if car_ids:
        db_layer.update_car_core_id(session, local_user_id, int(car_ids[0]))

    return {
        "local_user_id": local_user_id,
        "core_u_id": core_u_id,
        "role": auth_data.get("core_role"),
    }


def logout_user(session: Session, local_user_id: int) -> dict[str, Any]:
    token, u_hash = db_layer.get_user_tokens(session, int(local_user_id))
    if not token or not u_hash:
        raise CoreAuthError("No active tokens for user")
    result = core_client.logout(str(token), str(u_hash))
    db_layer.clear_user_u_hash(session, int(local_user_id))
    return {"ok": True, "core": result}


def create_car_for_user(
    session: Session,
    *,
    local_user_id: Optional[int] = None,
    core_u_id: Optional[int] = None,
    car_type: str = "courier",
    seats: int = 1,
) -> dict[str, Any]:
    if core_u_id is None and local_user_id is not None:
        core_u_id = db_layer.get_core_u_id_by_local_user_id(session, int(local_user_id))
    if core_u_id is None:
        raise CoreMappingError("User not mapped to Core")
    core_u_id = int(core_u_id)

    if local_user_id is None:
        local_user_id = db_layer.get_local_user_id_by_core_u_id(session, core_u_id)
    if not local_user_id:
        raise CoreMappingError(f"Core user {core_u_id} not mapped locally")
    local_user_id = int(local_user_id)

    if db_layer.get_car_core_id(session, local_user_id):
        raise CoreMappingError("User already has a car")

    token, u_hash = db_layer.get_user_core_tokens(session, core_u_id)
    if not token or not u_hash:
        raise CoreAuthError(f"Missing tokens for core_u_id {core_u_id}")

    prefix = "BIKE" if car_type == "courier" else "CAR"
    plate = f"{prefix}-{core_u_id}"
    car_data = to_core_car_payload(
        registration_plate=plate, car_type=car_type, seats=seats
    )
    response = core_client.create_car(str(token), str(u_hash), core_u_id, car_data)
    if response.get("status") != "success":
        raise CoreValidationError(
            str(response.get("message") or "create_car failed")
        )
    created = (response.get("data") or {}).get("created_car") or {}
    # legacy typo cteated_car
    if not created:
        created = (response.get("data") or {}).get("cteated_car") or {}
    core_car_id = created.get("c_id")
    if not core_car_id:
        raise CoreError("CORE_CAR_ID_MISSING", "Core did not return car id")
    db_layer.update_car_core_id(session, local_user_id, int(core_car_id))
    return {
        "local_user_id": local_user_id,
        "core_u_id": core_u_id,
        "car_core_id": int(core_car_id),
        "registration_plate": plate,
    }


def verify_user(
    session: Session,
    *,
    target_local_user_id: int,
    new_check_state: int,
    admin_local_user_id: int,
) -> dict[str, Any]:
    """Обновить u_check_state в Core от имени админа."""
    from domains.courier.core.mappers.user import (
        from_core_user_update_response,
        to_core_user_update_payload,
    )

    target_core_u_id = db_layer.get_core_u_id_by_local_user_id(
        session, int(target_local_user_id)
    )
    if not target_core_u_id:
        raise CoreMappingError(
            f"Target user {target_local_user_id} not mapped to Core"
        )

    admin_core_u_id = db_layer.get_core_u_id_by_local_user_id(
        session, int(admin_local_user_id)
    )
    if not admin_core_u_id:
        raise CoreAuthError(
            f"Admin user {admin_local_user_id} not mapped to Core"
        )

    admin_token, admin_u_hash = db_layer.get_user_core_tokens(
        session, int(admin_core_u_id)
    )
    if not admin_token or not admin_u_hash:
        raise CoreAuthError(
            f"Missing tokens for admin core_u_id {admin_core_u_id}"
        )

    response = core_client.update_user(
        int(target_core_u_id),
        str(admin_token),
        str(admin_u_hash),
        to_core_user_update_payload(int(new_check_state)),
    )
    parsed = from_core_user_update_response(response)
    logger.info(
        "verify_user target_local=%s core=%s state=%s affected=%s",
        target_local_user_id,
        target_core_u_id,
        new_check_state,
        parsed.get("affected_fields"),
    )
    return {
        "target_local_user_id": int(target_local_user_id),
        "target_core_u_id": int(target_core_u_id),
        "u_check_state": int(new_check_state),
        "affected_fields": parsed.get("affected_fields"),
        "forbidden_fields": parsed.get("forbidden_fields"),
    }

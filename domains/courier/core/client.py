"""HTTP к ibronevik Core через platform call_api (credential CORE).

base_url из секрета используется как есть (urljoin).
Пути — абсолютные path из доки форм (/taxi/api/v1/...), без rewrite base_url.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fsm_platform.host import side_effects

from domains.courier.core.exceptions import (
    CoreAuthError,
    CoreUnavailableError,
    CoreValidationError,
)

logger = logging.getLogger(__name__)

CREDENTIAL_KEY = "CORE"


def _raise_from_response(resp: side_effects.ApiResponse, endpoint: str) -> dict[str, Any]:
    if not resp.ok:
        body = (resp.text or "")[:500]
        if resp.status_code in (401, 403):
            raise CoreAuthError(f"{endpoint}: {body}")
        if resp.status_code == 400:
            raise CoreValidationError(f"{endpoint}: {body}")
        if resp.status_code >= 500:
            raise CoreUnavailableError(f"{endpoint}: HTTP {resp.status_code}")
        raise CoreUnavailableError(f"{endpoint}: HTTP {resp.status_code} {body}")

    data = resp.data
    if data is None:
        try:
            data = json.loads(resp.text) if resp.text else {}
        except json.JSONDecodeError as exc:
            raise CoreUnavailableError(f"{endpoint}: bad JSON") from exc
    if not isinstance(data, dict):
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
        raise CoreUnavailableError(f"{endpoint}: unexpected body type")
    return data


def post_form(path: str, data: dict[str, Any], *, timeout: float = 15.0) -> dict[str, Any]:
    """POST application/x-www-form-urlencoded."""
    resp = side_effects.call_api(
        CREDENTIAL_KEY,
        "POST",
        path,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=timeout,
    )
    return _raise_from_response(resp, path)


def get(
    path: str,
    *,
    params: Optional[dict[str, Any]] = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    resp = side_effects.call_api(
        CREDENTIAL_KEY,
        "GET",
        path,
        params=params,
        timeout=timeout,
    )
    return _raise_from_response(resp, path)


def register(payload: dict[str, Any]) -> dict[str, Any]:
    return post_form("/taxi/api/v1/register/", payload)


def auth(payload: dict[str, Any]) -> dict[str, Any]:
    return post_form("/taxi/api/v1/auth/", payload)


def get_token(auth_hash: str) -> dict[str, Any]:
    return post_form("/taxi/api/v1/token/", {"auth_hash": auth_hash})


def logout(token: str, u_hash: str) -> dict[str, Any]:
    return get(
        "/taxi/api/v1/logout/",
        params={"token": token, "u_hash": u_hash},
    )


def create_drive(payload: dict[str, Any], token: str, u_hash: str) -> dict[str, Any]:
    return post_form(
        "/taxi/api/v1/drive",
        {
            "data": json.dumps(payload, ensure_ascii=False),
            "token": token,
            "u_hash": u_hash,
        },
    )


def drive_action(
    b_id: int,
    form: dict[str, Any],
) -> dict[str, Any]:
    return post_form(f"/taxi/api/v1/drive/get/{int(b_id)}", form)


def perform_drive(
    core_order_id: int,
    performer_core_u_id: int,
    token: str,
    u_hash: str,
    c_id: int,
    c_payment_way: int = 2,
) -> dict[str, Any]:
    return drive_action(
        core_order_id,
        {
            "action": "set_performer",
            "u_id": performer_core_u_id,
            "performer": 1,
            "token": token,
            "u_hash": u_hash,
            "data": json.dumps(
                {"c_id": c_id, "c_payment_way": c_payment_way},
                ensure_ascii=False,
            ),
        },
    )


def cancel_drive(
    b_id: int,
    token: str,
    u_hash: str,
    *,
    reason: Optional[str] = None,
    cancel_states: Optional[str] = None,
) -> dict[str, Any]:
    form: dict[str, Any] = {
        "action": "set_cancel_state",
        "token": token,
        "u_hash": u_hash,
    }
    if reason:
        form["reason"] = reason
    if cancel_states:
        form["cancel_states"] = cancel_states
    return drive_action(b_id, form)


def complete_drive(b_id: int, token: str, u_hash: str) -> dict[str, Any]:
    return drive_action(
        b_id,
        {
            "action": "set_complete_state",
            "token": token,
            "u_hash": u_hash,
        },
    )


def get_drive(
    b_id: int,
    token: str,
    u_hash: str,
    *,
    kind: Optional[int] = None,
) -> dict[str, Any]:
    form: dict[str, Any] = {"token": token, "u_hash": u_hash}
    if kind is not None:
        form["kind"] = str(kind)
    return drive_action(b_id, form)


def create_car(
    token: str,
    u_hash: str,
    core_u_id: int,
    car_data: dict[str, Any],
) -> dict[str, Any]:
    return post_form(
        f"/taxi/api/v1/user/{int(core_u_id)}/car/",
        {
            "token": token,
            "u_hash": u_hash,
            "data": json.dumps(car_data, ensure_ascii=False),
        },
    )


def list_user_cars(core_u_id: int, token: str, u_hash: str) -> list[int]:
    response = post_form(
        f"/taxi/api/v1/user/{int(core_u_id)}/car/",
        {"token": token, "u_hash": u_hash},
    )
    if response.get("status") != "success":
        return []
    cars = (response.get("data") or {}).get("car") or {}
    if not isinstance(cars, dict):
        return []
    return [int(cid) for cid in cars.keys()]


def update_user(
    core_u_id: int,
    token: str,
    u_hash: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return post_form(
        f"/taxi/api/v1/user/{int(core_u_id)}/",
        {
            "token": token,
            "u_hash": u_hash,
            "data": json.dumps(payload, ensure_ascii=False),
        },
    )


def get_cache_cities() -> dict[str, Any]:
    """Публичный кэш городов (абсолютный URL)."""
    resp = side_effects.call_api(
        CREDENTIAL_KEY,
        "GET",
        "https://ibronevik.ru/taxi/cache/data_postamat.json",
        timeout=10.0,
        max_attempts=2,
    )
    if not resp.ok or not isinstance(resp.data, dict):
        return {}
    data = resp.data
    section = data.get("cities") or (data.get("data") or {}).get("cities")
    return section if isinstance(section, dict) else {}

"""Outbox consumer: выполнить Core op и обновить mapping (domain service)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fsm_platform.domain_runtime.session import domain_session

from domains.courier import db_layer
from domains.courier.core import client as core_client
from domains.courier.core.exceptions import (
    CoreAuthError,
    CoreError,
    CoreValidationError,
)
from domains.courier.core.mappers.order import (
    from_core_order_response,
    to_core_drive_payload,
    to_core_suborder_payload,
)

logger = logging.getLogger(__name__)


def handle_core_outbox(payload: dict[str, Any]) -> None:
    """Вызывается из domain_runtime при POST /contract/v1/outbox/deliver."""
    op = str(payload.get("op") or "").strip()
    if not op:
        raise CoreError("CORE_OP_REQUIRED", "payload.op required")

    sd = domain_session()
    try:
        if op == "create_order":
            _op_create_order(sd, payload)
        elif op == "create_suborder":
            _op_create_suborder(sd, payload)
        elif op == "assign_executor":
            _op_assign_executor(sd, payload)
        elif op == "remove_performer":
            _op_remove_performer(sd, payload)
        elif op == "cancel_main":
            _op_cancel_main(sd, payload)
        elif op == "complete_main":
            _op_complete_main(sd, payload)
        elif op == "complete_suborder":
            _op_complete_suborder(sd, payload)
        else:
            raise CoreError("CORE_OP_UNKNOWN", f"unknown op={op}")
        sd.commit()
    except Exception:
        sd.rollback()
        raise
    finally:
        sd.close()


def _client_tokens(session, local_user_id: int) -> tuple[str, str, int]:
    core_u_id = db_layer.get_core_u_id_by_local_user_id(session, int(local_user_id))
    if not core_u_id:
        raise CoreAuthError("CLIENT_NOT_MAPPED_TO_CORE")
    token, u_hash = db_layer.get_user_core_tokens(session, int(core_u_id))
    if not token or not u_hash:
        raise CoreAuthError("MISSING_CORE_TOKENS")
    return str(token), str(u_hash), int(core_u_id)


def _performer_tokens(session, local_user_id: int) -> tuple[str, str, int]:
    core_u_id = db_layer.get_core_u_id_by_local_user_id(session, int(local_user_id))
    if not core_u_id:
        raise CoreAuthError("PERFORMER_NOT_MAPPED_TO_CORE")
    token, u_hash = db_layer.get_user_core_tokens(session, int(core_u_id))
    if not token or not u_hash:
        raise CoreAuthError("MISSING_PERFORMER_TOKENS")
    return str(token), str(u_hash), int(core_u_id)


def _order_addresses(session, order: dict[str, Any]) -> tuple[str, str]:
    src = order.get("source_cell_id")
    dst = order.get("dest_cell_id")
    if not src or not dst:
        # fallback to text addresses on order
        start = str(order.get("from_address") or "")
        dest = str(order.get("to_address") or "")
        if start and dest:
            return start, dest
        raise CoreError("ORDER_ADDRESSES_MISSING", "no cell/address on order")
    return (
        db_layer.get_locker_address_by_cell(session, int(src)),
        db_layer.get_locker_address_by_cell(session, int(dst)),
    )


def _op_create_order(session, payload: dict[str, Any]) -> None:
    order_id = int(payload["local_order_id"])
    if db_layer.get_main_core_order_id(session, order_id):
        logger.info("create_order skip: main already mapped order=%s", order_id)
        # still ensure suborders if requested
        _maybe_create_leg_suborders(session, order_id, payload)
        return

    order = db_layer.get_order(session, order_id)
    if not order:
        raise CoreError("ORDER_NOT_FOUND", f"order {order_id}")

    client_user_id = int(order["client_user_id"])
    token, u_hash, _ = _client_tokens(session, client_user_id)
    start_address, dest_address = _order_addresses(session, order)
    client_city = db_layer.get_user_city(session, client_user_id)
    recipient_id = order.get("recipient_user_id")
    recipient_city = (
        db_layer.get_user_city(session, int(recipient_id))
        if recipient_id
        else client_city
    )

    b_options = {
        "parcel_type": order.get("parcel_type"),
        "cell_size": None,
        "sender_delivery": order.get("pickup_type"),
        "recipient_delivery": order.get("delivery_type"),
        "client_user_id": client_user_id,
        "recipient_user_id": recipient_id,
        "description": order.get("description"),
        "pickup_type": order.get("pickup_type"),
        "delivery_type": order.get("delivery_type"),
    }
    drive = to_core_drive_payload(
        start_address=start_address,
        dest_address=dest_address,
        start_city=client_city,
        dest_city=recipient_city,
        b_options=b_options,
        kind=1,
    )
    response = core_client.create_drive(drive, token, u_hash)
    if response.get("status") != "success":
        raise CoreValidationError(str(response.get("message") or "create drive failed"))
    core_order_id = int((response.get("data") or {})["b_id"])
    try:
        parsed = from_core_order_response(response, core_order_id)
        b_state = parsed["b_state"]
    except Exception:
        b_state = 1

    db_layer.save_core_order_mapping(
        session,
        local_order_id=order_id,
        core_order_id=core_order_id,
        role="main",
        kind=1,
        upper=None,
        b_state=b_state,
        client_local_user_id=client_user_id,
    )
    logger.info("create_order mapped local=%s core=%s", order_id, core_order_id)
    _maybe_create_leg_suborders(session, order_id, payload)


def _maybe_create_leg_suborders(
    session, order_id: int, payload: dict[str, Any]
) -> None:
    order = db_layer.get_order(session, order_id)
    if not order:
        return
    main_id = db_layer.get_main_core_order_id(session, order_id)
    if not main_id:
        return
    pickup = str(order.get("pickup_type") or payload.get("pickup_type") or "")
    delivery = str(order.get("delivery_type") or payload.get("delivery_type") or "")
    if pickup == "courier":
        _create_suborder(session, order_id, "courier1", main_id)
    if delivery == "courier":
        _create_suborder(session, order_id, "courier2", main_id)


def _create_suborder(
    session, local_order_id: int, role: str, main_core_id: int
) -> Optional[int]:
    existing = db_layer.get_suborder_core_id(
        session, local_order_id, role, main_core_id
    )
    if existing:
        return existing

    order = db_layer.get_order(session, local_order_id)
    if not order:
        raise CoreError("ORDER_NOT_FOUND", f"order {local_order_id}")
    client_local_id = int(order["client_user_id"])
    token, u_hash, _ = _client_tokens(session, client_local_id)
    start_address, dest_address = _order_addresses(session, order)
    kind = 2 if role == "driver" else 3
    payload = to_core_suborder_payload(
        start_address, dest_address, kind, main_core_id
    )
    response = core_client.create_drive(payload, token, u_hash)
    if response.get("status") != "success":
        raise CoreValidationError(
            str(response.get("message") or "create suborder failed")
        )
    core_sub_id = int((response.get("data") or {})["b_id"])
    try:
        b_state = from_core_order_response(response, core_sub_id)["b_state"]
    except Exception:
        b_state = 1
    db_layer.save_core_order_mapping(
        session,
        local_order_id=local_order_id,
        core_order_id=core_sub_id,
        role=role,
        kind=kind,
        upper=main_core_id,
        b_state=b_state,
    )
    return core_sub_id


def _op_create_suborder(session, payload: dict[str, Any]) -> None:
    _create_suborder(
        session,
        int(payload["local_order_id"]),
        str(payload["role"]),
        int(payload["main_core_id"]),
    )


def _op_assign_executor(session, payload: dict[str, Any]) -> None:
    local_order_id = int(payload["local_order_id"])
    performer_local_user_id = int(payload["performer_local_user_id"])
    role = str(payload.get("role") or "courier1")
    kind = 2 if role == "driver" else 3

    main_core_id = db_layer.get_main_core_order_id(session, local_order_id)
    if not main_core_id:
        raise CoreError("MAIN_ORDER_NOT_FOUND", "main core mapping missing")

    existing_core_id = db_layer.get_suborder_core_id(
        session, local_order_id, role, main_core_id
    )
    can_reuse = False
    if existing_core_id:
        st = db_layer.get_core_order_b_state(session, existing_core_id)
        if st == 1:
            can_reuse = True
        else:
            existing_core_id = None

    if can_reuse:
        core_order_id = int(existing_core_id)  # type: ignore[arg-type]
    else:
        created = _create_suborder(session, local_order_id, role, main_core_id)
        if not created:
            raise CoreError("SUBORDER_CREATE_FAILED", "no suborder id")
        core_order_id = int(created)

    car_core_id = db_layer.get_car_core_id(session, performer_local_user_id)
    if not car_core_id:
        raise CoreError("PERFORMER_NO_CAR", "car_core_id required")

    token, u_hash, performer_core_id = _performer_tokens(
        session, performer_local_user_id
    )
    response = core_client.perform_drive(
        core_order_id,
        performer_core_id,
        token,
        u_hash,
        c_id=int(car_core_id),
    )
    if response.get("status") != "success":
        raise CoreValidationError(
            str(response.get("message") or "set_performer failed")
        )

    data = response.get("data") or {}
    transition = str(data.get("b_state") or "")
    if "->" in transition:
        new_b_state = int(transition.split("->")[-1])
    else:
        new_b_state = db_layer.get_core_order_b_state(session, core_order_id) or 2

    db_layer.update_core_order_b_state(session, core_order_id, new_b_state)
    db_layer.save_core_order_mapping(
        session,
        local_order_id=local_order_id,
        core_order_id=core_order_id,
        role=role,
        kind=kind,
        upper=main_core_id,
        b_state=new_b_state,
        performer_local_user_id=performer_local_user_id,
    )


def _op_remove_performer(session, payload: dict[str, Any]) -> None:
    local_order_id = int(payload["local_order_id"])
    performer_local_user_id = int(payload["performer_local_user_id"])
    reason = payload.get("reason")

    core_order_id = db_layer.get_core_suborder_id_by_performer(
        session, local_order_id, performer_local_user_id
    )
    if not core_order_id:
        # fallback by role
        role = str(payload.get("role") or "")
        if role:
            row = db_layer.get_core_order_by_role(session, local_order_id, role)
            core_order_id = int(row["core_order_id"]) if row else None
    if not core_order_id:
        raise CoreError("SUBORDER_NOT_FOUND", "no suborder for performer")

    st = db_layer.get_core_order_b_state(session, int(core_order_id))
    if st == 1:
        return

    token, u_hash, _ = _performer_tokens(session, performer_local_user_id)
    core_client.cancel_drive(
        int(core_order_id), token, u_hash, reason=str(reason) if reason else None
    )
    db_layer.update_core_order_b_state(session, int(core_order_id), 1)
    db_layer.clear_core_order_performer(session, int(core_order_id))


def _op_cancel_main(session, payload: dict[str, Any]) -> None:
    local_order_id = int(payload["local_order_id"])
    user_id = int(payload["user_id"])
    reason = payload.get("reason")

    core_order_id = db_layer.get_main_core_order_id(session, local_order_id)
    if not core_order_id:
        raise CoreError("MAIN_ORDER_NOT_FOUND", "no main mapping")
    if db_layer.get_core_order_b_state(session, core_order_id) == 3:
        return

    token, u_hash, _ = _client_tokens(session, user_id)
    core_client.cancel_drive(
        core_order_id, token, u_hash, reason=str(reason) if reason else None
    )
    info = core_client.get_drive(core_order_id, token, u_hash, kind=1)
    try:
        new_b_state = from_core_order_response(info, core_order_id)["b_state"]
    except Exception:
        new_b_state = 3
    db_layer.update_core_order_b_state(session, core_order_id, new_b_state)


def _op_complete_main(session, payload: dict[str, Any]) -> None:
    local_order_id = int(payload["local_order_id"])
    core_order_id = db_layer.get_main_core_order_id(session, local_order_id)
    if not core_order_id:
        raise CoreError("MAIN_ORDER_NOT_FOUND", "no main mapping")
    if db_layer.get_core_order_b_state(session, core_order_id) == 4:
        return

    order = db_layer.get_order(session, local_order_id)
    if not order:
        raise CoreError("ORDER_NOT_FOUND", f"order {local_order_id}")
    client_local_id = int(order["client_user_id"])
    token, u_hash, _ = _client_tokens(session, client_local_id)
    core_client.complete_drive(core_order_id, token, u_hash)
    db_layer.update_core_order_b_state(session, core_order_id, 4)


def _op_complete_suborder(session, payload: dict[str, Any]) -> None:
    local_order_id = int(payload["local_order_id"])
    performer_user_id = int(payload["performer_local_user_id"])
    role = str(payload.get("role") or "").strip()

    core_order_id = db_layer.get_core_suborder_id_by_performer(
        session, local_order_id, performer_user_id
    )
    if not core_order_id and role:
        row = db_layer.get_core_order_by_role(session, local_order_id, role)
        core_order_id = int(row["core_order_id"]) if row else None
    if not core_order_id:
        raise CoreError("SUBORDER_NOT_FOUND", "no suborder")

    if db_layer.get_core_order_b_state(session, int(core_order_id)) == 4:
        return

    token, u_hash, _ = _performer_tokens(session, performer_user_id)
    core_client.complete_drive(int(core_order_id), token, u_hash)
    db_layer.update_core_order_b_state(session, int(core_order_id), 4)

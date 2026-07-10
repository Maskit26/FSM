from __future__ import annotations

from typing import Any, Dict

from fsm_core.types import GuardResult


def always_allow(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> GuardResult:
    """Default guard: transition без условий (guard_name=NULL в БД)."""
    return GuardResult(ok=True)


def is_driver(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> GuardResult:
    """Разрешить transition только если requested_user_role == driver."""
    if instance.get("requested_user_role") != "driver":
        return GuardResult(ok=False, reason="ROLE_NOT_ALLOWED: только водитель")
    return GuardResult(ok=True)


def can_cancel_driver_reservation(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> GuardResult:
    """Водитель + validate_reservation_for_cancellation перед отменой резерва."""
    role_check = is_driver(session, db, context, instance, params)
    if not role_check.ok:
        return role_check

    reservation_id = instance.get("entity_id")
    if reservation_id is None:
        return GuardResult(ok=False, reason="MISSING_ENTITY_ID")

    can_cancel, _blocked_ids, error = db.validate_reservation_for_cancellation(
        session, reservation_id
    )
    if not can_cancel:
        return GuardResult(ok=False, reason=error or "CANCEL_NOT_ALLOWED")
    return GuardResult(ok=True)


def can_create_order(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> GuardResult:
    """Проверки перед order_create: заявка валидна, маршрут, ячейки, Core."""
    request = context.get("request")
    if not request:
        return GuardResult(ok=False, reason="REQ_NOT_FOUND")

    if request.get("status") != "request_received":
        return GuardResult(ok=False, reason="REQ_NOT_IN_RECEIVED_STATE")

    client_user_id = context.get("client_user_id")
    if not client_user_id:
        return GuardResult(ok=False, reason="INVALID_DATA: client_user_id missing")

    recipient_user_id = context.get("recipient_user_id")
    if not recipient_user_id:
        return GuardResult(ok=False, reason="RECIPIENT_USER_ID_REQUIRED")

    client_city = context.get("from_city") or context.get("client_city")
    recipient_city = context.get("to_city") or context.get("recipient_city")
    if not client_city or not recipient_city:
        return GuardResult(ok=False, reason="CITY_REQUIRED")

    if client_city == recipient_city:
        return GuardResult(ok=False, reason=f"SELF_CITY_NOT_ALLOWED: {client_city}")

    cell_size = context.get("cell_size")
    if not cell_size:
        return GuardResult(ok=False, reason="CELL_SIZE_REQUIRED")

    if not db.has_free_cells_for_route(session, client_city, recipient_city, cell_size):
        return GuardResult(ok=False, reason="NO_FREE_CELLS")

    core_u_id = db.get_core_u_id_by_local_user_id(session, client_user_id)
    if not core_u_id:
        return GuardResult(ok=False, reason="CLIENT_NOT_MAPPED_TO_CORE")

    token, u_hash = db.get_user_core_tokens(session, core_u_id)
    if not token or not u_hash:
        return GuardResult(ok=False, reason="MISSING_CORE_TOKENS")

    return GuardResult(ok=True)

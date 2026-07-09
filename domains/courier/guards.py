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

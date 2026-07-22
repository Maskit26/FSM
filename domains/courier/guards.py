"""Guards домена courier: условия только из guard_params + context."""

from __future__ import annotations

from typing import Any

from fsm_platform.core.types import GuardResult

from domains.courier import db_layer


def _match_executor_edge(
    session_domain, context, instance, guard_params
) -> GuardResult:
    """
    Общая сверка context ↔ guard_params для assign/remove.
    Правила на ребре графа; Python-профилей нет.
    """
    ctx = context or {}
    params = guard_params or {}

    expected_leg = params.get("leg")
    actual_leg = str(ctx.get("leg") or expected_leg or "").strip().lower()
    if expected_leg and actual_leg != str(expected_leg).strip().lower():
        return GuardResult(
            ok=False,
            reason=f"LEG_MISMATCH:{actual_leg}!={expected_leg}",
        )
    if not actual_leg:
        return GuardResult(ok=False, reason="LEG_REQUIRED")

    executor_id = ctx.get("executor_id")
    if not executor_id:
        return GuardResult(ok=False, reason="EXECUTOR_ID_REQUIRED")

    user = ctx.get("executor")
    if user is None:
        return GuardResult(ok=False, reason="USER_NOT_FOUND")

    expected_role = params.get("user_role")
    if expected_role and str(user.get("role_name") or "") != str(expected_role):
        return GuardResult(ok=False, reason=f"ROLE_MISMATCH:{user.get('role_name')}")

    if params.get("require_city", True):
        executor_city = ctx.get("executor_city")
        if not executor_city:
            return GuardResult(ok=False, reason="EXECUTOR_CITY_REQUIRED")
        locker_city = ctx.get("locker_city")
        if not locker_city or locker_city != executor_city:
            return GuardResult(
                ok=False,
                reason=f"CITY_MISMATCH:{executor_city}->{locker_city}",
            )

    order = ctx.get("order")
    order_id = int(ctx.get("order_id") or instance["entity_id"])
    if order is None:
        return GuardResult(ok=False, reason="ORDER_NOT_FOUND")

    required_status = params.get("required_status")
    if required_status and str(order.get("status") or "") != str(required_status):
        return GuardResult(
            ok=False,
            reason=f"ORDER_NOT_AVAILABLE:{order.get('status')}",
        )

    type_field = params.get("type_field")
    type_value = params.get("type_value")
    if type_field is not None:
        if str(order.get(type_field) or "") != str(type_value):
            return GuardResult(ok=False, reason=f"ORDER_TYPE_MISMATCH:{type_field}")

    if params.get("require_cell", True) and not ctx.get("cell_id"):
        return GuardResult(ok=False, reason="CELL_MISSING")

    stage_must_be = str(params.get("stage_must_be") or "free").strip().lower()
    if stage_must_be == "free":
        if not db_layer.is_stage_slot_free(session_domain, order_id, actual_leg):
            return GuardResult(ok=False, reason="ALREADY_TAKEN")
    elif stage_must_be == "owned":
        stage_cid = ctx.get("stage_courier_id")
        if stage_cid is None:
            return GuardResult(ok=False, reason="STAGE_EMPTY")
        if int(stage_cid) != int(executor_id):
            return GuardResult(
                ok=False,
                reason=f"NOT_STAGE_OWNER:{stage_cid}!={executor_id}",
            )
    elif stage_must_be not in ("", "any", "none"):
        return GuardResult(ok=False, reason=f"UNKNOWN_STAGE_RULE:{stage_must_be}")

    return GuardResult(ok=True)


def can_assign_executor(
    session_domain, db, context, instance, guard_params
) -> GuardResult:
    """Назначение исполнителя: context ↔ guard_params (обычно stage_must_be=free)."""
    _ = db
    return _match_executor_edge(session_domain, context, instance, guard_params)


def can_remove_executor(
    session_domain, db, context, instance, guard_params
) -> GuardResult:
    """
    Снятие исполнителя: те же ключи params, обычно stage_must_be=owned
    и required_status=order_courier*_assigned.
    """
    _ = db
    return _match_executor_edge(session_domain, context, instance, guard_params)


def can_open_cell(
    session_domain, db, context, instance, guard_params
) -> GuardResult:
    """
    Открытие ячейки: role/leg/status/type + ownership + PIN + статус ячейки.
    Правила на ребре (guard_params).
    """
    _ = db
    ctx = context or {}
    params = guard_params or {}

    expected_leg = params.get("leg")
    actual_leg = str(ctx.get("leg") or expected_leg or "").strip().lower()
    if expected_leg and actual_leg != str(expected_leg).strip().lower():
        return GuardResult(
            ok=False,
            reason=f"LEG_MISMATCH:{actual_leg}!={expected_leg}",
        )
    if not actual_leg:
        return GuardResult(ok=False, reason="LEG_REQUIRED")

    actor_id = ctx.get("executor_id")
    if not actor_id:
        return GuardResult(ok=False, reason="ACTOR_ID_REQUIRED")

    user = ctx.get("executor")
    if user is None:
        return GuardResult(ok=False, reason="USER_NOT_FOUND")

    expected_role = params.get("user_role")
    if expected_role and str(user.get("role_name") or "") != str(expected_role):
        return GuardResult(ok=False, reason=f"ROLE_MISMATCH:{user.get('role_name')}")

    if params.get("require_city", True):
        actor_city = ctx.get("executor_city")
        if not actor_city:
            return GuardResult(ok=False, reason="ACTOR_CITY_REQUIRED")
        locker_city = ctx.get("locker_city")
        if not locker_city or locker_city != actor_city:
            return GuardResult(
                ok=False,
                reason=f"CITY_MISMATCH:{actor_city}->{locker_city}",
            )

    order = ctx.get("order")
    order_id = int(ctx.get("order_id") or instance["entity_id"])
    if order is None:
        return GuardResult(ok=False, reason="ORDER_NOT_FOUND")

    required_status = params.get("required_status")
    if required_status and str(order.get("status") or "") != str(required_status):
        return GuardResult(
            ok=False,
            reason=f"ORDER_NOT_AVAILABLE:{order.get('status')}",
        )

    type_field = params.get("type_field")
    type_value = params.get("type_value")
    if type_field is not None:
        if str(order.get(type_field) or "") != str(type_value):
            return GuardResult(ok=False, reason=f"ORDER_TYPE_MISMATCH:{type_field}")

    cell_id = ctx.get("cell_id")
    if params.get("require_cell", True) and not cell_id:
        return GuardResult(ok=False, reason="CELL_MISSING")

    actor_field = params.get("actor_field")
    if actor_field:
        owner_id = order.get(actor_field)
        if owner_id is None or int(owner_id) != int(actor_id):
            return GuardResult(
                ok=False,
                reason=f"NOT_ORDER_ACTOR:{actor_field}",
            )

    stage_must_be = str(params.get("stage_must_be") or "none").strip().lower()
    if stage_must_be == "free":
        if not db_layer.is_stage_slot_free(session_domain, order_id, actual_leg):
            return GuardResult(ok=False, reason="ALREADY_TAKEN")
    elif stage_must_be == "owned":
        stage_cid = ctx.get("stage_courier_id")
        if stage_cid is None:
            return GuardResult(ok=False, reason="STAGE_EMPTY")
        if int(stage_cid) != int(actor_id):
            return GuardResult(
                ok=False,
                reason=f"NOT_STAGE_OWNER:{stage_cid}!={actor_id}",
            )
    elif stage_must_be not in ("", "any", "none"):
        return GuardResult(ok=False, reason=f"UNKNOWN_STAGE_RULE:{stage_must_be}")

    allowed = params.get("allowed_cell_statuses")
    if allowed is None:
        allowed = ["locker_reserved", "locker_occupied"]
    if allowed:
        cell_status = ctx.get("cell_status")
        if cell_status not in set(allowed):
            return GuardResult(
                ok=False,
                reason=f"CELL_STATUS:{cell_status}",
            )

    if params.get("require_pin", True):
        pin = ctx.get("pin")
        if not pin:
            return GuardResult(ok=False, reason="MISSING_PIN")
        ok, err = db_layer.validate_access_code(
            session_domain,
            order_id,
            actual_leg,
            int(actor_id),
            str(pin),
            int(cell_id),
        )
        if not ok:
            return GuardResult(ok=False, reason=err or "INVALID_ACCESS_CODE")

    return GuardResult(ok=True)

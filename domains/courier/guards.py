"""Guards домена courier: условия только из guard_params + context."""

from __future__ import annotations

from typing import Any, Optional

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


def _match_locker_actor_edge(
    session_domain, context, instance, guard_params
) -> GuardResult:
    """
    Context ↔ params для open/close_cell / request|view PIN.
    Роль, ownership, status, cell, PIN — только из context + params.
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
        locker_city = ctx.get("locker_city")
        # Как old check_user_access: режем только явный mismatch.
        # Пустой city у актёра не блокирует (сиды/удалённый client).
        if actor_city and locker_city and actor_city != locker_city:
            return GuardResult(
                ok=False,
                reason=f"CITY_MISMATCH:{actor_city}->{locker_city}",
            )

    order = ctx.get("order")
    order_id = int(ctx.get("order_id") or instance["entity_id"])
    if order is None:
        return GuardResult(ok=False, reason="ORDER_NOT_FOUND")

    allowed_statuses = params.get("allowed_statuses")
    required_status = params.get("required_status")
    status = str(order.get("status") or "")
    if allowed_statuses is not None:
        if status not in {str(s) for s in allowed_statuses}:
            return GuardResult(ok=False, reason=f"ORDER_NOT_AVAILABLE:{status}")
    elif required_status and status != str(required_status):
        return GuardResult(ok=False, reason=f"ORDER_NOT_AVAILABLE:{status}")

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

    allowed_cells = params.get("allowed_cell_statuses")
    if allowed_cells is not None:
        if ctx.get("cell_status") not in set(allowed_cells):
            return GuardResult(
                ok=False,
                reason=f"CELL_STATUS:{ctx.get('cell_status')}",
            )

    if params.get("require_pin", False):
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
    """Открытие ячейки: params с ребра (+ PIN / cell status по умолчанию)."""
    _ = db
    params = dict(guard_params or {})
    if "require_pin" not in params:
        params["require_pin"] = True
    if "allowed_cell_statuses" not in params:
        params["allowed_cell_statuses"] = ["locker_reserved", "locker_occupied"]
    if "stage_must_be" not in params:
        params["stage_must_be"] = "none"
    return _match_locker_actor_edge(session_domain, context, instance, params)


def can_close_cell(
    session_domain, db, context, instance, guard_params
) -> GuardResult:
    """Закрытие ячейки: как open, но без PIN; ячейка обычно locker_opened."""
    _ = db
    params = dict(guard_params or {})
    if "require_pin" not in params:
        params["require_pin"] = False
    if "allowed_cell_statuses" not in params:
        params["allowed_cell_statuses"] = [
            "locker_opened",
            "locker_parcel_confirmed",
        ]
    if "stage_must_be" not in params:
        params["stage_must_be"] = "none"
    return _match_locker_actor_edge(session_domain, context, instance, params)


# Декларативные правила выдачи/просмотра PIN (аналог рёбер графа для sync-ops).
_LOCKER_ACCESS_CODE_RULES: list[dict[str, Any]] = [
    {
        "leg": "pickup",
        "user_role": "client",
        "actor_field": "client_user_id",
        "type_field": "pickup_type",
        "type_value": "self",
        "stage_must_be": "none",
        # PIN можно запросить удалённо (как в old: пустой city не режет geo)
        "require_city": False,
        "require_cell": True,
        "require_pin": False,
        "allowed_statuses": [
            "order_created",
            "order_courier1_assigned",
            "order_parcel_confirmed",
        ],
    },
    {
        "leg": "pickup",
        "user_role": "courier",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": True,
        "require_cell": True,
        "require_pin": False,
        "allowed_statuses": [
            "order_created",
            "order_courier1_assigned",
            "order_parcel_confirmed",
        ],
    },
    {
        "leg": "delivery",
        "user_role": "courier",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": True,
        "require_cell": True,
        "require_pin": False,
        "allowed_statuses": [
            "order_in_transit_to_post2",
            "order_courier2_assigned",
            "order_courier2_parcel_delivered",
            "order_parcel_confirmed_post2",
        ],
    },
    {
        "leg": "delivery",
        "user_role": "recipient",
        "actor_field": "recipient_user_id",
        "stage_must_be": "none",
        "require_city": False,
        "require_cell": True,
        "require_pin": False,
        "allowed_statuses": [
            "order_in_transit_to_post2",
            "order_courier2_assigned",
            "order_courier2_parcel_delivered",
            "order_parcel_confirmed_post2",
        ],
    },
]


def can_request_locker_access_code(
    session_domain, db, context, instance, guard_params=None
) -> GuardResult:
    """
    Выдача/просмотр PIN: первый подходящий rule по context.leg + role.
    Без if/elif по роли в command — только context ↔ declarative rules.
    """
    _ = db
    if guard_params:
        return _match_locker_actor_edge(
            session_domain, context, instance, guard_params
        )

    ctx = context or {}
    leg = str(ctx.get("leg") or "").strip().lower()
    actor_role = str(((ctx.get("executor") or {}).get("role_name")) or "")
    role_hit: Optional[GuardResult] = None
    other: Optional[GuardResult] = None
    for rule in _LOCKER_ACCESS_CODE_RULES:
        if rule.get("leg") and str(rule["leg"]) != leg:
            continue
        result = _match_locker_actor_edge(
            session_domain, context, instance, rule
        )
        if result.ok:
            return result
        expected = str(rule.get("user_role") or "")
        if expected and actor_role and expected == actor_role:
            if role_hit is None:
                role_hit = result
        elif other is None:
            other = result
    return role_hit or other or GuardResult(ok=False, reason="NO_ACCESS_RULE_MATCHED")

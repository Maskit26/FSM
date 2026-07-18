"""Effects after platform TransitionExecutor.apply."""

from __future__ import annotations

from fsm_platform.types import EffectResult

from domains.courier import db_layer


def sync_order_status(session_domain, db, context, instance, effect_params) -> EffectResult:
    """Denormalize FSM to_state into orders.status (legacy column)."""
    order_id = int(instance["entity_id"])
    to_state = (effect_params or {}).get("to_state") or (context or {}).get("to_state")
    # Prefer payload from runner via effect_params; fallback: read nothing — require param
    if not to_state:
        # TransitionRunner does not pass to_state in effect_params from graph;
        # graph effect_params may be null — use instance payload hint or skip.
        to_state = (instance.get("payload_json") or {}).get("expected_to_state")
    if not to_state:
        # Read from context if effect registered wrapper sets it — else sync from graph via db facade
        order = db_layer.get_order(session_domain, order_id)
        if order is None:
            return EffectResult(ok=False, error="ORDER_NOT_FOUND")
        return EffectResult(ok=True, payload={"skipped": True, "reason": "no_to_state"})

    db_layer.update_order_status(session_domain, order_id, str(to_state))
    return EffectResult(ok=True, payload={"order_id": order_id, "status": to_state})


def assign_courier1_effect(session_domain, db, context, instance, effect_params) -> EffectResult:
    """After order_created → order_courier1_assigned: sync business status."""
    order_id = int(instance["entity_id"])
    db_layer.update_order_status(session_domain, order_id, "order_courier1_assigned")
    return EffectResult(
        ok=True,
        payload={"order_id": order_id, "status": "order_courier1_assigned"},
    )

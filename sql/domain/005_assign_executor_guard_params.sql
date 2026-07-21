-- Full rules on the edge (guard_params), not Python profiles.

UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
SET
    t.guard_name = 'can_assign_executor',
    t.guard_params = CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_created",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "free",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    t.effect_name = 'assign_executor_effect',
    t.effect_params = CAST('{"leg":"pickup"}' AS JSON)
WHERE a.name = 'assign_executor'
  AND fs.name = 'order_created';

UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
SET
    t.guard_name = 'can_assign_executor',
    t.guard_params = CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_parcel_confirmed_post2",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "free",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    t.effect_name = 'assign_executor_effect',
    t.effect_params = CAST('{"leg":"delivery"}' AS JSON)
WHERE a.name = 'assign_executor'
  AND fs.name = 'order_parcel_confirmed_post2';

UPDATE fsm_transitions
SET
    guard_name = 'can_assign_executor',
    guard_params = CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_created",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "free",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    effect_name = 'assign_executor_effect',
    effect_params = CAST('{"leg":"pickup"}' AS JSON)
WHERE id = 130;

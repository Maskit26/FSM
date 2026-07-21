-- Unified remove_executor (mirror of assign_executor): one event, chains via guard_params.

INSERT INTO fsm_actions (name, label)
SELECT 'remove_executor', 'Snyat ispolnitelya'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'remove_executor');

-- courier1 refuse: order_courier1_assigned -> order_created (back to exchange)
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_remove_executor',
    'remove_executor_effect',
    100,
    CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_courier1_assigned",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    CAST('{"leg":"pickup"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_created'
JOIN fsm_actions a ON a.name = 'remove_executor'
WHERE fs.name = 'order_courier1_assigned'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'remove_executor'
        AND xfs.name = 'order_courier1_assigned'
  );

-- courier2 refuse: order_courier2_assigned -> order_arrived_at_post2
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_remove_executor',
    'remove_executor_effect',
    100,
    CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_courier2_assigned",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    CAST('{"leg":"delivery"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_arrived_at_post2'
JOIN fsm_actions a ON a.name = 'remove_executor'
WHERE fs.name = 'order_courier2_assigned'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'remove_executor'
        AND xfs.name = 'order_courier2_assigned'
  );

-- Unified assign_executor event for courier domain (guard-selected chains).
-- Keeps legacy actions order_assign_courier*_to_order for old main.py.

INSERT INTO fsm_actions (name, label)
SELECT 'assign_executor', 'Naznachit ispolnitelya'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'assign_executor');

-- courier1: order_created -> order_courier1_assigned
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_assign_executor',
    'assign_executor_effect',
    100,
    CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_created",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "free",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    CAST('{"leg":"pickup"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_courier1_assigned'
JOIN fsm_actions a ON a.name = 'assign_executor'
WHERE fs.name = 'order_created'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'assign_executor'
        AND xfs.name = 'order_created'
  );

-- courier2: order_parcel_confirmed_post2 -> order_courier2_assigned
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_assign_executor',
    'assign_executor_effect',
    100,
    CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_parcel_confirmed_post2",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "free",
        "require_city": true,
        "require_cell": true
    }' AS JSON),
    CAST('{"leg":"delivery"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_courier2_assigned'
JOIN fsm_actions a ON a.name = 'assign_executor'
WHERE fs.name = 'order_parcel_confirmed_post2'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'assign_executor'
        AND xfs.name = 'order_parcel_confirmed_post2'
  );

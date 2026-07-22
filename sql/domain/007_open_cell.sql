-- Unified open_cell: courier pickup/delivery + client self-drop.
-- Event open_cell; chains via guard_params. PIN required on all edges.

INSERT INTO fsm_actions (name, label)
SELECT 'open_cell', 'Otkryt yacheyku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'open_cell');

-- client self pickup: order_created -> order_client_post1
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_open_cell',
    'open_cell_effect',
    100,
    CAST('{
        "leg": "pickup",
        "user_role": "client",
        "required_status": "order_created",
        "type_field": "pickup_type",
        "type_value": "self",
        "actor_field": "client_user_id",
        "stage_must_be": "none",
        "require_city": true,
        "require_cell": true,
        "require_pin": true,
        "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]
    }' AS JSON),
    CAST('{"leg":"pickup"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_client_post1'
JOIN fsm_actions a ON a.name = 'open_cell'
WHERE fs.name = 'order_created'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'open_cell'
        AND xfs.name = 'order_created'
  );

-- courier1: order_courier1_assigned -> order_courier_has_parcel
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_open_cell',
    'open_cell_effect',
    100,
    CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_courier1_assigned",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true,
        "require_pin": true,
        "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]
    }' AS JSON),
    CAST('{"leg":"pickup"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_courier_has_parcel'
JOIN fsm_actions a ON a.name = 'open_cell'
WHERE fs.name = 'order_courier1_assigned'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'open_cell'
        AND xfs.name = 'order_courier1_assigned'
  );

-- courier2: order_courier2_assigned -> order_courier2_has_parcel
INSERT INTO fsm_transitions (
    entity_type, from_state_id, to_state_id, action_id,
    guard_name, effect_name, priority, guard_params, effect_params
)
SELECT
    'order',
    fs.id,
    ts.id,
    a.id,
    'can_open_cell',
    'open_cell_effect',
    100,
    CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_courier2_assigned",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true,
        "require_pin": true,
        "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]
    }' AS JSON),
    CAST('{"leg":"delivery"}' AS JSON)
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_courier2_has_parcel'
JOIN fsm_actions a ON a.name = 'open_cell'
WHERE fs.name = 'order_courier2_assigned'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions xa ON xa.id = t.action_id
      JOIN fsm_states xfs ON xfs.id = t.from_state_id
      WHERE t.entity_type = 'order'
        AND xa.name = 'open_cell'
        AND xfs.name = 'order_courier2_assigned'
  );

-- open_cell: reuse existing order edges; delete duplicate open_cell rows;
-- wire guards/effects + companions → locker_open_locker.

INSERT INTO fsm_actions (name, label)
SELECT 'open_cell', 'Otkryt yacheyku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'open_cell');

-- Remove duplicate open_cell transitions (same from/to as legacy edges).
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name = 'open_cell'
  AND fs.name IN (
      'order_created',
      'order_courier1_assigned',
      'order_courier2_assigned'
  );

-- client self: order_created -> order_client_post1 (was order_client_deliv_post1)
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'open_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_open_cell',
    t.effect_name = 'open_cell_effect',
    t.guard_params = CAST('{
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
    t.effect_params = CAST('{
        "leg": "pickup",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_open_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_client_deliv_post1'
  AND fs.name = 'order_created'
  AND ts.name = 'order_client_post1';

-- courier1: order_courier1_assigned -> order_courier_has_parcel
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'open_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_open_cell',
    t.effect_name = 'open_cell_effect',
    t.guard_params = CAST('{
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
    t.effect_params = CAST('{
        "leg": "pickup",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_open_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_courier_pickup_parcel'
  AND fs.name = 'order_courier1_assigned'
  AND ts.name = 'order_courier_has_parcel';

-- courier2: order_courier2_assigned -> order_courier2_has_parcel
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'open_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_open_cell',
    t.effect_name = 'open_cell_effect',
    t.guard_params = CAST('{
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
    t.effect_params = CAST('{
        "leg": "delivery",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_open_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_courier2_pickup_parcel'
  AND fs.name = 'order_courier2_assigned'
  AND ts.name = 'order_courier2_has_parcel';

-- locker graph: sync domain mirror after FSM apply
UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
SET
    t.effect_name = 'sync_locker_cell_status',
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'locker'
  AND a.name = 'locker_open_locker'
  AND (t.effect_name IS NULL OR t.effect_name = '' OR t.effect_name = 'sync_locker_cell_status');

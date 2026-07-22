-- close_cell: reuse existing order edges, wire guards/effects + companions
-- locker_close_locker (deposit) / locker_close_pickup (take-out).

INSERT INTO fsm_actions (name, label)
SELECT 'close_cell', 'Zakryt yacheyku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'close_cell');

-- Remove duplicate close_cell transitions (same from as legacy edges).
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name = 'close_cell'
  AND fs.name IN (
      'order_client_post1',
      'order_courier_has_parcel',
      'order_courier2_has_parcel'
  );

-- client self: order_client_post1 -> order_parcel_confirmed (was order_confirm_parcel_in)
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'close_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_close_cell',
    t.effect_name = 'close_cell_effect',
    t.guard_params = CAST('{
        "leg": "pickup",
        "user_role": "client",
        "required_status": "order_client_post1",
        "type_field": "pickup_type",
        "type_value": "self",
        "actor_field": "client_user_id",
        "stage_must_be": "none",
        "require_city": true,
        "require_cell": true,
        "require_pin": false,
        "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]
    }' AS JSON),
    t.effect_params = CAST('{
        "leg": "pickup",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_close_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_confirm_parcel_in'
  AND fs.name = 'order_client_post1'
  AND ts.name = 'order_parcel_confirmed';

-- courier1 pickup: order_courier_has_parcel -> order_parcel_confirmed
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'close_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_close_cell',
    t.effect_name = 'close_cell_effect',
    t.guard_params = CAST('{
        "leg": "pickup",
        "user_role": "courier",
        "required_status": "order_courier_has_parcel",
        "type_field": "pickup_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true,
        "require_pin": false,
        "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]
    }' AS JSON),
    t.effect_params = CAST('{
        "leg": "pickup",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_close_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_confirm_parcel_in'
  AND fs.name = 'order_courier_has_parcel'
  AND ts.name = 'order_parcel_confirmed';

-- courier2 delivery: order_courier2_has_parcel -> order_courier2_parcel_delivered
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'close_cell'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_close_cell',
    t.effect_name = 'close_cell_effect',
    t.guard_params = CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_courier2_has_parcel",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_city": true,
        "require_cell": true,
        "require_pin": false,
        "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]
    }' AS JSON),
    t.effect_params = CAST('{
        "leg": "delivery",
        "companions": [
            {
                "entity_type": "locker",
                "event_name": "locker_close_pickup",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_courier2_delivered_parcel'
  AND fs.name = 'order_courier2_has_parcel'
  AND ts.name = 'order_courier2_parcel_delivered';

-- locker graph: sync domain mirror after close companions
UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
SET
    t.effect_name = 'sync_locker_cell_status',
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'locker'
  AND a.name IN ('locker_close_locker', 'locker_close_pickup');

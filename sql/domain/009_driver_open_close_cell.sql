-- Driver open/close via order (same processes as client/courier).
-- pickup: parcel_confirmed -> parcel_submitted -> picked_up_from_post1
-- delivery: in_transit -> arrived_at_post2 -> parcel_confirmed_post2

INSERT INTO fsm_actions (name, label)
SELECT 'open_cell', 'Otkryt yacheyku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'open_cell');

INSERT INTO fsm_actions (name, label)
SELECT 'close_cell', 'Zakryt yacheyku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'close_cell');

INSERT INTO fsm_actions (name, label)
SELECT 'locker_close_pickup', 'Zakryt posle zabora'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'locker_close_pickup');

-- Remove prior driver open/close dupes if re-applied
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name IN ('open_cell', 'close_cell')
  AND fs.name IN (
      'order_parcel_confirmed',
      'order_parcel_submitted',
      'order_in_transit_to_post2',
      'order_arrived_at_post2'
  )
  AND JSON_UNQUOTE(JSON_EXTRACT(t.guard_params, '$.user_role')) = 'driver';

-- open pickup: order_parcel_confirmed -> order_parcel_submitted
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
        "user_role": "driver",
        "required_status": "order_parcel_confirmed",
        "stage_must_be": "driver_reserved",
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
  AND old_a.name = 'order_parcel_submitted'
  AND fs.name = 'order_parcel_confirmed'
  AND ts.name = 'order_parcel_submitted';

-- close pickup: order_parcel_submitted -> order_picked_up_from_post1
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
        "user_role": "driver",
        "required_status": "order_parcel_submitted",
        "stage_must_be": "driver_reserved",
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
                "event_name": "locker_close_pickup",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_pickup_by_voditel'
  AND fs.name = 'order_parcel_submitted'
  AND ts.name = 'order_picked_up_from_post1';

-- open delivery: order_in_transit_to_post2 -> order_arrived_at_post2
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
        "user_role": "driver",
        "required_status": "order_in_transit_to_post2",
        "stage_must_be": "driver_reserved",
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
  AND old_a.name = 'order_arrive_at_post2'
  AND fs.name = 'order_in_transit_to_post2'
  AND ts.name = 'order_arrived_at_post2';

-- close delivery: order_arrived_at_post2 -> order_parcel_confirmed_post2
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
        "user_role": "driver",
        "required_status": "order_arrived_at_post2",
        "stage_must_be": "driver_reserved",
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
                "event_name": "locker_close_locker",
                "entity_id_key": "cell_id"
            }
        ]
    }' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name = 'order_confirm_post2'
  AND fs.name = 'order_arrived_at_post2'
  AND ts.name = 'order_parcel_confirmed_post2';

-- ensure locker_close_pickup from opened has sync effect
UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
SET
    t.effect_name = 'sync_locker_cell_status',
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'locker'
  AND a.name IN ('locker_close_pickup', 'locker_close_locker', 'locker_open_locker');

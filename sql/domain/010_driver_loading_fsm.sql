-- Wire driver_reservations loading edges to platform processes/guards/effects.

INSERT INTO fsm_actions (name, label)
SELECT 'start_loading', 'Nachat pogruzku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'start_loading');

INSERT INTO fsm_actions (name, label)
SELECT 'complete_loading', 'Zavershit pogruzku'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'complete_loading');

-- start_loading: reservation_active -> reservation_loading
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'start_loading'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_start_loading',
    t.effect_name = 'sync_reservation_status',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "reservation_active"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'driver_reservations'
  AND old_a.name IN ('driver_reservation_start_loading', 'start_loading')
  AND fs.name = 'reservation_active'
  AND ts.name = 'reservation_loading';

-- complete_loading: reservation_loading -> reservation_completed
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'complete_loading'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_complete_loading',
    t.effect_name = 'sync_reservation_status',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "reservation_loading"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'driver_reservations'
  AND old_a.name IN ('driver_reservation_complete_loading', 'complete_loading')
  AND fs.name = 'reservation_loading'
  AND ts.name = 'reservation_completed';

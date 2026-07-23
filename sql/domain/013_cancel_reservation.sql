-- Wire driver reservation cancel (return orders to direction pool).
-- Edges: reservation_active|loading → reservation_cancelled.

INSERT INTO fsm_states (name, label)
SELECT 'reservation_cancelled', 'Rezerv otmenyon'
WHERE NOT EXISTS (SELECT 1 FROM fsm_states WHERE name = 'reservation_cancelled');

INSERT INTO fsm_actions (name, label)
SELECT 'cancel_reservation', 'Otmenit rezerv'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'cancel_reservation');

INSERT INTO fsm_actions (name, label)
SELECT 'driver_reservation_cancel', 'Otmenit rezerv (legacy)'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'driver_reservation_cancel');

-- Prefer platform event name cancel_reservation on existing cancel edges.
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'cancel_reservation'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_cancel_reservation',
    t.effect_name = 'cancel_reservation_effect',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "reservation_active"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'driver_reservations'
  AND old_a.name IN ('driver_reservation_cancel', 'cancel_reservation')
  AND fs.name = 'reservation_active'
  AND ts.name = 'reservation_cancelled';

UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'cancel_reservation'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_cancel_reservation',
    t.effect_name = 'cancel_reservation_effect',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "reservation_loading"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'driver_reservations'
  AND old_a.name IN ('driver_reservation_cancel', 'cancel_reservation')
  AND fs.name = 'reservation_loading'
  AND ts.name = 'reservation_cancelled';

-- Insert edges if dump never had them.
INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'driver_reservations',
    fs.id,
    a.id,
    ts.id,
    'can_cancel_reservation',
    'cancel_reservation_effect',
    CAST('{
        "user_role": "driver",
        "required_status": "reservation_active"
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'reservation_cancelled'
JOIN fsm_actions a ON a.name = 'cancel_reservation'
WHERE fs.name = 'reservation_active'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'driver_reservations'
        AND ta.name = 'cancel_reservation'
        AND tfs.name = 'reservation_active'
        AND tts.name = 'reservation_cancelled'
  );

INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'driver_reservations',
    fs.id,
    a.id,
    ts.id,
    'can_cancel_reservation',
    'cancel_reservation_effect',
    CAST('{
        "user_role": "driver",
        "required_status": "reservation_loading"
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'reservation_cancelled'
JOIN fsm_actions a ON a.name = 'cancel_reservation'
WHERE fs.name = 'reservation_loading'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'driver_reservations'
        AND ta.name = 'cancel_reservation'
        AND tfs.name = 'reservation_loading'
        AND tts.name = 'reservation_cancelled'
  );

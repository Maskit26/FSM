-- Driver delivery at post2 + complete_trip.
-- Order edges already exist (009); only fix require_city for traveling driver.
-- Trip edge exists: trip_in_progress --trip_complete_trip--> trip_completed (id~135).

INSERT INTO fsm_actions (name, label)
SELECT 'complete_trip', 'Zavershit reys'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'complete_trip');

-- Delivery open/close: driver is on the road (city may differ from home city).
UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
SET
    t.guard_params = JSON_SET(
        COALESCE(t.guard_params, CAST('{}' AS JSON)),
        '$.require_city',
        false
    )
WHERE t.entity_type = 'order'
  AND a.name IN ('open_cell', 'close_cell')
  AND JSON_UNQUOTE(JSON_EXTRACT(t.guard_params, '$.user_role')) = 'driver'
  AND JSON_UNQUOTE(JSON_EXTRACT(t.guard_params, '$.leg')) = 'delivery'
  AND fs.name IN ('order_in_transit_to_post2', 'order_arrived_at_post2');

-- Prefer platform event name complete_trip on existing trip_complete_trip edge.
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'complete_trip'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_complete_trip',
    t.effect_name = 'sync_trip_status',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "trip_in_progress"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'trip'
  AND old_a.name IN ('trip_complete_trip', 'complete_trip')
  AND fs.name = 'trip_in_progress'
  AND ts.name = 'trip_completed';

INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'trip',
    fs.id,
    a.id,
    ts.id,
    'can_complete_trip',
    'sync_trip_status',
    CAST('{
        "user_role": "driver",
        "required_status": "trip_in_progress"
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'trip_completed'
JOIN fsm_actions a ON a.name = 'complete_trip'
WHERE fs.name = 'trip_in_progress'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'trip'
        AND ta.name IN ('complete_trip', 'trip_complete_trip')
        AND tfs.name = 'trip_in_progress'
        AND tts.name = 'trip_completed'
  );

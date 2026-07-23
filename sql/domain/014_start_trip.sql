-- Wire trip start + order transit to platform processes/guards/effects.
-- Edges (already in dump):
--   trip: trip_assigned --start_trip--> trip_in_progress
--   order: order_picked_up_from_post1 --start_order_transit--> order_in_transit_to_post2

INSERT INTO fsm_actions (name, label)
SELECT 'start_trip', 'Nachat reys'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'start_trip');

INSERT INTO fsm_actions (name, label)
SELECT 'start_order_transit', 'Zakaz v tranzit'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'start_order_transit');

-- Prefer platform event name start_trip on existing trip_start_trip edge.
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'start_trip'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_start_trip',
    t.effect_name = 'sync_trip_status',
    t.guard_params = CAST('{
        "user_role": "driver",
        "required_status": "trip_assigned"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'trip'
  AND old_a.name IN ('trip_start_trip', 'start_trip')
  AND fs.name = 'trip_assigned'
  AND ts.name = 'trip_in_progress';

-- Prefer platform event name start_order_transit on existing order edge.
UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'start_order_transit'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_start_order_transit',
    t.effect_name = 'sync_order_status',
    t.guard_params = CAST('{
        "required_status": "order_picked_up_from_post1"
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name IN ('order_start_transit', 'start_order_transit')
  AND fs.name = 'order_picked_up_from_post1'
  AND ts.name = 'order_in_transit_to_post2';

-- Insert edges if dump never had them.
INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'trip',
    fs.id,
    a.id,
    ts.id,
    'can_start_trip',
    'sync_trip_status',
    CAST('{
        "user_role": "driver",
        "required_status": "trip_assigned"
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'trip_in_progress'
JOIN fsm_actions a ON a.name = 'start_trip'
WHERE fs.name = 'trip_assigned'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'trip'
        AND ta.name = 'start_trip'
        AND tfs.name = 'trip_assigned'
        AND tts.name = 'trip_in_progress'
  );

INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'order',
    fs.id,
    a.id,
    ts.id,
    'can_start_order_transit',
    'sync_order_status',
    CAST('{
        "required_status": "order_picked_up_from_post1"
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_in_transit_to_post2'
JOIN fsm_actions a ON a.name = 'start_order_transit'
WHERE fs.name = 'order_picked_up_from_post1'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'order'
        AND ta.name = 'start_order_transit'
        AND tfs.name = 'order_picked_up_from_post1'
        AND tts.name = 'order_in_transit_to_post2'
  );

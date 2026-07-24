-- Client self-pickup at post2 (order party recipient_user_id) + courier2 confirm PIN.
-- Remap legacy order edges to platform process names; wire guards/effects.
-- users.role_name for receivers is client (see also 019).

INSERT INTO fsm_actions (name, label)
SELECT 'confirm_courier2_delivery', 'Podtverdit dostavku kurierom2'
WHERE NOT EXISTS (SELECT 1 FROM fsm_actions WHERE name = 'confirm_courier2_delivery');

-- ---------------------------------------------------------------------------
-- 1) Recipient self: open_cell
--    order_parcel_confirmed_post2 -> order_delivered_to_client
--    (was order_pickup_poluchatel)
-- ---------------------------------------------------------------------------
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name = 'open_cell'
  AND fs.name = 'order_parcel_confirmed_post2';

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
        "user_role": "client",
        "required_status": "order_parcel_confirmed_post2",
        "type_field": "delivery_type",
        "type_value": "self",
        "actor_field": "recipient_user_id",
        "stage_must_be": "none",
        "require_city": true,
        "require_cell": true,
        "require_pin": true,
        "allowed_cell_statuses": ["locker_reserved", "locker_occupied", "locker_parcel_confirmed"]
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
  AND old_a.name = 'order_pickup_poluchatel'
  AND fs.name = 'order_parcel_confirmed_post2'
  AND ts.name = 'order_delivered_to_client';

-- ---------------------------------------------------------------------------
-- 2) Recipient self: close_cell
--    order_delivered_to_client -> order_completed
--    (was order_delivered_parcel)
-- ---------------------------------------------------------------------------
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name = 'close_cell'
  AND fs.name = 'order_delivered_to_client';

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
        "user_role": "client",
        "required_status": "order_delivered_to_client",
        "type_field": "delivery_type",
        "type_value": "self",
        "actor_field": "recipient_user_id",
        "stage_must_be": "none",
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
  AND old_a.name = 'order_delivered_parcel'
  AND fs.name = 'order_delivered_to_client'
  AND ts.name = 'order_completed';

-- ---------------------------------------------------------------------------
-- 3) Courier2: confirm_courier2_delivery
--    order_courier2_parcel_delivered -> order_completed
--    (was order_recipient_confirmed)
-- ---------------------------------------------------------------------------
DELETE t
FROM fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
WHERE t.entity_type = 'order'
  AND a.name = 'confirm_courier2_delivery'
  AND fs.name = 'order_courier2_parcel_delivered';

UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions old_a ON old_a.id = t.action_id
JOIN fsm_actions new_a ON new_a.name = 'confirm_courier2_delivery'
SET
    t.action_id = new_a.id,
    t.guard_name = 'can_confirm_courier2_delivery',
    t.effect_name = 'confirm_courier2_delivery_effect',
    t.guard_params = CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_courier2_parcel_delivered",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_pin": true
    }' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'order'
  AND old_a.name IN ('order_recipient_confirmed', 'confirm_courier2_delivery')
  AND fs.name = 'order_courier2_parcel_delivered'
  AND ts.name = 'order_completed';

INSERT INTO fsm_transitions (
    entity_type, from_state_id, action_id, to_state_id,
    guard_name, effect_name, guard_params, effect_params, priority
)
SELECT
    'order',
    fs.id,
    a.id,
    ts.id,
    'can_confirm_courier2_delivery',
    'confirm_courier2_delivery_effect',
    CAST('{
        "leg": "delivery",
        "user_role": "courier",
        "required_status": "order_courier2_parcel_delivered",
        "type_field": "delivery_type",
        "type_value": "courier",
        "stage_must_be": "owned",
        "require_pin": true
    }' AS JSON),
    CAST('{}' AS JSON),
    100
FROM fsm_states fs
JOIN fsm_states ts ON ts.name = 'order_completed'
JOIN fsm_actions a ON a.name = 'confirm_courier2_delivery'
WHERE fs.name = 'order_courier2_parcel_delivered'
  AND NOT EXISTS (
      SELECT 1
      FROM fsm_transitions t
      JOIN fsm_actions ta ON ta.id = t.action_id
      JOIN fsm_states tfs ON tfs.id = t.from_state_id
      JOIN fsm_states tts ON tts.id = t.to_state_id
      WHERE t.entity_type = 'order'
        AND ta.name IN ('confirm_courier2_delivery', 'order_recipient_confirmed')
        AND tfs.name = 'order_courier2_parcel_delivered'
        AND tts.name = 'order_completed'
  );

-- locker companions already sync via 007/008/009; ensure close_pickup sync
UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
SET
    t.effect_name = 'sync_locker_cell_status',
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'locker'
  AND a.name IN ('locker_close_locker', 'locker_close_pickup', 'locker_open_locker')
  AND (t.effect_name IS NULL OR t.effect_name = '' OR t.effect_name = 'sync_locker_cell_status');

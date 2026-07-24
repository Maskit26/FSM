-- Recipient is an order party (recipient_user_id), not users.role_name.
-- End-users who receive parcels are clients; remap guard_params on edges.

UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
SET t.guard_params = CAST('{
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
}' AS JSON)
WHERE t.entity_type = 'order'
  AND a.name = 'open_cell'
  AND fs.name = 'order_parcel_confirmed_post2'
  AND JSON_UNQUOTE(JSON_EXTRACT(t.guard_params, '$.actor_field')) = 'recipient_user_id';

UPDATE fsm_transitions t
JOIN fsm_actions a ON a.id = t.action_id
JOIN fsm_states fs ON fs.id = t.from_state_id
SET t.guard_params = CAST('{
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
}' AS JSON)
WHERE t.entity_type = 'order'
  AND a.name = 'close_cell'
  AND fs.name = 'order_delivered_to_client'
  AND JSON_UNQUOTE(JSON_EXTRACT(t.guard_params, '$.actor_field')) = 'recipient_user_id';

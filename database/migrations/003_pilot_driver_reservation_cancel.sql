-- Pilot declarative process: driver_reservation_cancel
-- Apply in testdb after entity_type is populated on fsm_transitions.

UPDATE fsm_transitions ft
JOIN fsm_actions fa ON fa.id = ft.action_id
SET
    ft.guard_name = 'can_cancel_driver_reservation',
    ft.effect_name = 'release_orders_on_reservation_cancel',
    ft.priority = 100
WHERE ft.entity_type = 'driver_reservations'
  AND fa.name = 'driver_reservation_cancel';

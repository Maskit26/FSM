-- Platform DB: сброс runtime FSM для тестового service_id.
-- Не трогает domain_services / registry.
--
-- Запускать ПОСЛЕ (или вместе с) domain CALL clear_test_data().
-- Иначе domain «чистый», а entity_fsm_state помнит locker_occupied / order_* —
-- и следующий create/open падает с NO_CANDIDATE_TRANSITIONS.

-- при необходимости поменяй service_id
SET @svc := 'svc_courier_01';

DELETE FROM fsm_timers
 WHERE service_id = @svc;

DELETE FROM fsm_schedules
 WHERE service_id = @svc;

DELETE FROM fsm_transition_logs
 WHERE service_id = @svc;

DELETE FROM server_fsm_instances
 WHERE service_id = @svc;

DELETE FROM entity_fsm_state
 WHERE service_id = @svc;

-- опционально idempotency
DELETE FROM idempotency_keys
 WHERE service_id = @svc;

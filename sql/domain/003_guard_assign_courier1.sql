-- Bind guard can_assign_courier1 to pickup assign transition.
UPDATE fsm_transitions
SET guard_name = 'can_assign_courier1'
WHERE id = 130;

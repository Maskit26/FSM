-- Wire locker_free → locker_reserved (locker_reserve_cell) to platform process.
-- Edge already exists in domain dump; attach guard + effect.

UPDATE fsm_transitions t
JOIN fsm_states fs ON fs.id = t.from_state_id
JOIN fsm_states ts ON ts.id = t.to_state_id
JOIN fsm_actions a ON a.id = t.action_id
SET
    t.guard_name = 'can_reserve_locker_cell',
    t.effect_name = 'reserve_locker_cell_effect',
    t.guard_params = CAST('{}' AS JSON),
    t.effect_params = CAST('{}' AS JSON)
WHERE t.entity_type = 'locker'
  AND a.name = 'locker_reserve_cell'
  AND fs.name = 'locker_free'
  AND ts.name = 'locker_reserved';

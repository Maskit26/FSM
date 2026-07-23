-- LEGACY: domain-side FSM apply (старый monolith).
-- В новой FSM Platform переходы делает TransitionRunner + platform entity_fsm_state.
-- Процедура нужна только если что-то ещё вызывает CALL fsm_perform_transition
-- или для ручной отладки статусов в domain-таблицах.
--
-- Источник: database/dump-testdb-202607091457.sql
-- В dump-domain-courier-importable.sql процедур не было — поэтому «пропали».

DROP PROCEDURE IF EXISTS fsm_perform_transition;

DELIMITER ;;
CREATE PROCEDURE fsm_perform_transition(
    IN p_entity_type VARCHAR(50),
    IN p_entity_id INT,
    IN p_transition_id INT,
    IN p_event_name VARCHAR(100),
    IN p_user_id INT
)
BEGIN
    DECLARE v_transition_entity_type VARCHAR(100);
    DECLARE v_event_name VARCHAR(100);
    DECLARE v_from_state_id INT;
    DECLARE v_to_state_id INT;
    DECLARE v_from_state_name VARCHAR(50);
    DECLARE v_to_state_name VARCHAR(50);
    DECLARE v_current_state_name VARCHAR(50);
    DECLARE v_now DATETIME;

    SET v_now = UTC_TIMESTAMP();

    SELECT
        ft.entity_type,
        fa.name,
        ft.from_state_id,
        ft.to_state_id,
        fs_from.name,
        fs_to.name
    INTO
        v_transition_entity_type,
        v_event_name,
        v_from_state_id,
        v_to_state_id,
        v_from_state_name,
        v_to_state_name
    FROM fsm_transitions ft
    JOIN fsm_actions fa ON fa.id = ft.action_id
    JOIN fsm_states fs_from ON fs_from.id = ft.from_state_id
    JOIN fsm_states fs_to ON fs_to.id = ft.to_state_id
    WHERE ft.id = p_transition_id;

    IF v_from_state_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transition not found';
    END IF;

    IF v_transition_entity_type <> p_entity_type THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transition entity_type mismatch';
    END IF;

    IF v_event_name <> p_event_name THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transition event_name mismatch';
    END IF;

    IF p_entity_type = 'locker' THEN
        SELECT status INTO v_current_state_name
        FROM locker_cells WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'order' THEN
        SELECT status INTO v_current_state_name
        FROM orders WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'trip' THEN
        SELECT status INTO v_current_state_name
        FROM trips WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'driver_reservations' THEN
        SELECT status INTO v_current_state_name
        FROM driver_reservations WHERE id = p_entity_id;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Unsupported entity_type in fsm_perform_transition';
    END IF;

    IF v_current_state_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Entity not found';
    END IF;

    IF v_current_state_name <> v_from_state_name THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Current state does not match transition.from_state';
    END IF;

    IF p_entity_type = 'locker' THEN
        UPDATE locker_cells SET status = v_to_state_name WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'order' THEN
        UPDATE orders SET status = v_to_state_name WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'trip' THEN
        UPDATE trips SET status = v_to_state_name WHERE id = p_entity_id;
    ELSEIF p_entity_type = 'driver_reservations' THEN
        UPDATE driver_reservations SET status = v_to_state_name WHERE id = p_entity_id;
    END IF;

    INSERT INTO fsm_action_logs (
        entity_type, entity_id, action_name, transition_id,
        from_state, to_state, user_id, created_at
    )
    VALUES (
        p_entity_type, p_entity_id, p_event_name, p_transition_id,
        v_from_state_name, v_to_state_name, p_user_id, v_now
    );

    SELECT CONCAT(
        'FSM transition completed: ', v_from_state_name, ' -> ', v_to_state_name
    ) AS result;
END;;
DELIMITER ;

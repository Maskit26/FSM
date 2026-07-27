-- Domain DB: полный сброс хвостов тестовых прогонов courier.
-- Справочники НЕ трогаем: users, lockers, строки locker_cells, граф fsm_*.
--
-- Схема locker_cells (importable dump):
--   id, locker_id, cell_code, cell_type, status, current_order_id, current_request_id, …
--
-- После CALL — обязательно platform: sql/platform/003_clear_test_runtime.sql

DROP PROCEDURE IF EXISTS clear_test_data;

DELIMITER ;;
CREATE PROCEDURE clear_test_data()
BEGIN
    DELETE FROM cell_access_tokens;

    DELETE FROM stage_orders;
    DELETE FROM driver_reservations;
    DELETE FROM directions;
    DELETE FROM trips;

    DELETE FROM orders;
    DELETE FROM order_requests;

    UPDATE locker_cells
    SET
        status = 'locker_free',
        current_order_id = NULL,
        current_request_id = NULL,
        updated_at = UTC_TIMESTAMP();
END;;
DELIMITER ;

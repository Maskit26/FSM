-- Поля заявки order_requests для резерва ячеек до create_order.
-- Apply: python scripts/apply_sql.py --db domain sql/domain/021_order_requests_for_hold.sql
-- Затем: python scripts/apply_sql.py --db domain sql/domain/012_clear_test_data.sql

ALTER TABLE order_requests
    ADD COLUMN from_address VARCHAR(512) NULL AFTER recipient_delivery,
    ADD COLUMN to_address VARCHAR(512) NULL AFTER from_address,
    ADD COLUMN source_cell_id BIGINT NULL AFTER to_address,
    ADD COLUMN dest_cell_id BIGINT NULL AFTER source_cell_id,
    ADD COLUMN expires_at DATETIME NULL AFTER dest_cell_id;

-- Устаревшая колонка current_hold_id (если была) → current_request_id.
ALTER TABLE locker_cells
    CHANGE COLUMN current_hold_id current_request_id BIGINT NULL
        COMMENT 'active order_requests.id while reserved before order bind';

DROP TABLE IF EXISTS cell_holds;

-- Retry policy for server_fsm_instances (Block 1)
-- Apply:
--   python scripts/apply_sql.py --db platform sql/platform/005_instance_retry.sql
--
-- Adds next_attempt_at + claim index. Re-run safe (duplicate → SKIP).

ALTER TABLE server_fsm_instances
    ADD COLUMN next_attempt_at DATETIME NULL
        COMMENT 'PENDING retry not before this UTC time'
        AFTER attempts;

ALTER TABLE server_fsm_instances
    ADD INDEX idx_instances_claim (status, next_attempt_at, id);

-- Platform: pin graph version on in-flight instances + periodic schedules.

SET @col_exists := (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'server_fsm_instances'
      AND column_name = 'graph_version'
);
SET @sql := IF(
    @col_exists = 0,
    'ALTER TABLE server_fsm_instances ADD COLUMN graph_version INT NULL COMMENT ''pinned domain graph version at enqueue'' AFTER actor_id',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS fsm_schedules (
    id                BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id        VARCHAR(64)  NOT NULL,
    process_name      VARCHAR(128) NOT NULL,
    entity_type       VARCHAR(128) NOT NULL DEFAULT 'schedule',
    entity_id         BIGINT       NOT NULL DEFAULT 0,
    interval_seconds  INT          NOT NULL,
    payload_json      JSON         NULL,
    next_run_at       DATETIME     NOT NULL,
    status            VARCHAR(32)  NOT NULL DEFAULT 'ACTIVE',
    last_error        TEXT         NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_schedules_due (status, next_run_at, id),
    KEY idx_schedules_service (service_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

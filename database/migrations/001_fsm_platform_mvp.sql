-- FSM Platform MVP migration.
-- Keeps legacy fsm_actions / fsm_action_logs and fsm_perform_action intact.

SET @db_name = DATABASE();

-- server_fsm_instances.service
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'server_fsm_instances'
      AND column_name = 'service'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE server_fsm_instances ADD COLUMN service VARCHAR(50) NOT NULL DEFAULT ''courier'' AFTER id',
    'SELECT ''server_fsm_instances.service already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- fsm_transitions declarative metadata
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'fsm_transitions'
      AND column_name = 'guard_name'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN guard_name VARCHAR(100) NULL AFTER action_id',
    'SELECT ''fsm_transitions.guard_name already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'fsm_transitions'
      AND column_name = 'guard_params'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN guard_params JSON NULL AFTER guard_name',
    'SELECT ''fsm_transitions.guard_params already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'fsm_transitions'
      AND column_name = 'priority'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN priority INT NOT NULL DEFAULT 100 AFTER guard_params',
    'SELECT ''fsm_transitions.priority already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'fsm_transitions'
      AND column_name = 'effect_name'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN effect_name VARCHAR(100) NULL AFTER priority',
    'SELECT ''fsm_transitions.effect_name already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = @db_name
      AND table_name = 'fsm_transitions'
      AND column_name = 'effect_params'
);
SET @ddl = IF(
    @column_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN effect_params JSON NULL AFTER effect_name',
    'SELECT ''fsm_transitions.effect_params already exists'''
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS core_outbox (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload_json JSON NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    attempts_count INT NOT NULL DEFAULT 0,
    next_retry_at DATETIME NULL,
    last_error TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME NULL,
    INDEX ix_core_outbox_status_retry (status, next_retry_at),
    INDEX ix_core_outbox_service_event (service, event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fsm_timers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    fire_at DATETIME NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    payload_json JSON NULL,
    idempotency_key VARCHAR(191) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fired_at DATETIME NULL,
    cancelled_at DATETIME NULL,
    UNIQUE KEY ux_fsm_timers_idempotency (idempotency_key),
    INDEX ix_fsm_timers_ready (status, fire_at),
    INDEX ix_fsm_timers_entity (service, entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Platform DB: async saga orchestration (parent + children + fan-in).
-- Apply to PLATFORM database only.

CREATE TABLE IF NOT EXISTS fsm_sagas (
    id               BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id       VARCHAR(64)  NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'RUNNING',
    fail_policy      VARCHAR(32)  NOT NULL DEFAULT 'fail_fast',
    on_success_json  JSON         NULL,
    on_fail_json     JSON         NULL,
    payload_json     JSON         NULL,
    actor_id         BIGINT       NULL,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    finished_at      DATETIME     NULL,
    KEY idx_sagas_service_status (service_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fsm_saga_children (
    id               BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    saga_id          BIGINT       NOT NULL,
    instance_id      BIGINT       NOT NULL,
    entity_type      VARCHAR(128) NOT NULL,
    entity_id        BIGINT       NOT NULL,
    process_name     VARCHAR(128) NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    last_error       TEXT         NULL,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    finished_at      DATETIME     NULL,
    UNIQUE KEY uq_saga_child_instance (instance_id),
    KEY idx_saga_children_saga_status (saga_id, status),
    CONSTRAINT fk_saga_children_saga
        FOREIGN KEY (saga_id) REFERENCES fsm_sagas (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

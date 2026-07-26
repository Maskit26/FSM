-- Platform DB schema (v1) — §4.5 / §4.14 / §4.7.1
-- Apply to PLATFORM database only (not domain DB).

CREATE TABLE IF NOT EXISTS domain_services (
    service_id          VARCHAR(64)  NOT NULL PRIMARY KEY,
    cartridge_type      VARCHAR(64)  NOT NULL,
    version             VARCHAR(32)  NOT NULL,
    package_ref         VARCHAR(512) NULL,
    package_checksum    VARCHAR(128) NULL,
    db_secret_ref       VARCHAR(256) NOT NULL,
    pool_options_json   JSON         NULL,
    status              VARCHAR(32)  NOT NULL DEFAULT 'pending',
    validation_report   TEXT         NULL,
    activated_by        VARCHAR(128) NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS server_fsm_instances (
    id                   BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id           VARCHAR(64)  NOT NULL,
    process_name         VARCHAR(128) NOT NULL,
    entity_type          VARCHAR(128) NOT NULL,
    entity_id            BIGINT       NOT NULL,
    status               VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    attempts             INT          NOT NULL DEFAULT 0,
    next_attempt_at      DATETIME     NULL,
    last_error           TEXT         NULL,
    payload_json         JSON         NULL,
    actor_id             BIGINT       NULL,
    created_at           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at           DATETIME     NULL,
    finished_at          DATETIME     NULL,
    KEY idx_instances_status_id (status, id),
    KEY idx_instances_service (service_id),
    KEY idx_instances_claim (status, next_attempt_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS entity_fsm_state (
    service_id     VARCHAR(64)  NOT NULL,
    entity_type    VARCHAR(128) NOT NULL,
    entity_id      BIGINT       NOT NULL,
    current_state  VARCHAR(128) NOT NULL,
    updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (service_id, entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fsm_transition_logs (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id     VARCHAR(64)  NOT NULL,
    entity_type    VARCHAR(128) NOT NULL,
    entity_id      BIGINT       NOT NULL,
    from_state     VARCHAR(128) NOT NULL,
    to_state       VARCHAR(128) NOT NULL,
    event_name     VARCHAR(128) NOT NULL,
    transition_id  BIGINT       NOT NULL,
    instance_id    BIGINT       NULL,
    user_id        BIGINT       NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_log_instance_transition (instance_id, transition_id),
    KEY idx_logs_entity (service_id, entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fsm_timers (
    id               BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id       VARCHAR(64)  NOT NULL,
    entity_type      VARCHAR(128) NOT NULL,
    entity_id        BIGINT       NOT NULL,
    process_name     VARCHAR(128) NOT NULL,
    fire_at          DATETIME     NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'SCHEDULED',
    payload_json     JSON         NULL,
    idempotency_key  VARCHAR(128) NULL,
    created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at     DATETIME     NULL,
    UNIQUE KEY uq_timer_idem (service_id, idempotency_key),
    KEY idx_timers_due (status, fire_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS idempotency_keys (
    service_id     VARCHAR(64)  NOT NULL,
    scope          VARCHAR(32)  NOT NULL,
    `key`          VARCHAR(128) NOT NULL,
    instance_id    BIGINT       NULL,
    response_json  JSON         NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at     DATETIME     NULL,
    PRIMARY KEY (service_id, scope, `key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS webhook_subscriptions (
    id           BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id   VARCHAR(64)  NOT NULL,
    url          VARCHAR(1024) NOT NULL,
    secret       VARCHAR(256) NOT NULL,
    event_types  JSON         NULL,
    active       TINYINT(1)   NOT NULL DEFAULT 1,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_webhooks_service (service_id, active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS platform_events (
    id                 BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id         VARCHAR(64)  NOT NULL,
    event_type         VARCHAR(128) NOT NULL,
    instance_id        BIGINT       NULL,
    entity_type        VARCHAR(128) NULL,
    entity_id          BIGINT       NULL,
    payload_json       JSON         NULL,
    correlation_id     VARCHAR(128) NULL,
    client_request_id  VARCHAR(128) NULL,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_events_service_id (service_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS platform_outbox (
    id                BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id        VARCHAR(64)  NOT NULL,
    channel           VARCHAR(64)  NOT NULL,
    destination       VARCHAR(1024) NOT NULL,
    event_type        VARCHAR(128) NOT NULL,
    payload_json      JSON         NULL,
    status            VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    attempts          INT          NOT NULL DEFAULT 0,
    next_attempt_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    idempotency_key   VARCHAR(128) NULL,
    last_error        TEXT         NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at           DATETIME     NULL,
    UNIQUE KEY uq_outbox_idem (service_id, idempotency_key),
    KEY idx_outbox_poll (status, next_attempt_at, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS platform_reconcile_queue (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    service_id     VARCHAR(64)  NOT NULL,
    instance_id    BIGINT       NOT NULL,
    entity_type    VARCHAR(128) NOT NULL,
    entity_id      BIGINT       NOT NULL,
    from_state     VARCHAR(128) NULL,
    to_state       VARCHAR(128) NOT NULL,
    event_name     VARCHAR(128) NULL,
    transition_id  BIGINT       NOT NULL,
    payload_json   JSON         NULL,
    status         VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    attempts       INT          NOT NULL DEFAULT 0,
    last_error     TEXT         NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    done_at        DATETIME     NULL,
    UNIQUE KEY uq_reconcile_instance_transition (instance_id, transition_id),
    KEY idx_reconcile_poll (status, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

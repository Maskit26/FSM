-- Template: domain DB FSM graph (per cartridge).
-- Matches live courier domain schema (legacy: fsm_actions + action_id).
-- Platform also supports fsm_events + event_id; this file documents the
-- schema currently deployed on the domain DB.
-- Platform does NOT own this DB.

CREATE TABLE IF NOT EXISTS fsm_states (
    id               INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(50)  NOT NULL,
    timeout_seconds  INT          NULL COMMENT 'сек жизни state; NULL = без авто-таймера',
    timeout_event    VARCHAR(128) NULL COMMENT 'event_name / process event при срабатывании',
    timeout_owner    VARCHAR(16)  NULL DEFAULT 'domain' COMMENT 'domain|platform — чья политика',
    label            VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS fsm_actions (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(50)  NOT NULL,
    label VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS fsm_graph_meta (
    id               TINYINT  NOT NULL PRIMARY KEY DEFAULT 1,
    current_version  INT      NOT NULL DEFAULT 1,
    updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT IGNORE INTO fsm_graph_meta (id, current_version) VALUES (1, 1);

CREATE TABLE IF NOT EXISTS fsm_transitions (
    id             INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    entity_type    VARCHAR(100) NOT NULL,
    from_state_id  INT          NOT NULL,
    action_id      INT          NOT NULL,
    guard_name     VARCHAR(100) NULL,
    guard_params   JSON         NULL,
    priority       INT          NOT NULL DEFAULT 100,
    effect_name    VARCHAR(100) NULL,
    effect_params  JSON         NULL,
    to_state_id    INT          NOT NULL,
    graph_version  INT          NOT NULL DEFAULT 1,
    KEY from_state_id (from_state_id),
    KEY action_id (action_id),
    KEY to_state_id (to_state_id),
    KEY idx_tr_graph (entity_type, graph_version),
    CONSTRAINT fsm_transitions_ibfk_1 FOREIGN KEY (from_state_id) REFERENCES fsm_states (id),
    CONSTRAINT fsm_transitions_ibfk_2 FOREIGN KEY (action_id) REFERENCES fsm_actions (id),
    CONSTRAINT fsm_transitions_ibfk_3 FOREIGN KEY (to_state_id) REFERENCES fsm_states (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

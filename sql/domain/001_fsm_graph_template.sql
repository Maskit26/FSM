-- Template: domain DB FSM graph (per cartridge).
-- Adjust entity_type / names for your domain. Platform does NOT own this DB.

CREATE TABLE IF NOT EXISTS fsm_states (
    id          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(128) NOT NULL,
    name        VARCHAR(128) NOT NULL,
    is_initial  TINYINT(1)   NOT NULL DEFAULT 0,
    UNIQUE KEY uq_state (entity_type, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fsm_events (
    id   BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    UNIQUE KEY uq_event (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fsm_transitions (
    id             BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    entity_type    VARCHAR(128) NOT NULL,
    from_state_id  BIGINT       NOT NULL,
    to_state_id    BIGINT       NOT NULL,
    event_id       BIGINT       NOT NULL,
    guard_name     VARCHAR(128) NULL,
    guard_params   JSON         NULL,
    priority       INT          NOT NULL DEFAULT 100,
    effect_name    VARCHAR(128) NULL,
    effect_params  JSON         NULL,
    KEY idx_candidates (entity_type, from_state_id, event_id, priority, id),
    CONSTRAINT fk_tr_from FOREIGN KEY (from_state_id) REFERENCES fsm_states(id),
    CONSTRAINT fk_tr_to   FOREIGN KEY (to_state_id) REFERENCES fsm_states(id),
    CONSTRAINT fk_tr_evt  FOREIGN KEY (event_id) REFERENCES fsm_events(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

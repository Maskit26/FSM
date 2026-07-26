-- Domain: versioned FSM transitions. In-flight instances pin version at enqueue.
-- Edits: POST /v1/{service_id}/graph/publish (copy current→+1) then edit the new version;
-- do not UPDATE live edges of a version that still has PENDING/PROCESSING instances.

CREATE TABLE IF NOT EXISTS fsm_graph_meta (
    id               TINYINT      NOT NULL PRIMARY KEY DEFAULT 1,
    current_version  INT          NOT NULL DEFAULT 1,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO fsm_graph_meta (id, current_version) VALUES (1, 1);

SET @col_exists := (
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'fsm_transitions'
      AND column_name = 'graph_version'
);
SET @sql := IF(
    @col_exists = 0,
    'ALTER TABLE fsm_transitions ADD COLUMN graph_version INT NOT NULL DEFAULT 1, ADD KEY idx_tr_graph (entity_type, graph_version)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE fsm_transitions SET graph_version = 1 WHERE graph_version IS NULL OR graph_version = 0;

-- Platform DB: optional graph DB credential refs (read / write) per tenant.
-- Apply to PLATFORM database only.

ALTER TABLE domain_services
    ADD COLUMN db_graph_secret_ref VARCHAR(256) NULL
        COMMENT 'Env key or URL: read-only access to fsm_states/fsm_transitions/fsm_graph_meta/fsm_actions'
        AFTER db_secret_ref,
    ADD COLUMN db_graph_write_secret_ref VARCHAR(256) NULL
        COMMENT 'Env key or URL: INSERT/UPDATE on graph tables only (graph/publish)'
        AFTER db_graph_secret_ref;

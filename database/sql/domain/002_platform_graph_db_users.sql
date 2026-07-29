-- Domain DB: MySQL users for platform graph access (read + publish).
-- Apply on DOMAIN database (e.g. courier), NOT on platform DB.
--
-- IMPORTANT — managed MySQL (Clever Cloud, RDS without admin, etc.):
-- The addon/application user usually does NOT have CREATE USER / GRANT.
-- Error 1227 "Access denied; you need CREATE USER privilege" is expected.
-- Options:
--   A) Skip for now: do not set DOMAIN_GRAPH_* env — platform uses DOMAIN_DATABASE_URL
--      (fallback in code). Safe for pilot until Contract API remote migration.
--   B) Self-hosted MySQL or DBA admin account: run this script as root/admin.
--   C) Clever Cloud: no table-level GRANT via UI; separate addon = separate DB
--      (not useful for same graph tables). Isolation then relies on Contract API
--      + platform code not reading business tables.
--
-- Replace before running (self-hosted / admin only):
--   your_domain_db   — database name
--   CHANGE_ME_ro/rw  — passwords
--   @host            — '%' or specific host
--
-- Platform env (after apply):
--   DOMAIN_GRAPH_DATABASE_URL=mysql+mysqlconnector://fsm_graph_ro:PASS@host:3306/your_domain_db
--   DOMAIN_GRAPH_WRITE_DATABASE_URL=mysql+mysqlconnector://fsm_graph_rw:PASS@host:3306/your_domain_db
--
-- domain_services (platform DB):
--   db_graph_secret_ref        = 'graph_database_url'       -- key in domain_secrets
--   db_graph_write_secret_ref  = 'graph_write_database_url' -- key in domain_secrets
-- URLs живут в domain_secrets, не в platform .env.
-- Онбординг: domain_services refs + PUT /v1/{service_id}/secrets
--   db_graph_secret_ref        = DOMAIN_GRAPH_DATABASE_URL
--   db_graph_write_secret_ref  = DOMAIN_GRAPH_WRITE_DATABASE_URL

-- ---------------------------------------------------------------------------
-- Read-only: SELECT on graph tables only
-- ---------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'fsm_graph_ro'@'%' IDENTIFIED BY 'CHANGE_ME_ro';
GRANT SELECT ON `your_domain_db`.fsm_states TO 'fsm_graph_ro'@'%';
GRANT SELECT ON `your_domain_db`.fsm_transitions TO 'fsm_graph_ro'@'%';
GRANT SELECT ON `your_domain_db`.fsm_graph_meta TO 'fsm_graph_ro'@'%';
GRANT SELECT ON `your_domain_db`.fsm_actions TO 'fsm_graph_ro'@'%';
-- If domain uses fsm_events instead of fsm_actions:
-- GRANT SELECT ON `your_domain_db`.fsm_events TO 'fsm_graph_ro'@'%';

-- ---------------------------------------------------------------------------
-- Graph publish: SELECT + INSERT/UPDATE on graph tables (no business tables)
-- ---------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'fsm_graph_rw'@'%' IDENTIFIED BY 'CHANGE_ME_rw';
GRANT SELECT, INSERT, UPDATE ON `your_domain_db`.fsm_states TO 'fsm_graph_rw'@'%';
GRANT SELECT, INSERT, UPDATE ON `your_domain_db`.fsm_transitions TO 'fsm_graph_rw'@'%';
GRANT SELECT, INSERT, UPDATE ON `your_domain_db`.fsm_graph_meta TO 'fsm_graph_rw'@'%';
GRANT SELECT, INSERT, UPDATE ON `your_domain_db`.fsm_actions TO 'fsm_graph_rw'@'%';
-- GRANT SELECT, INSERT, UPDATE ON `your_domain_db`.fsm_events TO 'fsm_graph_rw'@'%';

FLUSH PRIVILEGES;

-- Verify (as admin):
-- SHOW GRANTS FOR 'fsm_graph_ro'@'%';
-- SHOW GRANTS FOR 'fsm_graph_rw'@'%';

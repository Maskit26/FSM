-- Декларативные таймауты состояния (граф).
-- Platform читает timeout_seconds + timeout_event после apply и ставит fsm_timers.
-- timeout_owner: domain | platform
-- Apply: python scripts/apply_sql.py --db domain sql/domain/022_state_timeouts.sql
--
-- Пример (не применяется автоматически):
--   UPDATE fsm_states
--   SET timeout_seconds = 3600, timeout_event = 'expire_reservation', timeout_owner = 'domain'
--   WHERE name = 'reservation_active';

ALTER TABLE fsm_states
    ADD COLUMN timeout_seconds INT NULL
        COMMENT 'сек жизни state; NULL = без авто-таймера'
        AFTER name,
    ADD COLUMN timeout_event VARCHAR(128) NULL
        COMMENT 'event_name / process event при срабатывании'
        AFTER timeout_seconds,
    ADD COLUMN timeout_owner VARCHAR(16) NULL DEFAULT 'domain'
        COMMENT 'domain|platform — чья политика'
        AFTER timeout_event;

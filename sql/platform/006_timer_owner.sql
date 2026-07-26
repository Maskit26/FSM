-- Owner таймера: domain (политика домена / state timeout) | platform (служебный).
-- Apply: python scripts/apply_sql.py --db platform sql/platform/006_timer_owner.sql

ALTER TABLE fsm_timers
    ADD COLUMN owner VARCHAR(16) NOT NULL DEFAULT 'domain'
        COMMENT 'domain|platform — чья политика породила таймер'
        AFTER idempotency_key;

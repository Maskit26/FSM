-- Wipe one tenant domain from PLATFORM DB (not domain business DB).
-- Apply on platform database only.
--
-- Usage: set @service_id, run sections 1–2.
-- Section 3 (tenant_accounts wipe) is optional — uncomment what you need.

-- ========= config =========
SET @service_id = 'svc_courier_01';

-- Owner of this domain (for optional account wipe in §3)
SET @tenant_account_id = (
    SELECT tenant_account_id
    FROM domain_services
    WHERE service_id = @service_id
    LIMIT 1
);

-- ========= 1) Runtime for @service_id =========
-- Children before parents where FK exists (sagas).

DELETE sc
FROM fsm_saga_children AS sc
INNER JOIN fsm_sagas AS s ON s.id = sc.saga_id
WHERE s.service_id = @service_id;

DELETE FROM fsm_sagas WHERE service_id = @service_id;
DELETE FROM fsm_timers WHERE service_id = @service_id;
DELETE FROM fsm_transition_logs WHERE service_id = @service_id;
DELETE FROM platform_reconcile_queue WHERE service_id = @service_id;
DELETE FROM platform_outbox WHERE service_id = @service_id;
DELETE FROM platform_events WHERE service_id = @service_id;
DELETE FROM server_fsm_instances WHERE service_id = @service_id;
DELETE FROM entity_fsm_state WHERE service_id = @service_id;
DELETE FROM idempotency_keys WHERE service_id = @service_id;
DELETE FROM fsm_schedules WHERE service_id = @service_id;
DELETE FROM webhook_subscriptions WHERE service_id = @service_id;

-- ========= 2) Domain onboarding for @service_id =========
-- secrets before domain_services; audit can stay or go with service_id.

DELETE FROM domain_secrets WHERE service_id = @service_id;
DELETE FROM platform_audit_events WHERE service_id = @service_id;
DELETE FROM domain_services WHERE service_id = @service_id;

-- ========= 3) Tenant auth (optional) =========
-- A) Only the owner of @service_id (tokens CASCADE / audit SET NULL):
/*
DELETE FROM tenant_accounts WHERE id = @tenant_account_id;
*/

-- B) Wipe ALL accounts (only if no domain_services rows left for any tenant):
/*
-- fail if any domain still references an account
-- SELECT service_id, tenant_account_id FROM domain_services;

DELETE FROM platform_audit_events;
DELETE FROM domain_admin_tokens;
DELETE FROM tenant_refresh_tokens;
DELETE FROM tenant_email_verifications;
DELETE FROM tenant_accounts;
*/

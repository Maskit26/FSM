-- Additive upgrade: tenant auth + ownership on domain_services.
-- Apply to PLATFORM database only.
-- Safe to re-run (IF NOT EXISTS / information_schema guards).

CREATE TABLE IF NOT EXISTS tenant_accounts (
    id                  BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email               VARCHAR(255) NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    status              VARCHAR(32)  NOT NULL DEFAULT 'pending_verification',
    email_verified_at   DATETIME     NULL,
    failed_login_count  INT          NOT NULL DEFAULT 0,
    locked_until        DATETIME     NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_accounts_email (email),
    KEY idx_tenant_accounts_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS tenant_email_verifications (
    id                  BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tenant_account_id   BIGINT       NOT NULL,
    token_hash          CHAR(64)     NOT NULL,
    expires_at          DATETIME     NOT NULL,
    used_at             DATETIME     NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_email_verifications_hash (token_hash),
    KEY idx_tenant_email_verifications_account (tenant_account_id, used_at),
    CONSTRAINT fk_tenant_email_verifications_account
        FOREIGN KEY (tenant_account_id) REFERENCES tenant_accounts(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS tenant_refresh_tokens (
    id                  BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tenant_account_id   BIGINT       NOT NULL,
    token_hash          CHAR(64)     NOT NULL,
    family_id           CHAR(36)     NOT NULL,
    expires_at          DATETIME     NOT NULL,
    revoked_at          DATETIME     NULL,
    replaced_by_id      BIGINT       NULL,
    last_used_at        DATETIME     NULL,
    source_ip           VARCHAR(64)  NULL,
    user_agent          VARCHAR(512) NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tenant_refresh_tokens_hash (token_hash),
    KEY idx_tenant_refresh_tokens_account (tenant_account_id, revoked_at, expires_at),
    KEY idx_tenant_refresh_tokens_family (family_id),
    CONSTRAINT fk_tenant_refresh_tokens_account
        FOREIGN KEY (tenant_account_id) REFERENCES tenant_accounts(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tenant_refresh_tokens_replacement
        FOREIGN KEY (replaced_by_id) REFERENCES tenant_refresh_tokens(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS domain_admin_tokens (
    id                  BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tenant_account_id   BIGINT       NOT NULL,
    token_hash          CHAR(64)     NOT NULL,
    token_prefix        VARCHAR(16)  NOT NULL,
    name                VARCHAR(128) NULL,
    expires_at          DATETIME     NULL,
    revoked_at          DATETIME     NULL,
    last_used_at        DATETIME     NULL,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_domain_admin_tokens_hash (token_hash),
    KEY idx_domain_admin_tokens_account (tenant_account_id, revoked_at, expires_at),
    CONSTRAINT fk_domain_admin_tokens_account
        FOREIGN KEY (tenant_account_id) REFERENCES tenant_accounts(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS platform_audit_events (
    id                      BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tenant_account_id       BIGINT       NULL,
    service_id              VARCHAR(64)  NULL,
    domain_admin_token_id   BIGINT       NULL,
    event_type              VARCHAR(64)  NOT NULL,
    result                  VARCHAR(32)  NOT NULL,
    source_ip               VARCHAR(64)  NULL,
    user_agent              VARCHAR(512) NULL,
    detail_json             JSON         NULL,
    created_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_platform_audit_tenant (tenant_account_id, created_at),
    KEY idx_platform_audit_service (service_id, created_at),
    KEY idx_platform_audit_event (event_type, created_at),
    CONSTRAINT fk_platform_audit_tenant
        FOREIGN KEY (tenant_account_id) REFERENCES tenant_accounts(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_platform_audit_token
        FOREIGN KEY (domain_admin_token_id) REFERENCES domain_admin_tokens(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Bootstrap owner for any pre-existing domain_services rows before enforcing FK.
INSERT INTO tenant_accounts (email, password_hash, status, email_verified_at)
SELECT 'platform-bootstrap@localhost',
       '$argon2id$v=19$m=65536,t=3,p=4$bootstrap$notavalidpasswordhash000000000',
       'active',
       UTC_TIMESTAMP()
WHERE NOT EXISTS (
    SELECT 1 FROM tenant_accounts WHERE email = 'platform-bootstrap@localhost'
);

SET @bootstrap_tenant_id := (
    SELECT id FROM tenant_accounts WHERE email = 'platform-bootstrap@localhost' LIMIT 1
);

-- Add ownership column if missing (nullable first for backfill).
SET @col_exists := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'domain_services'
      AND COLUMN_NAME = 'tenant_account_id'
);
SET @sql := IF(
    @col_exists = 0,
    'ALTER TABLE domain_services ADD COLUMN tenant_account_id BIGINT NULL AFTER service_id',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE domain_services
SET tenant_account_id = @bootstrap_tenant_id
WHERE tenant_account_id IS NULL;

ALTER TABLE domain_services
    MODIFY COLUMN tenant_account_id BIGINT NOT NULL;

SET @idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'domain_services'
      AND INDEX_NAME = 'idx_domain_services_tenant'
);
SET @sql := IF(
    @idx_exists = 0,
    'ALTER TABLE domain_services ADD KEY idx_domain_services_tenant (tenant_account_id)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @fk_exists := (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'domain_services'
      AND CONSTRAINT_NAME = 'fk_domain_services_tenant'
      AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);
SET @sql := IF(
    @fk_exists = 0,
    'ALTER TABLE domain_services ADD CONSTRAINT fk_domain_services_tenant FOREIGN KEY (tenant_account_id) REFERENCES tenant_accounts(id)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

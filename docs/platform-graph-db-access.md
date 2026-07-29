# Platform graph DB access

Платформа читает FSM-граф из **domain DB** по SQL (`fsm_states`, `fsm_transitions`, `fsm_graph_meta`, `fsm_actions`).

Business-таблицы домена платформа **не** открывает. Domain service работает со своим `DOMAIN_DATABASE_URL` (только в процессе домена).

## Где что лежит (арендатор подключил courier)

| Что | Где |
|-----|-----|
| `DOMAIN_DATABASE_URL` | **только** `domains/courier/.env` (domain process) |
| Graph read/write URL | `domain_secrets`: `graph_database_url`, `graph_write_database_url` |
| Refs в каталоге | `domain_services.db_graph_secret_ref` / `db_graph_write_secret_ref` → имена ключей secrets |
| Contract URL / HMAC | `domain_secrets`: `contract_base_url`, `contract_shared_secret` |
| Telegram bot | `domain_secrets`: `TELEGRAM_BOT_TOKEN`, … |
| Platform API `.env` | process: `PLATFORM_DATABASE_URL`, `PLATFORM_SECRETS_KEY`, `PLATFORM_ADMIN_TOKEN`, … |
| Worker env | platform DB/secrets config + один `WORKER_SERVICE_ID` |

Онбординг tenant: `domain_services` + `PUT /v1/{service_id}/secrets`
(ключи `graph_database_url`, `graph_write_database_url`, `contract_base_url`, `contract_shared_secret`, Telegram).

Сейчас secrets API авторизован глобальным `PLATFORM_ADMIN_TOKEN`. Per-tenant `DOMAIN_ADMIN_TOKEN` и автоматический worker provisioning имеют статус «В разработке» в основной спецификации.

## Self-hosted MySQL

Отдельные MySQL-пользователи с GRANT только на graph-таблицы — шаблон: [`database/sql/domain/002_platform_graph_db_users.sql`](../database/sql/domain/002_platform_graph_db_users.sql).

## Platform DB: `domain_services`

```sql
UPDATE domain_services
SET db_graph_secret_ref = 'graph_database_url',
    db_graph_write_secret_ref = 'graph_write_database_url',
    status = 'active'
WHERE service_id = 'svc_courier_01';
```

## Код

- `resolve_tenant_ref()` — URL-литерал или `domain_secrets[key]`
- `graph_session()` / `graph_write_session()` — engines, зарегистрированные при boot
- Business domain session — только в `fsm_platform.domain_runtime.session`

## Boot (platform)

1. Active rows из `domain_services` → resolve graph URLs → register engines
2. `domain_bootstrap` — GET `/contract/v1/catalog` по `contract_base_url` арендатора

# Platform graph DB access

Платформа читает FSM-граф из **domain DB** по SQL (`fsm_states`, `fsm_transitions`, `fsm_graph_meta`, `fsm_actions` / `fsm_events`).

**Три отдельных credential ref — одна схема для всех окружений:**

| Ref | Назначение |
|-----|------------|
| `DOMAIN_DATABASE_URL` / `db_secret_ref` | Полный domain DB (embedded: guards/effects/commands) |
| `DOMAIN_GRAPH_DATABASE_URL` / `db_graph_secret_ref` | **Обязательно.** Чтение графа |
| `DOMAIN_GRAPH_WRITE_DATABASE_URL` / `db_graph_write_secret_ref` | **Обязательно.** `graph/publish` |

Fallback на `DOMAIN_DATABASE_URL` для graph **нет**. Без graph URL boot падает с `BootConfigError`.

## Self-hosted MySQL

Отдельные MySQL-пользователи с GRANT только на graph-таблицы — шаблон: [`database/sql/domain/002_platform_graph_db_users.sql`](../database/sql/domain/002_platform_graph_db_users.sql). Три ref в env/`domain_services` указывают на **разные** URL.

## Platform DB: `domain_services`

Миграция: [`database/sql/platform/002_domain_services_graph_refs.sql`](../database/sql/platform/002_domain_services_graph_refs.sql)

```sql
UPDATE domain_services
SET db_graph_secret_ref = 'DOMAIN_GRAPH_DATABASE_URL',
    db_graph_write_secret_ref = 'DOMAIN_GRAPH_WRITE_DATABASE_URL'
WHERE service_id = 'svc_courier_01';
```

Колонки **обязательны** для `status = 'active'`. NULL → boot error.

## Код

- `graph_session()` — только graph read engine
- `graph_write_session()` — только graph write engine
- `domain_session()` — полный domain (embedded business logic)

## Boot

При старте API/worker:

1. Регистрация engines из env (`SERVICE_ID` + три URL) и из `domain_services`
2. `_validate_graph_engines()` — graph read/write обязательны для `SERVICE_ID`
3. Active rows в `domain_services` без graph refs → `BootConfigError`

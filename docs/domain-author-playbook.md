# Domain author playbook — подключение картриджа

Чеклист для автора нового домена (или копии `courier`).  
Глубокая модель платформы — в [fsm-platform-domain-requirements.md](fsm-platform-domain-requirements.md);  
Contract API — [domain-contract-api-v1.md](domain-contract-api-v1.md).

Референс-картридж: `domains/courier/`.

---

## 0. Термины

| Термин | Смысл |
|--------|--------|
| **Картридж** | Код домена: граф SQL + Python (`guards` / `effects` / `commands` / …) |
| **`service_id`** | Runtime-id арендатора (`svc_<type>_<hex>`), не имя папки |
| **`cartridge_type`** | Тип продукта (`courier`, …); может повторяться у разных `service_id` |
| **Domain service** | Отдельный процесс (`uvicorn domains.<name>.main:app`) |
| **Platform API** | Public API + HMAC к Contract + worker per tenant |

Контуры auth (не смешивать):

- **Admin / ЛК:** `DOMAIN_ADMIN_TOKEN` — без Principal.
- **End-user apps:** Bearer `eut1.…` + Principal + access policy — без raw admin token в приложении.

---

## 1. Каркас кода

Скопируй структуру с `domains/courier/` (имена модулей можно сузить под домен):

```text
domains/<name>/
  main.py              # load .env; create_app(entry="…:register_all")
  processes.py         # register_all(service_id)
  manifest.yaml        # cartridge_type, version, entry, required_*
  commands.py          # operations type=command
  queries.py           # operations type=query
  guards.py / effects.py / context.py
  db_layer.py          # бизнес-SQL к Domain DB
  entity_ui.py         # optional: access + snapshot по entity_type
  .env.example         # без секретов в git
```

Минимум в `register_all(service_id)`:

1. `operations.register(service_id, name, "command"|"query", fn)`
2. `DomainProcessDef` + `processes.register` для каждого FSM-процесса
3. `guards.register` / `effects.register` — имена **как в graph SQL**
4. `set_outbox_handler(...)` если есть vendor outbox (`channel=core` / custom)
5. При entity UI / WS: `access_policies.register` + `snapshots.register` (см. §5)

`register_all` вызывается **при старте domain service**, не при boot Platform API.

---

## 2. Domain DB и граф

| Шаг | Действие |
|-----|----------|
| 1 | Создать MySQL schema арендатора |
| 2 | Накатить бизнес-таблицы домена |
| 3 | Накатить graph: `database/sql/domain/001_fsm_graph_template.sql` + SQL процессов картриджа |
| 4 | Graph users: `database/sql/domain/002_platform_graph_db_users.sql` — см. [platform-graph-db-access.md](platform-graph-db-access.md) |
| 5 | Имена guards/effects/context в SQL = имена в `register_all` |

Платформа ходит в **graph** через `graph_*` URLs из `domain_secrets`.  
Бизнес-данные — только через Domain Contract / domain process (не прямым SQL с Platform API).

---

## 3. Env domain service

Файл `domains/<name>/.env` (см. `.env.example`):

| Переменная | Назначение |
|------------|------------|
| `SERVICE_ID` | Тот же id, что в `domain_services` после онбординга |
| `DOMAIN_DATABASE_URL` | Business + graph schema (доменный процесс) |
| `CONTRACT_SHARED_SECRET` | HMAC с platform (= `domain_secrets.contract_shared_secret`) |
| `PLATFORM_API_BASE_URL` | База Public API для `call_api` proxy |

**Не** класть в domain `.env`: `PLATFORM_DATABASE_URL`, `PLATFORM_SECRETS_KEY`, raw vendor tokens, `DOMAIN_ADMIN_TOKEN` для end-user apps.

Vendor credentials, Telegram, graph URLs, `end_user_token_secret` — через  
`PUT /v1/{service_id}/secrets` (platform).

---

## 4. Онбординг арендатора (runtime)

Кратко (детали — requirements §6 / §9):

1. Арендатор: register → login → `POST /v1/tenant/admin-tokens` → `DOMAIN_ADMIN_TOKEN`
2. Domain DB + domain service подняты (`SERVICE_ID` пока можно заглушкой; после шага 3 — реальный id)
3. `POST /v1/tenant/domains` → получить `service_id`; прописать в domain `.env`
4. `PUT /v1/{service_id}/secrets` — graph URLs, `contract_shared_secret`, credentials, при необходимости `end_user_token_secret`
5. Domain service слушает Contract (порт из `contract_base_url`)
6. `POST /v1/{service_id}/connect` — Validator + bootstrap + dedicated worker
7. Проверки: `GET /v1/{service_id}/catalog`, `GET /v1/{service_id}/ready`, `GET …/worker/status`

Ошибки Validator → tenant не ready (`DOMAIN_NOT_READY` / 503).

---

## 5. End-user surface (если нужны клиентские apps)

| Что | Где |
|-----|-----|
| Access policy | `access_policies.register(service_id, entity_type, fn)` — Principal vs сущность |
| Snapshot | `snapshots.register(...)` — урезанный JSON для HTTP Snapshot / WS |
| Docs reconnect | [domain-app-realtime.md](domain-app-realtime.md) |
| Выдача eut1 | Admin: `POST /v1/{service_id}/end-user-tokens`; secret в `domain_secrets` |
| Apps | Только Bearer `eut1.…`, **не** `DOMAIN_ADMIN_TOKEN` |

Access policy ≠ PIN/FSM guards: отдельный слот для Snapshot/WS entity subscribe.

---

## 6. Внешние интеграции

На каждую интеграцию — [adapter-checklist.md](adapter-checklist.md):

- только `call_api` / outbox `http_external` (не голый HTTP-клиент к вендору);
- `timeout`, `idempotency_key`, correlation из envelope;
- credentials в `domain_secrets`, ключ = `credential_key`.

---

## 7. Клиентские конфликты (dual-commit)

Если команда «забирает» ресурс (take / assign):

- зафиксировать коды в домене + UX — [client-conflict-semantics.md](client-conflict-semantics.md);
- желательно race-тест по образцу `tests/test_parallel_take_race.py`.

Платформенный FSM race → `STATE_MISMATCH`; доменный take → свой код (`ALREADY_TAKEN`, …).

---

## 8. Ops checklist перед «готово к тенанту»

| # | Проверка |
|---|----------|
| 1 | `GET /v1/health` (liveness) и `GET /v1/{service_id}/ready` |
| 2 | Worker up: `GET /v1/{service_id}/worker/status` + metrics queue |
| 3 | Catalog: operations / processes / access_policies / snapshots согласованы с кодом |
| 4 | E2E: `tools/tenant_e2e.py` или сценарии домена |
| 5 | DR/RPO контекст — [ops-reliability.md](ops-reliability.md) (для продакшен-контура) |
| 6 | Correlation: invoke/enqueue прокидывают envelope (§2.4 backlog) |

---

## 9. Быстрый чеклист «новый картридж»

- [ ] Папка `domains/<name>/` + `manifest.yaml` + `main.py` → `register_all`
- [ ] Graph SQL + бизнес-таблицы + graph DB users
- [ ] Guards/effects/context имена = SQL
- [ ] Domain `.env` (4 ключа выше) без platform DB / admin token для apps
- [ ] Онбординг: domains → secrets → connect → catalog/ready
- [ ] (opt) access + snapshot + eut1 secret
- [ ] (opt) adapter checklist на каждый вендор
- [ ] (opt) conflict semantics + race test
- [ ] Worker + ready + E2E green

---

## Ссылки

| Тема | Документ |
|------|----------|
| Модель платформы / онбординг | [fsm-platform-domain-requirements.md](fsm-platform-domain-requirements.md) |
| Contract HTTP | [domain-contract-api-v1.md](domain-contract-api-v1.md) |
| Graph DB users | [platform-graph-db-access.md](platform-graph-db-access.md) |
| Realtime / Snapshot | [domain-app-realtime.md](domain-app-realtime.md) |
| Adapter | [adapter-checklist.md](adapter-checklist.md) |
| Conflicts | [client-conflict-semantics.md](client-conflict-semantics.md) |
| Ops | [ops-reliability.md](ops-reliability.md) |
| Бэклог | [platform-backlog.md](platform-backlog.md) |

# FSM Platform: работа платформы и подключение домена

Смежные документы:

| Документ | Содержание |
|----------|------------|
| [domain-contract-api-v1.md](domain-contract-api-v1.md) | HTTP+JSON Contract API (пути, HMAC, схемы тел) |
| [platform-graph-db-access.md](platform-graph-db-access.md) | Graph SQL credentials / `domain_secrets` |
| [../tools/domain_e2e/README.md](../tools/domain_e2e/README.md) | Запуск YAML E2E против живого API |

### Статусы требований

- **Реализовано** — поведение присутствует в текущем коде платформы.
- **В разработке** — целевая модель; соответствующие API, хранилища или процессы ещё требуется реализовать.

Если статус возле раздела не указан, раздел описывает текущую реализацию.

---

## 1. Видение

FSM Platform — **универсальный движок оркестрации**. Ей безразличны имена state/event и схема business-таблиц.

Домен — **отдельный процесс** (картридж: граф SQL + Python guards/effects/commands). Платформа исполняет FSM и вызывает домен по **Domain Contract API** (HTTP + HMAC).

```text
Клиенты (фронт / мобилка) / Telegram / исходящие webhooks клиентов
        ↓
Platform API (:8000)          FSM Worker × N (1 процесс = 1 tenant)
  Auth + Domain API + Input     claim / timers / outbox / reconcile
  DOMAIN_ADMIN_TOKEN gateway
        │  platform DB: instances, entity_fsm_state, outbox, secrets, tenants, …
        │  graph SQL (read / publish) — отдельные credentials
        ↓  HMAC Contract API
Domain service (:8100…) — DOMAIN_DATABASE_URL (business + fsm_* tables)
  guards / effects / commands / queries / context / on_failed
```

Топология: **один** Platform API, **N** worker-процессов и **N** domain services
(по числу активных арендаторов). `POST …/connect` поднимает dedicated worker
(`1 process = 1 service_id`) через локальный `WorkerProvisioner` (§7.1).

---

## 2. Принципы

1. **Platform agnostic** — `fsm_platform.core` не знает courier/taxi.
2. **Contract API** — бизнес-логика домена вызывается по HTTP; в RAM платформы — `RemoteRef`.
3. **Декларативный граф** — переходы в `fsm_transitions` (domain DB); платформа читает граф SQL-ом.
4. **Pipeline** — `context → guard → transition → effect` (context/guard/effect — HTTP к домену).
5. **Две БД, два владельца записи** — platform DB: FSM-инфраструктура; domain DB: бизнес. Worker работает с platform session + graph SQL.
6. **Декларативные side-effects** — домен в ответе отдаёт `notify` / `cancel_instances` / `entity_states`; платформа применяет их у себя (`apply_declared`).
7. **Per-tenant secrets** — graph URL, contract URL/secret, Telegram и т.п. в `domain_secrets` (Fernet). Platform `.env` — только процесс платформы.
8. **`service_id`** — уникальный runtime-ключ арендатора; `cartridge_type` может повторяться.
9. **Домен обслуживается после bootstrap** — `domain_services.status=active` + успешный catalog + Domain Validator.
10. **1 worker process = 1 tenant** — `WORKER_SERVICE_ID` обязателен; `boot(service_id)` и claim scoped на одного tenant; connect/start/stop/restart через `WorkerProvisioner` (§7.1).
11. **I/O каналов на платформе** — Telegram webhook/deep-link/send в `input/` + `output/`; привязка аккаунта — доменная команда по конвенции канала (§8.4).
12. **Один публичный контракт клиентов** — `/v1/{service_id}/…` закрыт tenant-scoped `DOMAIN_ADMIN_TOKEN`.

---

## 3. Процессы и конфиг

### 3.1. Что крутится

| Процесс | Entrypoint | Роль |
|---------|------------|------|
| Platform API | `uvicorn main:app` (порт 8000) | Auth, Domain API, Platform Admin, TG webhook, WS/events |
| FSM Worker | `python fsm_worker.py` | Claim instances / timers / outbox / reconcile **одного** tenant |
| Domain service | `uvicorn domains.<name>.main:app` | Contract API + бизнес SQL |

### 3.2. Где лежит конфиг арендатора

| Что | Где |
|-----|-----|
| Список active tenants | platform DB: `domain_services` |
| `db_secret_ref` | Обязательное legacy-поле schema `domain_services`; текущий remote runtime его не разрешает и не использует |
| Graph read/write URL | `domain_secrets`: `graph_database_url`, `graph_write_database_url` |
| Refs | `domain_services.db_graph_secret_ref` / `db_graph_write_secret_ref` → имена ключей secrets |
| Contract base URL / HMAC | `domain_secrets`: `contract_base_url`, `contract_shared_secret` |
| Telegram bot | `domain_secrets`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_LINK_SECRET` |
| Business DB URL | **только** `.env` процесса домена (`DOMAIN_DATABASE_URL`) |
| Platform process | корневой `.env`: `PLATFORM_DATABASE_URL`, `PLATFORM_SECRETS_KEY`, `PLATFORM_ADMIN_TOKEN`, … |
| Worker process | **свой** env процесса: `WORKER_SERVICE_ID`, плюс доступ к platform DB / secrets key (см. §7) |

Шаблоны: корневой `.env` (process-only), `domains/<name>/.env.example`.

---

## 4. Пакет `fsm_platform` — модули подробно

```text
fsm_platform/
  core/             # FSM runtime; текущий http_client — временное исключение
  host/             # API, worker, boot, contract client, secrets
  domain_runtime/   # библиотека процесса домена (Contract FastAPI)
```

Корень репозитория также содержит каналы вне пакета:

```text
input/telegram/     # входящий Telegram Update
output/telegram/    # исходящая отправка Bot API
output/webhook/     # исходящий HMAC POST на URL клиента
main.py             # entry Platform API
fsm_worker.py       # entry worker
domains/<name>/     # картриджи (отдельные процессы)
```

### 4.1. `core/` — движок FSM

Правила core: platform session/commit — у host; callables домена — через Contract / `domain_runtime`.

Текущий `core/http_client.py`: domain process при `PLATFORM_API_BASE_URL`
проксирует `call_api` на platform `POST /v1/{service_id}/external/call` (HMAC);
credentials читает только platform process.

| Модуль | Назначение |
|--------|------------|
| `engine.py` | `run_instance` — оркестрация одного FSM-instance до terminal |
| `transition_runner.py` | Один шаг: context → candidates → guards → apply → effect; companions |
| `transition_repository.py` | SELECT исходящих рёбер из graph DB (`fsm_transitions`) |
| `transition_executor.py` | UPSERT `entity_fsm_state` + запись `fsm_transition_logs` (platform DB) |
| `state_store.py` | Чтение/запись текущего FSM-state сущности |
| `db_layer.py` | Весь SQL **platform** DB (instances, timers, outbox, secrets rows, …) |
| `registry.py` | Process / Guard / Effect registries; на платформе значения = `RemoteRef` |
| `remote.py` | `RemoteRef` — дескриптор удалённого handler (имя + kind) |
| `types.py` | `ProcessDef`, `GuardResult`, `EffectResult`, `FsmResult`, нормализация |
| `timers.py` | `schedule_timer` → строки `fsm_timers` |
| `sagas.py` | Fan-in дочерних instances (`on_child_terminal`) |
| `http_client.py` | `call_api` для внешних HTTP с credentials из secrets (не Contract) |
| `errors.py` / `domain_errors.py` | Коды ошибок FSM / DomainError → API 409 |

### 4.2. `host/` — оболочка платформы

| Модуль | Назначение |
|--------|------------|
| `http/app.py` | FastAPI: `/v1/{service_id}/…`, admin, telegram routes |
| `http/request_runtime.py` | Sync invoke: Contract command/query + bootstrap/enqueue + `apply_declared`; poll instance |
| `http/events_ws.py` | WebSocket поток `platform_events` |
| `worker.py` | `process_one` / `run_loop`: timers → claim instance → `run_instance` → outbox → reconcile |
| `outbox_worker.py` | Claim `platform_outbox` → `output/*` или Contract `/outbox/deliver` |
| `reconcile_worker.py` | Докат platform-части после dual-commit сбоя |
| `boot.py` | Старт: list `domain_services` → resolve graph URLs → engines → bootstrap catalog |
| `domain_bootstrap.py` | `GET /catalog` → заполнить RemoteRef registries + Validator |
| `domain_validator.py` | Accept / hot-reload: catalog ↔ graph SQL |
| `contract_client.py` | HMAC HTTP-клиент; `resolve_contract_config` из secrets |
| `contract_invoke.py` | Обёртки: context / guard / effect / command / on_failed |
| `contract_side_effects.py` | `apply_declared` — §5.4 |
| `contract_auth.py` | Построение/проверка HMAC (общая с domain middleware) |
| `tenant_config.py` | `resolve_tenant_ref` / стандартные ключи secret names |
| `secrets.py` | Fernet CRUD `domain_secrets`; `require_admin` |
| `runtime_context.py` | `service_scope(service_id)` / `current_service_id()` — контекст арендатора в потоке |
| `engines.py` | Session makers: platform + per-tenant graph read/write |
| `operations.py` | OperationRegistry на платформе (`RemoteRef` после catalog) |
| `webhooks.py` | Подписки клиентов: fan-out события → outbox `channel=webhook` |
| `side_effects.py` | `notify`, `emit_event`, `schedule_timer`, `call_api`, `start_saga` |
| `graph_version.py` | Текущая версия графа для instance |
| `retry_policy.py` | Backoff / retry instance и Contract |
| `state_timeouts.py` | Политики таймаутов состояний (если включены) |
| `auth.py` | Dev/Bearer для Public API (actor tokens) |
| `metrics.py` | Метрики процесса |
| `hook_registry.py` | Inbound hooks из catalog (если домен их объявил) |

### 4.3. `domain_runtime/` — процесс домена

Живёт внутри domain service (`domains/<name>/main.py` → `create_app`). Platform API/worker исполняют домен через Contract HTTP, а не через этот пакет напрямую.

| Модуль | Назначение |
|--------|------------|
| `app.py` | FastAPI приложение `/contract/v1/*` |
| `boot.py` | Импорт `register_all(service_id)` → локальные callables |
| `dispatch.py` | Открывает domain session, вызывает guard/effect/command, commit |
| `registry.py` | Локальные registries operations/processes/guards/effects |
| `catalog.py` | Сборка JSON для `GET /catalog` |
| `session.py` | Engine из `DOMAIN_DATABASE_URL` |
| `contract_auth.py` | Middleware: secret из env домена (`CONTRACT_SHARED_SECRET`) |

### 4.4. Каналы `input/` и `output/`

См. §11–12. Каналы I/O лежат на границе платформы (`input/`, `output/`), отдельно от `fsm_platform.core`.

---

## 5. Домен (картридж)

### 5.1. Роль

Домен отвечает за:

- бизнес-таблицы и SQL в **своей** БД;
- декларативный граф `fsm_*` (те же DB, отдельные MySQL-юзеры для graph access платформы);
- Python: commands, queries, guards, effects, context builders, `on_failed`;
- HTTP Contract API (через `domain_runtime`).

Платформа отвечает за:

- очередь FSM instances и worker claim;
- запись `entity_fsm_state` / transition logs (в т.ч. применение деклараций `entity_states[]`);
- Telegram Bot API (парсинг Update, deep-link, send);
- шифрование и хранение `domain_secrets`;
- Public API клиентов.

### 5.2. Структура каталога

```text
domains/<name>/
  main.py              # load .env картриджа; create_app(entry=…:register_all)
  processes.py         # register_all(service_id): operations + DomainProcessDef + guards/effects
  commands.py          # sync commands → dict (entity_type, enqueue, notify, …)
  queries.py           # sync queries → dict
  guards.py            # → GuardResult / {ok, reason}
  effects.py           # → EffectResult + опц. notify/cancel/entity_states
  context.py           # builders для ProcessDef.context_builder
  db_layer.py          # SQL только business/domain
  recovery.py          # on_failed → декларации для платформы
  notifications.py     # builders списков notify[] (платформа кладёт в outbox)
  manifest.yaml        # метаданные картриджа
  .env                 # SERVICE_ID, DOMAIN_DATABASE_URL, CONTRACT_SHARED_SECRET, …
  .env.example
```

Пример entrypoint (`domains/courier/main.py`):

```python
app = create_app(entry="domains.courier.processes:register_all")
```

`register_all` выполняется **при старте domain service**, не при boot Platform API.

### 5.3. Что регистрирует `register_all`

1. **Operations** — имя → kind (`command`|`query`) → callable.
   Попадают в catalog → на платформе становятся `RemoteRef` в OperationRegistry.
2. **Guards / effects** — имена, на которые ссылается граф `fsm_transitions`.
3. **Processes** — `DomainProcessDef`: `process_name`, `entity_type`, `event_name`, `context_builder`, опц. `on_failed`. Runtime-событие вычисляется как `event_name or process_name`.
4. Опционально **outbox handler** (`set_outbox_handler`) — для `channel=http_external` → Contract `POST /outbox/deliver`.

Имена guards/effects в SQL-графе **должны** совпадать с зарегистрированными. Domain Validator ловит рассинхрон при bootstrap/reload.

### 5.4. Платформенные поля ответа Contract

Ответ domain service (command / effect / on_failed) может содержать поля, которые **пишет платформа** в platform DB после успешного HTTP-ответа. Домен к этому моменту уже закоммитил свою транзакцию (dual-commit).

Два механизма применения:

| Механизм | Модуль | Поля |
|----------|--------|------|
| Bootstrap / очередь / таймеры | `host/http/request_runtime` | `entity_type`, `related_entities`, `enqueue`/`enqueues`, `saga`, `timers`/`cancel_timers` |
| Декларативные side-effects | `host/contract_side_effects` | `notify`, `cancel_instances`, `entity_states` |

Ниже — полное описание `contract_side_effects`. Поля bootstrap/enqueue — §8; таймеры — §13.1. HTTP-схемы тел — также [domain-contract-api-v1.md](domain-contract-api-v1.md).

#### 5.4.1. Назначение `contract_side_effects`

Модуль: `fsm_platform/host/contract_side_effects.py`.

Домен **декларирует** желаемые изменения platform-инфраструктуры в JSON ответа. Платформа в своей открытой session применяет их через `apply_declared` и коммитит вместе с остальной platform-транзакцией (invoke или worker step).

Домен не открывает platform session и не INSERT в `platform_outbox` / `entity_fsm_state` напрямую.

#### 5.4.2. Точки вызова

| Контекст | Файл | Когда |
|----------|------|--------|
| Sync command | `request_runtime.run_operation` | После Contract command, до `sp.commit()` |
| FSM step completed | `host/worker.process_one` | После `run_instance` → COMPLETED, из `result.payload` |
| Terminal `on_failed` | `host/worker._call_on_failed` | После recovery Contract response, в отдельной platform-транзакции |
| Reconcile | `host/reconcile_worker` | При докате сохранённого payload без повтора domain handler |

Сигнатура:

```text
apply_declared(
  session_platform,
  service_id=…,
  data=<dict ответа Contract>,   # или
  notify=…, cancel_instances=…, entity_states=…  # явные списки
) → { "notify": N, "cancel_instances": N, "entity_states": N }
```

`extract_declared(data)` забирает из dict только ключи `notify`, `cancel_instances`, `entity_states` (каждый — list или omit). Явные аргументы дописываются к извлечённым.

#### 5.4.3. Порядок применения

Внутри одного вызова `apply_declared`:

1. **`entity_states[]`** — UPSERT текущего FSM-state сущности
2. **`cancel_instances[]`** — отмена подходящих PENDING instances
3. **`notify[]`** — постановка строк в `platform_outbox` через `side_effects.notify`

Ошибка валидации элемента (нет обязательных полей) → `ValueError`, откат platform-транзакции вызывающего кода.

#### 5.4.4. `entity_states[]`

UPSERT строки `entity_fsm_state` для арендатора.

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `entity_type` | да | тип сущности |
| `entity_id` | да | id |
| `state` | да | новое текущее состояние |

```json
"entity_states": [
  { "entity_type": "order", "entity_id": 15, "state": "cancelled" }
]
```

Реализация: `default_db_layer.upsert_entity_state(session, service_id, …)`.

#### 5.4.5. `cancel_instances[]`

Отмена PENDING-инстансов процесса с фильтром по payload.

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `process_name` | да | имя процесса |
| `payload_match` | нет (object) | все пары key→value должны совпасть с `payload_json` instance |
| `except_instance_id` | нет | этот id не трогать |
| `last_error` | нет | текст в cancelled (default `CANCELLED_BY_DOMAIN`) |

Алгоритм (`_cancel_pending`):

1. `list_pending_instances(service_id, process_name, limit=100)`
2. Пропуск `except_instance_id`
3. Сравнение `payload_match` с payload instance (все ключи)
4. `mark_instance_cancelled` для совпавших

```json
"cancel_instances": [
  {
    "process_name": "locker_reserve",
    "payload_match": { "order_id": 15 },
    "except_instance_id": null,
    "last_error": "ORDER_CANCELLED"
  }
]
```

#### 5.4.6. `notify[]`

Постановка исходящего сообщения в outbox (доставка — позже, `outbox_worker`, §12).

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `channel` | да | `telegram` \| `webhook` \| `http_external` \| `log` \| `dry_run` |
| `destination` | да | chat_id / URL / credential_key — по каналу |
| `event_type` | да | тип события для маршрутизации/логов |
| `payload` | нет (object) | тело; для telegram обычно `text` |
| `idempotency_key` | нет | дедуп в outbox |

```json
"notify": [
  {
    "channel": "telegram",
    "destination": "123456789",
    "event_type": "order.created",
    "payload": { "text": "Заказ создан" },
    "idempotency_key": "tg:order:15:created"
  }
]
```

Реализация: `host/side_effects.notify` → INSERT `platform_outbox`. Каналы доставки — §12.2.

#### 5.4.7. Command: поля вне `apply_declared`

Те же ответы command могут содержать поля, которые обрабатывает **`request_runtime`**, а не `contract_side_effects`:

| Поле | Модуль | Эффект |
|------|--------|--------|
| `entity_type` / `entity_id` / `initial_state` | `_bootstrap_and_maybe_enqueue` | `entity_fsm_state` |
| `related_entities[]` | то же | доп. states |
| `enqueue` / `enqueues[]` | то же | PENDING instances |
| `saga` | то же | saga + children |
| `timers[]` / `cancel_timers[]` | `_apply_timers` | `fsm_timers` (§13.1) |

После bootstrap/timers invoke всё равно вызывает `apply_declared` для `notify` / `cancel_instances` / `entity_states` из того же тела ответа.

### 5.5. Env домена

| Переменная | Назначение |
|------------|------------|
| `SERVICE_ID` | Должен совпадать с `domain_services.service_id` |
| `DOMAIN_DATABASE_URL` | Business + graph tables |
| `CONTRACT_SHARED_SECRET` | HMAC; **тот же** value → `domain_secrets.contract_shared_secret` |

Telegram для send/webhook кладётся в platform `domain_secrets` при онбординге.

`call_api` из domain process не читает platform DB: при `PLATFORM_API_BASE_URL`
идёт HMAC-прокси на `POST /v1/{service_id}/external/call`, где platform
резолвит credential из `domain_secrets` и выполняет исходящий HTTP.
Domain `.env` содержит `SERVICE_ID`, `DOMAIN_DATABASE_URL`, `CONTRACT_SHARED_SECRET`,
`PLATFORM_API_BASE_URL` — без `PLATFORM_DATABASE_URL` / `PLATFORM_SECRETS_KEY`.

### 5.6. Domain DB

- Business-таблицы + граф `fsm_*`.
- Отдельные MySQL-юзеры graph read/write: `database/sql/domain/002_platform_graph_db_users.sql`, см. [platform-graph-db-access.md](platform-graph-db-access.md).
- Business и graph tables — в Domain DB; платформа ходит в graph через credentials из `domain_secrets`, бизнес — через Contract API.

---

## 6. Подключение домена (онбординг)

### 6.1. Как появляется `service_id`

`service_id` — уникальный runtime-id домена. Платформа назначает его при
`POST /v1/tenant/domains` и записывает владельца в `domain_services.tenant_account_id` (§9.2).

| Где живёт | Назначение |
|-----------|------------|
| `domain_services.service_id` | Каталог доменов на platform DB |
| `domain_services.tenant_account_id` | Владелец (`domain_admin`) |
| `domains/<name>/.env` → `SERVICE_ID` | Domain service регистрирует handlers под этим id |
| URL Domain API | `/v1/{service_id}/…` — клиенты и E2E передают его явно |
| `WORKER_SERVICE_ID` | Env worker-процесса = тот же id |
| HMAC Contract | Заголовок `X-Service-Id` |

Типичное имя: `svc_<cartridge>_<hex>` (например `svc_courier_a1b2c3d4e5f6`). `cartridge_type` может повторяться у разных `service_id`.

Клиент получает `service_id` из ответа регистрации домена и ходит в `/v1/{service_id}/…`
с `X-Admin-Token: DOMAIN_ADMIN_TOKEN`.

### 6.2. Self-service подключение

1. Арендатор: `POST /v1/auth/register` → verify email → `POST /v1/auth/login`.
2. Выпустить tenant-scoped `DOMAIN_ADMIN_TOKEN` (`POST /v1/tenant/admin-tokens`).
3. Развернуть Domain DB (schema + graph + graph users) и domain service.
4. `POST /v1/tenant/domains` с `DOMAIN_ADMIN_TOKEN` → получить `service_id`.
5. Записать secrets через `PUT /v1/{service_id}/secrets` с тем же token.
6. `POST /v1/{service_id}/connect` — Domain Validator + bootstrap + dedicated worker.
7. Проверить `GET /v1/{service_id}/catalog`, затем E2E (§16 / `tools/tenant_e2e.py`).

### 6.3. Что платформа делает при boot

```text
main.py / fsm_worker.py
  → host/boot.py(service_id=…)
       list domain_services (active; worker — только свой service_id)
       для каждого выбранного tenant:
         tenant_config.resolve_tenant_ref → secrets graph_* URLs
         engines.register graph session makers
         domain_bootstrap: contract_client GET /catalog
         RemoteRef → operations / processes / guards / effects
         domain_validator (catalog ↔ graph SQL)
```

Ошибки Validator → tenant не ready; Public API отвечает HTTP 503 `DOMAIN_NOT_READY`.

Worker всегда стартует с `boot(service_id=WORKER_SERVICE_ID)` и загружает только свой tenant.

---

## 7. Worker

### 7.1. Модель и статус

**Реализовано:**

- `fsm_worker.py` требует `WORKER_SERVICE_ID` (fail-closed).
- `boot(service_id)` / `bootstrap_active_domains(service_id=…)` загружают только этот tenant.
- `host/worker.run_loop` передаёт `service_id` в timers, schedules, instances, outbox и reconcile.
- Claim выполняется только по этому `service_id`.
- `host/worker_provisioner.py` — lifecycle: start/stop/restart/status.
- `POST /v1/{service_id}/connect` после Validator/bootstrap вызывает `provision_worker`.
- Tenant API: `GET …/worker/status`, `POST …/worker/restart|stop`.
- При ошибке provisioning статус домена → `worker_failed`.

| Правило | Смысл |
|---------|--------|
| 1 процесс = 1 tenant | Env процесса содержит ровно один `WORKER_SERVICE_ID` |
| Один бинарь | Все воркеры запускают `python fsm_worker.py` (или образ с тем же entry) |
| Claim filter | `claim_*(..., service_id=WORKER_SERVICE_ID)` |
| Tenant-scoped boot | `boot(service_id)` только своего tenant |
| Fail-closed | Без `WORKER_SERVICE_ID` процесс не стартует |
| Lifecycle | connect поднимает worker; tenant stop/restart управляет им |

#### Worker provisioner backends

**Зачем.** Local `subprocess` удобен в dev (Platform API сам поднимает child), но в
проде worker обычно ведёт systemd / Docker / Kubernetes. Сменные бэкенды —
**расширение вариантов деплоя**, не обязанность: можно оставаться на `local`.

**Как работает.** `WORKER_PROVISION_BACKEND` выбирает адаптер; публичный API
модуля не меняется (`provision_worker` / `worker_status` / `stop_worker` /
`restart_worker`). Модель `1 worker = 1 service_id` одинакова для всех.

| Backend | Env | Поведение |
|---------|-----|-----------|
| `local` (default) | опц. `WORKER_PROVISION_COMMAND` | `Popen(fsm_worker.py)` у процесса API |
| `systemd` | `WORKER_SYSTEMD_UNIT_TEMPLATE` (default `fsm-worker-{service_id}.service`) | `systemctl start/stop/is-active`; unit’ы ставятся отдельно |
| `docker` | **`WORKER_DOCKER_IMAGE`** обязателен; опц. `WORKER_DOCKER_NETWORK` | контейнер `fsm-worker-{service_id}` |
| `kubernetes` / `k8s` | `WORKER_K8S_NAMESPACE`, `WORKER_K8S_DEPLOYMENT_PREFIX` | `kubectl scale` Deployment 0↔1; манифесты — снаружи |

**Ограничения.** systemd/docker/k8s предполагают, что unit/image/Deployment уже
описаны в инфраструктуре; provisioner только управляет lifecycle. На Windows
dev остаётся `local`.

**Проверка.** Без смены env — `WORKER_PROVISION_BACKEND` пуст → local; connect в ЛК
по-прежнему поднимает child process.

### 7.2. Entrypoint и цикл

Файлы: `fsm_worker.py` → `host/boot.py` → `host/worker.run_loop`.

Каждая итерация `run_loop`:

1. `process_one(service_id=…)` — timers/schedules, затем claim FSM instance.
2. `outbox_worker.process_one(service_id=…)` — доставка outbox.
3. `reconcile_worker.process_one(service_id=…)` — dual-commit recovery.
4. Sleep `FSM_WORKER_POLL_SECONDS` если не было работы.

### 7.3. Обработка одного instance (файлы)

```text
host/worker.process_one
  db_layer.claim_pending_instance          # platform DB
  engines.graph_session(service_id)        # graph SQL
  core.engine.run_instance
    transition_runner (цикл шагов)
      contract_invoke.call_context_builder → Domain POST /context/…
      transition_repository (graph)        # candidates
      contract_invoke.call_guard           → Domain POST /guards/…
      transition_executor                  # entity_fsm_state + logs (platform)
      contract_invoke.call_effect          → Domain POST /effects/…
  contract_side_effects.apply_declared     # notify → outbox, …
  webhooks.emit_event_with_webhooks
  db_layer.mark_instance_completed
  sp.commit  # при fail после domain-ok → enqueue_reconcile
```

Retry: `retry_policy` + `mark_instance_retry`. Terminal fail → `mark_instance_failed` + Contract `on_failed` при наличии.

### 7.4. Env воркера (минимум)

| Переменная | Обязательность |
|------------|----------------|
| `WORKER_SERVICE_ID` | Да (или явный `WORKER_ALLOW_ALL_TENANTS=1`) |
| `PLATFORM_DATABASE_URL` | Да |
| `PLATFORM_SECRETS_KEY` | Да (чтение contract/graph/telegram secrets) |
| `FSM_WORKER_POLL_SECONDS` | Нет (default 1) |
| `OUTBOX_MAX_ATTEMPTS` | Нет (default 8) |
| `CONTRACT_TIMEOUT_GUARD_EFFECT` | Нет (default 5s) |
| `CONTRACT_TIMEOUT_COMMAND` | Нет (default 10s) |
| `CONTRACT_TIMEOUT_CATALOG` | Нет (default 5s) |
| `CONTRACT_TIMEOUT_OUTBOX` | Нет (default 30s) |
| `CONTRACT_MAX_ATTEMPTS` | Нет (default 3) |

В env воркера: `PLATFORM_DATABASE_URL`, `PLATFORM_SECRETS_KEY`, `WORKER_SERVICE_ID`. Business DB домена воркеру не нужна.

### 7.5. Retry, terminal failure и reconcile

`host/retry_policy.py` классифицирует ошибки как transient/permanent. Настройки:

| Переменная | Default | Смысл |
|------------|---------|-------|
| `FSM_INSTANCE_MAX_ATTEMPTS` | `5` | Максимум попыток instance |
| Contract/External API retry settings | см. `contract_client.py`, `http_client.py` | Повторы отдельного HTTP-вызова |

Backoff instance: `5 × 3^(attempt-1)` секунд, максимум 900 секунд (5, 15, 45, …).

При transient error и доступных попытках worker возвращает instance в PENDING через `mark_instance_retry`. При permanent error или исчерпании попыток:

1. `mark_instance_failed`
2. событие `fsm.instance.failed` + webhook fan-out
3. завершение child в saga
4. отдельный Contract-вызов `on_failed` (если зарегистрирован)
5. `apply_declared` для recovery-ответа

Reconcile используется, когда domain commit уже произошёл, а platform commit не прошёл.
`reconcile_worker` докатывает только platform state/log/events/side-effects и **не повторяет**
domain command/effect.

**Зачем side-effects-only reconcile.** Sync invoke может вернуть только
`notify` / `cancel_instances` / `entity_states` без `entity_type`. Раньше
`_invoke_needs_reconcile` такие ответы пропускал — при сбое platform commit
outbox/cancel/state не докатывались.

**Как работает сейчас.**

1. `_invoke_needs_reconcile` (в `host/http/request_runtime.py`) = true, если есть
   `entity_type`, enqueue/saga/timers **или** непустые
   `notify` / `cancel_instances` / `entity_states`.
2. При dual-commit fail → `enqueue_reconcile` с `kind: invoke_command` и полным
   `result` (idempotent `transition_id` учитывает fingerprint длин side-effect списков).
3. `dock_invoke_command` (`host/reconcile_worker.py`):
   - с `entity_type` — bootstrap/enqueue + `apply_declared`;
   - только side-effects — только `apply_declared` (без graph bootstrap);
   - domain command **не** вызывается повторно.

**Проверка.** `python -m unittest tests.test_invoke_reconcile_side_effects`.

### 7.6. Безопасность worker

Worker — доверенный процесс платформы, выделенный для tenant. Он не передаётся арендатору: tenant не получает его env, DB credentials, shell или доступ к runtime/container. Domain service запускается в отдельной security boundary (отдельный container/OS user, без общих volumes и process namespace с worker).

#### 7.6.1. Логи и маскирование секретов

**Зачем.** Worker и Platform API пишут в stdout/файл traceback SQLAlchemy и драйвера.
Без защиты туда попадают пароли JDBC URL, bind-параметры SQL и значения
`PLATFORM_SECRETS_KEY` / токенов — риск при шаринге логов, CI-артефактах и
компрометации хоста. Tenant не должен видеть raw SQL/traceback в HTTP-ответах.

**Как работает.**

1. Все SQLAlchemy engines создаются с `hide_parameters=True`
   (`host/engines.py`, `domain_runtime/session.py`). В тексте
   `StatementError` параметры заменяются на
   `[SQL parameters hidden due to hide_parameters=True]`.
2. Центральный `logging.Filter` — `host/log_redaction.py` (`RedactingFilter`):
   - маскирует URI вида `scheme://user:password@host/…`;
   - маскирует пары `*_TOKEN` / `*_SECRET` / `*_PASSWORD` / `*_API_KEY`;
   - подставляет `***` вместо значений из env (`PLATFORM_DATABASE_URL`,
     `DOMAIN_DATABASE_URL`, `PLATFORM_SECRETS_KEY`, admin/contract/telegram secrets).
3. Фильтр ставится при старте процесса:
   - `fsm_worker.py` — сразу после `basicConfig`;
   - `main.py` (Platform API) — аналогично.
4. Для осознанной диагностики URL: `safe_db_url(url)` →
   `make_url(…).render_as_string(hide_password=True)`.

**Границы.** Redaction — best-effort для текста логов; не замена ACL на файлы
логов и не tenant-visible audit API. Разделение internal vs tenant-facing
каналов (п.6) и scrubbing всех HTTP `detail=str(exc)` — отдельные усиления.
Логи worker по-прежнему считаются **внутренними** (не отдаются арендатору).

**Проверка.** Unit: `python -m unittest tests.test_log_redaction`. Вручную:
спровоцировать DB error на worker и убедиться, что в traceback нет пароля URL
и plaintext `PLATFORM_SECRETS_KEY`.

Обязательные правила (итог):

1. Не логировать исходные DB URL, graph URLs, user/host/database, токены, пароли, `PLATFORM_SECRETS_KEY`.
2. В сообщениях предпочитать `db_role=platform|graph`, `service_id`, operation/error code.
3. Engines с `hide_parameters=True`.
4. Диагностический URL — только через `safe_db_url` / `hide_password=True`.
5. Центральный logging filter на URI / secret keys / env values / credential-like payloads.
6. Tenant-visible ответы: `service_id`, instance id, operation, безопасный error code — без SQL/traceback.
7. HTTP/events не возвращают raw exception, SQL, bind parameters или stack trace арендатору.

#### 7.6.2. Защита от SQL injection

**Зачем.** Platform/worker выполняют SQL к platform и graph DB. Конкатенация
пользовательских значений в текст запроса → классический SQL injection.
Правила ниже — обязательный стиль кода; CI ловит регрессии.

**Правила platform DB и graph SQL:**

1. Все значения — bind-параметры (`:service_id`, `:instance_id`, …); f-string/конкатенация пользовательских значений в SQL запрещены.
2. Имена таблиц, колонок, `ORDER BY` и SQL fragments нельзя брать напрямую из Contract/domain payload. Для динамических identifiers — закрытый whitelist.
3. Domain Contract не принимает и не передаёт произвольный SQL для выполнения платформой.
4. DB user worker: минимальные `SELECT`/`INSERT`/`UPDATE`/`DELETE` только на нужные таблицы; без DDL/GRANT/FILE.
5. Multi-statements отключены; platform DB — только во внутренней сети.
6. Ошибки SQL → безопасные platform error codes; текст драйвера — только во внутреннем журнале после redaction (§7.6.1).
7. **CI:** workflow `.github/workflows/security-sql.yml` запускает
   `python tools/check_dynamic_sql.py` на `fsm_platform/**`.
   Скрипт ищет f-string / `+` / `%` / `.format` со строками, содержащими
   `SELECT|INSERT|UPDATE|DELETE`. Локально: тот же команда из корня репо.
   Известные безопасные места (whitelist колонок + bind params) перечисляются в
   `tools/check_dynamic_sql.py` → `WHITELIST`; расширение whitelist — только после review.
8. Любой новый динамический SQL — отдельный code review.

**Проверка.** `python tools/check_dynamic_sql.py` → exit 0.

#### 7.6.3. Ограничение последствий компрометации

**Зачем.** Один master `PLATFORM_SECRETS_KEY` на API и всех worker означает: утечка
ключа с одного worker-хоста даёт расшифровку secrets **всех** tenant. Нужна
модель, где dedicated worker (`WORKER_SERVICE_ID`) может unwrap только свой
`service_id`.

**Как работает (scoped Secret Broker).**

1. Master KEK по-прежнему в process env: `PLATFORM_SECRETS_KEY` (Fernet key).
2. Per-tenant DEK = HKDF-SHA256(KEK, info=`domain_secrets:{service_id}`) —
   модуль `host/secret_broker.py`.
3. Записи шифруются только в envelope `v2.{service_id}.{fernet_token}` (`wrap`).
4. `unwrap(service_id, ciphertext)` принимает **только** этот формат: сверяет
   `service_id` в envelope и расшифровывает tenant DEK. Иные blob’ы →
   `SECRETS_CIPHER_INVALID` (без fallback на master Fernet).
5. **Fail-closed worker:** если задан `WORKER_SERVICE_ID` и он ≠ запрашиваемый
   `service_id` → `SECRETS_SCOPE_DENIED` (worker чужие secrets не читает).
6. Platform API без `WORKER_SERVICE_ID` может CRUD/unwrap любого tenant
   (онбординг, admin secrets API).
7. Публичный API домена: `host/secrets.py` → broker; `service_id` из
   `runtime_context`.

После смены формата все ключи в `domain_secrets` нужно записать заново
(`PUT /v1/{service_id}/secrets`) — старые ciphertext без префикса `v2.` не читаются.

Это **dev/self-hosted broker**, не внешний AWS KMS: KEK всё ещё в env процесса.
Внешний KMS / Internal Worker API без DB URL — дальнейшее усиление.

**Проверка.** `python -m unittest tests.test_secret_broker`.

Прочие границы:

- `WORKER_SERVICE_ID` даёт логическую фильтрацию claim/boot; MySQL grants по-прежнему
  не режут строки по `service_id`.
- Worker — platform-owned, изолирован от domain process, минимальный DB role.

---

## 8. Путь запроса: фронт → запись в БД

Ниже — два основных пути. Имена файлов — фактические модули репозитория.

### 8.1. Sync command (`POST /v1/{service_id}/invoke`)

Типичный путь фронта: создать заказ, открыть ячейку, запрос без ожидания полного FSM (часть команд сразу ставит `enqueues[]`).

```text
[Клиент]
  POST /v1/{service_id}/invoke
  { "operation": "create_order", "params": {…}, "actor": {…} }

[Platform API]
  main.py
  host/http/app.py                    # route + auth
  host/operations.py                  # RemoteRef по catalog
  host/http/request_runtime.run_operation
    runtime_context.service_scope
    host/contract_invoke.call_operation
      host/contract_client            # HMAC headers
        → HTTP POST {contract}/contract/v1/commands/{operation}

[Domain service]
  domains/<name>/main.py
  domain_runtime/app.py + contract_auth middleware
  domain_runtime/dispatch.py          # DOMAIN_DATABASE_URL session
  domains/<name>/commands.py          # business SQL → commit domain DB
  ← JSON { entity_type, entity_id, initial_state, enqueue?, notify?, data, … }

[Platform API — продолжение]
  request_runtime._bootstrap_and_maybe_enqueue
    core/db_layer                     # INSERT entity_fsm_state, server_fsm_instances, timers…
    engines.graph_session             # graph_version (read)
  contract_side_effects.apply_declared
    side_effects.notify → platform_outbox
  platform_session.commit             # platform DB
  ← HTTP 200 клиенту

[Асинхронно, если был enqueue]
  Worker (§7.3) доводит FSM; outbox доставляет telegram / webhook / http_external
```

**Где что пишется на этом пути**

| Момент | БД | Таблицы / действие |
|--------|-----|-------------------|
| Domain dispatch commit | domain | business rows |
| bootstrap | platform | `entity_fsm_state`, опц. `server_fsm_instances`, `fsm_timers` |
| `apply_declared` | platform | `platform_outbox`, отмены instances, UPSERT states |
| Final commit API | platform | commit всей platform-транзакции invoke |

Если domain уже закоммитил, а platform commit упал, `_enqueue_invoke_reconcile` ставит задачу при условиях §7.5.

### 8.2. Async FSM (`enqueue` → worker)

```text
[Клиент]
  POST /v1/{service_id}/fsm/enqueue
  { process_name, entity_type, entity_id, payload }
    или command вернул enqueue / enqueues[]

[Platform]
  request_runtime.enqueue_instance
    db_layer.insert_fsm_instance → PENDING
  ← 202 { instance_id, status_url }

[Worker]
  claim → run_instance → … (см. §7.3)
  Domain: context / guards / effects (HTTP)
  Platform: entity_fsm_state, fsm_transition_logs, outbox
  Domain effects: business SQL в domain DB

[Клиент poll]
  GET /v1/{service_id}/fsm/instances/{id}
    request_runtime.get_instance → db_layer
```

`Idempotency-Key` в header делает enqueue идемпотентным в рамках `(service_id, scope="enqueue", key)`: повтор возвращает сохранённый `instance_id` и не создаёт второй instance. `request_runtime.enqueue_instance` также разрешает гонку двух запросов через повторное чтение сохранённого ответа.

### 8.3. Query (только чтение бизнеса)

Тот же `invoke`, kind=`query`: Contract `POST /queries/…` → domain SELECT → ответ. Для query платформа не запускает bootstrap, enqueue, timers и `apply_declared`; платформенные поля в query-ответе не применяются.

### 8.4. Telegram inbound

```text
Telegram → POST /input/telegram/{service_id}/webhook
  host/http/app.py
  input/telegram/webhook.handle_telegram_update
    output/telegram/settings          # token/username из domain_secrets
    verify deep-link (TELEGRAM_LINK_SECRET)
    Contract POST /commands/bind_telegram
    output/telegram/sender            # reply пользователю
```

Канал `input/telegram` — I/O платформы: разбор Update, проверка deep-link, ответ пользователю. После успешной проверки payload вызывает Contract command с именем **`bind_telegram`** (конвенция этого input-модуля).

Параметры команды: `user_id`, `chat_id`. Схему хранения привязки задаёт домен в своём handler (например запись chat id в business-таблицу пользователя). Для работы привязки через этот webhook домен регистрирует operation `bind_telegram` в catalog.

Секреты бота: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_LINK_SECRET` в `domain_secrets`. Webhook URL: `POST /input/telegram/{service_id}/webhook`. Deep-link для приложения: `GET /input/telegram/{service_id}/link?user_id=`.

---

## 9. Регистрация, авторизация арендатора и secrets

### 9.1. Хранение

- Таблица platform DB: `domain_secrets` (`service_id`, `key`, `value_enc`).
- Шифрование at-rest: Fernet(`PLATFORM_SECRETS_KEY`) — ключ **процесса платформы** (не отдаётся арендатору).
- Чтение/запись значений — в `service_scope(service_id)` (`host/secrets.py`).

### 9.2. Реализованная модель tenant onboarding

Зарегистрированный арендатор (`domain_admin`) выпускает tenant-scoped
`DOMAIN_ADMIN_TOKEN`, регистрирует им один или несколько `service_id` и использует
тот же тип токена для всего service-scoped API своих доменов.

#### 9.2.1. Модель данных

| Сущность | Назначение |
|----------|------------|
| `tenant_accounts` | Учётная запись `domain_admin`: id, email, password hash, verification/status |
| `tenant_refresh_tokens` | Hash refresh token, rotation/revoke/expiry и данные сессии |
| `domain_admin_tokens` | `tenant_account_id`, token hash, prefix/id, created/expires/revoked, last_used |
| `domain_services` | Runtime-регистрация домена, lifecycle и обязательный владелец `tenant_account_id` |
| `domain_secrets` | Зашифрованные значения graph/contract/Telegram/credentials |
| `platform_audit_events` | Security audit tenant/token/domain операций |

Raw `DOMAIN_ADMIN_TOKEN` возвращается только при выпуске. В БД хранится криптографический hash токена, а не raw token и не запись в `domain_secrets`.

Ролей `owner/admin/viewer` и таблицы membership нет. Один tenant account всегда
имеет одну роль `domain_admin`, может владеть несколькими `service_id`, а каждый
`service_id` принадлежит ровно одному account через `domain_services.tenant_account_id`.

#### 9.2.2. Tenant authentication

1. Свободная self-service регистрация tenant account и подтверждение email.
2. Login по email/password → короткоживущий access token и ротируемый refresh token.
3. Access token используется только для управления account и выпуска/отзыва `DOMAIN_ADMIN_TOKEN`.
4. Арендатор выпускает tenant-scoped `DOMAIN_ADMIN_TOKEN`.
5. Этим token арендатор регистрирует домен; платформа записывает владельца в `domain_services.tenant_account_id`.
6. Доступ к `/v1/{service_id}/…` разрешён, только если account токена владеет `service_id`.
7. Platform-wide операции используют отдельный `PLATFORM_ADMIN_TOKEN` и не принимают tenant token.

#### 9.2.3. Выпуск `DOMAIN_ADMIN_TOKEN`

1. Аутентифицированный tenant account запрашивает выпуск токена.
2. Платформа генерирует криптографически случайный `DOMAIN_ADMIN_TOKEN`.
3. Hash сохраняется в `domain_admin_tokens` с `tenant_account_id`; raw token возвращается один раз.
4. Арендатор передаёт token в `X-Admin-Token` при регистрации домена и во всех `/v1/{service_id}/…`.
5. Один token действует для всех текущих и будущих `service_id` этого account, но не даёт доступа к чужим доменам.
6. Поддерживаются list, rotate, revoke, expiry и несколько активных токенов.

#### 9.2.4. API

| Метод | Авторизация | Назначение |
|-------|-------------|------------|
| `POST /v1/auth/register` | public | Создать tenant account |
| `POST /v1/auth/verify-email` | public verification token | Подтвердить email |
| `POST /v1/auth/login`, `/refresh`, `/logout` | credentials/refresh | Управление login session |
| `POST/GET /v1/tenant/admin-tokens` | tenant access token | Выпустить/list token |
| `POST …/admin-tokens/{token_id}/rotate|revoke` | tenant access token | Ротация/отзыв token |
| `POST /v1/tenant/domains` | `DOMAIN_ADMIN_TOKEN` | Зарегистрировать domain, получить `service_id` |
| Все `/v1/{service_id}/…` | `DOMAIN_ADMIN_TOKEN` | API принадлежащего account домена |
| Platform Admin API | `PLATFORM_ADMIN_TOKEN` | Platform-wide управление |

#### 9.2.5. Проверка `DOMAIN_ADMIN_TOKEN`

1. Найти token record по безопасному hash и проверить expiry/revoked status.
2. Получить `tenant_account_id` токена.
3. Для service-scoped route взять `service_id` из URL и проверить владельца в `domain_services`.
4. При несовпадении вернуть deny без раскрытия существования чужого `service_id`.
5. Записать audit event (`tenant_account_id`, `service_id`, token id, operation, result, source).
6. Применить rate limit к неуспешным проверкам.

### 9.3. API secrets и credentials

Tenant routes принимают только `DOMAIN_ADMIN_TOKEN`.
`PLATFORM_ADMIN_TOKEN` на них не является fallback.

```http
PUT /v1/{service_id}/secrets
X-Admin-Token: <DOMAIN_ADMIN_TOKEN>
Content-Type: application/json

{ "key": "contract_base_url", "value": "http://127.0.0.1:8100" }
```

```http
GET /v1/{service_id}/secrets
X-Admin-Token: <DOMAIN_ADMIN_TOKEN>
→ { "keys": ["contract_base_url", "graph_database_url", …] }   # без values
```

```http
DELETE /v1/{service_id}/secrets/{key}
X-Admin-Token: <DOMAIN_ADMIN_TOKEN>
```

После смены `contract_*` или graph URL — reload домена / рестарт API и worker.

### 9.4. Стандартные ключи онбординга

| key | Кто читает | Зачем |
|-----|------------|-------|
| `graph_database_url` | `boot` / `engines` через `db_graph_secret_ref` | Graph read SQL |
| `graph_write_database_url` | то же write-ref | Publish graph |
| `contract_base_url` | `contract_client.resolve_contract_config` | Base URL domain service |
| `contract_shared_secret` | то же | HMAC; = `CONTRACT_SHARED_SECRET` домена |
| `TELEGRAM_BOT_TOKEN` | `output/telegram/settings` | Bot API |
| `TELEGRAM_BOT_USERNAME` | deep-link | `t.me/<bot>?start=` |
| `TELEGRAM_LINK_SECRET` | `input/telegram/webhook` | Подпись `/start` |
| `INPUT_HOOK_SECRET_<CHANNEL>` / `INPUT_HOOK_SECRET` | `input/generic/webhook` | Auth партнёра на generic inbound |

Отдельно — **credentials** сторонних API (произвольные имена ключей, JSON value): см. §10.

### 9.5. Цепочка использования

```text
Tenant register/verify/login → DOMAIN_ADMIN_TOKEN → register domain
DOMAIN_ADMIN_TOKEN → весь /v1/{service_id}/… только своих доменов
     ↓
Boot / runtime:
  tenant_config.resolve_tenant_ref(service_id, ref)
    1) ref содержит :// → литерал URL
    2) иначе get_domain_secret(ref) под service_scope
       ↓
  engines / contract_client / telegram / call_api
```

Process `.env` платформы: `PLATFORM_DATABASE_URL`, `PLATFORM_SECRETS_KEY`,
`PLATFORM_ADMIN_TOKEN`, `TENANT_AUTH_SECRET`, mail/SMTP config. У worker — ещё
`WORKER_SERVICE_ID`. Tenant-конфиг — в `domain_secrets`.

### 9.6. Критерии готовности tenant auth

1. Таблицы tenant accounts, verification/refresh sessions, hashed admin tokens, audit events и owner FK в `domain_services`.
2. Register/verify/login/refresh/logout.
3. Issue/list/rotate/revoke tenant-scoped `DOMAIN_ADMIN_TOKEN`.
4. Разделение Public Auth, Tenant Account, Platform Admin, Domain API и Domain Input в FastAPI/Swagger.
5. Все `/v1/{service_id}/…` закрыты domain token; platform token только Platform Admin API.
6. Domain register/connect и worker `1 process = 1 service_id`.
7. Domain process без `PLATFORM_DATABASE_URL`/`PLATFORM_SECRETS_KEY`: `call_api`
   через platform `POST /v1/{service_id}/external/call` (HMAC + `PLATFORM_API_BASE_URL`).
8. Route-matrix/security/E2E: register → verify → login → token issue → domain register → secrets/credentials → connect → worker ready.

---

## 10. Credentials и сторонний API

### 10.1. Что такое credential

Credential — секрет в `domain_secrets`, value = **JSON-объект** с типом авторизации и `base_url`. Имя ключа выбирает домен (`PARTNER_API`, `PAYMENT_GW`, …).

Формат (`fsm_platform/core/http_client.py`):

```json
{
  "type": "bearer_token | api_key_header | basic_auth | custom | none",
  "base_url": "https://api.example.com",
  "token": "…",
  "api_key": "…",
  "header_name": "x-api-key",
  "username": "…",
  "password": "…",
  "signer": "package.module:sign_fn",
  "fields": {}
}
```

| `type` | Поля |
|--------|------|
| `bearer_token` | `token` |
| `api_key_header` | `api_key`, опц. `header_name` |
| `basic_auth` | `username`, `password` |
| `custom` | `fields` + `signer="module.path:func"` |
| `none` | только `base_url` (публичный API) |

### 10.2. Создание credential

Credential создаёт арендатор с tenant-scoped `DOMAIN_ADMIN_TOKEN`;
platform token этот endpoint не принимает:

```http
PUT /v1/{service_id}/secrets
X-Admin-Token: <DOMAIN_ADMIN_TOKEN>

{
  "key": "PARTNER_API",
  "value": "{\"type\":\"bearer_token\",\"base_url\":\"https://api.partner.com\",\"token\":\"…\"}"
}
```

`SecretBody.value` принимает строку, object или array; object/array API сериализует в компактный JSON перед шифрованием.

### 10.3. Вызов из домена: `call_api`

```python
from fsm_platform.host import side_effects

resp = side_effects.call_api(
    "PARTNER_API",          # credential_key = имя секрета
    method="POST",
    path="/v1/orders",
    json_body={...},
)
```

- Domain process: HMAC → platform `POST /v1/{service_id}/external/call`
  (`PLATFORM_API_BASE_URL` + `CONTRACT_SHARED_SECRET`).
- Platform: читает credential из `domain_secrets` в `service_scope`, выполняет HTTP
  на `base_url` + path с нужной auth.
- Ошибки: `EXTERNAL_API` / `EXTERNAL_API_TRANSIENT` (для retry FSM).
- Имя стороннего продукта и его протокол принадлежат картриджу; платформа
  использует обобщённый credential и канал `http_external`.

### 10.4. Асинхронная доставка через outbox

Если вызов наружу должен идти после commit FSM:

1. Домен в `notify[]` указывает `channel: http_external` (и обычно `destination` = credential_key).
2. Платформа пишет `platform_outbox`.
3. `outbox_worker` → Contract `POST /outbox/deliver` на domain service.
4. Domain outbox-handler (из `set_outbox_handler` / `register_all`) выполняет vendor-логику, часто через `call_api`.

Sync-путь (сразу в command/effect) и async-путь (outbox) используют **одни и те же** credentials в `domain_secrets`.

---

## 11. Input (входящие каналы)

| Путь | Файл | Роль |
|------|------|------|
| `POST /input/telegram/{service_id}/webhook` | `input/telegram/webhook.py` | Update, deep-link, Contract `bind_telegram`, reply |
| `GET /input/telegram/{service_id}/link?user_id=` | то же + `app.py` | Выдать `t.me/…?start=` |
| `POST /input/generic/{service_id}/{channel}` | `input/generic/webhook.py` | Универсальный inbound → Contract `hooks/{channel}` |

Онбординг бота: `setWebhook` → URL платформы с `{service_id}`. Секреты бота — в `domain_secrets`. Условия команды `bind_telegram` — §8.4.

### 11.1. Generic inbound (`input/generic`)

Базовый канал для YooKassa, SMS-gateway, произвольного партнёра. Платформа
не знает протокол провайдера: проверяет доступ, проксирует body/headers/query
в domain Contract `POST /hooks/{channel}`, применяет `apply_declared`.

**Регистрация канала (домен):**

```python
from fsm_platform.domain_runtime import hooks

hooks.register(service_id, "payment", on_payment_webhook)
```

После `connect` / reload catalog канал виден в `GET …/catalog` → `hooks`.

**Секрет** в `domain_secrets` (fail-closed):

| Ключ | Смысл |
|------|--------|
| `INPUT_HOOK_SECRET_<CHANNEL>` | Секрет конкретного канала (`payment` → `INPUT_HOOK_SECRET_PAYMENT`) |
| `INPUT_HOOK_SECRET` | Fallback на все каналы tenant |

**Auth партнёра** (один из вариантов):

1. Header `X-Input-Secret: <secret>`
2. HMAC: `X-Input-Timestamp` + `X-Input-Signature` =
   `hex(hmac_sha256(secret, "{timestamp}." + raw_body))` (skew ≤ 300s)

---

## 12. Output (исходящие каналы)

### 12.1. Производители → outbox

Строки `platform_outbox` создаёт платформа:

- `host/side_effects.notify` (прямой вызов из host-кода)
- `host/contract_side_effects.apply_declared` при наличии `notify[]` в ответе Contract (§5.4.6)
- `host/webhooks.emit_event_with_webhooks` (fan-out подписок → `channel=webhook`)

### 12.2. Доставка (`host/outbox_worker.py`)

| channel | Модуль доставки | Поведение |
|---------|-----------------|-----------|
| `telegram` | `output/telegram/sender.py` | Bot API `sendMessage` |
| `webhook` | `output/webhook/sender.py` | HMAC POST на URL подписки клиента |
| `http_external` | Contract `POST /outbox/deliver` | Сторонняя интеграция исполняется в domain service |
| `log` / `dry_run` | лог воркера | Без внешней сети |

`destination` для `http_external` обычно = имя credential-ключа (см. §10).

### 12.3. Другие исходящие без outbox

| Канал | Механизм |
|-------|----------|
| Poll instance / history | `GET …/fsm/instances/{id}`, history |
| Events poll | `GET …/events` |
| WebSocket | `host/http/events_ws.py` |
| Sync HTTP ответ invoke | тело ответа command/query |

---

## 13. Таймеры, state-timeouts, расписания

### 13.1. Runtime-таймеры (`fsm_timers`)

Таблица platform DB для отложенного запуска FSM-процесса.

**Жизненный цикл**

1. Платформа создаёт строку `SCHEDULED` с `fire_at`, `process_name`, entity, `payload`, опц. `idempotency_key`.
2. Worker (`host/worker._fire_due_timers`): строки с `fire_at <= now` → `insert_fsm_instance` + статус таймера `FIRED`.
3. Дальше обычный FSM pipeline по поставленному instance.

**Планирование из ответа command**

Модуль: `host/http/request_runtime._apply_timers` → `host/side_effects.schedule_timer`.

В теле ответа sync command:

| Поле | Назначение |
|------|------------|
| `timers[]` | Список таймеров к постановке |
| `cancel_timers[]` | Отмена по `idempotency_key` |

Элемент `timers[]`:

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `process_name` | да | какой процесс enqueue при срабатывании |
| `entity_type` / `entity_id` | да | сущность instance |
| `fire_at` | да | ISO datetime (UTC/naive по конвенции API) |
| `idempotency_key` | нет | UNIQUE `(service_id, idempotency_key)`; повторный INSERT с тем же ключом завершает platform-транзакцию ошибкой duplicate key |
| `payload` | нет | JSON в instance при fire |
| `owner` | нет | метка владельца (`domain` по умолчанию) |

```json
{
  "timers": [{
    "process_name": "expire_reservation",
    "entity_type": "reservation",
    "entity_id": 42,
    "fire_at": "2026-07-29T12:00:00",
    "idempotency_key": "reservation:42:expire",
    "payload": {},
    "owner": "domain"
  }],
  "cancel_timers": [{ "idempotency_key": "reservation:42:expire" }]
}
```

**Планирование из графа (state-timeout)** — §13.2: после перехода платформа сама ставит/сбрасывает таймер по политике `fsm_states`.

Декларации `notify` / `cancel_instances` / `entity_states` — §5.4 (`apply_declared`). Планирование `timers[]` / `cancel_timers[]` из command — `request_runtime._apply_timers` (этот подраздел).
### 13.2. Таймауты на состояниях графа (state-timeout)

Политика времени задаётся в graph SQL на строке `fsm_states`: колонки `timeout_seconds`, `timeout_event`, `timeout_owner`. Это декларация графа (как `guard_name` на transition), а не runtime-строка в business-таблицах домена.

После успешного apply перехода `transition_runner` вызывает `host/state_timeouts.reschedule_after_transition`:

```text
transition → to_state
  → cancel таймер с idempotency_key сущности
  → при наличии timeout_* у to_state → schedule_timer
       fire_at = now + timeout_seconds
       process = ProcessDef, у которого runtime_event_name == timeout_event
  → worker later: enqueue process → обычный FSM (guards/effects)
```

Idempotency key: `state_timeout:{service_id}:{entity_type}:{entity_id}`.

### 13.3. Расписания (`fsm_schedules`)

Периодический enqueue процесса. Public API:

| Метод | Назначение |
|-------|------------|
| `POST /v1/{service_id}/schedules` | Создать: `process_name`, `interval_seconds`, опц. entity |
| `GET /v1/{service_id}/schedules` | Список |
| `POST …/schedules/{id}/pause` | PAUSED |
| `POST …/schedules/{id}/resume` | ACTIVE |

Worker (`_fire_due_schedules`): ACTIVE с `next_run_at <= now` → enqueue `process_name`, сдвиг `next_run_at`. При необходимости создаёт `entity_fsm_state` для entity расписания.

Отличие от таймера: таймер — разовый `fire_at`; schedule — повторяющийся interval.

---

## 14. Guard routing, Companions, Domain Validator

### 14.1. Guard routing

На шаге FSM (`transition_repository` + `transition_runner`):

1. Из graph DB выбираются кандидаты рёбер: тот же `from_state`, `event_name`, `graph_version`.
2. Сортировка: `priority ASC`, затем `id ASC`.
3. Обход по порядку:
   - `guard_name` пустой / NULL → ребро **безусловное**, выбирается сразу;
   - иначе Contract `POST /guards/{name}` → `ok` / `reason`;
   - первый guard с `ok=true` побеждает;
   - если никто не ok → `NO_GUARD_MATCHED`.
4. Два кандидата с одинаковым `priority` → runtime `AMBIGUOUS_TRANSITION`.

Меньший `priority` = выше приоритет проверки.

Validator дополнительно требует:

- не более одного NULL guard в группе `(entity_type, from_state, event_name)`;
- NULL guard имеет **наибольшее числовое** значение priority, то есть проверяется последним;
- нарушение даёт `AMBIGUOUS_DEFAULT_GUARD` или `DEFAULT_GUARD_PRIORITY`.

### 14.2. Параметры guard/effect

`fsm_transitions.guard_params` и `effect_params` — JSON-конфиг конкретного ребра:

- `guard_params` передаётся в Contract guard без изменения;
- `effect_params` передаётся в Contract effect;
- служебный ключ `effect_params.companions` удаляется перед вызовом effect, потому что его обрабатывает runner;
- параметры являются конфигурацией графа, а runtime context/instance передаются отдельными полями Contract-запроса.

### 14.3. Companions (multi-entity)

После успешного primary-ребра runner читает `effect_params.companions` (JSON в графе на primary transition). Для каждого элемента — **полный** pipeline (candidates → guards → apply → effect) на другой entity.

Спека элемента companion:

| Поле | Смысл |
|------|--------|
| `entity_type` | Тип companion-сущности |
| `event_name` | Событие/рёбра для companion |
| `entity_id_key` | Ключ в **domain context** primary, откуда взять id |

Context строится один раз на process-step (primary); companions делят тот же context. Fail любого companion → FAILED всего шага (`COMPANION_FAILED`). Ключ `companions` из `effect_params` в effect callable не передаётся (оркестрация только runner).

Пример (идея): primary `order` + companion `locker_cell` с id из `context.source_cell_id`.

### 14.4. Domain Validator

Файл: `host/domain_validator.py`. Запуск: boot и `POST /v1/admin/domains/{service_id}/reload`.

Проверяет **catalog ↔ RAM RemoteRef ↔ graph SQL** (handlers не исполняет).

Blocking-проверки:

- catalog содержит `cartridge_type`, `version`, корректные operations/processes;
- operation name/kind корректны, handler в RAM является `RemoteRef`;
- catalog operations/processes совпадают с зарегистрированными RAM refs;
- `ProcessDef` содержит корректные `service_id`, `process_name`, `entity_type`, event, context/on_failed refs;
- обязательные graph-таблицы доступны;
- initial state существует и не неоднозначен;
- для каждого process есть candidates по `(entity_type, event_name)`;
- правила default/NULL guard из §14.1;
- все `guard_name` / `effect_name` графа зарегистрированы;
- graph DB доступна и читается.

Warnings (не блокируют): orphan guard/effect в registry без ссылок из графа.

`ok=false` → tenant не ready, Public API: HTTP 503 `DOMAIN_NOT_READY`. Отчёт: `errors` / `warnings` / `stats`.

---

## 15. Contract API (сводка)

Полные схемы тел: [domain-contract-api-v1.md](domain-contract-api-v1.md).

Префикс `/contract/v1`, HMAC: `X-Service-Id`, `X-Contract-Timestamp`, `X-Contract-Signature`. `GET /catalog` доступен при bootstrap без HMAC; остальные Contract endpoints проходят middleware-проверку.

| Метод | Назначение |
|-------|------------|
| `GET /catalog` | operations, processes, guards, effects |
| `POST /context/{name}` | context builder |
| `POST /guards/{name}` | GuardResult |
| `POST /effects/{name}` | EffectResult (+ декларации) |
| `POST /commands/{operation}` | sync command |
| `POST /queries/{operation}` | sync query |
| `POST /processes/{name}/on-failed` | recovery |
| `POST /outbox/deliver` | async delivery для `channel=http_external` |
| `POST /hooks/{channel}` | domain-side handler; вызывается платформой из `/input/generic` |

Pipeline шага: `context → guard → transition → effect` (+ companions, + state-timeout reschedule).

---

## 16. E2E автотестер (`tools/domain_e2e`)

### 16.1. Назначение

Гоняет YAML-сценарии против **живого** стека (Platform API + worker + domain service), не против моков. Проверяет sync invoke, async FSM (poll instance), capture переменных, expect по JSON.

Подробности запуска: [tools/domain_e2e/README.md](../tools/domain_e2e/README.md).

### 16.2. Структура

```text
tools/domain_e2e/
  __main__.py / runner.py   # CLI
  client.py                 # HTTP к Platform API (+ optional Bearer)
  scenario.py               # загрузка YAML, подстановки {{var}}
  report.py                 # Markdown отчёт
  scenarios/courier/*.yaml  # сценарии домена
  reports/                  # e2e_<timestamp>.md (обычно gitignore)
```

### 16.3. Предусловия

1. Domain service up (Contract).
2. Platform API up, tenant bootstrapped (secrets + catalog ok).
3. Worker up с `WORKER_SERVICE_ID` этого tenant.
4. Перед прогоном очистка:
   - domain: применить `database/sql/domain/012_clear_test_data.sql`, затем `CALL clear_test_data();`
   - platform: `database/sql/platform/003_clear_test_runtime.sql`
   Чистить только domain недостаточно: `entity_fsm_state` / instances живут на platform.

### 16.4. Запуск

```bash
cd C:\FSM_Platform
set PYTHONPATH=C:\FSM_Platform

python -m tools.domain_e2e.runner scenarios/courier/client_self_pickup.yaml
python -m tools.domain_e2e.runner scenarios/courier/
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--base-url` | `http://127.0.0.1:8000` | Platform API |
| `--service-id` | — | override YAML `service_id` |
| `--report` | `reports/e2e_<timestamp>.md` | отчёт |
| `--poll-timeout` | `30` | ожидание instance |
| `--poll-interval` | `0.5` | интервал poll |
| `--continue-on-fail` | off | не останавливать цепочку шагов |

Exit: `0` ok, `1` fail сценария, `2` path/API unavailable.

### 16.5. Контракт YAML

Обязателен корневой `service_id` (multi-tenant).

Типичный шаг:

```yaml
- name: create_order
  operation: create_order
  actor: { actor_type: user, actor_id: "{{client_id}}", channel: api }
  params: { request_id: "{{request_id}}" }
  expect:
    status_code: 200
    body: { data.status: order_created }
  capture: { order_id: data.order_id }
  wait_instance: true
  expect_instance: { status: COMPLETED }
```

- `{{var}}` — подстановка из `vars` / `capture`
- `capture` — JSON-path относительно тела ответа
- `wait_instance: true` — ждать terminal status через Public API poll
- `capture_instance` — взять значение из ответа poll instance
- `wait_until` — повторять шаг до выполнения условия/таймаута
- Auth: `DOMAIN_ADMIN_TOKEN` обязателен для invoke/poll; готовый actor Bearer
  передаётся отдельно, если включён `PLATFORM_AUTH_SECRET`

Сценарии courier покрывают happy-path и отдельные ветки. Порядок зависимых сценариев — в README e2e.

### 16.6. Что E2E доказывает

| Слой | Проверка |
|------|----------|
| Public API | invoke/enqueue/instance status |
| Contract | commands/guards/effects реально отвечают |
| Worker | instances доходят до COMPLETED |
| Secrets + outbox | при сценариях с TG — доставка (или dry-run) |
| Dual DB | business на domain + state на platform согласованы после clear-скриптов |

E2E — приёмочный контур «стек живой»; рядом с ним остаются Domain Validator и unit-тесты домена.

---

## 17. HTTP API и границы авторизации (справка)

Все routes с префиксом `/v1/{service_id}/…` требуют
`X-Admin-Token: DOMAIN_ADMIN_TOKEN`. Проверяется, что account токена владеет
`service_id`. `PLATFORM_ADMIN_TOKEN` на этих routes не принимается.

| Метод | Назначение |
|-------|------------|
| `GET /v1/health` | Platform health; политика Platform Admin |
| `GET /v1/metrics` | Метрики; политика Platform Admin |
| `POST /v1/auth/register|verify-email|login|refresh|logout` | Public/session tenant auth |
| `POST/GET /v1/tenant/admin-tokens…` | Выпуск/управление domain token по login access token |
| `POST /v1/tenant/domains` | Регистрация домена по `DOMAIN_ADMIN_TOKEN` |
| `POST …/invoke` | sync command/query → Contract |
| `POST …/fsm/enqueue` | async process; поддерживает `Idempotency-Key` (§8.2) |
| `GET …/fsm/instances/{id}` | статус instance |
| `GET …/catalog` | discovery (RAM после bootstrap) |
| `POST …/entities/{type}/{id}/actions` | Доступные переходы с read-only guard evaluation |
| `GET …/entities/{type}/{id}/history` | История переходов |
| `GET …/events` | Cursor-poll событий |
| `WS …/ws/events` | WebSocket событий |
| `POST/GET …/webhooks` | Создание/список outbound subscriptions |
| `POST …/webhooks/{id}/deactivate` | Отключить subscription |
| `POST/GET …/schedules` (+ pause/resume) | периодические процессы |
| `POST …/graph/publish` | Публикация новой версии графа |
| `PUT/GET/DELETE …/secrets` | `DOMAIN_ADMIN_TOKEN` |
| `POST …/connect|reload` | Tenant lifecycle по `DOMAIN_ADMIN_TOKEN` |
| Platform Admin routes | Только `PLATFORM_ADMIN_TOKEN` |
| `POST /input/telegram/{service_id}/webhook` | Telegram Update |
| `POST /input/generic/{service_id}/{channel}` | Generic inbound (секрет / HMAC) |
| `GET /input/telegram/{service_id}/link` | deep-link |

Основные статусы: domain business error → HTTP 409; tenant не ready → 503 `DOMAIN_NOT_READY`; reload bootstrap failure → 502 `DOMAIN_BOOTSTRAP_FAILED`.

`/input/telegram/…` использует Telegram/link security, а Domain Contract API —
HMAC. Они не используют admin tokens. Browser frontend не получает
`DOMAIN_ADMIN_TOKEN`: доступ к service API и WebSocket идёт через доверенный
backend/BFF.

---

## 18. Разделение записи в БД

| Шаг | Кто | Куда |
|-----|-----|------|
| Transition + log | Platform (`TransitionExecutor`) | platform: `entity_fsm_state`, `fsm_transition_logs` |
| Effect / command business SQL | Domain service | domain DB |
| Outbox / events / timers / schedules | Platform | platform DB |
| Graph read / publish | Platform engines | domain DB **только** graph-таблицы |

Владелец записи: platform — FSM-инфраструктура; domain — business-таблицы. Graph-таблицы в domain DB платформа читает/публикует отдельными credentials.

---

## 19. Границы ответственности

- Исполнение бизнес-логики — через Contract API (`RemoteRef`).
- Business SQL — в domain service; `fsm_platform.core` работает с platform DB и graph SQL.
- Tenant-конфиг (graph/contract/Telegram/credentials) — в `domain_secrets`.
- Tenant account имеет одну роль `domain_admin`; владение доменами хранится в `domain_services.tenant_account_id`.
- Tenant-scoped `DOMAIN_ADMIN_TOKEN` закрывает весь `/v1/{service_id}/…`; `PLATFORM_ADMIN_TOKEN` действует только на Platform Admin API (§9).
- Platform `.env` — process config (`PLATFORM_*`, у воркера ещё `WORKER_SERVICE_ID`).
- `DOMAIN_DATABASE_URL` — в env процесса домена.
- Domain `call_api` → platform `POST /v1/{service_id}/external/call` (`PLATFORM_API_BASE_URL`);
  domain process без `PLATFORM_DATABASE_URL` / `PLATFORM_SECRETS_KEY` (§9.6 / §10.3).
- Telegram I/O — `input/` / `output/`; привязка аккаунта — доменная команда по конвенции `bind_telegram` (§8.4).
- Сторонний API — credentials + `call_api` / outbox `http_external` (§10); имена вендоров — у картриджа.
- Commit platform-транзакций — host (`request_runtime`, worker).
- Масштаб воркеров: N процессов с разным `WORKER_SERVICE_ID`.
- `platform_outbox` / `entity_fsm_state` / `fsm_timers` / `fsm_schedules` пишет платформа.

---

## 20. Критерии готовности

### Реализовано

- [x] Remote Contract catalog, commands, queries, context, guards, effects, on_failed
- [x] Graph engines + Validator + reload
- [x] Worker claim scope по `WORKER_SERVICE_ID`
- [x] Tenant-scoped worker boot (`boot(service_id)`)
- [x] Локальный worker provisioning/lifecycle через connect
- [x] Timers, state-timeouts, schedules, outbox, reconcile
- [x] Invoke/enqueue/status/actions/history/events/webhooks
- [x] Guard routing, `guard_params`/`effect_params`, companions
- [x] Telegram input/output и webhook output
- [x] Зашифрованные `domain_secrets` и credentials JSON
- [x] Tenant registration/verification/login/refresh (§9.2)
- [x] Выпуск/rotate/revoke tenant-scoped `DOMAIN_ADMIN_TOKEN`
- [x] Ownership authorization всего `/v1/{service_id}/…`, включая WebSocket
- [x] Разделение Public/Tenant/Platform Admin/Domain/Input routers и Swagger
- [x] Регистрация нескольких `service_id` одним tenant account
- [x] E2E YAML runner + tenant onboarding E2E

### В разработке

- [x] Изоляция domain process от platform DB при `call_api`
- [x] Worker log redaction + SQLAlchemy `hide_parameters=True` (§7.6.1)
- [x] Scoped Secret Broker/KMS вместо master-only decrypt на worker (§7.6.3)
- [x] CI-проверки SQL injection и динамического SQL (§7.6.2)
- [x] Reconcile для invoke с одними `notify` / `cancel_instances` / `entity_states` (§7.5)
- [x] Worker provisioner backends: systemd / Docker / Kubernetes (§7.1)

---

## 21. Глоссарий

| Термин | Смысл |
|--------|--------|
| `service_id` | Уникальный id domain service; назначает платформа, владелец — tenant account |
| `cartridge_type` | Тип картриджа (`courier`, …) |
| `PLATFORM_ADMIN_TOKEN` | Platform-wide token только для Platform Admin API |
| `DOMAIN_ADMIN_TOKEN` | Tenant-scoped token для регистрации доменов и всего API принадлежащих `service_id` |
| Contract API | HTTP API доменного сервиса |
| `RemoteRef` | Дескриптор удалённого handler на платформе |
| Catalog | JSON operations/processes/guards/effects |
| Graph DB | Таблицы `fsm_*` в domain DB |
| Credential | JSON в `domain_secrets` для `call_api` / внешней интеграции |
| `http_external` | Outbox-канал: доставка в domain `/outbox/deliver` |
| State-timeout | Политика `timeout_*` на `fsm_states` → runtime `fsm_timers` |
| Schedule | Периодический enqueue из `fsm_schedules` |
| Companion | Secondary entity pipeline из `effect_params.companions` |
| Guard routing | Выбор ребра: `priority ASC`, первый `ok` |
| `apply_declared` | `host/contract_side_effects`: применение `notify` / `cancel_instances` / `entity_states` (§5.4) |
| Dual-commit | Domain commit + platform commit; reconcile при сбое |
| Outbox | `platform_outbox` + worker → `output/*` или Contract deliver |

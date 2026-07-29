# Domain Contract API v1

Спецификация HTTP+JSON контракта между **платформой FSM** и **доменным сервисом** (отдельный процесс на tenant).

**Версия документа:** `1.0.0`  
**Префикс URL на стороне домена:** `/contract/v1`

## Назначение

Платформа оркестрирует FSM (instances, timers, sagas, entity state) в своей БД. Доменный сервис исполняет бизнес-логику:

- context builders
- guards
- effects
- commands и queries (`invoke`)
- recovery (`on_failed`)

**FSM-граф** (`fsm_states`, `fsm_transitions`, `fsm_graph_meta`, `fsm_actions`) в Contract API **не входит**. Платформа читает и публует граф напрямую по SQL (read-only / graph-write креды), см. план миграции.

## Транспорт

| Параметр | Значение |
|----------|----------|
| Протокол | HTTPS (HTTP допустим только в dev) |
| Формат | JSON, UTF-8 |
| Content-Type | `application/json; charset=utf-8` |

## Аутентификация (v1)

Взаимная HMAC-подпись по образцу webhook-подписи платформы (`output/webhook/sender.py`).

### Заголовки запроса (платформа → домен)

| Заголовок | Описание |
|-----------|----------|
| `X-Service-Id` | `service_id` tenant (например `svc_courier_01`) |
| `X-Contract-Timestamp` | Unix timestamp (секунды, UTC), строка |
| `X-Contract-Signature` | `hex(HMAC-SHA256(secret, canonical_string))` |

**Canonical string:**

```
{METHOD}\n{PATH}\n{SHA256_HEX_RAW_BODY}\n{TIMESTAMP}
```

- `METHOD` — uppercase (`GET`, `POST`)
- `PATH` — путь без query string, например `/contract/v1/guards/can_assign_executor`
- `SHA256_HEX_RAW_BODY` — SHA-256 тела запроса в hex; для `GET` без тела — SHA-256 пустой строки
- `TIMESTAMP` — то же значение, что в `X-Contract-Timestamp`

Домен проверяет подпись и отклоняет запросы старше **300 секунд** (дрейф часов).

### Секрет

- Один shared secret на пару `(platform, service_id)` в v1.
- Хранится на платформе в `domain_secrets` под ключом `contract_shared_secret` (Fernet).
- На домене — `CONTRACT_SHARED_SECRET` в `.env` доменного сервиса.

### Ответы домена

v1: домен **не** подписывает ответы; платформа доверяет TLS и сетевому периметру. Подпись ответов — возможное расширение v2.

## Общие типы

### Actor

Используется в commands/queries (аналог Public API `invoke`).

```json
{
  "actor_type": "user",
  "actor_id": "7",
  "channel": "api"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `actor_type` | string | нет | `user`, `system`, … |
| `actor_id` | string | нет | Opaque id актора (строка для JSON) |
| `channel` | string | нет | `api`, `telegram`, … |

### FsmInstance

Snapshot строки `server_fsm_instances` + runtime-поля для guards/effects/context.

```json
{
  "id": 123,
  "service_id": "svc_courier_01",
  "process_name": "assign_executor",
  "entity_type": "order",
  "entity_id": 45,
  "actor_id": 7,
  "payload_json": {},
  "graph_version": 3,
  "status": "PROCESSING",
  "attempts": 1
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `id` | integer | да | ID instance в platform DB |
| `service_id` | string | да | Tenant |
| `process_name` | string | да | Имя процесса |
| `entity_type` | string | да | Тип сущности |
| `entity_id` | integer | да | ID сущности в domain DB |
| `actor_id` | integer \| null | нет | Actor из instance |
| `payload_json` | object | нет | Payload процесса (объект, не SQL-строка) |
| `graph_version` | integer \| null | нет | Версия графа на момент claim |
| `status` | string | нет | `PENDING`, `PROCESSING`, … |
| `attempts` | integer | нет | Счётчик попыток |

### DomainError (HTTP 4xx)

Бизнес-ошибки домена (аналог `fsm_platform.core.domain_errors.DomainError`).

```json
{
  "error_code": "ORDER_NOT_FOUND",
  "message": "Order 45 not found"
}
```

| HTTP | Когда |
|------|-------|
| 400 | Невалидное тело / неизвестное имя в path |
| 401 | Неверная подпись / просрочен timestamp |
| 404 | Неизвестная operation / guard / effect / context_builder / process |
| 409 | `DomainError` (бизнес-правило) |
| 422 | Guard вернул `ok: false` (опционально; платформа может принимать 200 + `ok:false`) |
| 500 | Необработанное исключение домена |
| 503 | Домен временно недоступен |

Платформа маппит `409` + `error_code` в Public API как сегодня.

### GuardResult

```json
{
  "ok": true,
  "reason": null,
  "payload": null
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `ok` | boolean | Разрешён ли переход |
| `reason` | string \| null | Причина отказа при `ok: false` |
| `payload` | object \| null | Доп. данные для движка |

### EffectResult

```json
{
  "ok": true,
  "error": null,
  "payload": {}
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `ok` | boolean | Успех effect |
| `error` | string \| null | Текст ошибки при `ok: false` |
| `payload` | object \| null | Доп. данные |
| `notify` | array \| omit | Декларации outbox: `{channel, destination, event_type, payload, idempotency_key}` — **применяет платформа** |
| `cancel_instances` | array \| omit | Отмена PENDING: `{process_name, payload_match, except_instance_id?, last_error?}` |
| `entity_states` | array \| omit | UPSERT `entity_fsm_state`: `{entity_type, entity_id, state}` |

Домен **не** пишет в platform DB и **не** вызывает HTTP callback на платформу. Side-effects только в ответе; платформа применяет их в своей транзакции после успешного Contract call.

**Семантика commit:** домен **коммитит** domain DB транзакцию **до** ответа `200` на effects, commands и `on-failed`. Платформа коммитит platform DB отдельно (dual-commit + reconcile при сбое).

## Эндпоинты

### 1. `GET /contract/v1/catalog`

Метаданные картриджа. Заменяет `register_all()` + `manifest.yaml` для remote-доменов.

**Response 200:**

```json
{
  "cartridge_type": "courier",
  "version": "0.1.0",
  "operations": [
    {"operation": "create_order", "kind": "command"},
    {"operation": "list_client_orders", "kind": "query"}
  ],
  "processes": [
    {
      "process_name": "assign_executor",
      "entity_type": "order",
      "event_name": "assign_executor",
      "initial_state": "order_created",
      "context_builder": "build_order_context",
      "on_failed": false
    }
  ],
  "guards": ["can_assign_executor"],
  "effects": ["assign_executor_effect"],
  "context_builders": ["build_order_context"],
  "hooks": []
}
```

| Поле | Описание |
|------|----------|
| `cartridge_type` | Тип картриджа (`courier`, …) |
| `version` | Версия доменного пакета |
| `operations[]` | Sync invoke; `kind`: `command` \| `query` |
| `processes[]` | FSM-процессы платформы |
| `processes[].on_failed` | `true` если зарегистрирован recovery handler |
| `guards` / `effects` / `context_builders` | Имена для валидации графа |
| `hooks` | Имена optional generic inbound handlers |

---

### 2. `POST /contract/v1/context/{name}`

Вызов context builder (`ContextBuilder`).

**Request:**

```json
{
  "runtime_ctx": {},
  "instance": { }
}
```

`instance` — объект **FsmInstance** (см. выше). `runtime_ctx` — mutable dict между шагами одного `run_instance`.

**Response 200:** произвольный JSON-object (контекст). Все значения должны быть JSON-serializable (datetime → ISO-8601 строки).

---

### 3. `POST /contract/v1/guards/{name}`

**Request:**

```json
{
  "context": {},
  "guard_params": {},
  "instance": { }
}
```

**Response 200:** **GuardResult**.

---

### 4. `POST /contract/v1/effects/{name}`

**Request:**

```json
{
  "context": {},
  "effect_params": {},
  "instance": { }
}
```

**Response 200:** **EffectResult**. Domain transaction committed.

---

### 5. `POST /contract/v1/commands/{operation}`

Sync command (`kind=command`). Заменяет `handler(sd, params, actor)`.

**Request:**

```json
{
  "params": {},
  "actor": {
    "actor_type": "user",
    "actor_id": "7",
    "channel": "api"
  }
}
```

**Response 200:** тот же словарь, что возвращают текущие command handlers. Платформа обрабатывает поля в `request_runtime._bootstrap_and_maybe_enqueue`.

Минимальная схема (все поля опциональны, кроме случаев create-command):

```json
{
  "entity_type": "order",
  "entity_id": 45,
  "initial_state": "order_created",
  "related_entities": [
    {
      "entity_type": "locker",
      "entity_id": 10,
      "initial_state": "locker_free"
    }
  ],
  "enqueue": {
    "process_name": "assign_executor",
    "payload": {}
  },
  "enqueues": [
    {
      "process_name": "assign_executor",
      "entity_type": "order",
      "entity_id": 45,
      "initial_state": "order_created",
      "payload": {}
    }
  ],
  "saga": {
    "children": [],
    "on_success": null,
    "on_fail": null,
    "fail_policy": "fail_fast",
    "payload": {}
  },
  "timers": [
    {
      "process_name": "expire_reservation",
      "entity_type": "reservation",
      "entity_id": 1,
      "fire_at": "2026-07-28T12:00:00",
      "payload": {},
      "idempotency_key": "reservation:1:expire",
      "owner": "domain"
    }
  ],
  "cancel_timers": [
    {"idempotency_key": "reservation:1:expire"}
  ],
  "data": {}
}
```

| Поле | Описание |
|------|----------|
| `entity_type` + `entity_id` | Bootstrap `entity_fsm_state` |
| `initial_state` | Начальное состояние главной сущности |
| `related_entities[]` | Companion-сущности с `initial_state` |
| `enqueue` | Один FSM instance в очередь |
| `enqueues[]` | Несколько instances (batch) |
| `saga` | Старт saga (`children` обязателен если saga задан) |
| `timers` / `cancel_timers` | Планирование / отмена таймеров |
| `data` | Произвольный DTO для клиента Public API |

**Response 409:** **DomainError**.

Domain transaction committed on success.

---

### 6. `POST /contract/v1/queries/{operation}`

Sync query (`kind=query`). Тот же request что у commands.

**Response 200:** JSON-serializable dict (обычно `{"data": [...]}`).

**Response 409:** **DomainError**.

Read-only: домен не должен писать в domain DB (кроме audit, если явно предусмотрено).

---

### 7. `POST /contract/v1/processes/{process_name}/on-failed`

Recovery после терминального `FAILED` instance.

**Request:**

```json
{
  "instance": { },
  "last_error": "GUARD_REJECTED: stage not free"
}
```

**Response 200:**

```json
{
  "entity_states": [
    {"entity_type": "locker", "entity_id": 7, "state": "locker_free"}
  ],
  "cancel_instances": [
    {
      "process_name": "locker_reserve",
      "payload_match": {"request_id": 42},
      "except_instance_id": 100,
      "last_error": "SIBLING_RESERVE_FAILED"
    }
  ]
}
```

Domain recovery committed in domain DB; `entity_states` / `cancel_instances` / `notify` применяет платформа.

Если для процесса `on_failed: false` в catalog — домен отвечает **404**.

---

### 8. `POST /contract/v1/hooks/{channel}`

Generic inbound delivery. Используется только если домен зарегистрировал handler с таким `channel`.

```json
{
  "body": {},
  "headers": {},
  "query": {},
  "raw_body_b64": ""
}
```

Не относится к Telegram input платформы: Telegram обслуживается `/input/telegram/{service_id}/webhook`.

---

### 9. `POST /contract/v1/outbox/deliver`

Асинхронная доставка сторонней интеграции в зарегистрированный domain outbox-handler.

```json
{
  "payload": {
    "credential_key": "PARTNER_API",
    "event_type": "order.created"
  }
}
```

---

## Таймауты и retry (рекомендации для `contract_client`)

| Вызов | Timeout | Retry |
|-------|---------|-------|
| catalog | 5s | да, 3 попытки |
| context / guard / effect | 5s | guard/effect — retry только при 503 / network |
| command | 10s | network / 503 → `CONTRACT_UNAVAILABLE`, retryable |
| query | 10s | network / 503 |
| on-failed | 10s | network / 503 |
| hook | 10s | network / 503 |
| outbox deliver | 30s (`CONTRACT_TIMEOUT_OUTBOX`) | network / 503 |

Backoff — из `fsm_platform.host.retry_policy`.

## Версионирование API

- URL содержит major версию: `/contract/v1/…`
- Breaking changes → `/contract/v2/…`; v1 поддерживается параллельно на время миграции.
- Поле `catalog.version` — версия картриджа домена, не версия HTTP API.

## Чеклист реализации (courier pilot)

- [x] FastAPI app с эндпоинтами 1–9
- [x] HMAC middleware на Contract endpoints; `GET /catalog` — bootstrap exception
- [x] Catalog собран из `processes.register_all` metadata
- [x] Context builders возвращают JSON-safe values
- [x] Commands/queries исполняются без переданной platform session
- [x] Effects/commands/on-failed commit domain session before 200

## Связанные файлы (platform)

| Файл | Роль |
|------|------|
| `fsm_platform/host/contract_client.py` | HTTP-клиент (часть 4 плана) |
| `fsm_platform/host/domain_bootstrap.py` | Загрузка catalog для remote |
| `fsm_platform/host/http/request_runtime.py` | Обработка command result |
| `fsm_platform/core/types.py` | GuardResult, EffectResult, ProcessDef |

## История изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0.0 | 2026-07-28 | Первая фиксация: catalog, context, guards, effects, commands, queries, on-failed; граф вне API |

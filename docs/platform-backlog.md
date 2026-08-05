# План доработок платформы (зафиксировано)

Дата фиксации: 2026-08-04  
Основание: разбор с владельцем продукта; внутренние доки платформы
(`docs/fsm-platform-domain-requirements.md`, Contract API, текущий runtime).

Статусы: `planned` — в бэклоге; `out` — сознательно не делаем.

---

## 1. End-user read / privacy / realtime

### 1.1. Principal + access policy (жёсткий стандарт) — `done`

- **Дверь перед операцией:** кто ты → можно ли → только потом выполнение.
- Платформа только вызывает callback домена; правил бизнеса не пишет.
- Распространяется не только на карточку сущности: чувствительные query/command
  (пример courier: `view_locker_access_code` / PIN).
- Домен реализует `can_access` / аналоги под свой бизнес.
- Principal (минимум): идентичность пользователя + роли/тип актора
  (например `userId`, `roles[]`); роль не принимать «с честью» из произвольного
  query-параметра клиента без проверки токена.

**Два контура доступа (как должно быть):**

| Контур | Кто | Auth | Principal / policy |
|--------|-----|------|---------------------|
| **Admin / ЛК** | арендатор, разработчик домена | `DOMAIN_ADMIN_TOKEN` | не требуется (или Principal = admin/system) |
| **End-user** | клиент / курьер / водитель в приложении домена | end-user токен (см. 1.6) | **обязательны** |

- Admin-пути ЛК (secrets, connect, worker, catalog, admin invoke) — как сейчас:
  хватает `DOMAIN_ADMIN_TOKEN`.
- End-user пути (snapshot, PIN, «мои заказы», биржа…) — Principal + policy.
- End-user **не должен знать** про FSM Platform как продукт; он видит только
  приложение домена арендатора.

### 1.2. Entity Snapshot (мягкий / опциональный стандарт) — `done`

- Отдельный read карточки **одной** сущности, отдельно от write
  (`invoke` / `enqueue`).
- Рекомендуемый endpoint: `…/entities/{type}/{id}/snapshot`.
- Перед выдачей: Principal + `can_access` домена; иначе 403.
- Автор домена **может** использовать Snapshot, **может** жить только на
  `invoke` / `enqueue` и своих query.
- Форма ответа (`поля + state + availableActions`) — **рекомендация**, не закон.
  `availableActions` можно оставить на существующем `…/entities/…/actions`.
- Списки / биржа / отчёты (`list_client_orders`, `list_courier_exchange`, …)
  **не** заменяются Snapshot и остаются обычными query.
- По сути Snapshot ≈ стандартизированный query «карточка сущности»; ценность —
  единый контракт для reconnect/WS и обязательная policy-дверь, а не «новый SQL».

### 1.3. WS: подписка на entity Snapshot — `done`

- Текущий `WS …/ws/events` **сохраняется**:
  - лента `platform_events` (cursor / `after_id`);
  - подписка на любую domain operation (`subscribe` + snapshot operation),
    например биржа `list_courier_exchange`.
- Доработка: стандартная подписка на **entity**
  (`entity_type` + `entity_id`):
  - connect → Snapshot сущности;
  - дальше events по этой сущности (фильтр `platform_events`);
  - reconnect → Snapshot + replay `after eventId` → снова live.
- Access policy — та же, что у HTTP Snapshot.
- Автор может собрать аналог сам через subscribe на свою operation —
  платформа даёт entity-режим из коробки.

### 1.4. Reconnect / realtime семантика — `done`

- **Карточка сущности:** после обрыва → Snapshot ± replay по eventId → снова WS.
- **Биржа / списки:** после обрыва → снова тот же query /
  refresh подписки на operation (перечитать список целиком).
  Entity Snapshot тут не нужен.
- **Live-биржа:** при событиях перечитывать `list_courier_exchange`
  (уже заложено в текущем WS: event → refresh snapshot operation);
  количество заказов — из свежего ответа бэка, не «−1» на фронте.
- Гонка двух курьеров на один заказ: UI обновляет список после факта;
  победителя решает command/guard на бэке (второй — отказ).

Документ для авторов приложений домена: `docs/domain-app-realtime.md`.

### 1.5. Универсальный entity screen в ЛК — `out`

Не делаем. Snapshot — формат данных; UI каждого домена свой.

### 1.6. End-user токены вместо сырого `DOMAIN_ADMIN_TOKEN` в приложениях — `done`

- Приложение курьера / клиента / водителя **не держит** сырой `DOMAIN_ADMIN_TOKEN`.
- End-user ходит с **end-user токеном** (Bearer / session), из которого платформа
  (или gateway арендатора) извлекает Principal.
- `DOMAIN_ADMIN_TOKEN` — только у бэкенда арендатора и ЛК (управление доменом).
- Следствие: утечка приложения ≠ полный контроль Domain API тенанта
  (secrets, connect, worker, чужие операции).

Реализация:
- `POST /v1/{service_id}/end-user-tokens` (только admin) → `eut1.…`
- Domain API / WS: `Authorization: Bearer eut1.…` **без** admin-токена
- Admin-пути (secrets/connect/worker/…) end-user токеном закрыты
- Секрет подписи: `domain_secrets.end_user_token_secret` на `service_id`
  (не platform `.env`; при первом issue создаётся сам)
- См. также `docs/domain-app-realtime.md`
---

## 2. Ops-пакет

### 2.1. Reliability Matrix + DR runbook + автотест — `done`

Документ: `docs/ops-reliability.md` (matrix + DR + ориентиры RPO/RTO Clever).

Reclaim: убитый worker оставляет PROCESSING → worker loop возвращает в PENDING
(`WORKER_STALE_PROCESSING_SECONDS`, default 300).

Автотест: `tests/test_worker_kill_recovery.py`
(`python -m unittest tests.test_worker_kill_recovery`).

### 2.2. Readiness ≠ liveness — `done`

- `GET /v1/health` — liveness (процесс жив).
- `GET /v1/ready` — platform DB + опционально backlog (пороги env);
  200 / 503.
- `GET /v1/{service_id}/ready` — domain + worker + DB (tenant probe).

Env: `READY_MAX_PENDING_AGE_SECONDS` (default 300, `0` = off),
`READY_MAX_OUTBOX_DEAD` / `READY_MAX_RECONCILE_DEAD` (если заданы).

### 2.3. Метрики per `service_id` — `done`

- `GET /v1/{service_id}/metrics` — tenant snapshot (admin token).
- Тот же снимок в `GET …/worker/status` → `metrics` (ЛК без лишнего round-trip).
- ЛК монитор: pending / processing / failed 1h / pending age / outbox / timers.

Первая итерация: instances, outbox (pending/retry/dead), timers (due/overdue),
reconcile в JSON metrics.

**Нарастить позже (не блокер первой итерации):**

- transition latency;
- число конфликтов (`STATE_MISMATCH` / гонки);
- guard rejects;
- outbox delivery latency;
- realtime/WS: backlog, connections/drops;
- DB pool saturation.

### 2.4. Correlation envelope (полный пакет) — `done`

На входе Public API (`invoke` / `enqueue`):

| Поле | Header | Body | Смысл |
|------|--------|------|--------|
| `commandId` | `X-Command-Id` | `commandId` | id этой команды |
| `correlationId` | `X-Correlation-Id` | `correlationId` | id цепочки |
| `causationId` | `X-Causation-Id` | `causationId` | id причины (опц.) |

Если не передали — генерируются. `Idempotency-Key` на enqueue, если нет
`commandId`, становится `commandId` (retry безопасен и связан).

Протаскивание: payload инстанса (`_correlation`) → worker ContextVar →
`platform_events` (`correlation_id` / `client_request_id`) → outbox/webhooks
(`correlation` в JSON) → логи `corr=` / `cmd=`.

Ответ invoke/enqueue содержит блок `correlation`.

### 3. Интеграции и конфликты

### 3.1. Adapter checklist (лёгкие требования) — `done`

Документ: `docs/adapter-checklist.md`.

Runtime:
- `call_api(..., timeout=, idempotency_key=, max_attempts=)` —
  timeout > 0; `Idempotency-Key` + correlation headers из envelope §2.4;
- outbox `http_external` / webhook прокидывают `correlation` (+ idempotency_key).

### 3.2. Семантика конфликтов для клиентов (dual-commit) — `done`

Документ: `docs/client-conflict-semantics.md`.

Код гонки FSM: `STATE_MISMATCH`. Доменный take: `ALREADY_TAKEN`.

Автотест: `tests/test_parallel_take_race.py`
(`python -m unittest tests.test_parallel_take_race`).

---

## 4. Domain author playbook — `done`

Документ: `docs/domain-author-playbook.md`.

Чеклист подключения картриджа: каркас `domains/<name>/`, Domain DB + graph,
env domain service, онбординг (domains → secrets → connect), end-user surface,
адаптеры, конфликты, ops перед «готово к тенанту». Референс: `domains/courier/`.

---

## 5. Краткий чеклист бэклога

| ID | Тема | Статус |
|----|------|--------|
| E1 | Principal + policy (end-user ops; admin ЛК без Principal) | done |
| E2 | Entity Snapshot endpoint (optional) | done |
| E3 | WS entity subscribe + reconnect semantics | done |
| E4 | Docs: reconnect для entity vs list/exchange | done |
| E5 | Universal LK entity screen | out |
| E6 | End-user token; no raw DOMAIN_ADMIN_TOKEN in domain apps | done |
| O1 | Reliability Matrix + DR runbook | done |
| O2 | Autotest: kill worker → queue drains | done |
| O3 | `/ready` vs `/health` | done |
| O4 | Metrics per `service_id` | done |
| O5 | Full correlation envelope | done |
| A1 | Adapter checklist + light call_api/outbox requirements | done |
| C1 | Conflict semantics docs for clients (dual-commit) | done |
| C2 | Autotest: parallel take race → one win / one conflict | done |
| P4 | Domain author playbook (чеклист картриджа) | done |

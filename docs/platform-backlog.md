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

### 1.4. Reconnect / realtime семантика — `planned`

- **Карточка сущности:** после обрыва → Snapshot ± replay по eventId → снова WS.
- **Биржа / списки:** после обрыва → снова тот же query /
  refresh подписки на operation (перечитать список целиком).
  Entity Snapshot тут не нужен.
- **Live-биржа:** при событиях перечитывать `list_courier_exchange`
  (уже заложено в текущем WS: event → refresh snapshot operation);
  количество заказов — из свежего ответа бэка, не «−1» на фронте.
- Гонка двух курьеров на один заказ: UI обновляет список после факта;
  победителя решает command/guard на бэке (второй — отказ).

Зафиксировать коротко в доке для авторов приложений домена (E4).

### 1.5. Универсальный entity screen в ЛК — `out`

Не делаем. Snapshot — формат данных; UI каждого домена свой.

### 1.6. End-user токены вместо сырого `DOMAIN_ADMIN_TOKEN` в приложениях — `planned`

- Приложение курьера / клиента / водителя **не держит** сырой `DOMAIN_ADMIN_TOKEN`.
- End-user ходит с **end-user токеном** (Bearer / session), из которого платформа
  (или gateway арендатора) извлекает Principal.
- `DOMAIN_ADMIN_TOKEN` — только у бэкенда арендатора и ЛК (управление доменом).
- Следствие: утечка приложения ≠ полный контроль Domain API тенанта
  (secrets, connect, worker, чужие операции).

---

## 2. Ops-пакет — `planned` (целиком)

### 2.1. Reliability Matrix + DR runbook + автотест

**Reliability Matrix (документ)** — таблица по сбоям вашей модели
(dual-commit domain → platform + reconcile, dedicated worker, outbox):

| Сбой (примеры строк) | Что теряется | Автовосстановление | Нужен человек |
|----------------------|--------------|--------------------|---------------|
| Рестарт Platform API | in-flight HTTP | да (клиент retry + idempotency) | обычно нет |
| Убит / упал dedicated worker | незавершённый PROCESSING → stale/retry | да после restart/provision | если не поднят worker |
| Dual-commit: domain ok, platform fail | рассинхрон до доката | reconcile | если DEAD / исчерпаны попытки |
| Рестарт outbox worker | intent в outbox остаётся | retry / повтор HTTP | если внешний API не идемпотентен |
| Падение / недоступность platform DB | запись/чтение platform | после восстановления DB | да при потере данных |
| Потеря сайта / нужен restore из backup | зависит от backup | по DR runbook | да |

В каждой строке при реализации дока: ориентиры RPO/RTO под ваш хостинг
(Clever и т.п.), без выдуманных SLA.

**DR runbook (документ)** — пошагово: порядок подъёма (DB → platform API →
worker provision → domain service), проверки backlog PENDING, outbox dead,
reconcile, контрольный invoke/enqueue.

**Автотест (O2):** убить worker → убедиться, что PENDING/зависшие instances
догоняются после restart/provision (failure-injection).

### 2.2. Readiness ≠ liveness

- `GET /v1/health` (liveness) — процесс API отвечает (как сейчас / уточнить).
- `GET /v1/ready` (или эквивалент) — **не** пускать трафик, если критично плохо:
  - platform DB недоступна;
  - (для tenant-ready, если probe scoped) catalog/domain not ready;
  - worker для тенанта not running / failed (где применимо к probe);
  - критический backlog: due PENDING старше порога / outbox DEAD выше порога
    (пороги — при реализации, согласовать с монитором ЛК).
- 200 = ready, 503 = not ready.

### 2.3. Метрики per `service_id`

- Сейчас есть глобальный `GET /v1/metrics` и кусок queue в worker/status.
- Нужен tenant-scoped снимок + отображение в ЛК.

**Первая итерация (блокер):**

- instances: pending count, oldest due pending age, processing count;
- failed (например за 1h);
- outbox: pending / retry / dead;
- timers: due / overdue;
- всё **per `service_id`**.

**Нарастить позже (не блокер первой итерации):**

- transition latency;
- число конфликтов (`STATE_MISMATCH` / гонки);
- guard rejects;
- outbox delivery latency;
- realtime/WS: backlog, connections/drops;
- DB pool saturation.

### 2.4. Correlation envelope (полный пакет)

Сразу полный конверт на входе Public API (`invoke` / `enqueue` и далее):

| Поле | Смысл |
|------|--------|
| `commandId` | id конкретной команды/запроса клиента |
| `correlationId` | id всей цепочки (сквозной след) |
| `causationId` | id причины (предыдущее событие/команда), если есть |

Плюс по пути уже известные: actor, `instance_id`, при наличии — outbox/event ids.

- Принимать от клиента и/или генерировать на входе, если не передали.
- Протаскивать: invoke/enqueue → instance/payload → `platform_events` →
  outbox/webhooks → логи (без сырых секретов).
- Связать с Idempotency-Key на enqueue (уже есть): retry безопасен.

---

## 3. Интеграции и конфликты — `planned`

### 3.1. Adapter checklist (лёгкие требования) — `planned`

Дисциплина внешних вызовов через уже существующие `call_api` /
outbox `http_external` (не новый framework).

**Документ-чеклист для каждой интеграции:**

- timeout;
- retry / backoff;
- idempotency (ключ и семантика повтора);
- mapping ошибок внешней системы → домен/платформа;
- authentication (credential из `domain_secrets`);
- correlation (`correlationId` и др. из §2.4);
- поведение при недоступности внешней системы (fail / отложить в outbox).

**Лёгкие требования к runtime:** `call_api` и доставка outbox `http_external`
должны явно задавать/прокидывать минимум: timeout, idempotency key
(где применимо), correlation; без обхода этих полей «голым» HTTP в обход
контракта (детали валидации — на реализации).

### 3.2. Семантика конфликтов для клиентов (dual-commit) — `planned`

Клиентский контракт (дока) для авторов приложений домена и E2E:

| Класс | Пример | Что делать клиенту |
|-------|--------|-------------------|
| Conflict / гонка | `STATE_MISMATCH`, доменный «уже занято» | перечитать карточку/биржу; не долбить то же вслепую |
| Business reject | DomainError / guard reject | показать reason; обычно без auto-retry |
| Transient | 5xx, сеть, worker down | retry с Idempotency-Key / тем же correlation |
| Dual-commit в полёте | domain ок, platform догоняет | не создавать сущность второй раз; поллить instance / дождаться события |

- Код гонки по FSM state — существующий `STATE_MISMATCH`; не переименовываем.
- **Автотест гонки (C2):** два параллельных take (или аналог) на одну сущность →
  один успех, второй conflict — в этой же задаче.

---

## 4. Вне этого плана (пока не фиксировали)

- Domain author playbook (чеклист подключения картриджа) — отдельно, когда дойдём.

---

## 5. Краткий чеклист бэклога

| ID | Тема | Статус |
|----|------|--------|
| E1 | Principal + policy (end-user ops; admin ЛК без Principal) | planned |
| E2 | Entity Snapshot endpoint (optional) | planned |
| E3 | WS entity subscribe + reconnect semantics | planned |
| E4 | Docs: reconnect для entity vs list/exchange | planned |
| E5 | Universal LK entity screen | out |
| E6 | End-user token; no raw DOMAIN_ADMIN_TOKEN in domain apps | planned |
| O1 | Reliability Matrix + DR runbook | planned |
| O2 | Autotest: kill worker → queue drains | planned |
| O3 | `/ready` vs `/health` | planned |
| O4 | Metrics per `service_id` | planned |
| O5 | Full correlation envelope | planned |
| A1 | Adapter checklist + light call_api/outbox requirements | planned |
| C1 | Conflict semantics docs for clients (dual-commit) | planned |
| C2 | Autotest: parallel take race → one win / one conflict | planned |

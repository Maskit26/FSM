# FSM Platform: инструкция по разработке

Документ — **единая инструкция** по разработке автономной FSM Platform и подключению доменов-картриджей (courier, taxi, cargo и др.): принципы, модули, контракты, БД, валидация, runtime.

Связанный документ (доп. детали legacy/RFC pipeline): [fsm-platform-rfc-implementation.md](fsm-platform-rfc-implementation.md).

Как читать:

| Раздел | Содержание |
|--------|------------|
| §1–3 | видение, принципы, кто пишет в какую БД |
| §4 | platform: компоненты, worker, HTTP, bootstrap |
| §5 | картридж домена: структура, guards/effects/queries/db_layer |
| §6 | контракт platform ↔ domain, Domain Registry, RAM-реестры |
| §7 | Accept нового домена, Domain Validator |
| §8 | модули `fsm_core`: файлы, алгоритмы, таблицы |
| §9–10 | эволюция от монолита, примеры доменов |
| §11–12 | критерии готовности |
| §13 | глоссарий |

---

## 1. Видение

FSM Platform — **универсальный движок оркестрации**. Ему безразлично:

- какой домен подключён (courier, taxi, cargo);
- какие имена state/event используются;
- как устроены бизнес-таблицы домена.

Домен подключается как **картридж** (SQL + Python), регистрируется в platform без изменения ядра `fsm_core`.

В перспективе поверх platform добавляется **слой каналов** (Telegram, WhatsApp, Web, голос): каналы вызывают процессы доменов и доставляют ответы пользователю, не зная внутренней логики courier/taxi.

```text
Каналы / HTTP
        ↓
Platform HTTP-слой (Gateway → Dispatcher → Request Runtime)
        ├─ Command  → domain handler → domain db_layer → enqueue FSM → worker → fsm_core
        └─ Query    → domain handler → domain db_layer → (опционально FSM-state от platform)
        ↓
Домены-картриджи (courier, taxi, …)
```

---

## 2. Принципы

1. **Platform agnostic** — `fsm_core` не содержит бизнес-условий и не импортирует домены напрямую (только registry/bootstrap).
2. **Декларативный граф** — переходы описаны в данных (`fsm_transitions`), не в Python handler map (`state → function`).
3. **Pipeline** — `context → guard → transition → effect`.
4. **Guard routing** — при нескольких candidate transitions выбор по `priority ASC` и первому guard с `ok=true`.
5. **Разделение ответственности за UPDATE** — SQL Core platform меняет только FSM-state в platform DB; бизнес-таблицы домена меняются в **effects** домена.
6. **Картридж** — добавление домена = SQL seed + Python register + конфиг, без правки ядра platform.
7. **Side effects наружу** — HTTP в Core, push, мессенджеры только через outbox/worker, не внутри SQL-транзакции FSM.
8. **Session только platform** — session к любой БД открывает worker (FSM) или Request Runtime (REST); домен session не создаёт.
9. **Доступ к данным домена** — SQL к domain DB только через **domain db_layer**, не из gateway и не из `fsm_core`.
10. **Домен только после валидации** — status `active` после Domain Validator; иначе REST/FSM для `service_id` не обслуживаются.
11. **service_id ≠ cartridge_type** — тип картриджа может повторяться у разных заказчиков; runtime-ключ всегда уникальный `service_id`.

---

## 3. Разделение записи в БД

Pipeline делит запись в БД на два слоя:

| Шаг | Исполнитель | Обновляемые данные |
|-----|-------------|-------------------|
| SQL transition | Platform (`perform_transition`, SQL Core) | FSM-state в platform DB (`entity_fsm_state`), запись в log platform |
| Effect | Домен (`domains/<name>/effects.py`) | Бизнес-таблицы domain DB: `orders`, ячейки, `stage_orders`, связи, outbox |

**Требования:**

- SQL Core platform не выполняет `UPDATE`/`INSERT` в таблицы domain DB (`orders`, `order_requests` и т.п.).
- Запись в domain DB выполняется только в effect, зарегистрированном доменом.
- Platform выполняет FSM transition и вызывает effect; effect несёт ответственность за бизнес-данные домена.

```text
Worker
  → guard (read-only, допускается чтение domain DB)
  → perform_transition  → platform DB: entity_fsm_state, fsm_action_logs
  → effect              → domain DB: orders, locker_cells, …
  → commit
```

**Запрещено:** изменение бизнес-таблиц домена из SQL Core platform (в т.ч. `orders.status`).

**Обязательно:** effect домена выполняет все необходимые INSERT/UPDATE в domain DB для данного перехода.

---

## 4. Platform: компоненты и работа

### 4.1. Назначение

Platform обеспечивает:

- HTTP-вход (Gateway, Route Registry, Dispatcher, Request Runtime);
- постановку и выполнение FSM-задач (`server_fsm_instances`);
- единый pipeline перехода (`fsm_core`);
- хранение **FSM-state** сущностей в platform DB (`entity_fsm_state`);
- журнал переходов, таймеры, outbox для асинхронных интеграций;
- маршрутизацию к домену по полю `service` (instance и HTTP);
- чтение FSM-графа (transitions) из **БД домена** по connection, привязанному к `service`.

Platform **не** обязана:

- знать схему `orders`, `taxi_orders` и т.п. в SQL Core / Gateway;
- содержать бизнес-правила courier/taxi в ядре;
- держать бизнес-SQL доменов в platform-коде.

### 4.2. Компоненты platform (Python)

| Компонент | Путь (целевой) | Ответственность |
|-----------|----------------|-----------------|
| Runtime engine | `fsm_core/engine.py` | `run_instance` → ProcessDef → TransitionRunner (§8.4) |
| Transition runner | `fsm_core/transition_runner.py` | context → candidates → guards → apply → effect (§8.5) |
| FSM Registry | `fsm_core/registry.py` | Process/Guard/Effect в RAM, ключ с `service_id` (§8.3) |
| Types / errors | `fsm_core/types.py`, `errors.py` | контракты и коды ошибок (§8.2, §8.7) |
| State store | `fsm_core/state_store.py` | **добавить:** `entity_fsm_state` (§8.8) |
| Transition repository | `fsm_core/transition_repository.py` | **добавить:** SELECT candidates из domain DB (§8.9) |
| Transition executor | `fsm_core/transition_executor.py` | **добавить:** apply state+log только platform (§8.10) |
| Timers helper | `fsm_core/timers.py` | schedule/cancel → `fsm_timers` (§8.6) |
| Worker | `fsm_worker.py` | poll, claim, session, commit/rollback, mark FAILED |
| Bootstrap | `domains/bootstrap.py` | загрузка доменов из Domain Registry / `FSM_DOMAINS` |
| HTTP Gateway | `platform/http/gateway.py` (или `main.py`) | HTTP in/out, auth, status code, JSON |
| Route Registry | `platform/http/registry.py` | RAM: `(service_id, method, path) → handler, kind` |
| Dispatcher | `platform/http/` (функция/класс) | поиск route → передача в Request Runtime |
| Request Runtime | `platform/http/request_runtime.py` | session(s) на HTTP-запрос, вызов handler, commit/close |

**Запрещено** в `fsm_core`:

- импорты `domains.courier`, `domains.taxi`;
- проверки вида `if pickup_type == "courier"` (это guards домена);
- знание имён domain-таблиц.

### 4.3. Pipeline одного шага FSM

Worker открывает session, владеет транзакцией и передаёт session в pipeline.

```text
1. Worker открывает session (platform DB; при необходимости — session domain DB)
2. Worker claim server_fsm_instance (PENDING → PROCESSING)
3. ProcessRegistry: service + process_name → ProcessDef
4. context_builder(session, db, runtime_ctx, instance) → domain context
5. get_entity_current_state(...) — platform DB
6. get_candidate_transitions(...) — domain DB (по instance.service)
7. Сортировка по priority ASC; проверка уникальности priority
8. Для каждого candidate: guard → первый ok=true (или guard_name=NULL)
9. perform_transition(transition_id) — platform DB: FSM-state + log
10. effect (если задан) — запись в domain DB / outbox
11. update instance → COMPLETED / FAILED; commit
```

### 4.4. Guard routing

- Несколько transitions на один `(entity_type, from_state, event_name)` — **норма** (ветвление courier/self и т.д.).
- `priority`: меньше = проверяется раньше; **уникален** внутри набора candidates.
- Default transition: `guard_name = NULL`, самый большой `priority`.
- Ни один guard не прошёл → `NO_GUARD_MATCHED`, instance FAILED (или WAITING — по политике домена).

### 4.5. База данных platform

**Только инфраструктура platform** — без бизнес-таблиц и без FSM-графа доменов:

| Таблица | Назначение |
|---------|------------|
| `server_fsm_instances` | очередь задач: service, process_name, entity_type, entity_id, fsm_state, attempts |
| `fsm_action_logs` / `fsm_transition_logs` | аудит переходов |
| `fsm_timers` | отложенные события |
| `entity_fsm_state` | текущий FSM-state: `(service_id, entity_type, entity_id) → current_state` |
| `domain_services` (Domain Registry) | экземпляры доменов: service_id, cartridge_type, status, DB secret, package (см. §6.3) |
| `core_outbox` | асинхронные вызовы внешних систем (опционально) |

FSM-граф домена (`fsm_states`, `fsm_events`, `fsm_transitions`) хранится в **БД домена** и поставляется **SQL seed картриджа**.

Platform при обработке instance:

- читает/пишет FSM-state в **platform DB**;
- читает candidates из **domain DB** по `service` (реестр подключений).

### 4.6. SQL Core (platform)

Процедура `fsm_perform_transition` (или эквивалент в platform layer):

- проверяет transition_id, entity_type, event_name, совпадение current_state с from_state (данные transition — из domain DB, state — из platform DB);
- обновляет **только** `entity_fsm_state` и log в **platform DB**;
- **не** выполняет UPDATE таблиц domain DB.

Platform SQL Core **не** содержит IF-цепочек `entity_type → orders/trips/...`.

### 4.7. Worker и транзакции

- Worker **владеет** session и границами транзакции.
- Один instance = одна логическая операция; commit при успехе, rollback при guard/effect/SQL ошибке.
- Platform transition и domain effect — согласованная последовность; при ошибке effect — FAILED instance (при необходимости saga/outbox).
- Внешние HTTP/push — только через outbox после commit.

### 4.8. Bootstrap и реестр доменов

- Источник списка доменов: `FSM_DOMAINS` и/или записи **Domain Registry** в platform DB (после Accept в админ-UI).
- При старте API/worker для каждого **active** `service_id` из Domain Registry:
  1. загрузить пакет по `cartridge_type` / package ref;
  2. прочитать `manifest.yaml` (`cartridge_type`, version, entry);
  3. открыть connection к domain DB этого `service_id`;
  4. вызвать `register_all(service_id)` → наполнить **RAM** FSM Registry + Route Registry;
  5. прогнать **Domain Validator** (см. §6–7); при ошибке домен не активируется.
- Реестр подключений: `service_id` → URL/secret domain DB.

### 4.9. Валидация при старте

Краткая форма полного Domain Validator (§7):

1. Целостность пакета и `manifest` (`cartridge_type`).
2. `register_all(service_id)` без ошибок; уникальность `(service_id, process_name)`.
3. Connectivity к domain DB.
4. Готовность SQL/ХП и FSM-графа в domain DB.
5. Согласованность `guard_name` / `effect_name` (граф ↔ RAM registry).
6. Нет orphan `entity_type` без ProcessDef (warning или fail — по политике).

Домен со статусом validation failed **не** обслуживает REST и FSM.

### 4.10. HTTP API: жизненный цикл REST

REST всегда входит в **platform**. Не каждый REST-запрос — FSM.

**Command** и **Query** — типы запроса (нужен ли FSM), а не «прямой SQL в базу».

| | Command | Query |
|---|---------|-------|
| Смысл | меняет lifecycle сущности | только чтение |
| Примеры | создать/отменить заказ | список заказов, детали, каталог |
| Дальше | staging + enqueue → worker → fsm_core | domain handler → domain db_layer |
| FSM instance | да | нет |

Оба пути: **Gateway → Dispatcher → Request Runtime → domain handler → domain db_layer**.

#### Роли HTTP-слоя (не обязательно 4 отдельных файла с такими именами)

| Роль | Где в коде | Ответственность |
|------|------------|-----------------|
| **Gateway** | `platform/http/gateway.py` / `main.py` | path, method, headers, auth, HTTP status, JSON. Без бизнес-SQL. |
| **Route Registry** | `platform/http/registry.py` | таблица маршрутов; `register(...)` при bootstrap |
| **Dispatcher** | функция/класс в `platform/http/` | найти route → вызвать Request Runtime |
| **Request Runtime** | `platform/http/request_runtime.py` | **владелец session** на HTTP-запрос (аналог worker для REST) |
| **Domain handler** | `domains/<name>/queries.py` или command-entry | use-case; session только принимает |
| **Domain db_layer** | `domains/<name>/db_layer.py` | SQL к domain DB через переданную session |

Registry и Dispatcher — platform. Domain handler — код домена. Отдельный `api.py` в картридже не нужен.

#### Session: кто создаёт и что значит domain session

Session к любой БД открывает **только platform**:

| Контекст | Владелец session |
|----------|------------------|
| REST | Request Runtime |
| FSM job | Worker |
| Domain handler / db_layer / context / guards / effects | только **принимают** session |

Имя `domain_session` (или `sessions["domain"]`) означает: session, которую **platform** открыл к **БД домена** (engine по `service`). Это не session, созданная доменом.

```text
Request Runtime
  ├── engine_platform → platform_session  → platform DB
  └── engine_<service> → domain_session   → domain DB
         │
         ▼ передаётся аргументом
  domain handler → domain db_layer(domain_session, …)
```

Домен не знает connection string platform DB и не открывает session сам.

#### Регистрация маршрутов (bootstrap)

При старте `domains/<name>/processes.register_all()` (или соседний register):

1. ProcessDef / guards / effects → FSM registry.
2. HTTP bindings → Route Registry, например:

```text
RouteRegistry.register(
  service_id="svc_courier_acme_01",
  method="GET",
  path="/orders",
  kind="query",
  handler=list_client_orders,
)
```

#### Жизненный цикл Query

Пример: `GET /api/courier/orders?client_id=42`

```text
1. Фронт → HTTP
2. Gateway: auth, service=courier, method, path, query params
3. Dispatcher: Route Registry → handler, kind=query
4. Request Runtime:
     - открывает domain_session (engine courier)
     - при необходимости platform_session (для enrichment FSM-state)
     - вызывает list_client_orders(domain_session, params, user_ctx)
5. Domain handler → domain db_layer (SELECT только domain DB) → DTO
     DTO может содержать opaque ключи entity_type / entity_id
6. Request Runtime (опционально):
     - читает entity_fsm_state в platform DB
     - мержит state в ответ
     - close sessions (read-only; commit не обязателен)
7. Gateway: DTO → JSON, HTTP 200
8. Фронт получает JSON
```

Ошибка в handler/db_layer → Runtime close/rollback → Gateway 4xx/5xx.

**Запрещено:** Query как прямой SQL из Gateway в domain DB.  
**Запрещено:** domain handler/db_layer читает platform DB.  
**Запрещено:** прогонять read-only через FSM «для единообразия».

#### Жизненный цикл Command

Пример: `POST /api/courier/order-requests`

```text
1. Фронт → HTTP + body
2. Gateway → auth, service=courier
3. Dispatcher → handler, kind=command
4. Request Runtime:
     - открывает domain_session (+ platform_session для enqueue)
     - вызывает create_order_request(sessions, body, user_ctx)
5. Domain handler + domain db_layer:
     - INSERT staging в domain DB (без lifecycle UPDATE «как в FSM»)
6. Platform (в том же Runtime):
     - INSERT server_fsm_instance (PENDING)
     - начальный entity_fsm_state (целевая модель)
7. Request Runtime → commit → close
8. Gateway → 202 Accepted { request_id, instance_id } (или 200 по политике)
9. Вне REST: worker → fsm_core → guard → transition → effect
```

HTTP Command не вызывает guards/effects напрямую. Lifecycle исполняет worker.

#### Ответ на фронт

1. Handler возвращает структуру данных (dataclass / model), не HTTP Response.
2. Runtime может обогатить ответ (FSM-state).
3. Gateway единственный ставит status code, headers, JSON body.
4. Клиент всегда ходит в platform HTTP, не в домен напрямую.

#### Сводная схема

```text
Browser
  │  HTTP
  ▼
Gateway (auth, HTTP in/out)
  │  service, method, path, body
  ▼
Dispatcher + Route Registry     ← наполняется domain.register_all() при boot
  │  handler, kind=query|command
  ▼
Request Runtime                 ← создаёт/закрывает session(s)
  │
  ├─ domain handler
  │     └─ domain db_layer → Domain DB
  │
  └─ (query, опционально) platform state reader → entity_fsm_state
  │
  ▼
Gateway → JSON → Browser
```

#### Что куда относится

| Запрос | kind | Кто реализует логику |
|--------|------|----------------------|
| `GET` список заказов | query | `domains/courier/queries.py` + `db_layer.py` |
| `GET` заказ по id | query | domain queries + db_layer |
| `POST` создать заказ | command | domain command-entry + db_layer + enqueue |
| `POST` отменить заказ | command | ProcessDef + worker после enqueue |
| `GET` health / metrics | — | platform, без домена |

### 4.11. Каналы (расширение platform)

Слой **не в домене**:

```text
channels/telegram/   — parse update → тот же Command/Query путь (через Runtime или общий application API)
channels/whatsapp/
```

- Канал не знает guards/effects и domain SQL.
- Mapping на `service` + зарегистрированный handler / process_name.
- Ответы — HTTP JSON или channel outbox / notification worker.
- Один и тот же domain handler вызывается из HTTP, Telegram, голоса.

---

## 5. Домен (картридж): структура и модули

### 5.1. Структура картриджа

Домен поставляется как SQL-пакет + Python-пакет. Подключение выполняется без изменения кода platform core.

```text
domains/<domain_name>/
  manifest.yaml          # cartridge_type, version, entry, required tables/routines
  sql/
    fsm/                 # fsm_states, fsm_events, fsm_transitions → domain DB
    domain/              # orders, taxi_orders, … → domain DB
  processes.py           # ProcessDef + register_all (FSM + HTTP routes)
  context.py
  guards.py
  effects.py
  queries.py             # Query handlers (use-case); без SQL
  db_layer.py            # SQL к domain DB; принимает session от platform
```

HTTP-роуты объявляет platform (Gateway + Route Registry). Домен регистрирует handlers в registry при bootstrap. Целостность пакета и готовность domain DB проверяет **Domain Validator** (§7) до статуса `active`.

**Процедура подключения:**

1. Накатить SQL/ХП в domain DB (на стороне заказчика в v1).
2. Установить Python-пакет + URL DB (ops или Accept в админ-UI).
3. Domain Validator → `active` → bootstrap `register_all()`.

Platform DB не содержит states/events/transitions домена — только instances, logs, `entity_fsm_state`, Domain Registry.

### 5.2. Обязательные Python-модули

| Файл | Требование |
|------|------------|
| `processes.py` | `register_all()`: ProcessDef, guards, effects, HTTP routes в Route Registry |
| `context.py` | сбор данных для guards/effects по instance |
| `guards.py` | `(session, db, context, instance, params) → GuardResult` |
| `effects.py` | `→ EffectResult`; запись через domain db_layer / outbox |
| `queries.py` | Query use-case handlers; без SQL и без открытия session |
| `db_layer.py` | единственное место SQL к domain DB; session только аргумент |

**ProcessDef** минимум:

```python
ProcessDef(
    service="<service_id>",       # уникальный id инстанса, не cartridge_type
    process_name="<job>",         # order_creation | submit_ride
    entity_type="<entity>",       # order_request | taxi_order
    event_name="<fsm_event>",     # order_create | ride_submit
    context_builder=build_..._context,
)
```

- `service` в ProcessDef = **`service_id`**.
- `process_name` — job для worker/API.
- `event_name` — внутренний FSM trigger; **не** приходит с frontend напрямую.

### 5.3. SQL seed картриджа

Один domain DB, два типа файлов:

**1. FSM-граф** (`sql/fsm/*.sql`):

- `fsm_states`, `fsm_events`, `fsm_transitions` для **этого** домена;
- entity_type, guard_name, effect_name, priority.

**2. Бизнес-схема** (`sql/domain/*.sql`):

- `orders`, `order_requests`, `locker_cells`, …;
- без таблиц platform (`server_fsm_instances`).

Домен **сам** определяет:

- staging (`order_request`) или сразу основная сущность (`taxi_order`);
- цепочку state (courier ≠ taxi);
- какие entity_type используются в processes.

Platform не навязывает единый lifecycle всем доменам.

### 5.4. Guards

- Имена регистрируются в GuardRegistry и совпадают с `guard_name` в `fsm_transitions`.
- Guard — **read-only** проверки до SQL transition (может читать domain DB через переданный `session`).
- На развилках — **отдельные guards** (`pickup_is_courier`, `pickup_is_self`).

### 5.5. Effects

- Выполняются **после** успешного SQL transition в platform DB.
- **Здесь** обновляются domain tables: резерв ячеек, INSERT `orders`, `stage_orders`, link request→order, `core_outbox`.
- При ошибке effect — rollback, instance FAILED.

### 5.6. Context

Сбор данных для guards/effects из domain DB по `instance.entity_type` / `entity_id` (через domain db_layer). Преобразование полей домена (например `sender_delivery` → `pickup_type`) — только здесь. Session передаёт worker / Request Runtime.

### 5.7. Queries и domain db_layer

**Query** — тип REST/канального запроса без FSM, не «прямой доступ к БД».

- `queries.py` — use-case: параметры, DTO, вызов db_layer.
- `db_layer.py` — SQL к domain DB через session, открытую Request Runtime / worker.
- Не открывают connection, не читают platform DB.
- Не вызывают `perform_transition`.
- Если в ответе нужен FSM-state — handler возвращает `entity_type`/`entity_id`; merge делает Request Runtime / platform state reader.

Пример: `list_client_orders(domain_session, client_id, filters)` → db_layer → `list[OrderSummary]`.

### 5.8. Что домен не должен делать

- Менять код `fsm_core` / `transition_runner` / HTTP Gateway Runtime.
- Писать бизнес-UPDATE в SQL Core platform.
- Открывать session самостоятельно.
- Читать или писать platform DB (`entity_fsm_state`, `server_fsm_instances`, logs).
- Держать бизнес-SQL вне `db_layer.py` (в gateway, queries без db_layer, fsm_core).
- Вызывать Core API синхронно внутри effect без outbox (production).
- Класть worker-статусы instance (`PENDING`/`COMPLETED`) в `fsm_states` как entity states.

### 5.9. Подключение домена (чеклист разработчика картриджа)

1. Создать `domains/<name>/` по структуре §5.1, включая `manifest.yaml`.
2. Написать SQL seed: `sql/fsm/` + `sql/domain/` (+ ХП домена при необходимости).
3. Подготовить domain DB: накатить схему/граф/ХП **до** Accept в platform (v1: накат на стороне заказчика/devops).
4. Зарегистрировать в `register_all()`: ProcessDef, guards, effects, HTTP routes.
5. Пройти Domain Validator (§7) → статус active.
6. Smoke Command и Query после активации.

Детали контракта вызова и валидации — §6–7.

---

## 6. Контракт общения platform ↔ domain

### 6.1. `service_id` и `cartridge_type`

| Понятие | Пример | Смысл |
|---------|--------|--------|
| **cartridge_type** | `cargo`, `courier`, `taxi` | тип картриджа (код продукта); задаётся в `manifest.yaml` |
| **service_id** | `svc_8f2c…` или `cargo_acme_01` | уникальный id **экземпляра** домена у заказчика в этой platform |

- Во всех runtime-ключах platform используется **`service_id`**: Route Registry, FSM Registry, `server_fsm_instances.service`, `entity_fsm_state`, connection к domain DB.
- **`cartridge_type` не уникален**: два заказчика могут подключить тип `cargo`.
- При Accept platform **генерирует** `service_id` и сохраняет в Domain Registry вместе с `cartridge_type`, package ref, DB secret.
- URL/API: `/api/{service_id}/…` (или эквивалент с резолвом tenant → `service_id`).
- Один и тот же код картриджа (`cartridge_type=cargo`) может обслуживать много `service_id` с разными domain DB.

### 6.2. Модель взаимодействия и где живут реестры

Общение **in-process**, без отдельного сетевого RPC «platform → domain service».

- Домен — Python-пакет в процессе API/worker **на сервере** (не в браузере).
- **RAM** = память процесса API/worker на сервере platform. Браузер к реестрам не обращается.
- Platform вызывает зарегистрированные функции домена и передаёт session.
- Домен возвращает обычные Python-результаты (DTO, `GuardResult`, `EffectResult`) или бросает исключение.
- Домен не открывает HTTP-порт и не обращается к platform DB.

**Route Registry и FSM Registry — не исходные файлы, которые дописываются годами.**  
Это **runtime-структуры в RAM** процесса API/worker. Код `registry.py` — тонкая обёртка platform; размер файла не растёт от числа клиентов.

```text
Boot (один раз при старте процесса API/worker на сервере):
  Domain Registry (platform DB) → список active service_id
  для каждого service_id:
      load package (по cartridge_type / package ref)
      open engine[service_id] → domain DB
      register_all(service_id) → записи в RAM сервера:
          Route Registry[(service_id, method, path)] = handler
          FSM Registry[(service_id, process_name)] = ProcessDef
          Guard/Effect Registry[service_id, name] = callable

Запрос (каждый REST / каждая FSM-задача):
  Dispatcher / worker
    → lookup в RAM-реестре по service_id (+ path или process_name)
    → если найдено: вызвать callable, передать domain_session для этого service_id
    → если нет: 404 / ошибка process not found
```

После рестарта процесса RAM строится заново из Domain Registry + `register_all(service_id)`.

```text
Platform                              Domain cartridge
────────                              ────────────────
Domain Registry (DB) / boot
  → load package (cartridge_type)
  → open domain DB engine[service_id]
  → register_all(service_id) ───────→  заполняет Route/FSM Registry в RAM

Request Runtime / Worker
  → lookup RAM → call handler ──────→  domain function(session, …)
  ← return DTO / Result ────────────   обычный return
```

### 6.3. Domain Registry (таблица в platform DB)

Постоянный каталог **экземпляров** доменов. Не бизнес-схема courier/cargo и не список HTTP-handler'ов (handlers живут в RAM после boot).

Имя таблицы условное, например `domain_services`.

| Поле | Смысл |
|------|--------|
| `service_id` | PK; уникальный id экземпляра (`svc_8f2c…`) |
| `cartridge_type` | тип картриджа: `cargo`, `courier`, `taxi` |
| `version` | версия пакета картриджа |
| `package_ref` | путь/хранилище пакета |
| `package_checksum` | контроль целостности пакета |
| `db_secret_ref` | ссылка на URL/креды domain DB в secret store (не пароль в открытом виде) |
| `status` | `pending` \| `active` \| `failed` \| `disabled` |
| `validation_report` | краткий результат Domain Validator |
| `created_at` / `updated_at` | аудит |
| `activated_by` | кто выполнил Accept |

**Назначение:**

- источник списка доменов после рестарта API/worker;
- хранение `service_id` ↔ `cartridge_type` ↔ domain DB;
- статус допуска к работе (`active` только после Validator);
- аудит Accept / Upgrade / Disable.

**Не хранит:** тела Python-функций, SQL бизнес-таблиц домена, FSM-граф домена.

Accept в админ-UI = INSERT/UPDATE в Domain Registry + валидация + при успехе `status=active`.  
Boot читает строки со `status=active` и для каждой вызывает загрузку пакета и `register_all(service_id)`.

### 6.4. Как `registry.py` кладёт маппинг в RAM

`registry.py` (и аналоги в `fsm_core/registry.py`) держит **модульные dict в памяти процесса сервера** и функции `register_*`. Это не запись в файл на диск.

Упрощённая модель:

```python
# platform http / fsm_core registry — пустые dict при старте процесса
_routes: dict[tuple[str, str, str], object] = {}
# key = (service_id, method, path) → {kind, handler}

_processes: dict[tuple[str, str], ProcessDef] = {}
# key = (service_id, process_name) → ProcessDef

_guards: dict[tuple[str, str], object] = {}   # (service_id, guard_name) → callable
_effects: dict[tuple[str, str], object] = {}  # (service_id, effect_name) → callable

def register_route(service_id, method, path, kind, handler) -> None:
    _routes[(service_id, method, path)] = {"kind": kind, "handler": handler}
    # handler — объект функции в памяти после import пакета

def register_process(process_def: ProcessDef) -> None:
    key = (process_def.service, process_def.process_name)  # service = service_id
    _processes[key] = process_def
```

Домен при boot вызывает регистрацию (передаёт **callable**, не путь к файлу):

```python
# domains/<cartridge_type>/processes.py
def register_all(service_id: str) -> None:
    RouteRegistry.register(
        service_id=service_id,
        method="GET",
        path="/orders",
        kind="query",
        handler=list_client_orders,
    )
    ProcessRegistry.register(
        ProcessDef(
            service=service_id,
            process_name="order_creation",
            entity_type="order_request",
            event_name="order_create",
            context_builder=build_courier_context,
        )
    )
    GuardRegistry.register(service_id, "can_create_order", can_create_order)
    EffectRegistry.register(service_id, "finalize_order_creation", finalize_order_creation)
```

Lookup на запросе:

```text
GET /api/svc_courier_acme_01/orders
  → key = ("svc_courier_acme_01", "GET", "/orders")
  → handler = _routes[key]["handler"]
  → handler(domain_session, params, user_ctx)

FSM instance: service=svc_courier_acme_01, process_name=order_creation
  → ProcessDef = _processes[("svc_courier_acme_01", "order_creation")]
  → fsm_core.run_instance(...)
```

**Итог:** сопоставление «path → функция» / «process_name → ProcessDef» = ключ в dict → значение (callable или ProcessDef). Наполнение RAM = побочный эффект `register_*` во время `register_all(service_id)` при boot.

### 6.5. Что регистрирует домен

При `register_all(service_id)` домен передаёт platform только callable и метаданные:

| Регистрация | Назначение |
|-------------|------------|
| HTTP route (`service_id`, method, path, kind, handler) | REST Query/Command |
| `ProcessDef` (с полем `service_id`) | async FSM job для worker |
| `guard_name` → функция | выбор transition |
| `effect_name` → функция | побочные записи в domain DB после transition |
| `context_builder` | сбор context для pipeline |

Имена `guard_name` / `effect_name` в `fsm_transitions` (domain DB) **обязаны** совпадать с registry.

### 6.6. Как передаётся запрос и ответ

| Путь | Вызов | Ответ |
|------|-------|-------|
| REST Query/Command | Runtime вызывает domain handler `(domain_session, params, user_ctx)` | DTO → Gateway → JSON |
| FSM | `fsm_core` вызывает context → guard → effect с session | `GuardResult` / `EffectResult`; статус instance пишет worker |

Platform не парсит внутренности DTO домена для бизнес-логики. Для enrichment FSM-state использует только opaque `entity_type` / `entity_id` из ответа (если есть).

### 6.7. Граница данных

| Данные | Где | Кто пишет |
|--------|-----|-----------|
| instances, `entity_fsm_state`, logs, timers | platform DB | platform |
| FSM-граф, бизнес-таблицы, ХП домена | domain DB | домен (seed/devops + effects/db_layer) |
| Domain Registry (`service_id`, `cartridge_type`, version, package hash, DB secret, status) | platform DB / config | platform (Accept / bootstrap) |

### 6.8. Связка сущностей (пример)

```text
server_fsm_instance (platform DB):
  service=svc_courier_acme_01          # service_id, не cartridge_type
  process_name=order_creation
  entity_type=order_request
  entity_id=348

entity_fsm_state (platform DB):
  (svc_courier_acme_01, order_request, 348) → request_fulfilled

Domain Registry (platform DB):
  service_id=svc_courier_acme_01, cartridge_type=courier, status=active

fsm_transitions (domain DB этого service_id):
  order_request: request_received --order_create--> request_fulfilled

order_requests / orders (domain DB):
  бизнес-данные; обновляются в effect через domain db_layer
```

Platform: HTTP-слой + процесс + FSM-state + log + Domain Registry.  
Домен: граф FSM + бизнес-данные + handlers + db_layer + effects.

---

## 7. Добавление нового домена и Domain Validator

### 7.1. Условия, при которых platform может работать с доменом

Домен допускается к работе только если одновременно:

1. Пакет картриджа (`cartridge_type`) установлен и проходит **проверку целостности пакета**.
2. В Domain Registry сохранены уникальный **`service_id`**, `cartridge_type`, version, package checksum, secret domain DB.
3. Domain DB доступна и проходит **проверку готовности SQL/ХП/графа**.
4. Python RAM-registry согласован с FSM-графом в domain DB.
5. Статус в Domain Registry = `active` (после успешного Accept / boot validation).

Иначе статус `failed` / `pending` — REST и FSM для этого `service_id` не обслуживаются.

### 7.2. Способы добавления

| Способ | Действия |
|--------|----------|
| Ops / конфиг | пакет картриджа, URL DB, выдача `service_id`, рестарт |
| Админ-UI (целевой) | upload пакета (`cartridge_type`), Domain DB URL, Accept → validate → **сгенерировать service_id** → persist → install → restart |

Накат схемы domain DB в v1 — **на стороне заказчика** до Accept. Platform проверяет готовность, не накатывает DDL по умолчанию.

### 7.3. Domain Validator — целостность пакета

Компонент platform (например `platform/domain_validator.py`), запускается на Accept и при каждом boot active-домена.

**Пакет:**

- архив/дерево: размер, отсутствие path traversal (`..`), allowlist расширений;
- обязателен `manifest.yaml`: `cartridge_type`, `version`, `entry` (`…:register_all`), required tables/routines;
- `cartridge_type` — тип пакета; **`service_id` уникален** (выдаёт platform, не заказчик);
- checksum пакета сохранён в Domain Registry;
- обязательные модули на месте (`processes.py`, … по контракту картриджа);
- `import` entrypoint и вызов `register_all(service_id)` без исключения;
- после регистрации: есть ≥1 ProcessDef и/или ≥1 HTTP route;
- `(service_id, process_name)` уникальны глобально в FSM Registry (RAM).

### 7.4. Domain Validator — готовность domain DB (SQL / ХП / граф)

По connection из Accept / env:

1. **Connectivity** — connect + auth в timeout.
2. **FSM-граф** — существуют таблицы `fsm_states`, `fsm_events`, `fsm_transitions` (или эквивалент контракта); в transitions есть строки для entity_type домена.
3. **Согласованность граф ↔ Python** — каждый непустой `guard_name` / `effect_name` из transitions зарегистрирован в Guard/Effect Registry; лишние Python-имена — warning.
4. **Бизнес-схема** — минимальный набор объектов из `manifest` (required tables / routines); отсутствие → fail.
5. **ХП домена** (если указаны в manifest) — routines существуют и доступны пользователю DB.
6. **Граница** — очередь FSM (`server_fsm_instances`) и `entity_fsm_state` живут в platform DB; domain DB не является их источником истины.

Platform не интерпретирует бизнес-смысл таблиц; только наличие объектов и связность с registry.

### 7.5. Поток Accept (админ-UI)

```text
1. Upload package (zip, cartridge_type из manifest) + Domain DB URL → secret store
2. Domain Validator: пакет
3. Platform генерирует service_id
4. Install files (package ref / domains/<cartridge_type>/… версионированно)
5. Persist Domain Registry: service_id, cartridge_type, version, checksum, secret_id, status=pending
6. Domain Validator: domain DB (SQL/ХП/граф) + register_all(service_id) в RAM + согласованность
7. status=active | failed (+ отчёт ошибок в UI)
8. Restart API/worker (v1) → boot: для каждого active service_id заново наполняет RAM-реестры
9. UI показывает service_id и результат валидации
```

Каналы входа после регистрации (OpenAPI, enqueue UX, мессенджеры) — вне scope этого раздела.

**Запрещено:** Accept без успешного Validator; обслуживание `service_id` при `failed`.

### 7.6. Что хранит platform о домене

Схема полей Domain Registry — §6.3 (`domain_services`).  
Кратко: `service_id`, `cartridge_type`, `version`, package ref/checksum, `db_secret_ref`, `status`, validation report, аудит.

### 7.7. Disable / Upgrade (минимум)

- **Disable** — status=`disabled`, routes/FSM для `service_id` не принимаются; пакет и DB не удаляются.
- **Upgrade** — новый пакет → Validator → смена version/checksum → restart; при fail остаётся предыдущий active.

---


## 8. Модули fsm_core

Пакет `fsm_core/` — **единственный** runtime декларативного FSM. Его вызывает worker (и только worker) для async lifecycle. HTTP Query/Command в `fsm_core` не входят.

### 8.0. Состав пакета

| Файл | Статус | Роль |
|------|--------|------|
| `__init__.py` | есть | публичный API пакета |
| `types.py` | есть | dataclass и сигнатуры |
| `registry.py` | есть → доработать | RAM: ProcessDef, guards, effects **с ключом service_id** |
| `engine.py` | есть | вход `run_instance` |
| `transition_runner.py` | есть | pipeline одного шага |
| `timers.py` | есть | schedule/cancel → `fsm_timers` |
| `errors.py` | **добавить** | типизированные коды ошибок FSM |
| `state_store.py` | **добавить** | чтение/запись `entity_fsm_state` (platform DB) |
| `transition_repository.py` | **добавить** | чтение candidates из domain DB (`fsm_transitions`…) |
| `transition_executor.py` | **добавить** | применение перехода: state + log **только** platform DB |

Сейчас часть SQL сидит в монолитном `db_layer.py` (IF по entity_type, `fsm_perform_transition` трогает domain). Цель: вынести доступ к FSM-state и графу в модули выше; `db_layer` общий не знает схему courier.

**Зависимости снаружи пакета (не файлы fsm_core, но обязательны):**

| Компонент | Где | Роль относительно fsm_core |
|-----------|-----|----------------------------|
| `fsm_worker.py` | platform | session, claim `server_fsm_instances`, commit, вызывает `run_instance` |
| Domain `register_all` | domains/ | наполняет `registry.py` |
| platform/http Route Registry | platform | HTTP; **не** часть fsm_core |
| Domain Validator | platform | сверяет граф SQL с Guard/Effect Registry |

```text
fsm_worker
  → fsm_core.engine.run_instance(session_platform, session_domain|db_facade, runtime_ctx, instance)
       → registry.ProcessRegistry
       → transition_runner.TransitionRunner
            → state_store          (platform DB)
            → transition_repository (domain DB)
            → registry guards
            → transition_executor  (platform DB)
            → registry effects     (domain DB через session домена)
```

---

### 8.1. Общие правила для всего `fsm_core`

1. **Не импортировать** `domains.*`. Только callable из registry / ProcessDef.
2. **Не открывать** session/engine. Session(s) передаёт worker.
3. **Не коммитить** транзакцию. Commit/rollback — worker.
4. **Не знать** имён business-таблиц (`orders`, `taxi_orders`, …).
5. **Не обслуживать** HTTP. Только FSM instance.
6. Ошибки шага возвращать как `FsmResult(new_state="FAILED", last_error="<CODE>: …")`, не ронять процесс worker необработанным исключением (кроме неожиданных багов инфраструктуры).
7. `service` везде = **`service_id`** (§6.1).

---

### 8.2. `types.py`

**Назначение:** единый контракт данных между worker ↔ fsm_core ↔ доменом. Без I/O и без SQL.

#### 8.2.1. `FsmResult`

Возвращается из `engine.run_instance` в worker.

| Поле | Тип | Смысл |
|------|-----|--------|
| `new_state` | `str` | статус **instance** для worker: `COMPLETED`, `FAILED`, `WAITING` (и др. по политике), не путать с entity FSM-state |
| `last_error` | `str \| None` | код/текст для `server_fsm_instances.last_error` |
| `next_timer_at` | `datetime \| None` | подсказка worker/timer (опционально) |
| `attempts_increment` | `int` | на сколько увеличить `attempts` (обычно 1) |
| `payload` | `dict \| None` | диагностика: transition_id, from/to, effect payload |

Worker по `new_state`:
- `COMPLETED` → commit, instance COMPLETED;
- `FAILED` → rollback (или политика), instance FAILED + last_error;
- `WAITING` → по политике (не завершать окончательно / отложить).

#### 8.2.2. `GuardResult` / `EffectResult`

| Тип | Поля | Кто возвращает |
|-----|------|----------------|
| `GuardResult` | `ok: bool`, `reason`, `payload` | guard домена |
| `EffectResult` | `ok: bool`, `error`, `payload` | effect домена |

`TransitionRunner` обязан нормализовать legacy-ответы (`bool`, `(ok, reason)`) к этим типам — для совместимости, но **новые** домены пишут только dataclass.

#### 8.2.3. `ProcessDef`

Описание job, который worker кладёт в `server_fsm_instances.process_name`.

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `service` | да | `service_id` |
| `process_name` | да | имя job; ключ вместе с service |
| `entity_type` | да (цель) | тип сущности FSM |
| `event_name` | да (цель) | событие графа; если пусто — fallback `process_name` (`runtime_event_name`) |
| `context_builder` | да для реальных процессов | `(session, db, runtime_ctx, instance) → dict` |

Свойство `runtime_event_name` = `event_name or process_name`.

#### 8.2.4. `TransitionDef`

Нормализованный candidate после чтения из domain DB.

| Поле | Источник в SQL |
|------|----------------|
| `id` | `fsm_transitions.id` |
| `entity_type` | `fsm_transitions.entity_type` |
| `from_state` / `to_state` | имена из `fsm_states` |
| `event_name` | имя из `fsm_events` |
| `guard_name` / `guard_params` | колонки transition |
| `priority` | меньше = раньше |
| `effect_name` / `effect_params` | колонки transition |

#### 8.2.5. Сигнатуры callable (цель)

```python
ContextBuilder = Callable[
    [Any, Any, RuntimeContext, InstanceDict], Dict[str, Any]
]
# (platform_or_domain_session, db_facade, runtime_ctx, instance) → context

GuardFunction = Callable[
    [Any, Any, Dict[str, Any], InstanceDict, Dict[str, Any]], GuardResult
]
# (session, db, context, instance, guard_params) → GuardResult

EffectFunction = Callable[
    [Any, Any, Dict[str, Any], InstanceDict, Dict[str, Any]], EffectResult
]
# (session, db, context, instance, effect_params) → EffectResult
```

**БД:** файл таблицы не трогает.

---

### 8.3. `registry.py`

**Назначение:** хранить в **RAM процесса worker/API на сервере** соответствие имён из SQL-графа и ProcessDef → Python-callable. Наполнение при boot через `register_all(service_id)`. Не персистится на диск; после рестарта строится заново.

Глобальные синглтоны (или один контейнер `FsmRegistries`, передаваемый в engine — допустимо при тестах):

- `default_process_registry`
- `default_guard_registry`
- `default_effect_registry`

#### 8.3.1. `ProcessRegistry` (есть)

**Структура RAM:**

```text
_processes: dict[(service_id, process_name), ProcessDef]
```

| Метод | Контракт |
|-------|----------|
| `register(process_def) -> ProcessDef` | key=`(process_def.service, process_def.process_name)`; повторная регистрация заменяет |
| `get(service_id, process_name) -> ProcessDef \| None` | lookup для engine |
| `has(service_id, process_name) -> bool` | |
| `list_process_names(service_id=None) -> list[str]` | для валидации enqueue |
| `list_processes() -> list[ProcessDef]` | для Validator / отладки |
| `clear()` **добавить** | для тестов / hot-reload |
| `unregister(service_id)` **добавить** | убрать все процессы одного домена при Disable |

**Кто вызывает register:** только bootstrap / `domains.*.register_all`, не TransitionRunner.

**БД:** нет.

#### 8.3.2. `GuardRegistry` / `EffectRegistry` (есть → доработать)

**Сейчас в коде:** ключ = `name: str` (глобально на процесс).  
**Цель (обязательная доработка):**

```text
_guards:  dict[(service_id, guard_name), GuardFunction]
_effects: dict[(service_id, effect_name), EffectFunction]
```

| Метод (цель) | Контракт |
|--------------|----------|
| `register(service_id, name, fn)` | записать callable |
| `get(service_id, name) -> fn \| None` | lookup в TransitionRunner |
| `names(service_id=None) -> list[str]` | для Domain Validator |
| `unregister(service_id)` | снять все имена домена |

Пример наполнения — как в §6.4 (`GuardRegistry.register(service_id, "can_create_order", can_create_order)`).

**Связь с БД (косвенная):** строки `fsm_transitions.guard_name` / `effect_name` в **domain DB** должны существовать в registry для этого `service_id`. Проверяет Domain Validator при Accept/boot; в runtime отсутствие → `UNKNOWN_GUARD` / `UNKNOWN_EFFECT`.

**БД напрямую:** нет.

#### 8.3.3. Алгоритм boot → RAM

```text
1. Domain Registry (platform DB): SELECT service_id WHERE status='active'
2. Для каждого service_id:
   a. import package по cartridge_type
   b. register_all(service_id)
        → ProcessRegistry.register(ProcessDef(service=service_id, …))
        → GuardRegistry.register(service_id, name, fn)
        → EffectRegistry.register(service_id, name, fn)
   c. Domain Validator сверяет SQL-граф domain DB с names(service_id)
3. Worker готов вызывать engine.run_instance
```

---

### 8.4. `engine.py`

**Назначение:** фасад для worker. Одна функция — весь FSM-шаг для одного instance. Не содержит бизнес-логики и SQL.

#### 8.4.1. Сигнатура (цель)

```python
def run_instance(
    session,                    # session platform DB (и/или facade)
    db,                         # facade: state_store + transition_repository + domain access для guards/effects
    runtime_ctx: dict,          # корреляция, trace_id, опции
    instance: dict,             # строка server_fsm_instances как dict
    *,
    process_registry: ProcessRegistry | None = None,
    guard_registry: GuardRegistry | None = None,
    effect_registry: EffectRegistry | None = None,
) -> FsmResult:
```

`instance` минимально содержит:

| Ключ | Смысл |
|------|--------|
| `id` | id instance (для логов) |
| `service` | service_id |
| `process_name` | ключ ProcessDef |
| `entity_type` | тип сущности |
| `entity_id` | id сущности |
| `requested_by_user_id` | для audit transition (опционально) |
| `payload_json` / extras | по необходимости context_builder |

#### 8.4.2. Алгоритм по шагам

```text
1. process_registry = process_registry or default_process_registry
2. service = instance["service"]; process_name = instance.get("process_name")
3. Если process_name пуст:
     return FsmResult(FAILED, last_error="MISSING_PROCESS_NAME", attempts_increment=1)
4. process_def = process_registry.get(service, process_name)
5. Если process_def is None:
     log error
     return FsmResult(FAILED, last_error=f"UNKNOWN_PROCESS: {service}/{process_name}")
6. runner = TransitionRunner(guard_registry=…, effect_registry=…,
                             state_store=…, transition_repository=…, transition_executor=…)
   (в целевой реализации зависимости передаются явно или через db-facade)
7. result = runner.run(session, db, runtime_ctx, instance, process_def)
8. Если result.new_state не из допустимого набора instance-статусов:
     result = FsmResult(FAILED, last_error=result.last_error or "INVALID_STATE_RETURNED")
9. return result
```

Допустимые `new_state` для instance: `COMPLETED`, `FAILED`, `WAITING`, при необходимости `PROCESSING` (обычно не возвращается из runner).

#### 8.4.3. БД

Напрямую — **нет**.  
Косвенно: worker до вызова уже прочитал/обновил `server_fsm_instances` (claim PROCESSING).

#### 8.4.4. Запрещено в engine

- вызывать guards/effects напрямую в обход TransitionRunner;
- писать в domain tables;
- менять статус instance (это worker после return).

---

### 8.5. `transition_runner.py`

**Назначение:** исполнить **ровно один** декларативный переход: выбрать transition по графу и guards, применить FSM-state, выполнить effect.

Класс: `TransitionRunner`.

#### 8.5.1. Зависимости (цель)

```python
class TransitionRunner:
    def __init__(
        self,
        guard_registry: GuardRegistry,
        effect_registry: EffectRegistry,
        state_store: EntityStateStore,           # §8.8
        transition_repository: TransitionRepository,  # §8.9
        transition_executor: TransitionExecutor,      # §8.10
    ): ...
```

Сейчас в коде вместо store/repository/executor вызывается монолитный `db.*`. При разработке заменить на модули ниже, сохранив алгоритм `run`.

#### 8.5.2. Алгоритм `run` (нормативный)

Вход: `session`, `db`, `runtime_ctx`, `instance`, `process_def`.  
`service_id = instance["service"]`.

```text
1. CONTEXT
   Если process_def.context_builder задан:
     domain_context = context_builder(session, db, runtime_ctx, instance)
   Иначе domain_context = {}
   Ошибка builder → FAILED (CONTEXT_BUILD_FAILED) или проброс по политике

2. ИДЕНТИФИКАТОРЫ
   entity_type = process_def.entity_type or instance["entity_type"]
   entity_id = instance["entity_id"]
   event_name = process_def.runtime_event_name
   user_id = instance.get("requested_by_user_id") or 0
   Если нет entity_type → FAILED MISSING_ENTITY_TYPE
   Если entity_id is None → FAILED MISSING_ENTITY_ID

3. CURRENT STATE
   current_state = state_store.get(session_platform, service_id, entity_type, entity_id)
   Если None → FAILED ENTITY_STATE_NOT_FOUND: {entity_type}/{entity_id}

4. CANDIDATES
   rows = transition_repository.list_candidates(
       session_domain, entity_type, current_state, event_name
   )
   candidates = [TransitionDef.from_row(r) for r in rows]
   Если пусто → FAILED NO_CANDIDATE_TRANSITIONS: {entity_type}/{current_state}/{event_name}

5. PRIORITY
   Если два candidate с одинаковым priority → FAILED AMBIGUOUS_TRANSITION: …/priority=N
   Иначе сортировка уже priority ASC, id ASC (из SQL ORDER BY)

6. SELECT (guards)
   selected = None
   Для каждого candidate в порядке priority:
     Если guard_name is NULL/пустой → selected = candidate; break
     guard_fn = guard_registry.get(service_id, guard_name)
     Если нет → FAILED UNKNOWN_GUARD: {guard_name}
     result = normalize(guard_fn(session, db, domain_context, instance, guard_params))
     Если result.ok → selected = candidate; break
     Иначе log warning (transition_id, guard, reason); продолжить
   Если selected is None → FAILED NO_GUARD_MATCHED: {entity_type}/{current_state}/{event_name} [+ last reason]

7. SQL TRANSITION (platform only)
   transition_executor.apply(
       session_platform,
       service_id=service_id,
       entity_type=entity_type,
       entity_id=entity_id,
       transition=selected,
       event_name=event_name,
       user_id=user_id,
   )
   # пишет entity_fsm_state + log; НЕ трогает orders/…

8. EFFECT
   Если selected.effect_name:
     effect_fn = effect_registry.get(service_id, effect_name)
     Если нет → FAILED UNKNOWN_EFFECT
     effect_result = normalize(effect_fn(session, db, domain_context, instance, effect_params))
     Если не ok → FAILED EFFECT_FAILED / effect_result.error
     # effect пишет domain DB через domain db_layer

9. SUCCESS
   return FsmResult(
     new_state="COMPLETED",
     attempts_increment=1,
     payload={
       "transition_id", "from_state", "to_state", "event_name",
       "effect": effect_payload
     }
   )
```

#### 8.5.3. Коды `last_error` (зафиксировать в `errors.py`)

| Код | Когда |
|-----|--------|
| `MISSING_ENTITY_TYPE` | нет entity_type |
| `MISSING_ENTITY_ID` | нет entity_id |
| `ENTITY_STATE_NOT_FOUND` | нет строки state |
| `NO_CANDIDATE_TRANSITIONS` | граф не дал переходов |
| `AMBIGUOUS_TRANSITION` | два transition с одним priority |
| `UNKNOWN_GUARD` | guard_name нет в registry |
| `NO_GUARD_MATCHED` | все guards false |
| `UNKNOWN_EFFECT` | effect_name нет в registry |
| `EFFECT_FAILED` | effect вернул ok=false |
| `TRANSITION_APPLY_FAILED` | executor/SQL ошибка |

#### 8.5.4. БД (через зависимости, не сырой SQL в runner)

| Шаг | Модуль | БД | Таблицы |
|-----|--------|-----|---------|
| current state | state_store | platform | `entity_fsm_state` |
| candidates | transition_repository | domain | `fsm_transitions`, `fsm_states`, `fsm_events` |
| apply | transition_executor | platform | `entity_fsm_state`, `fsm_action_logs` / `fsm_transition_logs` |
| effect | код домена | domain | business tables (через domain db_layer) |

#### 8.5.5. Запрещено в TransitionRunner

- IF по `entity_type` / pickup_type / courier;
- прямой SQL;
- commit;
- обновление `server_fsm_instances`;
- UPDATE business tables (только effect домена).

---

### 8.6. `timers.py`

**Назначение:** API для планирования отложенного повторного запуска процесса. Не поллит таймеры и не создаёт instance сам.

#### 8.6.1. `schedule_timer`

```python
def schedule_timer(
    session, db, *,
    service: str,          # service_id
    entity_type: str,
    entity_id: int,
    process_name: str,     # какой ProcessDef поставить в очередь при срабатывании
    fire_at: datetime,
    payload: dict | None = None,
    idempotency_key: str | None = None,
) -> int:  # timer id
```

Поведение: делегирует в persistence (`db.create_fsm_timer` или прямой INSERT через platform timer store).

**Таблица platform DB `fsm_timers` (поля минимум):**

| Колонка | Смысл |
|---------|--------|
| `id` | PK |
| `service` | service_id |
| `entity_type`, `entity_id` | сущность |
| `process_name` | какой job enqueue при fire |
| `fire_at` | когда сработать |
| `status` | `SCHEDULED` / `FIRED` / `CANCELLED` |
| `payload_json` | опционально |
| `idempotency_key` | опционально, уникальность |
| `created_at`, `cancelled_at` | аудит |

Возврат: `id` вставленной строки.

#### 8.6.2. `cancel_timer`

```python
def cancel_timer(session, db, timer_id: int) -> None
```

`UPDATE fsm_timers SET status='CANCELLED', cancelled_at=NOW() WHERE id=:timer_id` (и при необходимости только если `SCHEDULED`).

#### 8.6.3. Кто вызывает fire (вне timers.py)

Отдельный **timer worker** (platform):

```text
SELECT … FROM fsm_timers WHERE status='SCHEDULED' AND fire_at <= NOW()
  → enqueue server_fsm_instances(service, process_name, entity_type, entity_id)
  → пометить timer FIRED
```

`fsm_core.timers` это **не** делает.

---

### 8.7. `errors.py` — **добавить**

**Назначение:** константы кодов ошибок и optionally исключения для инфраструктуры (не для штатного NO_GUARD_MATCHED).

```python
class FsmErrorCodes:
    MISSING_PROCESS_NAME = "MISSING_PROCESS_NAME"
    UNKNOWN_PROCESS = "UNKNOWN_PROCESS"
    MISSING_ENTITY_TYPE = "MISSING_ENTITY_TYPE"
    # … полный список из §8.5.3 и engine
```

Штатный fail шага = `FsmResult` + код в `last_error`, не обязательно exception.  
Exception — для поломки SQL connection, багов executor.

**БД:** нет.

---

### 8.8. `state_store.py` — **добавить**

**Назначение:** единственное место в fsm_core, которое читает/пишет текущий FSM-state сущности в **platform DB**. Заменяет IF `entity_type → SELECT status FROM orders` в монолите.

#### 8.8.1. Интерфейс

```python
class EntityStateStore:
    def get(
        self, session, service_id: str, entity_type: str, entity_id: int
    ) -> str | None:
        """SELECT current_state FROM entity_fsm_state WHERE …"""

    def set(
        self, session, service_id: str, entity_type: str, entity_id: int,
        new_state: str, *, expected_state: str | None = None,
    ) -> None:
        """UPSERT/UPDATE current_state; optimistic lock по expected_state опционально."""
```

#### 8.8.2. Таблица `entity_fsm_state` (platform DB)

| Колонка | Смысл |
|---------|--------|
| `service_id` | экземпляр домена |
| `entity_type` | opaque тип |
| `entity_id` | opaque id |
| `current_state` | имя состояния (как в fsm_states.name домена) |
| `updated_at` | аудит |

PK: `(service_id, entity_type, entity_id)`.

#### 8.8.3. Кто вызывает

- `get` — TransitionRunner шаг 3;
- `set` — TransitionExecutor при apply (или store вызывается из executor).

**Запрещено:** читать status из `orders` / domain tables.

---

### 8.9. `transition_repository.py` — **добавить**

**Назначение:** читать declarative graph из **domain DB**. Единственное место fsm_core с SELECT по `fsm_transitions`.

#### 8.9.1. Интерфейс

```python
class TransitionRepository:
    def list_candidates(
        self,
        session_domain,
        *,
        entity_type: str,
        current_state: str,
        event_name: str,
    ) -> list[dict]:
        """Строки для TransitionDef; ORDER BY priority ASC, id ASC."""
```

#### 8.9.2. SQL (норматив)

```sql
SELECT
  ft.id,
  ft.entity_type,
  fs_from.name AS from_state,
  fs_to.name   AS to_state,
  fe.name      AS event_name,
  ft.guard_name,
  ft.guard_params,
  ft.priority,
  ft.effect_name,
  ft.effect_params
FROM fsm_transitions ft
JOIN fsm_states fs_from ON fs_from.id = ft.from_state_id
JOIN fsm_states fs_to   ON fs_to.id   = ft.to_state_id
JOIN fsm_events fe      ON fe.id      = ft.event_id
WHERE ft.entity_type = :entity_type
  AND fs_from.name   = :current_state
  AND fe.name        = :event_name
ORDER BY ft.priority ASC, ft.id ASC
```

Session = connection к domain DB данного `service_id` (worker уже открыл).

#### 8.9.3. Таблицы domain DB

`fsm_transitions`, `fsm_states`, `fsm_events` — только чтение в этом модуле.

---

### 8.10. `transition_executor.py` — **добавить**

**Назначение:** атомарно применить выбранный transition к platform state + записать audit log. **Запрещено** UPDATE/INSERT business tables домена.

#### 8.10.1. Интерфейс

```python
class TransitionExecutor:
    def apply(
        self,
        session_platform,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        transition: TransitionDef,
        event_name: str,
        user_id: int,
    ) -> None:
        """
        1) Проверить, что entity_fsm_state.current_state == transition.from_state
           (иначе ошибка CONCURRENT_STATE_MISMATCH / TRANSITION_APPLY_FAILED)
        2) state_store.set(…, new_state=transition.to_state)
        3) INSERT в fsm_transition_logs / fsm_action_logs
        """
```

#### 8.10.2. Таблицы platform DB

| Таблица | Операция |
|--------|----------|
| `entity_fsm_state` | UPDATE/UPSERT `current_state = to_state` |
| `fsm_transition_logs` или `fsm_action_logs` | INSERT: service_id, entity_type, entity_id, transition_id, from, to, event, user_id, ts |

#### 8.10.3. Что удаляется из легаси

Процедура/`db.perform_transition`, которая делает `UPDATE orders SET status=…` и IF по entity_type — **не используется**. Бизнес-status, если нужен денормализованно в domain — только в **effect** домена.

Реализация может быть Python SQLAlchemy или тонкая stored procedure **только** над platform tables — без знания domain schema.

---

### 8.11. `__init__.py`

**Назначение:** стабильный публичный API:

```python
from .engine import run_instance
from .registry import (
    ProcessRegistry, GuardRegistry, EffectRegistry,
    default_process_registry, default_guard_registry, default_effect_registry,
)
from .types import FsmResult, GuardResult, EffectResult, ProcessDef, TransitionDef
from .timers import schedule_timer, cancel_timer
# целевое:
# from .state_store import EntityStateStore
# from .transition_repository import TransitionRepository
# from .transition_executor import TransitionExecutor
# from .errors import FsmErrorCodes
```

Логики нет. **БД:** нет.

---

### 8.12. Полный runtime-сценарий (сборка модулей)

```text
A. BOOT
   Domain Registry → active service_id
   register_all(service_id) → registry.py (RAM)
   Validator: domain fsm_transitions names ⊆ Guard/Effect Registry

B. ENQUEUE (не fsm_core)
   INSERT server_fsm_instances(service_id, process_name, entity_type, entity_id, PENDING)
   при создании сущности: INSERT entity_fsm_state(…, current_state=initial)

C. WORKER
   BEGIN
   claim instance → PROCESSING
   open session_platform + session_domain(service_id)
   result = engine.run_instance(...)
       ProcessRegistry.get
       TransitionRunner.run
         context_builder (domain)
         state_store.get → entity_fsm_state
         transition_repository.list_candidates → fsm_* domain
         guards (domain callables)
         transition_executor.apply → entity_fsm_state + logs
         effect (domain db_layer → business tables)
   if COMPLETED: COMMIT; instance COMPLETED
   if FAILED: ROLLBACK; instance FAILED + last_error
```

---

### 8.13. Сводка таблиц по модулям fsm_core

| Модуль | Platform DB | Domain DB |
|--------|-------------|-----------|
| `types.py`, `__init__.py`, `errors.py`, `registry.py` | — | — |
| `engine.py` | — (instance dict уже из worker) | — |
| `state_store.py` | `entity_fsm_state` R/W | — |
| `transition_repository.py` | — | `fsm_transitions`, `fsm_states`, `fsm_events` R |
| `transition_executor.py` | `entity_fsm_state` W, logs W | — |
| `transition_runner.py` | через store/executor | через repository; effect → business |
| `timers.py` | `fsm_timers` | — |

Вне fsm_core: `server_fsm_instances`, `domain_services` — worker/bootstrap/Accept.

---

### 8.14. Чеклист реализации fsm_core

- [ ] Доработать Guard/Effect Registry: ключ `(service_id, name)`.
- [ ] Добавить `errors.py` с кодами §8.5.3.
- [ ] Добавить `state_store.py` + миграция `entity_fsm_state`.
- [ ] Добавить `transition_repository.py` (SQL §8.9.2) на session domain DB.
- [ ] Добавить `transition_executor.py` без UPDATE domain business tables.
- [ ] Перевести `TransitionRunner` на store/repository/executor; убрать зависимость от IF в `db_layer`.
- [ ] `engine.run_instance` принимает/прокидывает registry и зависимости явно (удобно для тестов).
- [ ] Юнит-тесты: ambiguous priority, NO_GUARD_MATCHED, UNKNOWN_EFFECT, happy path COMPLETED.
- [ ] Интеграционный smoke: один service_id courier end-to-end через worker.

---

## 9. Эволюция от текущего монолита

| Сейчас | Цель |
|--------|------|
| Одна БД testdb | platform DB + domain DB на каждый домен |
| FSM-граф и business в одной БД | граф в domain DB (картридж) |
| state на `orders.status` | `entity_fsm_state` в platform DB |
| `fsm_perform_transition` UPDATE domain tables | только platform state; domain UPDATE в effects |
| IF entity_type в общем `db_layer` | domain `db_layer.py` + routing по `service` |
| Роуты и session в `main.py` | Gateway + Route Registry + Request Runtime |
| Ручной список доменов без validator | Domain Registry + Domain Validator (пакет + SQL/ХП) |
| `fsm_engine.PROCESS_DEFS` | declarative transitions + registry |
| общие migrations | SQL seed в `domains/<name>/sql/` (накат вне Accept в v1) |

---

## 10. Пример: courier vs taxi

| | Courier | Taxi |
|---|---------|------|
| Staging | `order_request` | опционально / сразу `taxi_order` |
| Creation process | `order_creation` | `submit_ride` |
| entity_type | `order_request` | `taxi_order` |
| event | `order_create` | `ride_submit` |
| Первый state | `request_received` | `draft` |
| Domain DB | FSM-граф + orders, locker_cells, … | FSM-граф + taxi_orders, … |

Один `fsm_core`, разные картриджи. Подключение каждого — через контракт §6 и Validator §7.

---

## 11. Критерии готовности platform

- [ ] Worker обрабатывает instance через `fsm_core.run_instance` без domain-specific кода в core.
- [ ] Guard routing по priority работает и логирует reason при отказе.
- [ ] SQL Core обновляет только platform DB (`entity_fsm_state`, logs).
- [ ] `get_candidate_transitions` читает domain DB по `service`.
- [ ] Bootstrap: active домены из Domain Registry / `FSM_DOMAINS` → `register_all`.
- [ ] Domain Validator: целостность пакета + готовность SQL/ХП/графа + согласованность registry.
- [ ] Домен `failed`/`disabled` не обслуживает REST и FSM.
- [ ] Route Registry + Dispatcher + Request Runtime для REST.
- [ ] Request Runtime владеет session на HTTP-запрос; домен session не открывает.
- [ ] Query: Gateway → Runtime → domain handler → domain db_layer; без FSM instance.
- [ ] Command: staging/enqueue через Runtime; lifecycle в worker.
- [ ] Smoke: минимум один домен end-to-end (Command + Query).

## 12. Критерии готовности домена

- [ ] `manifest.yaml` + структура картриджа §5.1.
- [ ] `register_all()` (FSM + HTTP routes).
- [ ] Domain DB: FSM-граф + бизнес-схема (+ ХП по manifest) до Accept.
- [ ] Все guard_name/effect_name из SQL зарегистрированы в Python.
- [ ] Effects обновляют domain DB через domain db_layer; SQL Core platform domain tables не трогает.
- [ ] `db_layer.py` — единственное место бизнес-SQL домена; session только аргумент.
- [ ] Query handlers в `queries.py`; список сущностей не идёт через FSM.
- [ ] Проходит Domain Validator → `active`.
- [ ] Smoke Command / Query после активации.

---

## 13. Глоссарий

| Термин | Значение |
|--------|----------|
| Platform | FSM Platform: worker, fsm_core, HTTP-слой, platform DB, bootstrap, validator |
| Domain / картридж | courier, taxi, cargo — SQL + Python + db_layer, своя domain DB |
| Domain Registry | таблица platform DB (`domain_services`): каталог service_id / cartridge_type / status / DB / package; см. §6.3 |
| Domain Validator | проверка целостности пакета и готовности domain DB (SQL/ХП/граф) |
| cartridge_type | тип картриджа (`cargo`, `courier`); не обязан быть уникальным |
| service_id | уникальный id экземпляра домена; ключ runtime и Domain Registry |
| Route/FSM Registry | dict в RAM процесса API/worker на сервере; наполняется `register_*` при boot; см. §6.4 |
| manifest.yaml | метаданные картриджа: cartridge_type, version, entry, required objects |
| ProcessDef | job: service_id, process_name, entity_type, event_name |
| Instance | строка `server_fsm_instances` — задача worker |
| entity_type + entity_id | opaque указатель домена для platform |
| SQL transition | смена FSM-state в platform DB (SQL Core) |
| Effect | доменный код после transition; запись через domain db_layer |
| Domain db_layer | SQL-доступ к domain DB; session от platform |
| SQL seed | SQL картриджа для domain DB (накат до Accept в v1) |
| Guard routing | выбор transition по priority и guards |
| Gateway | HTTP in/out, auth, JSON; без бизнес-SQL |
| Route Registry | RAM: `(service_id, method, path) → handler, kind`; наполняется при boot |
| Dispatcher | поиск route и передача в Request Runtime |
| Request Runtime | владелец session на REST-запрос; вызов domain handler |
| Domain handler | use-case домена (query/command entry); session только принимает |
| domain session | session к domain DB, созданная platform (Runtime/worker), не доменом |
| Command | REST, меняющий lifecycle → enqueue FSM |
| Query | REST без FSM; чтение через domain handler + db_layer |
| Accept | операция добавления/активации домена (UI или ops) после Validator |
| Channel | Telegram/WhatsApp/Web — адаптер ввода-вывода (вне scope §6–7) |
| TransitionRunner | `fsm_core/transition_runner.py` — pipeline одного FSM-шага; §8.5 |
| run_instance | `fsm_core/engine.py` — вход worker в FSM; §8.4 |
| EntityStateStore | `fsm_core/state_store.py` — R/W `entity_fsm_state`; §8.8 (**добавить**) |
| TransitionRepository | `fsm_core/transition_repository.py` — candidates из domain DB; §8.9 (**добавить**) |
| TransitionExecutor | `fsm_core/transition_executor.py` — apply state+log platform; §8.10 (**добавить**) |

# FSM Platform и домены: требования к архитектуре

Документ фиксирует целевую модель **автономной FSM Platform** и правила подключения **доменов-картриджей** (courier, taxi, cargo и др.).

Связанный документ с деталями runtime pipeline: [fsm-platform-rfc-implementation.md](fsm-platform-rfc-implementation.md).

---

## 1. Видение

FSM Platform — **универсальный движок оркестрации**. Ему безразлично:

- какой домен подключён (courier, taxi, cargo);
- какие имена state/event используются;
- как устроены бизнес-таблицы домена.

Домен подключается как **картридж**: пакет SQL + Python, который регистрируется в platform без изменения ядра `fsm_core`.

В перспективе поверх platform добавляется **слой каналов** (Telegram, WhatsApp, Web, голос): каналы вызывают процессы доменов и доставляют ответы пользователю, не зная внутренней логики courier/taxi.

```text
Каналы (Telegram, Web, …)
        ↓
FSM Platform (instances, worker, fsm_core)
        ↓
Домены-картриджи (courier, taxi, …)
        ↓
БД домена (orders, taxi_orders, …)
```

---

## 2. Принципы

1. **Platform agnostic** — `fsm_core` не содержит бизнес-условий и не импортирует домены напрямую (только registry/bootstrap).
2. **Декларативный граф** — переходы описаны в данных (`fsm_transitions`), не в Python handler map (`state → function`).
3. **Pipeline** — `context → guard → transition → effect`.
4. **Guard routing** — при нескольких candidate transitions выбор по `priority ASC` и первому guard с `ok=true`.
5. **Домен изолирован** — свой граф FSM (или свой namespace), свои таблицы, свои guards/effects; platform не UPDATEит domain tables при смене FSM-state (целевой вариант A).
6. **Картридж** — добавление домена = SQL seed + Python register + конфиг, без правки ядра platform.
7. **Side effects наружу** — HTTP в Core, push, мессенджеры только через outbox/worker, не внутри SQL-транзакции FSM.

---

## 3. Требования к FSM Platform

### 3.1. Назначение

Platform обеспечивает:

- постановку и выполнение FSM-задач (`server_fsm_instances`);
- единый pipeline перехода (`fsm_core`);
- хранение FSM-state сущностей (целевой вариант — в platform DB);
- журнал переходов, таймеры, outbox для асинхронных интеграций;
- маршрутизацию к домену по полю `service` на instance.

Platform **не** обязана:

- знать схему `orders`, `taxi_orders` и т.п.;
- содержать бизнес-правила courier/taxi в ядре.

### 3.2. Компоненты platform (Python)

| Компонент | Путь | Ответственность |
|-----------|------|-----------------|
| Runtime engine | `fsm_core/engine.py` | `run_instance`: ProcessDef → TransitionRunner |
| Transition runner | `fsm_core/transition_runner.py` | context → candidates → guards → SQL transition → effect |
| Registry | `fsm_core/registry.py` | ProcessDef, GuardRegistry, EffectRegistry |
| Types | `fsm_core/types.py` | FsmResult, GuardResult, EffectResult, ProcessDef, TransitionDef |
| Worker | `fsm_worker.py` | poll, claim, commit/rollback, mark FAILED |
| Bootstrap | `domains/bootstrap.py` | загрузка доменов из `FSM_DOMAINS` |

**Запрещено** в `fsm_core`:

- импорты `domains.courier`, `domains.taxi`;
- проверки вида `if pickup_type == "courier"` (это guards домена);
- знание имён domain-таблиц.

### 3.3. Pipeline одного шага FSM

```text
1. Worker claim server_fsm_instance (PENDING → PROCESSING)
2. ProcessRegistry: service + process_name → ProcessDef
3. context_builder(session, db, runtime_ctx, instance) → domain context
4. get_entity_current_state(entity_type, entity_id)
5. get_candidate_transitions(entity_type, current_state, event_name)
6. Сортировка по priority ASC; проверка уникальности priority
7. Для каждого candidate: guard → первый ok=true (или guard_name=NULL)
8. perform_transition(transition_id) — SQL Core / platform state
9. effect (если задан) — доменная логика записи в domain DB / outbox
10. update instance → COMPLETED / FAILED; commit
```

### 3.4. Guard routing

- Несколько transitions на один `(entity_type, from_state, event_name)` — **норма** (ветвление courier/self и т.д.).
- `priority`: меньше = проверяется раньше; **уникален** внутри набора candidates.
- Default transition: `guard_name = NULL`, самый большой `priority`.
- Ни один guard не прошёл → `NO_GUARD_MATCHED`, instance FAILED (или WAITING — по политике домена).

### 3.5. База данных platform (целевая)

**Обязательные таблицы platform:**

| Таблица | Назначение |
|---------|------------|
| `server_fsm_instances` | очередь задач: service, process_name, entity_type, entity_id, fsm_state, attempts |
| `fsm_action_logs` / `fsm_transition_logs` | аудит переходов |
| `fsm_timers` | отложенные события |
| `entity_fsm_state` | текущий FSM-state: `(service, entity_type, entity_id) → current_state` |
| `core_outbox` | асинхронные вызовы внешних систем (опционально на platform) |

**Граф FSM (states, events, transitions)** — один из двух режимов (выбирается при деплое):

| Режим | Где хранится граф | Когда использовать |
|-------|-------------------|---------------------|
| **A. Central catalog** | platform DB, поле `service` на строках | проще старт, одна БД platform |
| **B. Domain catalog** | БД домена | полная изоляция картриджа |

Platform в режиме B при `get_candidate_transitions` использует **connection домена** по `instance.service`.

**Целевое правило (вариант A для state):**

- FSM-state хранится в `entity_fsm_state` (platform).
- SQL Core **не** делает `UPDATE orders.status` / domain tables.
- Domain tables обновляются только в **effects**.

### 3.6. SQL Core

Процедура `fsm_perform_transition` (или эквивалент в platform layer):

- проверяет transition_id, entity_type, event_name, совпадение current_state с from_state;
- обновляет **только** FSM-state в platform (не domain tables);
- пишет log.

Platform SQL Core **не** содержит IF-цепочек `entity_type → orders/trips/...`.

### 3.7. Worker и транзакции

- Один instance = одна логическая операция; commit при успехе, rollback при guard/effect/SQL ошибке.
- При двух БД (platform + domain): platform transition и domain effect — **согласованная последовательность**; при ошибке effect — компенсация или FAILED instance (saga/outbox при необходимости).
- Внешние HTTP/push — только через outbox после commit.

### 3.8. Bootstrap и реестр доменов

- Переменная `FSM_DOMAINS=courier,taxi` — список подключаемых картриджей.
- При старте worker/API: `domains/<name>/processes.register_all()`.
- Целевой **manifest** домена (опционально): `service`, env keys для DB, версия картриджа.

### 3.9. Валидация при старте

Platform/worker при boot:

1. Каждый `ProcessDef` из registry имеет уникальный `(service, process_name)`.
2. Все `guard_name` / `effect_name` из FSM-графа зарегистрированы в registry.
3. Нет orphan `entity_type` в transitions без ProcessDef (warning).
4. (Режим B) connection к domain DB доступен.

### 3.10. Каналы (будущее расширение platform)

Слой **не в домене**:

```text
channels/telegram/   — parse update → Command → enqueue FSM / API
channels/whatsapp/
```

- Канал не знает guards/effects; знает команды и mapping на `service` + `process_name`.
- Ответы — через channel outbox или отдельный notification worker.
- Один и тот же domain process вызывается из Swagger, Telegram, голоса.

---

## 4. Требования к домену (картридж)

### 4.1. Метафора

Домен = **картридж**: SQL-пакет + Python-пакет. Подключение без пересборки platform.

```text
domains/<domain_name>/
  manifest.yaml          # опционально: service, version, db env keys
  sql/
    platform/            # seed FSM-графа (режим A) или регистрация
    domain/              # schema + seed бизнес-таблиц
  processes.py
  context.py
  guards.py
  effects.py
```

### 4.2. Обязательные Python-модули

| Файл | Требование |
|------|------------|
| `processes.py` | `register_all()`: ProcessDef, guards, effects в registry |
| `context.py` | `build_<domain>_context(...)` — данные для guards/effects |
| `guards.py` | функции с сигнатурой `(session, db, context, instance, params) → GuardResult` |
| `effects.py` | функции → `EffectResult`; побочные записи в domain DB / outbox |

**ProcessDef** минимум:

```python
ProcessDef(
    service="<domain>",           # courier | taxi | cargo
    process_name="<job>",         # order_creation | submit_ride
    entity_type="<entity>",       # order_request | taxi_order
    event_name="<fsm_event>",     # order_create | ride_submit
    context_builder=build_..._context,
)
```

- `process_name` — job для worker/API.
- `event_name` — внутренний FSM trigger; **не** приходит с frontend напрямую.

### 4.3. SQL seed домена

При добавлении домена накатываются **два класса** SQL (могут быть разные файлы):

**1. FSM-граф** (platform DB в режиме A **или** domain DB в режиме B):

- `fsm_states` (с `service=<domain>` в режиме A)
- `fsm_events`
- `fsm_transitions` (entity_type, from/to, event, guard_name, effect_name, priority)

**2. Domain schema** (БД домена):

- бизнес-таблицы (`orders`, `taxi_orders`, …);
- **не** смешивать с platform tables (`server_fsm_instances`).

Домен **сам** определяет:

- нужен ли staging (`order_request`) или сразу основная сущность (`taxi_order`);
- цепочку state (courier ≠ taxi);
- какие entity_type используются в processes.

Platform не навязывает единый lifecycle всем доменам.

### 4.4. Guards

- Имена регистрируются в GuardRegistry: `guard_registry.register("can_create_order", fn)`.
- Имена совпадают с `guard_name` в `fsm_transitions`.
- Guard — **read-only** проверки до SQL transition (города, роли, свободные ресурсы, mapping Core).
- На развилках — **отдельные guards** (`pickup_is_courier`, `pickup_is_self`), не один большой if на весь сценарий.

### 4.5. Effects

- Имена в EffectRegistry ↔ `effect_name` в transitions.
- Effect выполняется **после** успешного SQL transition.
- Запись в domain DB, `stage_orders`, резерв ячеек, link request→order, `core_outbox` — здесь.
- При ошибке effect — rollback транзакции worker, instance FAILED.

### 4.6. Context

- Собирает всё нужное для guards/effects из domain DB по `instance.entity_type` / `entity_id`.
- Маппинг полей домена (`sender_delivery` → `pickup_type`) — **только в context**, не в fsm_core.

### 4.7. Что домен не должен делать

- Менять код `fsm_core` / `transition_runner`.
- Хардкодить IF по `entity_type` других доменов в platform db layer.
- Вызывать Core API синхронно внутри effect без outbox (для production).
- Класть instance-статусы (`PENDING`/`COMPLETED` worker) в `fsm_states` как entity states.

### 4.8. Подключение домена (чеклист)

1. Создать `domains/<name>/` с Python-модулями.
2. Написать SQL: FSM seed + domain schema.
3. Накатить SQL в нужные БД (platform и/или domain).
4. Добавить `<name>` в `FSM_DOMAINS`.
5. Настроить connection string domain DB (если отдельная БД).
6. Зарегистрировать guards/effects/processes.
7. Прогнать smoke: enqueue instance → worker → проверка logs + domain rows.
8. Документировать entity_type, processes, events для API/каналов.

---

## 5. Связь platform ↔ domain

```text
server_fsm_instance:
  service=courier
  process_name=order_creation
  entity_type=order_request    ← opaque для platform
  entity_id=348                ← opaque id в domain DB

entity_fsm_state (platform):
  (courier, order_request, 348) → request_fulfilled

order_requests (courier DB):
  id=348, order_id=1569, …     ← domain data; FSM-state дублировать не обязательно
```

Platform хранит **какой процесс** и **какой FSM-state**.  
Домен хранит **бизнес-данные** и выполняет **effects**.

---

## 6. Эволюция от текущего монолита

| Сейчас | Цель |
|--------|------|
| Одна БД testdb | platform DB + domain DB(s) |
| state на `orders.status` | `entity_fsm_state` на platform |
| `fsm_perform_transition` UPDATE domain tables | только platform state |
| IF entity_type в db_layer | registry / domain DB routing |
| `fsm_engine.PROCESS_DEFS` | declarative transitions + registry |
| migrations в общем каталоге | SQL seed per domain в `domains/<name>/sql/` |

Допустима поэтапная миграция: сначала картриджи при одной platform DB (режим A), затем вынос domain DB и `entity_fsm_state`.

---

## 7. Пример: courier vs taxi

| | Courier | Taxi |
|---|---------|------|
| Staging | `order_request` | опционально / сразу `taxi_order` |
| Creation process | `order_creation` | `submit_ride` |
| entity_type | `order_request` | `taxi_order` |
| event | `order_create` | `ride_submit` |
| Первый state | `request_received` | `draft` |
| Domain DB | orders, locker_cells, … | taxi_orders, drivers, … |

Один `fsm_core`, разные картриджи.

---

## 8. Критерии готовности platform (Definition of Done)

- [ ] Worker обрабатывает instance через `fsm_core.run_instance` без domain-specific кода в core.
- [ ] Guard routing по priority работает и логирует reason при отказе.
- [ ] ProcessDef регистрируется через bootstrap; `FSM_DOMAINS` управляет набором картриджей.
- [ ] FSM-state не зависит от UPDATE domain tables в SQL Core (целевой вариант A).
- [ ] Документирован контракт domain cartridge (этот файл + RFC).
- [ ] Smoke-тест: минимум один домен (courier) end-to-end.

## 9. Критерии готовности домена (Definition of Done)

- [ ] `domains/<name>/processes.py` с `register_all()`.
- [ ] SQL seed: states, events, transitions с уникальными priority на ветках.
- [ ] Все guard_name/effect_name из SQL зарегистрированы в Python.
- [ ] context_builder покрывает все processes домена.
- [ ] Domain schema отделена от platform schema.
- [ ] README или manifest: entity_types, processes, env vars.
- [ ] Smoke: API/enqueue → worker COMPLETED → корректные строки в domain DB + platform logs.

---

## 10. Глоссарий

| Термин | Значение |
|--------|----------|
| Platform | FSM Platform: worker, fsm_core, platform DB, bootstrap |
| Domain / картридж | courier, taxi, … — SQL + Python пакет |
| ProcessDef | описание job: service, process_name, entity_type, event_name |
| Instance | строка `server_fsm_instances` — одна задача worker |
| entity_type + entity_id | opaque указатель домена для platform |
| SQL seed | SQL-файлы домена для наката schema/data при деплое |
| Guard routing | выбор transition по priority и guards |
| Channel | Telegram/WhatsApp/Web — адаптер ввода-вывода, не часть домена |

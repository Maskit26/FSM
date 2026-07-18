# FSM Platform: инструкция по разработке

Документ — **единая инструкция** по разработке автономной FSM Platform и подключению доменов-картриджей (courier, taxi, cargo и др.): принципы, модули, контракты, БД, валидация, runtime.

Доп. материалы (не часть этой инструкции): [fsm-platform-rfc-implementation.md](fsm-platform-rfc-implementation.md).

Как читать:

| Раздел | Содержание |
|--------|------------|
| §1–3 | видение, принципы, кто пишет в какую БД |
| §4 | platform: компоненты, worker, HTTP, bootstrap |
| §5 | картридж домена: структура, guards/effects/queries/db_layer |
| §6 | контракт platform ↔ domain, Domain Registry, RAM-реестры |
| §7 | Accept нового домена, Domain Validator |
| §8 | модули `fsm_core`: файлы, алгоритмы, таблицы |
| §9 | публичный API клиентов, channel adapters |
| §10 | исходящие ответы клиенту: poll, SSE, outbox, webhooks |
| §11–12 | запрещённые решения, примеры доменов |
| §13–14 | критерии готовности |
| §15 | глоссарий |

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
4. **Guard routing** — `priority ASC, id ASC`; NULL-guard = unconditional; иначе первый `ok=true` (§4.4).
5. **Разделение ответственности за UPDATE** — `TransitionExecutor` / `fsm_core` db_layer меняет только FSM-state и log в platform DB; бизнес-таблицы домена меняются в **effects** домена.
6. **Картридж** — добавление домена = SQL seed + Python register + конфиг, без правки ядра platform.
7. **Side effects наружу** — HTTP/push через `platform.notify` → `platform_outbox`; события — `platform.emit_event`; таймеры — `platform.schedule_timer` (после commit — outbox_worker).
8. **Session только platform** — session к любой БД открывает worker (FSM) или Request Runtime (REST); домен session не создаёт.
9. **Два db_layer** — `fsm_core/db_layer.py` только platform DB; `domains/<type>/db_layer.py` только domain DB.
10. **Домен только после валидации** — status `active` после Domain Validator; иначе REST/FSM для `service_id` не обслуживаются.
11. **service_id ≠ cartridge_type** — тип картриджа может повторяться у разных заказчиков; runtime-ключ всегда уникальный `service_id`.
12. **Один внешний контракт** — клиенты только `/v1/{service_id}/…` (§9–10). Pipeline §4.10 — внутренний, не публичный API.
13. **`ProcessDef.service_id`** — одно имя поля/колонки: `service_id` (не `service`).
14. **Outbox producer** — запись в `platform_outbox` только через `platform.notify` (и platform fan-out webhooks); не из сырого SQL домена и не из трёх независимых точек.
15. **Accept без remote code exec в prod** — пакеты только из доверенного registry; произвольный zip→import в prod запрещён (§7.5).

---

## 3. Разделение записи в БД

Pipeline делит запись в БД на два слоя:

| Шаг | Исполнитель | Обновляемые данные |
|-----|-------------|-------------------|
| SQL transition | Platform (`TransitionExecutor` → db_layer) | FSM-state + `fsm_transition_logs` в platform DB |
| Effect | Домен (`domains/<name>/effects.py`) | Бизнес-таблицы domain DB; side effects — `platform.notify` / `emit_event` / `schedule_timer` (§4.13) |

**Требования:**

- `TransitionExecutor` / `fsm_core` db_layer не выполняют `UPDATE`/`INSERT` в business-таблицы domain DB.
- Запись в domain DB выполняется только в effect, зарегистрированном доменом.
- Platform выполняет FSM transition и вызывает effect; effect несёт ответственность за бизнес-данные домена.

```text
Worker
  → guard (read-only, чтение domain DB)
  → TransitionExecutor  → platform DB: entity_fsm_state, fsm_transition_logs
  → effect              → domain DB + опц. platform.notify / emit_event / schedule_timer
  → commit (§4.7)
```

**Запрещено:** изменение business-таблиц домена из `fsm_core` / TransitionExecutor.

**Обязательно:** effect домена выполняет все необходимые INSERT/UPDATE в domain DB для данного перехода.

---

## 4. Platform: компоненты и работа

### 4.1. Назначение

Platform обеспечивает:

- HTTP-вход (Gateway, Public API routes, OperationRegistry, Dispatcher, Request Runtime);
- постановку и выполнение FSM-задач (`server_fsm_instances`);
- единый pipeline перехода (`fsm_core`);
- хранение **FSM-state** сущностей в platform DB (`entity_fsm_state`);
- журнал переходов, таймеры, outbox для асинхронных интеграций;
- маршрутизацию к домену по полю `service_id` (instance и HTTP);
- чтение FSM-графа (transitions) из **БД домена** по connection, привязанному к `service_id`.

Platform **не** обязана:

- знать схему business-таблиц домена в Gateway / `fsm_core`;
- содержать бизнес-правила courier/taxi в ядре;
- держать бизнес-SQL доменов в platform-коде.

### 4.2. Компоненты platform (Python)

| Компонент | Путь (целевой) | Ответственность |
|-----------|----------------|-----------------|
| Runtime engine | `fsm_core/engine.py` | `run_instance` → ProcessDef → TransitionRunner (§8.4) |
| Transition runner | `fsm_core/transition_runner.py` | context → candidates → guards → apply → effect (§8.5) |
| FSM Registry | `fsm_core/registry.py` | Process/Guard/Effect в RAM, ключ с `service_id` (§8.3) |
| Types / errors | `fsm_core/types.py`, `errors.py` | контракты, guard/effect params, коды (§8.2, §8.7) |
| FSM db_layer | `fsm_core/db_layer.py` | SQL platform DB: state, logs, timers (§8.8) |
| State store | `fsm_core/state_store.py` | API `entity_fsm_state` через db_layer (§8.9) |
| Transition repository | `fsm_core/transition_repository.py` | SELECT candidates + params из domain DB (§8.10) |
| Transition executor | `fsm_core/transition_executor.py` | apply state+log через db_layer (§8.11) |
| Timers helper | `fsm_core/timers.py` | schedule/cancel → `fsm_timers` (§8.6) |
| Worker | `fsm_worker.py` | poll, claim, session, commit/rollback, mark FAILED |
| Bootstrap | `domains/bootstrap.py` | загрузка доменов из Domain Registry / `FSM_DOMAINS` |
| HTTP Gateway | `platform/http/gateway.py` (или `main.py`) | HTTP in/out, auth, status code, JSON |
| Public API routes | `platform/http/*` | фиксированные `/v1/...` (§9); не наполняется доменом |
| Operation Registry | `platform/http/operations.py` (или аналог) | RAM: `(service_id, operation) → handler, kind` (§6.4.1) |
| Dispatcher | `platform/http/` (функция/класс) | Public API path → enqueue/invoke/… → Runtime / OperationRegistry |
| Request Runtime | `platform/http/request_runtime.py` | session(s) на HTTP-запрос, вызов handler, commit/close |

**Запрещено** в `fsm_core`:

- импорты `domains.courier`, `domains.taxi`;
- проверки вида `if <business_field> == ...` (это guards домена);
- знание имён domain-таблиц.

### 4.3. Pipeline одного шага FSM

Worker открывает `session_platform` + `session_domain`, владеет транзакциями и передаёт обе в pipeline (§4.7, §8.4).

```text
1. Worker открывает session_platform + session_domain
2. claim server_fsm_instance → PROCESSING
3. ProcessRegistry: service_id + process_name → ProcessDef
4. context_builder → domain context
5. state_store.get → entity_fsm_state
6. transition_repository.list_candidates (domain DB)
7. ORDER BY priority ASC, id ASC; unique priority; NULL-guard = unconditional
8. guards → первый ok=true (NULL считается ok)
9. TransitionExecutor.apply → entity_fsm_state + fsm_transition_logs
10. effect → domain DB; side effects — platform.notify / emit_event / schedule_timer (§4.13)
11. instance COMPLETED/FAILED; commit по §4.7
```

### 4.4. Guard routing

- Несколько transitions на один `(entity_type, from_state, event_name)` — норма.
- `priority`: меньше = раньше; **уникален** в наборе candidates.
- Единый алгоритм выбора (нет отдельного «алгоритма для NULL»):
  1. candidates: `ORDER BY priority ASC, id ASC`;
  2. для каждого candidate: `guard_name IS NULL` → selected (unconditional); иначе вызвать guard; `ok=true` → selected;
  3. иначе следующий candidate.
- **Seed / Validator:** default-переход = ровно один candidate с `guard_name IS NULL` на набор `(entity_type, from_state, event_name)` **или** ноль таких. Если default есть — у него **наибольший** `priority` (проверяется последним при ASC). Два NULL-guard на набор → fail Validator (`AMBIGUOUS_DEFAULT_GUARD`).
- Ни один candidate не выбран → `NO_GUARD_MATCHED` → instance **FAILED** (WAITING в v1 не используется; retry по этому коду не делается). В `last_error` — код + last guard reason.

### 4.5. База данных platform

**Только инфраструктура platform** — без бизнес-таблиц и без FSM-графа доменов:

| Таблица | Назначение |
|---------|------------|
| `server_fsm_instances` | очередь: `service_id`, process_name, entity_type, entity_id, status, attempts, last_error |
| `fsm_transition_logs` | аудит FSM-переходов (единственная log-таблица; не `fsm_action_logs`) |
| `fsm_timers` | отложенные события |
| `entity_fsm_state` | `(service_id, entity_type, entity_id) → current_state` |
| `domain_services` | Domain Registry + `db_secret_ref` (§6.3); boot → `engine_by_service_id` в RAM |
| `idempotency_keys` | Idempotency-Key → результат enqueue/invoke (§4.14) |
| `platform_outbox` | webhooks, channel push, external HTTP (§10) |
| `platform_events` | события для SSE/подписок (§10) |
| `webhook_subscriptions` | URL клиентов (§4.14, §10) |
| `platform_reconcile_queue` | докат platform после «domain committed / platform failed» (§4.7.1) |

FSM-граф домена — в **domain DB**.

### 4.6. Применение перехода (TransitionExecutor)

Единственный runtime-путь применения перехода — **`TransitionExecutor`** через `fsm_core/db_layer.py`:

- проверка `current_state == from_state`;
- запись `entity_fsm_state` + INSERT `fsm_transition_logs`;
- без UPDATE business-таблиц domain DB;
- отдельная stored procedure «SQL Core» как параллельный путь **не используется** (ХП допустима лишь как внутренняя реализация db_layer над platform tables).

### 4.7. Worker и транзакции (две БД)

Worker владеет `session_platform` и `session_domain` и передаёт обе в `run_instance` (§8.4).

**COMPLETED:**

```text
1. TransitionExecutor.apply
2. effect (+ опц. platform.notify / emit_event / schedule_timer)
3. Platform fan-out hook (COMPLETED): platform.emit_event + webhook fan-out через platform.notify
4. UPDATE server_fsm_instances → COMPLETED
5. COMMIT domain DB
6. COMMIT platform DB
```

**Ошибка (guard / executor / effect):**

```text
ROLLBACK domain; ROLLBACK platform
→ затем отдельная короткая tx (§ ниже) для FAILED
```

**FAILED notify** (чтобы не откатилось вместе с рабочей tx):

```text
ROLLBACK рабочей tx
BEGIN  -- только platform session
  UPDATE server_fsm_instances → FAILED + last_error
  platform.emit_event(fsm.instance.failed, …)
  Platform fan-out hook (FAILED) → platform.notify для подписчиков
COMMIT
```

Fan-out / notify при FAILED **не** выполняются в откатываемой рабочей tx.  
Внешний HTTP — только `outbox_worker` после commit outbox.

2PC / XA **не используются**. Порядок COMMIT domain → COMMIT platform сохраняется; разрыв закрывается §4.7.1.

### 4.7.1. Dual-commit recovery (domain ok / platform fail)

**Проблема:** после успешного `COMMIT domain` падает `COMMIT platform` → откатываются `entity_fsm_state`, log, instance, outbox; бизнес-данные домена уже изменены. Повторный полный `run_instance` **запрещён** (effect нельзя выполнять дважды).

**Норматив v1:** идемпотентный докат **только platform-части** через очередь reconcile. Компенсация domain (откат заказа и т.п.) — вне ядра, вручную/доменом.

#### Таблица `platform_reconcile_queue` (platform DB)

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | |
| `instance_id` | |
| `entity_type`, `entity_id` | |
| `from_state`, `to_state` | |
| `event_name` | |
| `transition_id` | id перехода графа (для UNIQUE log) |
| `payload_json` | опц. снимок для fan-out / диагностики |
| `status` | `PENDING` \| `PROCESSING` \| `DONE` \| `DEAD` |
| `attempts` | |
| `last_error` | |
| `created_at`, `updated_at`, `done_at` | |

UNIQUE рекомендуется: `(instance_id, transition_id)` — повторная постановка той же дыры не плодит строки.

#### Когда писать в очередь

После `COMMIT domain` = ok и `COMMIT platform` = **fail** (или process crash в этом окне):

```text
НЕ маркировать instance бизнес-FAILED из-за platform commit
НЕ вызывать effect повторно
Отдельная короткая platform tx (новый connection при необходимости):
  INSERT platform_reconcile_queue (…, status=PENDING)
  -- или UPSERT по (instance_id, transition_id)
Алерт / метрика: DUAL_COMMIT_PLATFORM_FAILED
```

Worker для постановки в очередь использует **уже известный** результат успешного шага (to_state, transition_id, …) из памяти/`FsmResult.payload` до попытки platform commit.

#### Reconcile worker (platform)

Отдельный цикл (или режим `fsm_worker`):

```text
LOOP:
  1. claim PENDING → PROCESSING (SKIP LOCKED)
  2. Идемпотентный докат platform ONLY:
     a. UPSERT entity_fsm_state → to_state
        (если current_state уже to_state → ok)
     b. INSERT fsm_transition_logs
        UNIQUE (instance_id, transition_id) → при конфликте skip
     c. UPDATE server_fsm_instances → COMPLETED
        (если уже COMPLETED → ok)
     d. platform.emit_event + fan-out notify
        с idempotency_key = reconcile:{instance_id}:{transition_id}
  3. status=DONE
  При ошибке: attempts++, backoff; attempts > max → DEAD + pager
```

**Запрещено в reconcile:** вызов domain effect / guards / `run_instance` целиком; ROLLBACK domain; 2PC.

#### Идемпотентность TransitionExecutor / log

Для безопасного доката:

- `entity_fsm_state`: UPSERT; повтор с тем же `to_state` — успех;
- `fsm_transition_logs`: уникальность `(instance_id, transition_id)` (или эквивалент);
- outbox/events: `idempotency_key` на fan-out COMPLETED из reconcile.

#### Ops

| Ситуация | Действие |
|----------|----------|
| `PENDING`/`PROCESSING` дольше SLA | pager + ручной retry того же reconcile |
| `DEAD` | разбор; ручной `UPDATE … status=PENDING` или правка state; **не** повтор effect |
| Сомнительный drift без строки queue | алерт; сверка domain vs `entity_fsm_state` (ops), постановка queue вручную при известном to_state |

Тот же паттерн допустим для Request Runtime (§4.10.1), если после `COMMIT domain` падает `COMMIT platform` на bootstrap/enqueue: очередь с типом операции `bootstrap_enqueue` (или отдельный `intent_kind`) и докат только platform-строк (`entity_fsm_state`, `server_fsm_instances`, idempotency).

### 4.8. Bootstrap и реестр доменов

- Источник списка доменов: `FSM_DOMAINS` и/или записи **Domain Registry** в platform DB (после Accept в админ-UI).
- При старте API/worker для каждого **active** `service_id` из Domain Registry:
  1. загрузить пакет по `cartridge_type` / package ref;
  2. прочитать `manifest.yaml` (`cartridge_type`, version, entry);
  3. открыть connection к domain DB этого `service_id`;
  4. вызвать `register_all(service_id)` → наполнить **RAM** FSM Registry + OperationRegistry;
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

### 4.10. Внутренний HTTP-pipeline (не Public API)

Внешний контракт клиентов — только **§9–10** (`/v1/{service_id}/…`).  
§4.10 — как Public API внутри процесса вызывает domain handlers: не второй набор публичных URL.

| | Command | Query |
|---|---------|-------|
| Смысл | lifecycle / staging | чтение |
| Дальше | handler → enqueue → worker | handler → domain db_layer |

Цепочка: **Public API → Request Runtime → domain handler → domain db_layer**.

| Роль | Путь | Ответственность |
|------|------|-----------------|
| Public API handlers | `platform/http/*` (§9.13) | `/v1/...`, auth, JSON |
| Operation Registry | RAM | `(service_id, operation)` → handler, kind |
| Request Runtime | `request_runtime.py` | sessions, commit/rollback (§4.10.1) |
| Domain handler | `queries.py` / `commands.py` | use-case (без bootstrap state / без commit) |
| Domain db_layer | `db_layer.py` | SQL domain DB |

`domain_session` = session к domain DB `engine_by_service_id[service_id]`, открытая Runtime/worker.

Публичные URL фиксированы platform (§9). Домен **не** регистрирует `(method, path)` — только `OperationRegistry` + FSM registries.

```text
register_all(service_id):
  ProcessDef, guards, effects
  OperationRegistry.register(service_id, operation, kind, handler)
```

**Query:** invoke → handler → DTO → опц. merge `entity_fsm_state` → 200.

**Command create (lifecycle):** handler INSERT staging из JSON `params` → Runtime bootstrap `entity_fsm_state` (§4.12) → **обязательный** enqueue → COMMIT (§4.10.1) → 200/202 + `instance_id`.

**Bare enqueue:** только если `entity_fsm_state` уже есть (§4.12); иначе 400.

#### 4.10.1. Request Runtime: commit / rollback

Успех (как §4.7 COMPLETED, без worker fan-out instance):

```text
COMMIT domain DB → COMMIT platform DB
```

Ошибка после частичных записей (staging / bootstrap / enqueue):

```text
ROLLBACK domain; ROLLBACK platform
```

Короткая FAILED-tx worker (§4.7) **не** применяется к HTTP, пока instance не создан. Если enqueue уже INSERT'нул instance и затем fail до commit — rollback снимает и instance. HTTP-код — 4xx/5xx envelope, не статус FSM instance.

### 4.11. Каналы

Слой не в домене. Контракт — **§9–10**. Adapter → только Public API `/v1/{service_id}/…`.

### 4.12. Bootstrap `entity_fsm_state`

Без строки state runner → `ENTITY_STATE_NOT_FOUND`.

| Сценарий | Кто INSERT initial | Правило |
|----------|-------------------|---------|
| Invoke-create (command создаёт сущность) | **Request Runtime** (не command handler) после успешного staging INSERT | см. алгоритм ниже |
| Bare enqueue | state уже должен быть | нет строки → **400** `ENTITY_STATE_NOT_FOUND`, instance не создаётся |
| Создание entity внутри первого effect | вне базового v1 | не использовать без отдельного расширения |

**Владелец INSERT:** только Request Runtime (platform session). Command handler возвращает `{entity_type, entity_id}` (и опц. `initial_state` override); сам в `entity_fsm_state` не пишет.

**Алгоритм invoke-create + enqueue (норматив — всегда lifecycle):**

Параметры создания сущности приходят в JSON тела `POST .../invoke` как `params` (схема — контракт операции домена). Handler пишет их в staging/бизнес-таблицы domain DB; в `server_fsm_instances.payload_json` Runtime кладёт нужный срез для context (по политике домена / ProcessDef).

```text
1. handler (commands.py) ← params (JSON) → INSERT staging в domain DB → entity_id
2. Runtime определяет initial_state:
   a. если handler вернул initial_state — использовать его
   b. иначе SELECT name FROM fsm_states (domain DB)
        WHERE entity_type=:et AND is_initial=true
   c. 0 строк → 400 NO_INITIAL_STATE
      >1 строк → 400 AMBIGUOUS_INITIAL_STATE (Validator тоже fail при Accept)
3. Runtime: INSERT entity_fsm_state(service_id, entity_type, entity_id, current_state=initial)
4. Runtime: INSERT server_fsm_instances(PENDING) — **обязательно** для invoke-create
5. COMMIT domain → COMMIT platform (§4.10.1)
6. Ответ 200/202: entity_id + instance_id (+ status_url)
```

Staging-only create без FSM — отдельная операция `kind=command` **без** ProcessDef/enqueue; не смешивать с invoke-create lifecycle.

**Validator (§7.4):** для каждого `entity_type` из ProcessDef / графа — ровно один `fsm_states.is_initial=true` (если домен использует invoke-create для этого типа).

### 4.13. Platform side-effect API

Домен не пишет произвольный SQL в platform DB. Только:

```python
platform.schedule_timer(session_platform, service_id=..., entity_type=..., entity_id=...,
                        process_name=..., fire_at=..., payload=...)
platform.notify(session_platform, service_id=..., channel=..., destination=...,
                event_type=..., payload=..., idempotency_key=...)
# notify → INSERT platform_outbox
platform.emit_event(session_platform, service_id=..., event_type=...,
                    instance_id=..., entity_type=..., entity_id=..., payload=...)
# emit_event → INSERT platform_events (единственный writer событий)
```

Fan-out webhooks — platform hook (§10.6): `emit_event` + `notify` для подписчиков.  
Сырой INSERT в `platform_events` / `platform_outbox` вне этих API — **запрещён**.  
HTTP наружу — `outbox_worker` после commit (§10).

### 4.14. Нормативные схемы platform-таблиц (минимум v1)

#### `server_fsm_instances`

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | экземпляр домена |
| `process_name` | ключ ProcessDef |
| `entity_type`, `entity_id` | opaque указатель |
| `status` | `PENDING` \| `PROCESSING` \| `COMPLETED` \| `FAILED` |
| `attempts` | int |
| `last_error` | код/текст |
| `payload_json` | опц. |
| `requested_by_user_id` | опц. audit |
| `created_at`, `updated_at`, `started_at`, `finished_at` | |

#### `fsm_transition_logs`

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | |
| `entity_type`, `entity_id` | |
| `from_state`, `to_state` | |
| `event_name` | |
| `transition_id` | id строки графа (domain) |
| `instance_id` | опц. |
| `user_id` | опц. |
| `created_at` | |

Единственная log-таблица переходов (не `fsm_action_logs`).  
Для dual-commit recovery: UNIQUE `(instance_id, transition_id)` (§4.7.1).

#### `platform_reconcile_queue`

Схема и алгоритм — §4.7.1.

#### `idempotency_keys`

| Поле | Смысл |
|------|--------|
| `service_id` | |
| `key` | значение заголовка `Idempotency-Key` |
| `scope` | `enqueue` \| `invoke` |
| `instance_id` | для enqueue (если применимо) |
| `response_json` | тело ответа для повтора |
| `created_at` / `expires_at` | TTL |

UNIQUE(`service_id`, `scope`, `key`).

#### `webhook_subscriptions`

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | |
| `url` | callback URL |
| `secret` | HMAC (не в открытых логах) |
| `event_types` | JSON array или `*` |
| `active` | bool |
| `created_at` | |

#### Engines map (RAM, не отдельная «магия»)

Отдельной таблицы `engines` в v1 нет. Источник: `domain_services.db_secret_ref` (+ опц. `pool_options_json`).  
При boot: `engine_by_service_id[service_id] = create_engine(secret)`. Connection к domain DB — только через этот map.

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
  processes.py           # register_all: ProcessDef, OperationRegistry, guards/effects
  context.py
  guards.py
  effects.py
  queries.py             # Query handlers; без SQL
  commands.py            # Sync Command handlers; без SQL
  db_layer.py            # SQL domain DB; session от platform
```

Публичные HTTP-пути объявляет platform (§9). Домен регистрирует **operations** (и FSM) при bootstrap — не `(method, path)`. Целостность пакета и готовность domain DB проверяет **Domain Validator** (§7) до статуса `active`.

**Процедура подключения:**

1. Накатить SQL/ХП в domain DB (на стороне заказчика в v1).
2. Установить Python-пакет + URL DB (ops или Accept в админ-UI).
3. Domain Validator → `active` → bootstrap `register_all()`.

Platform DB не содержит states/events/transitions домена — только instances, logs, `entity_fsm_state`, Domain Registry.

### 5.2. Обязательные Python-модули

| Файл | Требование |
|------|------------|
| `processes.py` | `register_all()`: ProcessDef, OperationRegistry, guards, effects (без HTTP routes) |
| `context.py` | сбор данных для guards/effects по instance |
| `guards.py` | `(session, db, context, instance, params) → GuardResult` |
| `effects.py` | `→ EffectResult`; запись через domain db_layer; notify/timers — `platform.*` (§4.13) |
| `queries.py` | Query handlers (`kind=query`); без SQL |
| `commands.py` | Sync Command handlers (`kind=command`); без SQL; async lifecycle — только через enqueue |
| `db_layer.py` | SQL domain DB; session только аргумент |

**ProcessDef** минимум:

```python
ProcessDef(
    service_id="<service_id>",
    process_name="<job>",
    entity_type="<entity>",
    event_name="<fsm_event>",
    context_builder=build_..._context,
)
```

- Поле только **`service_id`** (алиас `service` — не норматив; при миграции кода — rename).
- `process_name` — job для enqueue/worker.
- `event_name` — событие графа.

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
- На развилках — отдельные guards или один guard с разными `guard_params`.
- Сигнатура: `(session, db, context, instance, guard_params) → GuardResult`.
- `guard_params` — JSON из `fsm_transitions`; смысл ключей задаёт домен (§8.2.5).

### 5.5. Effects

- Выполняются **после** успешного SQL transition в platform DB.
- Здесь обновляются business-таблицы domain DB через domain `db_layer`; наружу — `platform.notify` / `emit_event` / `schedule_timer` (§4.13). Instance completed/failed events — обычно platform fan-out (§10.6), не обязанность каждого effect.
- Сигнатура: `(session, db, context, instance, effect_params) → EffectResult`.
- `effect_params` — JSON из `fsm_transitions`; смысл ключей задаёт домен (§8.2.5).
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

- Менять код `fsm_core` / Gateway.
- Писать business через TransitionExecutor / fsm_core db_layer.
- Открывать session сам.
- Произвольный SQL в platform DB — только `platform.notify` / `platform.emit_event` / `platform.schedule_timer` (§4.13).
- Бизнес-SQL вне domain `db_layer.py`.
- Синхронный внешний HTTP из effect.
- Статусы instance в `fsm_states` как entity states.

### 5.9. Подключение домена (чеклист разработчика картриджа)

1. Создать `domains/<name>/` по структуре §5.1, включая `manifest.yaml`.
2. Написать SQL seed: `sql/fsm/` + `sql/domain/` (+ ХП домена при необходимости).
3. Подготовить domain DB: накатить схему/граф/ХП **до** Accept в platform (v1: накат на стороне заказчика/devops).
4. Зарегистрировать в `register_all()`: ProcessDef, guards, effects, OperationRegistry.
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

- Во всех runtime-ключах platform используется **`service_id`**: OperationRegistry, FSM Registry, `server_fsm_instances.service_id`, `entity_fsm_state`, connection к domain DB.
- **`cartridge_type` не уникален**: два заказчика могут подключить тип `cargo`.
- При Accept platform **генерирует** `service_id` и сохраняет в Domain Registry вместе с `cartridge_type`, package ref, DB secret.
- URL/API: `/v1/{service_id}/…` (§9); tenant → `service_id` резолвится auth-слоем при необходимости.
- Один и тот же код картриджа (`cartridge_type=cargo`) может обслуживать много `service_id` с разными domain DB.

### 6.2. Модель взаимодействия и где живут реестры

Общение **in-process**, без отдельного сетевого RPC «platform → domain service».

- Домен — Python-пакет в процессе API/worker **на сервере** (не в браузере).
- **RAM** = память процесса API/worker на сервере platform. Браузер к реестрам не обращается.
- Platform вызывает зарегистрированные функции домена и передаёт session.
- Домен возвращает обычные Python-результаты (DTO, `GuardResult`, `EffectResult`) или бросает исключение.
- Домен не открывает HTTP-порт и не пишет в platform DB сырым SQL; запись только через §4.13 (`notify` / `emit_event` / `schedule_timer`).

**OperationRegistry и FSM Registry — не исходные файлы, которые дописываются годами.**  
Это **runtime-структуры в RAM** процесса API/worker. Код `registry.py` — тонкая обёртка platform; размер файла не растёт от числа клиентов.

```text
Boot (один раз при старте процесса API/worker на сервере):
  Domain Registry (platform DB) → список active service_id
  для каждого service_id:
      load package (по cartridge_type / package ref)
      open engine[service_id] → domain DB
      register_all(service_id) → записи в RAM сервера:
          OperationRegistry[(service_id, operation)] = {kind, handler}
          FSM Registry[(service_id, process_name)] = ProcessDef
          Guard/Effect Registry[service_id, name] = callable

Запрос:
  Public API / invoke → OperationRegistry.get(service_id, operation)
  Worker → ProcessRegistry.get(service_id, process_name)
  → вызвать callable, передать domain_session для этого service_id
  → если нет: 404 / UNKNOWN_PROCESS
```

После рестарта процесса RAM строится заново из Domain Registry + `register_all(service_id)`.

```text
Platform                              Domain cartridge
────────                              ────────────────
Domain Registry (DB) / boot
  → load package (cartridge_type)
  → open domain DB engine[service_id]
  → register_all(service_id) ───────→  заполняет Operation/FSM Registry в RAM

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
| `pool_options_json` | опц. параметры пула для `engine_by_service_id` |
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
# Публичные path (/v1/.../invoke, enqueue, …) — код platform, не register_route домена.

_operations: dict[tuple[str, str], object] = {}
# key = (service_id, operation) → {kind, handler}

_processes: dict[tuple[str, str], ProcessDef] = {}
# key = (service_id, process_name) → ProcessDef

_guards: dict[tuple[str, str], object] = {}   # (service_id, guard_name) → callable
_effects: dict[tuple[str, str], object] = {}  # (service_id, effect_name) → callable

def register_operation(service_id, operation, kind, handler) -> None:
    assert kind in ("query", "command")
    _operations[(service_id, operation)] = {"kind": kind, "handler": handler}

def register_process(process_def: ProcessDef) -> None:
    key = (process_def.service_id, process_def.process_name)
    _processes[key] = process_def
```

**Route Registry (platform-internal):** фиксированные handlers Public API §9 (`enqueue`, `invoke`, `instances`, `catalog`, `events/stream`, `webhooks`). Домен в него не пишет.

#### 6.4.1. Контракт `OperationRegistry` (норматив)

| Метод | Контракт |
|-------|----------|
| `register(service_id, operation, kind, handler)` | `kind` ∈ {`query`, `command`}; handler из `queries.py` / `commands.py` |
| `get(service_id, operation) → {kind, handler} \| None` | lookup для `POST .../invoke` |
| `list(service_id) → list[{operation, kind}]` | источник `GET .../catalog` |
| `clear` / `unregister(service_id)` | тесты / Disable |

`register_all(service_id)` **обязан** зарегистрировать: ProcessDef(+guards/effects) **и** все sync operations, которые видны в catalog/invoke.

Домен при boot (передаёт **callable**, не путь к файлу):

```python
def register_all(service_id: str) -> None:
    OperationRegistry.register(service_id, "list_entities", "query", list_entities)
    OperationRegistry.register(service_id, "create_entity", "command", create_entity)
    ProcessRegistry.register(ProcessDef(
        service_id=service_id,
        process_name="entity_creation",
        entity_type="order_request",
        event_name="order_create",
        context_builder=build_context,
    ))
    GuardRegistry.register(service_id, "can_proceed", can_proceed)
    EffectRegistry.register(service_id, "finalize", finalize)
```

```text
POST /v1/{service_id}/invoke { "operation": "list_entities" }
  → OperationRegistry → kind=query → queries.list_entities

POST /v1/{service_id}/invoke { "operation": "create_entity" }
  → OperationRegistry → kind=command → commands.create_entity

FSM: service_id + process_name=entity_creation
  → ProcessRegistry → run_instance (только worker)
```

**Итог:** RAM-реестры наполняются `register_*` во время `register_all(service_id)` при boot.

### 6.5. Что регистрирует домен

При `register_all(service_id)` домен передаёт platform только callable и метаданные:

| Регистрация | Назначение |
|-------------|------------|
| Operation (`service_id`, operation, kind, handler) | sync invoke (§9); query→`queries.py`, command→`commands.py` |
| `ProcessDef` (`service_id`, …) | async FSM job |
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
  service_id=svc_courier_acme_01       # не cartridge_type
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
| Ops / конфиг (**норматив prod v1**) | пакет из доверенного registry (git/image/`FSM_DOMAINS`), URL DB, выдача `service_id`, Validator, рестарт |
| Админ-UI | Accept = привязка Domain DB + выбор **уже доверенного** `package_ref` / `cartridge_type` → validate → **сгенерировать service_id** → persist → restart |

Накат схемы domain DB в v1 — **на стороне заказчика** до Accept. Platform проверяет готовность, не накатывает DDL по умолчанию.

**Security Accept (норматив):** в **prod** запрещён upload произвольного zip с Python и немедленный `import` (remote code execution). Пакеты — только signed/checksummed из allowlist registry. Upload zip → import допустим **только** в dev/staging при явной конфигурации + allowlist расширений + checksum + изолированный import path (§7.5).

### 7.3. Domain Validator — целостность пакета

Компонент platform (например `platform/domain_validator.py`), запускается на Accept и при каждом boot active-домена.

**Пакет:**

- архив/дерево: размер, отсутствие path traversal (`..`), allowlist расширений;
- обязателен `manifest.yaml`: `cartridge_type`, `version`, `entry` (`…:register_all`), required tables/routines;
- `cartridge_type` — тип пакета; **`service_id` уникален** (выдаёт platform, не заказчик);
- checksum пакета сохранён в Domain Registry;
- обязательные модули на месте (`processes.py`, … по контракту картриджа);
- `import` entrypoint и вызов `register_all(service_id)` без исключения;
- после регистрации: есть ≥1 ProcessDef и/или ≥1 Operation;
- `(service_id, process_name)` уникальны глобально в FSM Registry (RAM).

### 7.4. Domain Validator — готовность domain DB (SQL / ХП / граф)

По connection из Accept / env:

1. **Connectivity** — connect + auth в timeout.
2. **FSM-граф** — существуют таблицы `fsm_states`, `fsm_events`, `fsm_transitions` (или эквивалент контракта); в transitions есть строки для entity_type домена.
3. **Согласованность граф ↔ Python** — каждый непустой `guard_name` / `effect_name` из transitions зарегистрирован в Guard/Effect Registry; лишние Python-имена — warning.
4. **Default guards** — на каждый набор `(entity_type, from_state, event_name)` не более одного `guard_name IS NULL`; если есть — у него max `priority` в наборе (§4.4).
5. **Initial states** — для каждого `entity_type` из ProcessDef: ровно один `fsm_states.is_initial=true` (если домен использует invoke-create для типа).
6. **Бизнес-схема** — минимальный набор объектов из `manifest` (required tables / routines); отсутствие → fail.
7. **ХП домена** (если указаны в manifest) — routines существуют и доступны пользователю DB.
8. **Граница** — очередь FSM (`server_fsm_instances`) и `entity_fsm_state` живут в platform DB; domain DB не является их источником истины.

Platform не интерпретирует бизнес-смысл таблиц; только наличие объектов и связность с registry.

### 7.5. Поток Accept (админ-UI)

**Prod v1 (норматив):**

```text
1. Выбрать package_ref из доверенного registry (cartridge_type, version, checksum уже известны)
2. Domain DB URL → secret store (db_secret_ref)
3. Platform генерирует service_id
4. Persist Domain Registry: service_id, cartridge_type, version, checksum, secret_id, status=pending
5. Domain Validator: пакет (из registry) + domain DB + register_all(service_id) + согласованность (§7.3–7.4)
6. status=active | failed (+ отчёт в UI)
7. Restart API/worker (v1) → boot: engine_by_service_id + RAM-реестры
8. UI показывает service_id и результат валидации
```

**Dev/staging (опционально):** upload zip допускается только если `ACCEPT_ALLOW_ZIP_UPLOAD=true`, пакет проходит allowlist/checksum/path checks, entrypoint импортируется из изолированного каталога. В prod этот режим **выключен**.

Каналы и публичный API клиентов — §9.

**Запрещено:** Accept без успешного Validator; обслуживание `service_id` при `failed`; prod Accept с произвольным zip→import.

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

| Файл | Роль |
|------|------|
| `__init__.py` | публичный API пакета |
| `types.py` | dataclass и сигнатуры (в т.ч. guard_params / effect_params) |
| `registry.py` | RAM: ProcessDef, guards, effects с ключом `service_id` |
| `db_layer.py` | SQL к **platform DB** (FSM-инфраструктура); единственное место SQL platform внутри fsm_core |
| `engine.py` | вход `run_instance` |
| `transition_runner.py` | pipeline одного шага |
| `state_store.py` | API текущего FSM-state поверх `db_layer` → `entity_fsm_state` |
| `transition_repository.py` | чтение candidates из **domain DB** (`fsm_transitions`…) |
| `transition_executor.py` | apply перехода: state + log через `db_layer` (только platform) |
| `timers.py` | schedule/cancel → `fsm_timers` через `db_layer` |
| `errors.py` | коды ошибок FSM |

Две БД — два канала доступа:

| Канал | Модуль | БД |
|-------|--------|-----|
| Platform persistence | `fsm_core/db_layer.py` (+ state_store / executor / timers) | platform DB |
| Domain graph read | `transition_repository.py` | domain DB (session от worker) |
| Domain business R/W | domain `db_layer.py` в effects/handlers | domain DB |

**Зависимости снаружи пакета:**

| Компонент | Где | Роль относительно fsm_core |
|-----------|-----|----------------------------|
| `fsm_worker.py` | platform | session(s), claim instance, commit, вызывает `run_instance` |
| Domain `register_all` | domains/ | наполняет `registry.py` |
| platform/http | platform | Public API / OperationRegistry; не часть fsm_core |
| Domain Validator | platform | сверяет граф SQL с Guard/Effect Registry |

```text
fsm_worker
  → открывает session_platform + session_domain
  → fsm_core.engine.run_instance(...)
       → registry.ProcessRegistry
       → transition_runner.TransitionRunner
            → state_store → db_layer        (platform DB)
            → transition_repository         (domain DB: fsm_*)
            → registry guards               (могут читать domain DB)
            → transition_executor → db_layer (platform DB: state + log)
            → effects → domain db_layer; platform.notify / emit_event / schedule_timer
```

---

### 8.1. Общие правила для всего `fsm_core`

1. **Не импортировать** `domains.*`. Только callable из registry / ProcessDef.
2. **Не открывать** session/engine. Session(s) передаёт worker.
3. **Не коммитить** транзакцию. Commit/rollback — worker.
4. **Не знать** имён business-таблиц (`orders`, `taxi_orders`, …).
5. **Не обслуживать** HTTP. Только FSM instance.
6. Ошибки шага возвращать как `FsmResult(new_state="FAILED", last_error="<CODE>: …")`, не ронять процесс worker необработанным исключением (кроме неожиданных багов инфраструктуры).
7. Везде ключ **`service_id`** (§6.1); поле `ProcessDef.service_id`.

---

### 8.2. `types.py`

**Назначение:** единый контракт данных между worker ↔ fsm_core ↔ доменом. Без I/O и без SQL.

#### 8.2.1. `FsmResult`

Возвращается из `engine.run_instance` в worker.

| Поле | Тип | Смысл |
|------|-----|--------|
| `new_state` | `str` | статус **instance** для worker: `COMPLETED` \| `FAILED` (WAITING в v1 не используется); не путать с entity FSM-state |
| `last_error` | `str \| None` | код/текст для `server_fsm_instances.last_error` |
| `next_timer_at` | `datetime \| None` | подсказка worker/timer (опционально) |
| `attempts_increment` | `int` | на сколько увеличить `attempts` (обычно 1) |
| `payload` | `dict \| None` | диагностика: transition_id, from/to, effect payload |

Worker по `new_state` (§4.7):
- `COMPLETED` → fan-out (`emit_event` + notify) → UPDATE COMPLETED → COMMIT domain → COMMIT platform;
- `FAILED` → ROLLBACK обеих; затем short tx: UPDATE FAILED + `emit_event` + fan-out `notify`.

#### 8.2.2. `GuardResult` / `EffectResult`

| Тип | Поля | Кто возвращает |
|-----|------|----------------|
| `GuardResult` | `ok: bool`, `reason`, `payload` | guard домена |
| `EffectResult` | `ok: bool`, `error`, `payload` | effect домена |

`TransitionRunner` принимает `GuardResult` / `EffectResult`. Допускается нормализация `bool` / `(ok, reason)` к этим типам.

#### 8.2.3. `ProcessDef`

Описание job, который worker кладёт в `server_fsm_instances.process_name`.

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `service_id` | да | id экземпляра домена; ключ registry/instance |
| `process_name` | да | имя job; ключ вместе с `service_id` |
| `entity_type` | да (цель) | тип сущности FSM |
| `event_name` | да (цель) | событие графа; если пусто — fallback `process_name` (`runtime_event_name`) |
| `context_builder` | да для реальных процессов | `(session_domain, db, runtime_ctx, instance) → dict` |
| `initial_state` | нет | опц. override для bootstrap (§4.12); иначе `fsm_states.is_initial` |

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

#### 8.2.5. `guard_params` и `effect_params`

Параметры перехода хранятся в **domain DB** (граф), передаются в Python без интерпретации в `fsm_core`.

| Поле | Где в SQL | Тип | Кто читает | Кто получает |
|------|-----------|-----|------------|--------------|
| `guard_params` | `fsm_transitions.guard_params` | JSON object (dict) | `transition_repository` → `TransitionDef` | guard: последний аргумент |
| `effect_params` | `fsm_transitions.effect_params` | JSON object (dict) | то же | effect: последний аргумент |

**Правила:**

1. В SQL — JSON (или NULL → в runtime пустой dict).
2. `TransitionRunner` не интерпретирует ключи params (не знает бизнес-смысла).
3. Guard/effect домена сами читают нужные ключи.
4. Один `guard_name` может стоять на разных transitions с разными `guard_params`.
5. Пустой/NULL params допустим; runner передаёт пустой dict.
6. Невалидный JSON при чтении графа → ошибка candidates / Validator fail.

Пример:

```json
{
  "guard_name": "has_capacity",
  "guard_params": { "min_free_cells": 1 },
  "effect_name": "finalize_entity",
  "effect_params": { "notify": true }
}
```

```text
guard(session, db, context, instance, transition.guard_params)  → GuardResult
effect(session, db, context, instance, transition.effect_params) → EffectResult
```

#### 8.2.6. Сигнатуры callable

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
| `register(process_def) -> ProcessDef` | key=`(process_def.service_id, process_def.process_name)`; повторная регистрация заменяет |
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
        → ProcessRegistry.register(ProcessDef(
        service_id=service_id, …))
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
    session_platform,           # session platform DB
    session_domain,             # session domain DB (тот же service_id)
    db,                         # facade: state_store + transition_repository + domain db helpers
    runtime_ctx: dict,          # корреляция, trace_id, опции
    instance: dict,             # строка server_fsm_instances как dict
    *,
    process_registry: ProcessRegistry | None = None,
    guard_registry: GuardRegistry | None = None,
    effect_registry: EffectRegistry | None = None,
) -> FsmResult:
```

**Сессии:** worker открывает обе (§4.7) и передаёт явно.  
- platform-путь (state_store, transition_executor, timers, notify) → `session_platform`;  
- domain-путь (context, guards, effects, transition_repository) → `session_domain`.  
Допускается facade `db` с атрибутами `.platform` / `.domain`, но оба connection обязательны.

`instance` минимально содержит:

| Ключ | Смысл |
|------|--------|
| `id` | id instance (для логов) |
| `service_id` | экземпляр домена |
| `process_name` | ключ ProcessDef |
| `entity_type` | тип сущности |
| `entity_id` | id сущности |
| `requested_by_user_id` | для audit transition (опционально) |
| `payload_json` / extras | по необходимости context_builder |

#### 8.4.2. Алгоритм по шагам

```text
1. process_registry = process_registry or default_process_registry
2. service_id = instance["service_id"]; process_name = instance.get("process_name")
3. Если process_name пуст:
     return FsmResult(FAILED, last_error="MISSING_PROCESS_NAME", attempts_increment=1)
4. process_def = process_registry.get(service_id, process_name)
5. Если process_def is None:
     log error
     return FsmResult(FAILED, last_error=f"UNKNOWN_PROCESS: {service_id}/{process_name}")
6. runner = TransitionRunner(guard_registry=…, effect_registry=…,
                             state_store=…, transition_repository=…, transition_executor=…)
   (в целевой реализации зависимости передаются явно или через db-facade)
7. result = runner.run(session_platform, session_domain, db, runtime_ctx, instance, process_def)
8. Если result.new_state не из допустимого набора instance-статусов:
     result = FsmResult(FAILED, last_error=result.last_error or "INVALID_STATE_RETURNED")
9. return result
```

Допустимые `new_state` для instance в v1: `COMPLETED`, `FAILED`. `WAITING` не используется.

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
        state_store: EntityStateStore,                # §8.9
        transition_repository: TransitionRepository,  # §8.10
        transition_executor: TransitionExecutor,      # §8.11
    ): ...
```

Зависимости внедряются явно (store / repository / executor / registries / db_layer). Алгоритм `run` ниже — нормативный.

#### 8.5.2. Алгоритм `run` (нормативный)

Вход: `session_platform`, `session_domain`, `db`, `runtime_ctx`, `instance`, `process_def`.  
`service_id = instance["service_id"]`.

```text
1. CONTEXT
   Если process_def.context_builder задан:
     domain_context = context_builder(session_domain, db, runtime_ctx, instance)
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
   ORDER BY priority ASC, id ASC (из SQL).
   Если два candidate с одинаковым priority → FAILED AMBIGUOUS_TRANSITION: …/priority=N

6. SELECT (guards) — §4.4
   selected = None; last_reason = None
   Для каждого candidate в порядке ASC:
     Если guard_name is NULL/пустой → selected = candidate; break   # unconditional
     guard_fn = guard_registry.get(service_id, guard_name)
     Если нет → FAILED UNKNOWN_GUARD: {guard_name}
     result = normalize(guard_fn(session_domain, db, domain_context, instance, guard_params))
     Если result.ok → selected = candidate; break
     Иначе last_reason = result.reason; log warning; продолжить
   Если selected is None → FAILED NO_GUARD_MATCHED (+ last_reason); без retry

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
     effect_result = normalize(effect_fn(session_domain, db, domain_context, instance, effect_params))
     Если не ok → FAILED EFFECT_FAILED / effect_result.error
     # effect: domain DB через domain db_layer; notify/timers через session_platform API

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
| apply | transition_executor | platform | `entity_fsm_state`, `fsm_transition_logs` |
| effect | код домена | domain | business tables (через domain db_layer) |

#### 8.5.5. Запрещено в TransitionRunner

- IF по бизнес-полям домена;
- прямой SQL;
- commit;
- обновление `server_fsm_instances`;
- UPDATE business tables (только effect домена).

---

### 8.6. `timers.py`

**Назначение:** запись/отмена строк в `fsm_timers` через `fsm_core` db_layer. Не поллит таймеры.

Вход для домена — **`platform.schedule_timer`** (§4.13), не прямой import из effect в обход platform API.

#### 8.6.1. `schedule_timer`

```python
def schedule_timer(
    session, *,  # platform session
    service_id: str,
    entity_type: str,
    entity_id: int,
    process_name: str,
    fire_at: datetime,
    payload: dict | None = None,
    idempotency_key: str | None = None,
) -> int:
```

**Таблица platform DB `fsm_timers` (поля минимум):**

| Колонка | Смысл |
|---------|--------|
| `id` | PK |
| `service_id` | экземпляр домена |
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
  → enqueue server_fsm_instances(service_id, process_name, entity_type, entity_id)
  → пометить timer FIRED
```

`fsm_core.timers` это **не** делает.

---

### 8.7. `errors.py`

**Назначение:** константы кодов ошибок и optionally исключения для инфраструктуры (не для штатного NO_GUARD_MATCHED).

```python
class FsmErrorCodes:
    MISSING_PROCESS_NAME = "MISSING_PROCESS_NAME"
    UNKNOWN_PROCESS = "UNKNOWN_PROCESS"
    MISSING_ENTITY_TYPE = "MISSING_ENTITY_TYPE"
    # полный список из §8.5.3 и engine
```

Штатный fail шага = `FsmResult` + код в `last_error`, не обязательно exception.  
Exception — для поломки SQL connection, багов executor.

**БД:** нет.

---

### 8.8. `db_layer.py` (platform DB для fsm_core)

**Назначение:** слой доступа fsm_core к **своей** базе — platform DB. Единственный модуль внутри `fsm_core`, который содержит SQL (или вызовы ХП) к таблицам платформы.

Domain DB этот файл не трогает. Граф `fsm_transitions` читает `transition_repository` через session domain. Бизнес-таблицы домена — только domain `db_layer` в effects/handlers.

#### Таблицы platform DB

| Таблица | Операции |
|--------|----------|
| `entity_fsm_state` | SELECT / UPSERT current_state |
| `fsm_transition_logs` | INSERT audit перехода |
| `fsm_timers` | INSERT schedule, UPDATE cancel |
| `server_fsm_instances` | опционально helpers для worker (claim/update) |

Не входит: business-таблицы доменов; `fsm_states` / `fsm_events` / `fsm_transitions` домена.

#### Интерфейс (минимум)

```python
class FsmDbLayer:
    # session к platform DB передаёт worker

    def get_entity_state(self, session, service_id, entity_type, entity_id) -> str | None: ...
    def upsert_entity_state(self, session, service_id, entity_type, entity_id, new_state, *, expected_state=None) -> None: ...

    def insert_transition_log(self, session, *, service_id, entity_type, entity_id,
                              transition_id, from_state, to_state, event_name, user_id) -> None: ...

    def insert_timer(self, session, **fields) -> int: ...
    def cancel_timer(self, session, timer_id: int) -> None: ...
```

#### Кто вызывает

| Модуль | Через db_layer |
|--------|----------------|
| `state_store.py` | get/upsert entity state |
| `transition_executor.py` | upsert state + insert log |
| `timers.py` | insert/cancel timer |
| `fsm_worker` (допустимо) | claim/update `server_fsm_instances` |

`TransitionRunner` и `engine` не пишут SQL сами: только через store/executor/timers → `db_layer`.

#### Правила

1. Session открывает worker / Request Runtime; `db_layer` session не создаёт.
2. Нет IF по бизнес-entity_type ради выбора таблицы домена.
3. Нет UPDATE/INSERT в domain DB.
4. Ошибки SQL → exception / TRANSITION_APPLY_FAILED наверх.

---

### 8.9. `state_store.py`

**Назначение:** узкий API текущего FSM-state. Читает/пишет только через `fsm_core/db_layer.py` → `entity_fsm_state`.

#### 8.9.1. Интерфейс

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

#### 8.9.2. Таблица `entity_fsm_state` (platform DB)

| Колонка | Смысл |
|---------|--------|
| `service_id` | экземпляр домена |
| `entity_type` | opaque тип |
| `entity_id` | opaque id |
| `current_state` | имя состояния (как в fsm_states.name домена) |
| `updated_at` | аудит |

PK: `(service_id, entity_type, entity_id)`.

#### 8.9.3. Кто вызывает

- `get` — TransitionRunner шаг 3;
- `set` — TransitionExecutor при apply (или store вызывается из executor).

**Запрещено:** читать state из business-таблиц домена; только `entity_fsm_state` через db_layer.

---

### 8.10. `transition_repository.py`

**Назначение:** читать declarative graph из **domain DB**. Единственное место fsm_core с SELECT по `fsm_transitions`.

#### 8.10.1. Интерфейс

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

#### 8.10.2. SQL (норматив)

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

#### 8.10.3. Таблицы domain DB

`fsm_transitions`, `fsm_states`, `fsm_events` — только чтение в этом модуле.

Колонки `guard_params` / `effect_params` парсятся в `dict` и попадают в `TransitionDef` (§8.2.5).

---

### 8.11. `transition_executor.py`

**Назначение:** атомарно применить выбранный transition к platform state + записать audit log. **Запрещено** UPDATE/INSERT business tables домена.

#### 8.11.1. Интерфейс

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
        3) INSERT в fsm_transition_logs
        """
```

#### 8.11.2. Таблицы platform DB

| Таблица | Операция |
|--------|----------|
| `entity_fsm_state` | UPDATE/UPSERT `current_state = to_state` |
| `fsm_transition_logs` | INSERT audit перехода |

#### 8.11.3. Ограничения

- Только platform tables через `fsm_core/db_layer.py`.
- Денормализованный бизнес-статус в domain DB — только в **effect** домена.
- Реализация apply: SQL через db_layer или ХП только над platform tables — без знания schema домена.
- Для §4.7.1: повтор apply при `current_state == to_state` и дубликат log `(instance_id, transition_id)` — идемпотентный успех (не ошибка).

---

### 8.12. `__init__.py`

**Назначение:** стабильный публичный API:

```python
from .engine import run_instance
from .registry import (
    ProcessRegistry, GuardRegistry, EffectRegistry,
    default_process_registry, default_guard_registry, default_effect_registry,
)
from .types import FsmResult, GuardResult, EffectResult, ProcessDef, TransitionDef
from .timers import schedule_timer, cancel_timer
from .db_layer import FsmDbLayer
from .state_store import EntityStateStore
from .transition_repository import TransitionRepository
from .transition_executor import TransitionExecutor
from .errors import FsmErrorCodes
```

Логики нет. **БД:** нет.

---

### 8.13. Полный runtime-сценарий (сборка модулей)

```text
A. BOOT — Domain Registry → register_all → Validator

B. CREATE+ENQUEUE (invoke command) — всегда lifecycle (§4.12)
   params JSON → INSERT staging (domain)
   INSERT entity_fsm_state(initial) (platform)
   INSERT server_fsm_instances(PENDING)  -- обязательно
   COMMIT domain; COMMIT platform → 200/202 + instance_id

C. BARE ENQUEUE
   проверить entity_fsm_state; иначе 400
   INSERT server_fsm_instances(PENDING); COMMIT platform

D. WORKER
   claim PROCESSING; open session_platform + session_domain
   run_instance(session_platform, session_domain, …)
   COMPLETED → fan-out + UPDATE COMPLETED → COMMIT domain → COMMIT platform (§4.7)
   domain ok / platform fail → INSERT platform_reconcile_queue (§4.7.1); не повторять effect
   FAILED → ROLLBACK обеих; отдельная tx: FAILED + emit_event + fan-out notify (§4.7)
```

---

### 8.14. Сводка таблиц по модулям fsm_core

| Модуль | Platform DB | Domain DB |
|--------|-------------|-----------|
| `types.py`, `__init__.py`, `errors.py`, `registry.py` | — | — |
| `engine.py` | — (instance dict уже из worker) | — |
| `db_layer.py` | SQL: `entity_fsm_state`, logs, `fsm_timers` (+ instances helpers) | — |
| `state_store.py` | через db_layer → `entity_fsm_state` | — |
| `transition_repository.py` | — | `fsm_transitions`, `fsm_states`, `fsm_events` R (+ params) |
| `transition_executor.py` | через db_layer → state + logs | — |
| `transition_runner.py` | через store/executor/db_layer | через repository; effect → domain db_layer |
| `timers.py` | через db_layer → `fsm_timers` | — |

Вне fsm_core: `server_fsm_instances`, `domain_services` — worker/bootstrap/Accept.

---

### 8.15. Чеклист реализации fsm_core

- [ ] Guard/Effect Registry: ключ `(service_id, name)`.
- [ ] `errors.py` с кодами §8.5.3.
- [ ] `db_layer.py` — SQL только platform DB (§8.8).
- [ ] `state_store.py` + таблица `entity_fsm_state` через db_layer.
- [ ] `transition_repository.py` (SQL §8.10.2); передача guard_params/effect_params.
- [ ] `transition_executor.py` через db_layer; без UPDATE domain business tables.
- [ ] `TransitionRunner` передаёт guard_params/effect_params в callable.
- [ ] `engine.run_instance` принимает registry и зависимости явно.
- [ ] Юнит-тесты: ambiguous priority, NO_GUARD_MATCHED, UNKNOWN_EFFECT, params→guard, COMPLETED.
- [ ] Интеграционный smoke: один service_id end-to-end через worker.

---

## 9. Публичный API клиентов и channel adapters

Внешние клиенты (сайт заказчика, Telegram, WhatsApp, автотестер, Postman) **не** ходят в `fsm_core` и **не** вызывают domain db_layer напрямую. Единая точка входа — **Platform Public API**. Адаптеры каналов только переводят свой протокол в вызовы этого API.

```text
Telegram / WhatsApp / сайт / автотестер / Postman
        ↓
Channel adapter (парсит свой протокол → вызов Platform API)
        ↓
Platform Public API
        ├─ Async Command  → enqueue → worker → fsm_core
        ├─ Sync Invoke    → Request Runtime → domain handler → domain db_layer
        └─ Status / Discovery / Webhooks
```

Единственный внешний HTTP-контракт клиентов — `/v1/{service_id}/…` из этого раздела.

### 9.1. Роли слоёв

| Слой | Ответственность | Не делает |
|------|-----------------|-----------|
| **Клиент** | UX, свой протокол (Bot API, браузер, тест-скрипт) | не знает guards/effects/SQL домена |
| **Channel adapter** | parse update/HTTP → Platform API; доставка ответа пользователю | не содержит бизнес-правил домена |
| **Platform Public API** | auth, routing по `service_id`, enqueue / invoke / status / catalog | не знает business-таблиц домена |
| **Request Runtime / worker / fsm_core** | исполнение (§4.10, §8) | не парсит Telegram update |

Один и тот же Platform API используют сайт, автотест и мессенджеры. Разница только в adapter.

### 9.2. Три типа вызовов

| Тип | Endpoint (норматив) | Когда | Ответ |
|-----|---------------------|--------|--------|
| **Async Command** | `POST /v1/{service_id}/fsm/enqueue` | lifecycle, работа через worker | `202` + `instance_id` |
| **Sync Invoke** | `POST /v1/{service_id}/invoke` | Query и короткие sync Command | `200` + DTO |
| **Status** | `GET /v1/{service_id}/fsm/instances/{id}` | результат async | state instance + last_error + payload |

Дополнительно:

| Endpoint | Назначение |
|----------|------------|
| `GET /v1/{service_id}/catalog` | discovery: process_name + operation из registry |
| `GET /v1/{service_id}/events/stream` | SSE (§10.5) |
| `POST /v1/{service_id}/webhooks` | регистрация callback URL (§10) |
| `GET /v1/health` | liveness platform (без домена) |

`service_id` в path — уникальный id экземпляра домена (§6.1), не `cartridge_type`.

### 9.3. Async Command: `POST /v1/{service_id}/fsm/enqueue`

Постановка задачи в `server_fsm_instances`. Нормативный path — `POST /v1/{service_id}/fsm/enqueue` (§9.14).

#### Запрос

```http
POST /v1/{service_id}/fsm/enqueue
Authorization: Bearer <token>
Idempotency-Key: <client-unique-key>
X-Request-Id: <optional-correlation>
Content-Type: application/json
```

```json
{
  "process_name": "order_creation",
  "entity_type": "order_request",
  "entity_id": 348,
  "payload": {},
  "client_request_id": "tg-msg-99",
  "actor": {
    "actor_type": "user",
    "actor_id": "42",
    "channel": "telegram"
  },
  "mode": "async"
}
```

| Поле | Обязательность | Смысл |
|------|----------------|--------|
| `process_name` | да | ключ ProcessDef вместе с `service_id` |
| `entity_type` | да* | тип сущности FSM |
| `entity_id` | да | сущность и `entity_fsm_state` уже существуют (§4.12); иначе 400 |
| `payload` | нет | данные для context/metadata (не размытый произвольный bag без схемы) |
| `client_request_id` | нет | id со стороны клиента/канала |
| `actor` | да (цель) | кто инициировал; не доверять голому `user_id` из body без auth |
| `mode` | нет | `async` (default) \| `wait` (ждать финала в том же HTTP — для автотестов; см. алгоритм ниже) |

**Auth:** токен привязан к `service_id` (и правам). Нельзя enqueue в чужой `service_id`.

**Idempotency-Key:** lookup в `idempotency_keys` (§4.14); повтор не создаёт второй instance.

#### Ответ `202 Accepted`

```json
{
  "instance_id": 1001,
  "status": "PENDING",
  "service_id": "svc_courier_acme_01",
  "status_url": "/v1/svc_courier_acme_01/fsm/instances/1001",
  "accepted_at": "2026-07-18T12:00:00Z"
}
```

При `mode=wait` — `200` с финальным статусом instance или `504` по timeout.

#### Алгоритм gateway

```text
1. Auth → проверить доступ к service_id
2. Domain Registry: service_id status=active
3. ProcessRegistry.has(service_id, process_name) иначе 400 UNKNOWN_PROCESS
4. Idempotency lookup (idempotency_keys) → если есть, вернуть прежний результат
5. Проверить entity_fsm_state существует; иначе 400 ENTITY_STATE_NOT_FOUND
6. INSERT server_fsm_instances (PENDING); сохранить idempotency_keys
7. Если mode=async → 202 + status_url; выход
8. Если mode=wait:
     НЕ вызывать run_instance / claim в HTTP-процессе
     poll SELECT status из server_fsm_instances (backoff) до COMPLETED|FAILED|timeout
     → 200 финальный статус или 504
9. Claim + fsm_core — только fsm_worker (§8)
```

**Запрещено при `mode=wait`:** выполнять FSM в том же HTTP-процессе (риск double-claim с worker). Wait = poll-in-request.

**Не делает enqueue-handler:** вызов guards/effects, бизнес-UPDATE domain tables, `TransitionExecutor`.

### 9.4. Sync Invoke: `POST /v1/{service_id}/invoke`

Общий вход для Query и sync Command: клиент вызывает именованную `operation`, а не произвольный набор разрозненных URL.

#### Запрос

```http
POST /v1/{service_id}/invoke
Authorization: Bearer <token>
Idempotency-Key: <для command, обязателен при мутациях>
Content-Type: application/json
```

```json
{
  "operation": "list_client_orders",
  "params": { "client_id": 42, "limit": 20 },
  "actor": {
    "actor_type": "user",
    "actor_id": "42",
    "channel": "web"
  }
}
```

| Поле | Смысл |
|------|--------|
| `operation` | имя из Operation Registry домена (при `register_all`) |
| `params` | аргументы handler |
| `actor` | инициатор |

Альтернатива (тот же registry): `GET/POST /v1/{service_id}/ops/{operation}` с query/body = params.

#### Ответ `200`

```json
{
  "operation": "list_client_orders",
  "data": [ … ],
  "meta": { "fsm_states": { … } }
}
```

`meta.fsm_states` — опционально: platform мержит `entity_fsm_state` по ключам из DTO (§4.10). Домен platform DB не читает.

#### Алгоритм

```text
1. Auth → service_id
2. OperationRegistry.get(service_id, operation) → handler, kind=query|command; иначе 404
3. Request Runtime: открыть session_platform + session_domain
4. kind=query → handler (queries.py) → domain db_layer read → DTO
5. kind=command → handler (commands.py) ← params JSON → staging/бизнес в domain;
     invoke-create: handler → entity_type/entity_id → Runtime bootstrap state + **обязательный** enqueue (§4.12);
     (не TransitionRunner)
6. (опц.) enrichment FSM-state
7. успех → COMMIT domain → COMMIT platform (§4.10.1); fail → ROLLBACK обеих
8. JSON 200; при мутациях — idempotency_keys
```

**Запрещено:** sync invoke как скрытый вызов TransitionRunner / claim instance в обход worker; INSERT `entity_fsm_state` из command handler.

### 9.5. Status: `GET /v1/{service_id}/fsm/instances/{instance_id}`

```json
{
  "instance_id": 1001,
  "service_id": "svc_courier_acme_01",
  "process_name": "order_creation",
  "entity_type": "order_request",
  "entity_id": 348,
  "status": "COMPLETED",
  "last_error": null,
  "payload": { "transition_id": 167, "to_state": "request_fulfilled" },
  "created_at": "…",
  "updated_at": "…"
}
```

`status` — статус **instance** (`PENDING`/`PROCESSING`/`COMPLETED`/`FAILED`/…), не обязательно имя entity FSM-state. Entity state — через invoke или enrichment.

Таблица: `server_fsm_instances` (platform DB).

### 9.6. Discovery: `GET /v1/{service_id}/catalog`

Отдаёт то, что зарегистрировал домен при boot (без утечки SQL):

```json
{
  "service_id": "svc_courier_acme_01",
  "cartridge_type": "courier",
  "processes": [
    { "process_name": "order_creation", "entity_type": "order_request", "event_name": "order_create" }
  ],
  "operations": [
    { "operation": "list_client_orders", "kind": "query" },
    { "operation": "create_order_request", "kind": "command" }
  ]
}
```

Источник: ProcessRegistry + OperationRegistry в RAM (§6.4.1). После Accept UI/клиент опирается на catalog, а не на хардкод имён.

### 9.7. Auth и актор

| Механизм | Назначение |
|----------|------------|
| API key / JWT | доступ к конкретному `service_id` (+ scopes: enqueue, invoke, admin) |
| `actor` в теле/claims | user/bot/system; канал `web` / `telegram` / `autotest` / `postman` |
| Запрет | принимать `user_id` из body как единственный auth |

Автотестер и сайт получают разные ключи; ключ sandbox не пишет в production domain DB (политика деплоя).

### 9.8. Ошибки (единый envelope)

```json
{
  "code": "UNKNOWN_PROCESS",
  "message": "Process not registered for this service_id",
  "details": { "service_id": "…", "process_name": "…" },
  "request_id": "…"
}
```

HTTP: `400` контракт/валидация, `401`/`403` auth, `404` неизвестный instance/operation, `409` конфликт idempotency/state, `504` wait timeout. Коды FSM instance (`NO_GUARD_MATCHED` и т.д.) — в status/`last_error` после async, не обязательно как HTTP 500 на enqueue (enqueue уже принял задачу).

### 9.9. Webhooks (outbound) — кратко

Клиент регистрирует URL (`POST /v1/{service_id}/webhooks`). События после commit доставляются через **platform_outbox** (не из SQL transition).

Полная модель исходящих каналов (poll, SSE, outbox, channel push, external) — **§10**.

### 9.10. Channel adapters

Каталог (вне домена):

```text
channels/
  telegram/
  whatsapp/
  web/          # опционально тонкий BFF
```

**Обязанности adapter:**

1. Принять update/HTTP канала.
2. Аутентифицировать канал (bot token / verify webhook).
3. Смапить пользователя канала → `actor` (+ user mapping при необходимости).
4. Выбрать `service_id` + `operation` или `process_name` (конфиг канала, не хардкод в fsm_core).
5. Вызвать Platform Public API (`invoke` / `enqueue`).
6. Отформатировать ответ/ошибку обратно в канал (сообщение, кнопки).

**Запрещено в adapter:** SQL домена, вызов guards/effects, прямой import модулей домена (только HTTP к Platform API или общий application client).

Пример Telegram:

```text
message "/orders"
  → adapter
  → POST /v1/{service_id}/invoke { operation: list_client_orders, actor: … }
  → reply text с списком
```

### 9.11. Как подключаются типы клиентов

| Клиент | Типичный путь |
|--------|----------------|
| Сайт заказчика | напрямую Public API: invoke + enqueue + status |
| Postman / OpenAPI | то же; catalog для списка operation/process |
| Автотестер | enqueue + Idempotency-Key + poll status или `mode=wait` |
| Telegram / WhatsApp | channel adapter → Public API |
| Голос / другие | свой adapter → тот же Public API |

### 9.12. Связь с внутренним HTTP-слоем (§4.10)

| Public API | Внутри platform |
|------------|-----------------|
| `/v1/.../fsm/enqueue` | запись `server_fsm_instances` (+ idempotency store) |
| `/v1/.../invoke` | Dispatcher + Operation Registry + Request Runtime |
| `/v1/.../catalog` | чтение ProcessRegistry + Operation Registry (RAM) |
| `/v1/.../fsm/instances/{id}` | SELECT `server_fsm_instances` |

OperationRegistry — единственный реестр sync handler'ов (§6.4.1). Публичные path фиксированы platform; домен path не регистрирует.

### 9.13. Модули platform (входящий контур)

Реализация Public API §9. Исходящая доставка (SSE hub, outbox_worker) — §10.

| Модуль (целевой путь) | Назначение |
|-----------------------|------------|
| `platform/http/gateway.py` | HTTP `/v1/...`: routing, status code, JSON in/out |
| `platform/http/dispatcher.py` | lookup Operation Registry / ProcessRegistry |
| `platform/http/request_runtime.py` | session(s) на invoke; вызов domain handler; commit/close |
| `platform/http/enqueue.py` | `POST .../fsm/enqueue`: валидация process, INSERT instance |
| `platform/http/instances.py` | `GET .../fsm/instances/{id}` |
| `platform/http/catalog.py` | `GET .../catalog` из RAM-реестров |
| `platform/http/invoke.py` | `POST .../invoke` → dispatcher → Request Runtime |
| `platform/auth/` | API key / JWT → `service_id`, scopes, `actor` |
| `platform/idempotency/` | таблица `idempotency_keys` (§4.14) |
| OperationRegistry | RAM §6.4.1; наполняет `register_all` (домен) |
| Public API routes | фиксированные path §9; код platform |
| ProcessRegistry (`fsm_core`) | проверка `process_name` при enqueue |
| Domain Registry | `service_id` active, connection domain DB |

**Запрещено во входящем контуре:** SQL business-таблиц домена в gateway; вызов guards/effects в обход enqueue/invoke pipeline; открытие session в domain handler.

### 9.14. Нормативный набор Public API (сводка)

| Метод | Path | Назначение |
|-------|------|------------|
| POST | `/v1/{service_id}/fsm/enqueue` | async Command |
| GET | `/v1/{service_id}/fsm/instances/{id}` | status instance |
| POST | `/v1/{service_id}/invoke` | sync Query/Command |
| GET | `/v1/{service_id}/catalog` | processes + operations |
| GET | `/v1/{service_id}/events/stream` | SSE (§10.5) |
| POST | `/v1/{service_id}/webhooks` | регистрация webhook |
| GET | `/v1/health` | health |

Полный внешний HTTP-контракт. §4.10 — не публичные URL. Admin/Accept — отдельно.

### 9.15. Чеклист реализации Public API

- [ ] Модули входящего контура §9.13.
- [ ] Версия `/v1/{service_id}/…` + auth на service_id.
- [ ] Доработанный enqueue: idempotency, actor, status_url, проверка ProcessRegistry.
- [ ] `GET .../fsm/instances/{id}`.
- [ ] `POST .../invoke` + Operation Registry (register из `register_all`).
- [ ] `GET .../catalog`.
- [ ] Единый error envelope.
- [ ] Webhooks / SSE / outbox — по §10.
- [ ] Хотя бы один channel adapter только через Public API.
- [ ] OpenAPI для `/v1` из registry/catalog.
- [ ] Автотест: enqueue → poll COMPLETED; invoke list без FSM instance.

---

## 10. Исходящие ответы клиенту и outbox

Входящий контракт — §9 (enqueue / invoke). Этот раздел — **как platform отдаёт результат наружу** после принятия запроса: сразу в HTTP-ответе, через poll, SSE, webhook/outbox или push в канал.

### 10.1. Два разных «ответа»

| Вид | Когда | Механизм |
|-----|--------|----------|
| **Синхронный HTTP-ответ** | `invoke` (query / короткий command); `enqueue` → `202` | тело текущего HTTP-запроса (§9.3–9.4) |
| **Отложенное уведомление** | worker завершил FSM; изменился entity state; нужен push во внешнюю систему | poll / SSE / webhook / channel push — через **события** и при необходимости **outbox** |

Правило (§4.7 / §10.6):  
- **COMPLETED** — `emit_event` / `notify` (outbox) в рабочей tx **до** COMMIT platform;  
- **FAILED** — только в **отдельной short tx** после ROLLBACK обеих;  
фактический HTTP/push наружу — после commit, `outbox_worker` (или SSE-hub читает закоммиченные строки).

```text
Клиент                    Platform                         Внешние системы
  │                          │
  │── invoke / enqueue ─────▶│
  │◀── 200 / 202 ────────────│   (синхронный ответ)
  │                          │
  │                          │ COMPLETED: transition+effect+fan-out → COMMIT
  │                          │ FAILED: ROLLBACK → short tx emit/notify → COMMIT
  │                          │
  │◀── poll / SSE / webhook ─│◀── outbox_worker доставляет
  │    или channel push      │
```

### 10.2. Каталог способов доставки

| Способ | Направление | Типичный клиент | Плюсы | Минусы / когда не брать |
|--------|-------------|-----------------|-------|-------------------------|
| **Sync HTTP body** | request→response | сайт, Postman, invoke | просто | не ждёт долгий FSM |
| **Poll status** | клиент → `GET .../instances/{id}` | автотест, простой сайт | просто, за NAT | задержка, нагрузка при частом poll |
| **SSE** | platform → клиент (длинный HTTP) | веб-UI, отладка | push без отдельного callback URL | нужен держащийся HTTP; плохо для serverless-клиентов |
| **Webhook (HTTP callback)** | platform → URL клиента | сайт заказчика, интеграции | стандарт для B2B | клиент должен иметь публичный HTTPS |
| **Channel push** | platform → Telegram/WhatsApp API | мессенджеры | UX в чате | через channel adapter + outbox |
| **WebSocket** | двусторонний канал | богатый realtime UI | гибко | сложнее SSE в эксплуатации; v2 |
| **External system outbox** | platform → Core/ERP/… | бэкенд-интеграции | надёжная доставка после commit | не для браузера напрямую |

Рекомендуемый минимум v1: **sync + poll + transactional outbox (webhooks / channel / external)**. SSE — для веб-UI и автотестов с живым соединением. WebSocket — опционально позже.

### 10.3. Единая модель события

Все отложенные доставки опираются на одно событие в platform DB (имя таблицы условное: `platform_events`).

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | экземпляр домена |
| `event_type` | например `fsm.instance.completed`, `fsm.instance.failed`, `fsm.entity.state_changed` |
| `instance_id` | опционально |
| `entity_type`, `entity_id` | опционально |
| `payload_json` | данные для клиента (без внутренних секретов) |
| `created_at` | время commit-логики |
| `correlation_id` / `client_request_id` | связь с исходным запросом |

**Кто пишет:** только **`platform.emit_event`** (§4.13). COMPLETED — в рабочей tx до COMMIT platform; FAILED — в отдельной короткой tx после rollback (§4.7). Модуль `platform/events.py` реализует `emit_event`, не пишет в обход API.

**Кто читает:**

- poll/SSE — SELECT новых events (или status instance, см. ниже);
- outbox_worker — строки доставки, связанные с event.

Упрощение v1: для статуса instance достаточно `server_fsm_instances` (poll/SSE по instance); `platform_events` — когда нужны подписки шире, чем один instance (entity updates, fan-out на несколько webhooks).

### 10.4. Poll (обязательный базовый канал)

Уже есть контракт: `GET /v1/{service_id}/fsm/instances/{instance_id}` (§9.5).

```text
enqueue → 202 { instance_id, status_url }
клиент: каждые N мс/с GET status_url
пока status in (PENDING, PROCESSING) → ждать
COMPLETED / FAILED → взять payload / last_error
```

Правила:

- auth на тот же `service_id`;
- не использовать poll как единственный канал для тысяч UI-клиентов с интервалом &lt;1s (лучше SSE/webhook);
- автотесты: poll или `enqueue mode=wait`.

### 10.5. SSE (Server-Sent Events)

Односторонний поток событий от platform к клиенту по длинному HTTP.

#### Endpoint

```http
GET /v1/{service_id}/events/stream?instance_id=1001
Authorization: Bearer …
Accept: text/event-stream
```

Фильтры query (минимум один): `instance_id` и/или `entity_type`+`entity_id`, опционально `Last-Event-ID` для resume.

#### Поток

```text
1. Gateway: auth, service_id active
2. SSE hub подписывается на события service_id (+ фильтр)
3. При появлении закоммиченного события (или смене instance status):
     data: {"event_type":"fsm.instance.completed","instance_id":1001,...}
4. Клиент закрывает поток или держит для следующих entity-событий
```

#### Источник данных для SSE hub (норматив — вариант A)

SSE hub **читает platform DB** (закоммиченные строки): `platform_events` и/или `server_fsm_instances` — с коротким интервалом poll или `LISTEN/NOTIFY`, если СУБД позволяет.

Так hub работает при любом числе реплик HTTP API и отдельном `fsm_worker`: событие видно всем pod’ам после commit, без in-process pub/sub и без обязательного Redis.

```text
fsm_worker                    API pod 1 … N (SSE)
  COMMIT event/instance  →    каждый hub: SELECT новых строк из platform DB
                              → push в открытые SSE-соединения своего pod
```

#### Когда SSE

- веб-фронт ждёт результат enqueue;
- операторская доска статусов;
- отладка.

#### Когда не SSE

- Telegram/WhatsApp (нет длинного HTTP от клиента бота) → channel push / webhook;
- клиент за жёстким proxy, режущим long-lived HTTP → poll/webhook.

### 10.6. Transactional outbox (общий механизм)

**Outbox** — таблица «доставить наружу» в platform DB. Пишется только через `platform.notify`: при COMPLETED — в рабочей tx до COMMIT platform; при FAILED — в short tx после ROLLBACK (§4.7). Отдельный **outbox_worker** после commit делает HTTP/API вызов.

Это не замена Public API. Это транспорт для:

1. **Client webhooks** — POST на URL заказчика;
2. **Channel push** — вызов Bot API мессенджера;
3. **External integrations** — Core API, ERP, SMS-шлюз (канал `http_external` / `core`).

#### Таблица `platform_outbox` (platform DB)

| Поле | Смысл |
|------|--------|
| `id` | PK |
| `service_id` | |
| `channel` | `webhook` \| `telegram` \| `whatsapp` \| `http_external` \| … |
| `destination` | URL / chat_id / system code |
| `event_type` | тип события |
| `payload_json` | тело доставки |
| `status` | `PENDING` \| `PROCESSING` \| `SENT` \| `FAILED` \| `DEAD` |
| `attempts` | счётчик |
| `next_attempt_at` | backoff |
| `idempotency_key` | уникальность доставки |
| `last_error` | |
| `created_at`, `sent_at` | |

Поле **`depends_on_outbox_id` в v1 отсутствует**. Оркестрация цепочек = FSM + `platform.schedule_timer`, не граф outbox.

#### Producer (единственные точки записи)

Запись в `platform_outbox` — **только** через `platform.notify` (§4.13).  
Запись в `platform_events` — **только** через `platform.emit_event` (§4.13).

1. **`platform.notify(...)`** из domain effect / sync command — явная доставка (channel push, external, точечный webhook).
2. **Platform fan-out hook:**
   - **COMPLETED** — в рабочей tx **до** COMMIT platform: `emit_event` + `notify` по `webhook_subscriptions`;
   - **FAILED** — **только** в отдельной короткой tx после ROLLBACK (§4.7): `emit_event` + `notify` по подпискам на failed.
   Не дублировать в effect то, что уже делает fan-out по `event_type`.

```text
COMPLETED:
  effect → platform.notify (опц.)
  fan-out → emit_event + notify(webhooks)
  UPDATE instance COMPLETED
  COMMIT domain → COMMIT platform

FAILED:
  ROLLBACK обеих
  short tx → UPDATE FAILED + emit_event + notify(webhooks)
  COMMIT
→ outbox_worker доставляет HTTP
```

**Запрещено:** сырой INSERT в `platform_outbox` / `platform_events`; fan-out FAILED в откатываемой рабочей tx; HTTP наружу до commit.

**Норматив:** только **`platform_outbox` + platform `outbox_worker`**.

#### Алгоритм outbox_worker (consumer)

```text
LOOP:
  1. SELECT … FROM platform_outbox
       WHERE status='PENDING' AND next_attempt_at <= NOW()
       ORDER BY id LIMIT N
       FOR UPDATE SKIP LOCKED
  2. status=PROCESSING
  3. по channel:
       webhook → HTTP POST destination + HMAC signature
       telegram → Bot API sendMessage (токен из secrets канала)
       http_external → HTTP по контракту destination
  4. успех → SENT + sent_at
     ошибка → attempts++, backoff next_attempt_at, status=PENDING
     attempts > max → DEAD + alert
```

**Запрещено:** HTTP наружу из `transition_runner` / SQL transition / до commit.

### 10.7. Webhooks (клиентский callback)

Регистрация: `POST /v1/{service_id}/webhooks` (§9.9) → `webhook_subscriptions` (§4.14).

При событии — **только platform fan-out hook** (§10.6):

```text
COMPLETED/FAILED (+ platform_events)
  → подходящие webhook_subscriptions
  → platform.notify(channel=webhook, …) → platform_outbox
```

Тело callback (пример):

```json
{
  "event_type": "fsm.instance.completed",
  "service_id": "svc_…",
  "instance_id": 1001,
  "entity_type": "order_request",
  "entity_id": 348,
  "payload": {},
  "created_at": "…"
}
```

Заголовки: `X-Platform-Signature`, `X-Request-Id`. Клиент отвечает `2xx`; иначе retry outbox_worker.

### 10.8. Channel push (мессенджеры)

```text
FSM COMPLETED (или effect)
  → platform.notify(channel=telegram, destination=chat_id, payload={text|template})
  → platform_outbox
  → outbox_worker
  → channels/telegram sender (Bot API)
```

Adapter на **входе** парсит update → Public API.  
Sender на **выходе** только доставляет сообщения из outbox. Не смешивать с TransitionRunner.

### 10.9. External outbox (Core / ERP)

External-интеграции (Core/ERP) — тот же `platform_outbox` с `channel=http_external` (или `core`) через **`platform.notify`**. Цепочки вызовов — отдельные FSM transitions / timers, не зависимости между строками outbox.

Браузер external outbox не читает: ему poll / SSE / webhook.

### 10.10. WebSocket (опционально, v2)

Двусторонний канал для UI. Имеет смысл, если нужны клиент→server команды поверх того же сокета. Для только server→client достаточно SSE. Если внедряется: те же `platform_events`, fan-out в socket hub после commit; auth при connect на `service_id`.

### 10.11. Что выбрать клиенту

| Клиент | Вход | Ожидание результата async |
|--------|------|---------------------------|
| Сайт (SPA) | invoke / enqueue | SSE или webhook; poll как fallback |
| Автотестер | enqueue | poll или `mode=wait` |
| Postman | enqueue / invoke | poll |
| Telegram / WhatsApp | adapter → API | channel push через outbox |
| Backend заказчика | enqueue + webhooks | webhook (outbox) |
| Внешняя система (Core) | — | external outbox |

### 10.12. Модули platform (исходящий контур)

| Модуль | Назначение |
|--------|------------|
| `platform/outbox/db_layer.py` или методы в platform db | INSERT/claim `platform_outbox` |
| `platform/outbox/worker.py` | доставка, retry, DEAD |
| `platform/reconcile/worker.py` | докат platform из `platform_reconcile_queue` (§4.7.1) |
| `platform/events.py` | реализация `platform.emit_event` → `platform_events` |
| `platform/http/sse.py` | endpoint stream |
| `platform/webhooks/registry.py` | subscriptions |
| `channels/*/sender.py` | отправка в мессенджер из outbox |

Worker FSM после `run_instance`: при COMPLETED — fan-out в рабочей tx (§10.6); при FAILED — только short tx после rollback (§4.7). Domain effect мог вызвать `notify` ранее в той же рабочей tx (COMPLETED path).

### 10.13. Связь с sync-ответом Public API

| Запрос | Сразу в HTTP | Потом |
|--------|--------------|--------|
| `invoke` query | `200` + data | обычно ничего |
| `invoke` command (короткий) | `200` + data | опц. event |
| `enqueue` | `202` + instance_id | poll / SSE / webhook / channel push |
| `enqueue mode=wait` | INSERT + poll status в HTTP (без claim); финал 200/504 | outbox после commit worker — как обычно |

### 10.14. Запрещено

- HTTP к клиенту/Telegram/Core из transition/effect до commit;
- SSE, читающий незакоммиченные данные другой транзакции без правил isolation;
- обязать всех клиентов только webhook (нет публичного URL у бота/Postman);
- заводить отдельный domain-outbox worker для клиентских/канальных уведомлений (только `platform_outbox`);
- `depends_on_outbox_id` / оркестрация в outbox (v1);
- выполнять `run_instance` внутри HTTP при `mode=wait`.

### 10.15. Чеклист

- [ ] Poll status (§9.5) стабилен и задокументирован.
- [ ] Таблица `platform_outbox` + outbox_worker (retry, backoff, DEAD).
- [ ] Публикация: COMPLETED — в рабочей tx; FAILED — short tx после ROLLBACK (§4.7 / §10.6).
- [ ] Webhook subscriptions → outbox channel=webhook.
- [ ] SSE endpoint для `service_id` + фильтр instance/entity.
- [ ] Channel sender(s) читают outbox, не вызываются из fsm_core.
- [ ] (опц.) external outbox для Core/ERP.
- [ ] Smoke: enqueue → SSE или poll COMPLETED; enqueue → webhook 2xx.

---

## 11. Запрещённые решения (анти-паттерны)

При реализации platform эти подходы **запрещены**:

| Запрещено | Вместо этого |
|-----------|--------------|
| Одна общая БД для platform + всех доменов | platform DB + отдельная domain DB на `service_id` |
| FSM-state сущности в business-колонке домена как источник истины для runner | `entity_fsm_state` в platform DB |
| SQL transition / fsm_core UPDATE business-таблиц | только domain effects |
| Параллельная «SQL Core» procedure рядом с TransitionExecutor | один путь: TransitionExecutor (§4.6) |
| `core_outbox` + `platform_outbox` | только `platform_outbox` |
| Произвольный SQL домена в platform DB | только notify / emit_event / schedule_timer (§4.13) |
| IF `entity_type` → выбор таблицы домена внутри `fsm_core` | opaque `entity_type`/`entity_id`; схему знает только домен |
| Смешение SQL platform и domain в одном db_layer | `fsm_core/db_layer.py` + `domains/*/db_layer.py` |
| Хардкод внешних URL клиентов в обход Public API | только `/v1/{service_id}/…` (§9) |
| Домен без Validator / без Domain Registry | Accept → Validator → `active` |
| Python map `state → handler` вместо графа | declarative `fsm_transitions` + guards/effects |
| Импорт `domains.*` из `fsm_core` | только registry + callable |
| Channel adapter с прямым SQL домена | adapter → Platform Public API |
| `fsm_action_logs` как вторая log-таблица | только `fsm_transition_logs` |
| `ProcessDef.service` / колонка `service` | только `service_id` |
| `depends_on_outbox_id` / граф outbox | FSM + timers |
| mode=wait → claim/run в HTTP | poll-in-request; claim только worker |
| Prod Accept: произвольный zip→import | пакет из доверенного registry (§7.5) |
| Несколько независимых outbox producer | только `platform.notify` + fan-out hook |
| Fan-out FAILED в рабочей tx | short tx после ROLLBACK (§4.7) |
| 2PC / повтор effect при platform commit fail | `platform_reconcile_queue` (§4.7.1) |
| Домен регистрирует HTTP `(method, path)` | только OperationRegistry + FSM |
| Сырой INSERT `platform_events` | только `platform.emit_event` |

## 12. Пример: courier vs taxi

| | Courier | Taxi |
|---|---------|------|
| Staging | `order_request` | опционально / сразу `taxi_order` |
| Creation process | `order_creation` | `submit_ride` |
| entity_type | `order_request` | `taxi_order` |
| event | `order_create` | `ride_submit` |
| Первый state | `request_received` | `draft` |
| Domain DB | FSM-граф + orders, locker_cells, … | FSM-граф + taxi_orders, … |

Один `fsm_core`, разные картриджи. Подключение — §6–7; внешние клиенты — Public API §9.

---

## 13. Критерии готовности platform

- [ ] Worker обрабатывает instance через `fsm_core.run_instance` без domain-specific кода в core.
- [ ] Guard routing по priority работает и логирует reason при отказе.
- [ ] TransitionExecutor → только `entity_fsm_state` + `fsm_transition_logs`.
- [ ] Dual-DB commit §4.7; recovery §4.7.1 (`platform_reconcile_queue` + reconcile worker).
- [ ] Bootstrap state §4.12; side-effect API §4.13.
- [ ] Guard default §4.4; `list_candidates` через `session_domain` (engine этого `service_id`).
- [ ] Bootstrap: active домены из Domain Registry / `FSM_DOMAINS` → `register_all`.
- [ ] Domain Validator: пакет + SQL/ХП/граф + default-guard + OperationRegistry + согласованность.
- [ ] Accept prod без zip-exec; `engine_by_service_id` из Domain Registry (§4.14).
- [ ] Домен `failed`/`disabled` не обслуживает REST и FSM.
- [ ] `idempotency_keys` + `webhook_subscriptions` (§4.14).
- [ ] Public API routes (platform) + OperationRegistry + Request Runtime (§4.10.1).
- [ ] Request Runtime владеет session на HTTP-запрос; домен session не открывает.
- [ ] Query: Gateway → Runtime → domain handler → domain db_layer; без FSM instance.
- [ ] Command: staging/enqueue через Runtime; lifecycle в worker.
- [ ] Public API `/v1/{service_id}`: enqueue, invoke, instances status, catalog (§9).
- [ ] Auth и Idempotency-Key на enqueue; actor не только из body.
- [ ] Smoke: минимум один домен end-to-end (Command + Query) через Public API.
- [ ] (опц.) один channel adapter ходит только в Public API.
- [ ] Исходящий контур §10: poll + outbox_worker; SSE и/или webhooks.
- [ ] Нет HTTP наружу из fsm_core / effect до commit.
- [ ] Outbox/events только через notify/emit_event; FAILED fan-out в short tx; без `depends_on_outbox_id`.
- [ ] `mode=wait` = poll-in-request (без claim в HTTP).
- [ ] SSE hub — чтение platform DB (вариант A), не in-process pub/sub.

## 14. Критерии готовности домена

- [ ] `manifest.yaml` + структура картриджа §5.1.
- [ ] `register_all()` (ProcessDef + OperationRegistry + guards/effects).
- [ ] Domain DB: FSM-граф + бизнес-схема (+ ХП по manifest) до Accept.
- [ ] Все guard_name/effect_name из SQL зарегистрированы в Python.
- [ ] Effects → domain db_layer; наружу только notify / emit_event / schedule_timer (§4.13).
- [ ] `db_layer.py` — единственное место бизнес-SQL домена; session только аргумент.
- [ ] Query → `queries.py`; sync Command → `commands.py`; operations в OperationRegistry.
- [ ] Проходит Domain Validator → `active`.
- [ ] Smoke Command / Query после активации.

---

## 15. Глоссарий

| Термин | Значение |
|--------|----------|
| Platform | FSM Platform: worker, fsm_core, HTTP-слой, platform DB, bootstrap, validator |
| Domain / картридж | courier, taxi, cargo — SQL + Python + db_layer, своя domain DB |
| Domain Registry | таблица platform DB (`domain_services`): каталог service_id / cartridge_type / status / DB / package; см. §6.3 |
| Domain Validator | проверка целостности пакета и готовности domain DB (SQL/ХП/граф) |
| cartridge_type | тип картриджа (`cargo`, `courier`); не обязан быть уникальным |
| service_id | уникальный id экземпляра домена; ключ runtime и Domain Registry |
| Operation/FSM Registry | dict в RAM; наполняется `register_*` при boot; см. §6.4 |
| platform.emit_event | единственный writer `platform_events`; §4.13 |
| platform_reconcile_queue | докат platform после domain commit / platform fail; §4.7.1 |
| manifest.yaml | метаданные картриджа: cartridge_type, version, entry, required objects |
| ProcessDef | поля `service_id`, process_name, entity_type, event_name |
| Instance | строка `server_fsm_instances` — задача worker |
| entity_type + entity_id | opaque указатель домена для platform |
| SQL transition | TransitionExecutor → fsm_core db_layer |
| Effect | доменный код после transition; запись через domain db_layer |
| Domain db_layer | `domains/*/db_layer.py` — SQL domain DB; session от platform |
| fsm_core db_layer | `fsm_core/db_layer.py` — SQL platform DB; §8.8 |
| guard_params / effect_params | JSON в `fsm_transitions`; аргументы guard/effect; §8.2.5 |
| SQL seed | SQL картриджа для domain DB (накат до Accept в v1) |
| Guard routing | выбор transition по priority и guards |
| Gateway | HTTP in/out, auth, JSON; без бизнес-SQL |
| Public API routes | фиксированные `/v1/...` в коде platform; §9 |
| Operation Registry | RAM §6.4.1: `(service_id, operation) → handler, kind`; catalog/invoke |
| Dispatcher | Public API path → enqueue/invoke/… → Runtime / OperationRegistry |
| Request Runtime | владелец session на REST-запрос; commit §4.10.1; bootstrap state §4.12 |
| Domain handler | use-case домена (query/command entry); session только принимает |
| domain session | session к domain DB, созданная platform (Runtime/worker), не доменом |
| Command | REST, меняющий lifecycle → enqueue FSM |
| Query | REST без FSM; чтение через domain handler + db_layer |
| Accept | операция добавления/активации домена (UI или ops) после Validator |
| Channel adapter | Telegram/WhatsApp/… → парсит протокол → Platform Public API; §9.10 |
| Platform Public API | внешний контракт `/v1/{service_id}/…`: enqueue, invoke, status, catalog; §9 |
| Idempotency-Key | заголовок; store = `idempotency_keys` §4.14; §9.3 |
| engine_by_service_id | RAM map connection к domain DB из `domain_services.db_secret_ref` |
| mode=wait | enqueue + poll status в том же HTTP; claim только worker |
| platform_outbox | единственный outbox; §10.6 |
| platform.notify / emit_event / schedule_timer | side-effect API домена; §4.13 |
| fsm_transition_logs | единственный audit log переходов |
| outbox_worker | процесс отправки webhook/channel/external из outbox; §10.6 |
| SSE | Server-Sent Events: поток событий к клиенту; §10.5 |
| platform_events | журнал событий platform для SSE/подписок; §10.3 |
| TransitionRunner | `fsm_core/transition_runner.py` — pipeline одного FSM-шага; §8.5 |
| run_instance | `fsm_core/engine.py` — вход worker в FSM; §8.4 |
| EntityStateStore | `fsm_core/state_store.py` — API state поверх db_layer; §8.9 |
| TransitionRepository | `fsm_core/transition_repository.py` — candidates (+ params) из domain DB; §8.10 |
| TransitionExecutor | `fsm_core/transition_executor.py` — apply через db_layer; §8.11 |

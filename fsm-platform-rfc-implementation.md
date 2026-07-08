# FSM Platform: инструкция по доработке движка

## Цель

Развить текущий табличный FSM в декларативную FSM Platform, пригодную для нескольких доменов: courier, taxi и будущих сервисов.

Базовая идея:

```text
state + event -> candidate transitions -> selected transition -> new_state
```

Но вокруг SQL-ядра добавляется Python Runtime, который выполняет общий pipeline:

```text
context -> guard -> transition -> effect
```

## Термины

### SQL Core

Минимальное SQL-ядро FSM:

```text
fsm_states
fsm_events
fsm_transitions
fsm_transition_logs
fsm_perform_transition
```

Ответственность SQL Core:

- проверить, что выбранный Runtime transition всё ещё допустим для текущего state;
- сменить статус сущности;
- записать журнал перехода.

SQL Core не должен содержать бизнес-логику такси, курьерки, Core API, realtime или платежей.

### Python Runtime

Общий Python-слой исполнения FSM:

```text
fsm_core/
  engine.py
  transition_runner.py
  registry.py
  types.py
  timers.py
```

В документе `Runtime` означает весь общий движок `fsm_core`. `transition_runner.py` — внутренний компонент Runtime, который физически реализует pipeline перехода.

Ответственность Runtime:

- получить FSM instance;
- найти зарегистрированный ProcessDef;
- собрать context через доменный context_builder;
- найти candidate transitions;
- выполнить guards;
- выбрать ровно один transition;
- вызвать SQL Core для перехода;
- выполнить local effects;
- вернуть результат worker.

### Domain Layer

Доменные модули:

```text
domains/
  taxi/
    context.py
    guards.py
    effects.py
    processes.py
    engine.py

  courier/
    context.py
    guards.py
    effects.py
    processes.py
    engine.py
```

Домен отвечает за бизнес-смысл:

- какие данные нужны для процесса;
- какие проверки выполнить;
- какие локальные действия сделать;
- какие outbox/realtime/timer события создать.

Если в Runtime появляется бизнес-условие такси или курьерки, это ошибка архитектуры.

## Расширение `fsm_transitions`

Для декларативной модели `fsm_transitions` расширяется:

```sql
RENAME TABLE fsm_actions TO fsm_events;

ALTER TABLE fsm_transitions
CHANGE COLUMN action_id event_id BIGINT NOT NULL;

RENAME TABLE fsm_action_logs TO fsm_transition_logs;

ALTER TABLE fsm_transition_logs
CHANGE COLUMN action_name event_name VARCHAR(100) NOT NULL;

ALTER TABLE fsm_transition_logs
ADD COLUMN transition_id BIGINT NULL;

ALTER TABLE fsm_transitions
ADD COLUMN guard_name VARCHAR(100) NULL,
ADD COLUMN guard_params JSON NULL,
ADD COLUMN priority INT NOT NULL DEFAULT 100,
ADD COLUMN effect_name VARCHAR(100) NULL,
ADD COLUMN effect_params JSON NULL;

CREATE UNIQUE INDEX ux_fsm_transition_priority
ON fsm_transitions (entity_type, from_state_id, event_id, priority);
```

`guard_name`, `guard_params`, `effect_name`, `effect_params` nullable, чтобы существующие постаматные переходы продолжили работать без изменений. `priority` получает `DEFAULT 100`.

`guard_name` и `effect_name` — это не SQL-логика. Это ссылки на Python-функции, зарегистрированные в Runtime.

Для MVP используется event/guard-routing модель:

```text
entity_type + from_state + event_name -> candidate transitions
candidate transitions sorted by priority ASC + guard_name -> selected transition
```

`event_name` — это FSM event/trigger. Историческое название `action` в старом SQL Core больше не используется в новой инструкции.

`guard_name` выбирает конкретный transition из candidate transitions. Для одного `entity_type + from_state + event_name` может быть несколько строк `fsm_transitions`.

Runtime выбирает transition по правилу:

```text
1. candidate transitions сортируются по priority ASC;
2. чем меньше priority, тем раньше проверяется transition;
3. более специфичные guards должны иметь меньший priority;
4. fallback/default transition должен иметь самый большой priority;
5. transition без guard_name считается default transition;
6. Runtime выбирает первый transition, у которого guard=true или guard_name=NULL;
7. если не подошёл ни один guard, переход не выполняется;
8. если для одного entity_type + from_state + event_name есть несколько transitions с одинаковым priority, Runtime возвращает AMBIGUOUS_TRANSITION.
```

`priority` должен быть уникален внутри одного набора candidate transitions. Это нужно, чтобы порядок выбора не зависел от порядка строк в БД.

Default transition (`guard_name = NULL`) должен быть единственным для одного `entity_type + from_state + event_name` и иметь самый большой `priority`.

SQL Core вызывается уже после выбора transition:

```text
fsm_perform_transition(
  entity_type,
  entity_id,
  transition_id,
  event_name,
  user_id
)
```

SQL Core обязан повторно проверить, что:

```text
- transition_id существует;
- transition.entity_type совпадает с entity_type;
- transition.event_name совпадает с event_name;
- текущий state сущности всё ещё равен transition.from_state.
```

После этого SQL Core меняет state на `transition.to_state` и пишет `fsm_transition_logs`, включая `transition_id` и `event_name`.

Пример:

```text
entity_type = taxi_order
from_state = draft
event_name = order_submit
to_state = searching_driver

guard_name = can_submit_taxi_order
guard_params = {"require_payment_method": true}
priority = 100

effect_name = create_trip_and_start_matching
effect_params = {"notify_client": true}
```

Смысл:

```text
БД хранит декларативную карту перехода.
Python Runtime исполняет guard/effect и выбирает transition.
SQL Core фиксирует выбранный transition.
```

## Структура `fsm_core`

```text
fsm_core/
  engine.py
    -- главный вход: run_event / run_instance
    -- получает instance
    -- берёт ProcessDef из registry
    -- запускает transition_runner

  transition_runner.py
    -- общий pipeline:
       build context
       load candidate transitions
       run guards
       select transition
       perform selected transition
       run effect

  registry.py
    -- ProcessRegistry
    -- GuardRegistry
    -- EffectRegistry

  types.py
    -- FsmResult
    -- GuardResult
    -- EffectResult
    -- ProcessDef
    -- TransitionDef

  timers.py
    -- создание/отмена/срабатывание таймеров
    -- timer -> обычный server_fsm_instance(process_name)
```

## Структура домена

Пример для taxi:

```text
domains/taxi/context.py
  -- собирает TaxiOrderContext из БД/репозиториев

domains/taxi/guards.py
  -- can_submit_taxi_order
  -- driver_can_accept_order
  -- payment_is_confirmed

domains/taxi/effects.py
  -- start_driver_matching
  -- assign_driver
  -- create_realtime_event
  -- schedule_matching_timeout

domains/taxi/processes.py
  -- регистрирует ProcessDef
  -- регистрирует guard functions
  -- регистрирует effect functions

domains/taxi/engine.py
  -- опционально
  -- только для сложных многошаговых orchestration-процессов
```

`processes.py` не хранит карту `state -> guard/effect`. Эта карта находится в `fsm_transitions`.

`processes.py` только сообщает Runtime:

```text
я умею выполнять процесс submit_order;
я умею выполнять guard can_submit_taxi_order;
я умею выполнять effect start_driver_matching.
```

## Process Registry

`server_fsm_instances` хранит конкретную запущенную задачу:

```text
service = taxi
process_name = submit_order
entity_type = taxi_order
entity_id = 123
instance_status = PENDING
```

Таблица не является справочником всех процессов. Она хранит только инстансы.

Список допустимых процессов регистрируется в домене:

```python
ProcessDef(
    service="taxi",
    process_name="submit_order",
    entity_type="taxi_order",
    event_name="order_submit",
    context_builder=build_taxi_order_context,
)
```

Runtime делает lookup:

```text
instance.service + instance.process_name -> ProcessDef
```

Если процесс не зарегистрирован, Runtime возвращает ошибку `UNKNOWN_PROCESS`.

Правило именования:

```text
process_name — внешняя job/команда для worker и Runtime;
event_name — внутренний FSM event/trigger для Runtime.
```

`event_name` не хранится в `server_fsm_instances` и не приходит напрямую с frontend. Runtime получает его из `ProcessDef`.

Для мультидомена в `server_fsm_instances` нужно добавить поле:

```text
service VARCHAR(50)
```

## Общая формула Runtime

Runtime выполняет любой доменный процесс по одной формуле:

```text
1. Worker взял строку из server_fsm_instances.
2. Runtime читает service, process_name, entity_type, entity_id.
3. Runtime ищет ProcessDef в ProcessRegistry.
4. Runtime получает event_name из ProcessDef.
5. Runtime вызывает context_builder из ProcessDef.
6. Runtime читает текущий state сущности.
7. Runtime ищет candidate transitions в fsm_transitions по entity_type + current_state + event_name.
8. Runtime выполняет guards из GuardRegistry и выбирает один transition.
9. Runtime вызывает SQL Core / fsm_perform_transition для выбранного transition.
10. Runtime выполняет effect из EffectRegistry.
11. Runtime возвращает FsmResult.
```

Для Runtime нет разницы между taxi и courier. Различается только доменная реализация context/guard/effect.

## Flow: заказать такси

```text
1. Frontend -> POST /api/taxi/order_request

2. API создаёт taxi_order_request или taxi_order со статусом draft.

3. API или domain service создаёт server_fsm_instance:
   service = taxi
   process_name = submit_order
   entity_type = taxi_order
   entity_id = order_id
   instance_status = PENDING

4. fsm_worker забирает instance.

5. fsm_core.engine получает instance и находит ProcessDef:
   service = taxi
   process_name = submit_order
   event_name = order_submit

6. Runtime вызывает taxi context_builder:
   domains/taxi/context.py

7. transition_runner читает transition:
   taxi_order + current_state=draft + event_name=order_submit

8. transition содержит:
   guard_name = can_submit_taxi_order
   effect_name = create_trip_and_start_matching

9. GuardRegistry находит:
   domains.taxi.guards.can_submit_taxi_order

10. Guard выполняется внутри той же DB session/transaction.

11. Если guard failed:
    переход не выполняется;
    instance_status -> FAILED или WAITING по правилам процесса.

12. Если guard ok:
    transition_runner выполняет шаг perform transition:
    вызывает SQL Core / fsm_perform_transition;
    state: draft -> searching_driver;
    пишется fsm_transition_logs.

13. EffectRegistry находит:
    domains.taxi.effects.create_trip_and_start_matching

14. Effect выполняет local DB effects:
    - создать trip;
    - записать realtime_event;
    - поставить timer;
    - записать core_outbox для вызова Core API.

15. Worker делает COMMIT.

16. После commit:
    realtime gateway доставляет события;
    core_outbox_worker вызывает Core API;
    timer subsystem позже создаёт обычные FSM jobs.
```

## Транзакции

Transaction boundary находится на уровне worker/session_scope.

Worker открывает и закрывает DB session:

```text
fsm_worker
  BEGIN / open session
    fsm_core.engine.run_instance(session, instance)
      build context
      guard()
      fsm_perform_transition()
      local effects
      core_outbox/realtime_events/fsm_timers insert
  COMMIT

если ошибка:
  ROLLBACK
  mark instance FAILED в отдельной короткой transaction

finally:
  close session
```

Правило:

```text
worker владеет session lifecycle;
Runtime использует уже открытую session;
domain code использует эту же session;
commit/rollback делает только worker boundary.
```

Guard — Python-функция, но она получает ту же DB session, что и `fsm_perform_transition`.

Guard failed не считается exception:

```text
guard false
  -> SQL Core не вызывается
  -> state сущности не меняется
  -> instance_status обновляется на WAITING или FAILED
  -> worker делает COMMIT
```

Exception в guard, SQL Core или local effect считается ошибкой выполнения:

```text
exception
  -> ROLLBACK всей transaction перехода
  -> новая короткая transaction помечает instance_status = FAILED
```

## Атомарность перехода

В одной транзакции должны быть:

```text
1. выбор текущего состояния сущности;
2. выбор candidate transitions из fsm_transitions;
3. выполнение guard;
4. выбор ровно одного selected transition;
5. смена состояния entity;
6. запись fsm_transition_logs;
7. local DB effects, если они часть консистентного состояния;
8. insert в core_outbox/realtime_events/fsm_timers.
```

Внешние side effects не выполняются внутри транзакции:

```text
- HTTP-вызов в Core API;
- реальная отправка WebSocket-сообщения;
- push-уведомление;
- команда железу/постамату;
- вызов стороннего сервиса.
```

Причина:

```text
внешний вызов нельзя откатить rollback'ом локальной БД.
```

## Effects

Effects стоит разделять концептуально.

Domain Effects:

```text
- assign_driver
- reserve_cells
- create_trip
```

Infrastructure Effects:

```text
- create_realtime_event
- write_core_outbox
- schedule_timer
```

Для MVP достаточно:

```text
effect_name
effect_params
```

`effect_type` можно оставить концепцией в документации/Python-коде.

Если transition должен выполнить несколько локальных действий, для MVP используется composite effect:

```text
effect_name = create_trip_and_start_matching
```

Внутри Python effect может:

```text
- создать trip;
- записать realtime_event;
- записать core_outbox;
- поставить timer.
```

После MVP, если понадобится строгая декларативность и несколько effects на один transition, добавляется отдельная таблица:

```sql
CREATE TABLE fsm_transition_effects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transition_id BIGINT NOT NULL,
    effect_order INT NOT NULL,
    effect_name VARCHAR(100) NOT NULL,
    effect_type VARCHAR(32) NULL,
    effect_params JSON NULL
);
```

## Outbox / Saga для Core API

Core API — внешний сервис. Его нельзя откатить через rollback локальной БД.

Поэтому FSM transition не должен напрямую вызывать Core API.

Правильная схема:

```text
FSM effect:
  - пишет core_outbox.

worker boundary:
  - commit.

core_outbox_worker:
  - читает core_outbox;
  - вызывает Core API;
  - сохраняет результат;
  - при необходимости создаёт следующий server_fsm_instance.
```

Запись в `core_outbox` — это local DB effect.

Runtime не должен знать бизнес-смысл outbox-события. Runtime только даёт транзакцию и вызывает effect.

Для MVP `core_outbox` закладывается сразу.

Минимальная схема:

```text
core_outbox
  id
  service
  event_type
  payload_json
  status = PENDING / PROCESSING / COMPLETED / FAILED
  attempts_count
  next_retry_at
  last_error
  created_at
  processed_at
```

Все вызовы Core API проходят через `core_outbox`. Внешний Core API не вызывается напрямую из guard/effect внутри transition. Effect только пишет `core_outbox`.

## Timers

Таймер — это источник новой FSM job, а не отдельный способ менять состояние.

Нельзя:

```text
timer -> напрямую поменять status
```

Нужно:

```text
timer fired -> server_fsm_instance(process_name) -> Runtime -> event_name -> обычный FSM pipeline
```

То есть:

```text
timer -> process_name -> ProcessDef.event_name -> transition lookup -> guard routing -> state change -> effect -> log
```

Timer subsystem нужна для:

```text
- создания таймера;
- отмены таймера;
- безопасного срабатывания;
- защиты от повторного выполнения.
```

Но результатом работы таймера всегда должен быть обычный `server_fsm_instance` с `process_name`.

Для MVP таймеры хранятся в отдельной таблице `fsm_timers`. `server_fsm_instances.next_timer_at` не используется как source of truth.

Минимальная схема:

```text
fsm_timers
  id
  service
  entity_type
  entity_id
  process_name
  fire_at
  status = SCHEDULED / FIRED / CANCELLED / FAILED
  payload_json
  idempotency_key
  created_at
  fired_at
  cancelled_at
```

При срабатывании `timer_worker` создаёт `server_fsm_instance`:

```text
service = taxi
process_name = rematch_driver
entity_type = taxi_order
entity_id = order_id
instance_status = PENDING
```

## Taxi MVP decisions

`Trip` сразу выделяется отдельной доменной сущностью и отдельной таблицей `trips`.

Для MVP допускается, что основной lifecycle заказа остаётся в `taxi_order`, а `create_trip` является effect перехода заказа. Отдельный сложный Trip FSM добавляется, когда у поездки появляется самостоятельный lifecycle.

`BOARDING_VERIFICATION` для MVP не выделяется в отдельную сущность.

Посадка моделируется как guard/effect между переходами:

```text
order_driver_arrived -> order_in_ride
guard_name = can_start_ride
effect_name = mark_trip_started
```

`BoardingSession` добавляется позже только при появлении отдельного lifecycle посадки: OTP, retry, dispute, timeout, audit.

`Re-matching` для MVP не является отдельной saga/orchestration.

Он моделируется обычным FSM flow:

```text
NO_DRIVERS_AVAILABLE --event_name=order_rematch_driver--> SEARCHING_DRIVER
```

Запуск делает не worker по знанию taxi state. Доменный effect создаёт timer:

```text
effect_name = schedule_rematch_timer
```

Timer subsystem позже создаёт:

```text
process_name = rematch_driver
```

Точные таймеры taxi для MVP:

```text
VOTE:
  pickupWindowTimeout -> process_name=vote_no_show -> event_name=order_vote_no_show

DIRECT:
  pickup_timeout/no-show не реализуется в MVP.

OFFER:
  pickup_timeout/no-show не реализуется в MVP.
  offer_accept_timeout не реализуется в MVP.
```

Расширение DIRECT/OFFER таймерами после MVP делается через новые `fsm_timers`, `ProcessDef` и `fsm_transitions` без изменения общей архитектуры.

## Worker

Если проектировать worker заново, его роль нужно сузить.

`fsm_worker` должен:

```text
- забрать ready instance;
- поставить PROCESSING/lock;
- открыть DB session/transaction;
- вызвать fsm_core.engine;
- сохранить result;
- commit/rollback;
- закрыть session.
```

Из worker нужно вынести:

```text
- прямые вызовы Core API;
- cleanup-задачи;
- таймерную логику;
- доменные if process_name == ...;
- бизнес-логику taxi/courier.
```

Для нескольких worker-процессов нужны поля:

```text
instance_status = PENDING / PROCESSING / WAITING / COMPLETED / FAILED
locked_at
locked_by
processing_started_at
```

Забирать задачи нужно атомарно: claim -> PROCESSING -> process -> complete/fail.

## Registry

Registry относится к Python Runtime, не к SQL Core.

```text
FSM Platform
├── SQL Core
│   ├── fsm_states
│   ├── fsm_events
│   ├── fsm_transitions
│   ├── fsm_transition_logs
│   └── fsm_perform_transition
│
└── Python Runtime
    ├── engine
    ├── transition_runner
    ├── registry
    ├── timers
    └── process registry
```

Runtime предоставляет механизм регистрации:

```text
register_process
register_guard
register_effect
```

Домены поставляют содержимое:

```text
domains/taxi/processes.py
domains/courier/processes.py
```

Runtime не должен заранее знать имена процессов такси или курьерки.

## Ограничения и риски

Основные риски:

```text
- попытка перенести бизнес-логику в ХП;
- гонки между guard и transition;
- внешние effects внутри DB-транзакции;
- Runtime начинает знать доменную логику;
- строковые имена guard/effect без startup validation;
- таймеры меняют состояние в обход FSM;
- несовместимость со старыми transitions.
```

Как управлять рисками:

```text
- guard выполняется в той же transaction;
- external effects идут через outbox/realtime_events после commit;
- context собирается доменом;
- Runtime содержит только механику;
- старые transitions допускают NULL guard/effect;
- при старте валидировать, что все guard_name/effect_name из БД зарегистрированы.
```

## Итоговая позиция

SQL Core остаётся простым:

```text
проверить transition;
сменить status;
записать log.
```

Python Runtime даёт универсальный pipeline:

```text
context -> guard -> transition -> effect
```

Домены содержат бизнес-смысл:

```text
taxi: водители, поездки, matching, offers;
courier: ячейки, курьеры, постаматы, резервы.
```

Core API, WebSocket, push и железо выполняются не внутри перехода, а через outbox/realtime/timer workers после commit.

Так FSM Platform остаётся универсальной, расширяемой и готовой к мультидоменности.

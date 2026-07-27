# Domain E2E (YAML → API)

Гоняет YAML-сценарии против живого API (`POST /v1/{service_id}/invoke`), ждёт async FSM через poll instance, пишет Markdown-отчёт.

## Layout

```
tools/domain_e2e/
  scenarios/courier/   # YAML сценарии
  reports/             # отчёты (gitignore)
  runner.py, …
```

## Запуск

API и worker должны быть подняты.

```bash
cd C:\FSM_Platform
$env:PYTHONPATH = "C:\FSM_Platform"

python -m tools.domain_e2e.runner scenarios/courier/client_self_pickup.yaml
python -m tools.domain_e2e.runner scenarios/courier/client_deposit_x3_to_direction.yaml
python -m tools.domain_e2e.runner scenarios/courier/driver_loading_x3.yaml
python -m tools.domain_e2e.runner scenarios/courier/driver_cancel_reservation.yaml
python -m tools.domain_e2e.runner scenarios/courier/self_and_courier_to_start_trip.yaml
python -m tools.domain_e2e.runner scenarios/courier/driver_delivery_and_complete_trip.yaml
python -m tools.domain_e2e.runner scenarios/courier/
```

Порядок x3: сначала `client_deposit_x3_to_direction` (заказы на бирже), потом `driver_loading_x3` или `driver_cancel_reservation`.

`self_and_courier_to_start_trip` — автономный happy-path до `start_trip` (и дальше в том же файле — разгрузка/complete, если шаги есть).  
`driver_delivery_and_complete_trip` — отдельно: разгрузка post2 + `complete_trip` при уже `trip_in_progress` (после start_trip; для СПб `driver_id=5`).

Перед прогонами на domain DB: `CALL clear_test_data();` (скрипт `sql/domain/012_clear_test_data.sql`).  
Сразу после — на **platform** DB: `sql/platform/003_clear_test_runtime.sql` (entity_fsm_state + instances).  
Чистить только домен недостаточно: platform хранит свои FSM-состояния по тем же entity_id.

Пути к сценариям и `--report` резолвятся относительно `tools/domain_e2e/` (и CWD).

| Flag | Default | Meaning |
|------|---------|---------|
| `--base-url` | `http://127.0.0.1:8000` | API |
| `--service-id` | _(пусто)_ | override YAML `service_id` (сценарий обязан объявить свой) |
| `--report` | `tools/domain_e2e/reports/e2e_<timestamp>.md` | Markdown |
| `--poll-timeout` | `30` | сек ожидания instance |
| `--poll-interval` | `0.5` | интервал poll |
| `--continue-on-fail` | off | не skip шаги после fail |

Exit code: `0` all green, `1` fail, `2` path/API unavailable.

## Контракт YAML

См. примеры в [`scenarios/courier/`](scenarios/courier/).

**Обязательно:** корневой `service_id` (multi-tenant). Без него сценарий не загрузится.  
`--service-id` в CLI — только **override** YAML, не fallback.

- `{{var}}` — подстановка в params / actor / expect
- `capture` — JSON-path (`data.pin`, `data.directions.0.id`)
- `wait_instance: true` — poll `instance_id` или все `instance_ids` до COMPLETED/FAILED
- `create_order` ставит `enqueues[]` `locker_reserve` на source/dest; дожидайтесь их перед open_cell

**Auth:** при `PLATFORM_AUTH_SECRET` + `PLATFORM_AUTH_DEV_TOKENS=1` клиент сам берёт Bearer на каждого `actor` через `GET /v1/auth/token` (кэш per `service_id|actor`). Формат Markdown-отчёта без изменений.

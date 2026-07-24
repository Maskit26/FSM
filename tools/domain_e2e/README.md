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
python -m tools.domain_e2e.runner scenarios/courier/
```

Порядок x3: сначала `client_deposit_x3_to_direction` (заказы на бирже), потом `driver_loading_x3` или `driver_cancel_reservation`.

`self_and_courier_to_start_trip` — автономный happy-path (self/self + courier/courier) до `start_trip` включительно; на чистой БД после `clear_test_data`.

Перед прогонами на domain DB: `CALL clear_test_data();` (скрипт `sql/domain/012_clear_test_data.sql`).  
Сразу после — на **platform** DB: `sql/platform/003_clear_test_runtime.sql` (entity_fsm_state + instances).  
Чистить только домен недостаточно: platform хранит свои FSM-состояния по тем же entity_id.

Пути к сценариям и `--report` резолвятся относительно `tools/domain_e2e/` (и CWD).

| Flag | Default | Meaning |
|------|---------|---------|
| `--base-url` | `http://127.0.0.1:8000` | API |
| `--service-id` | `svc_courier_01` | если не задан в YAML |
| `--report` | `tools/domain_e2e/reports/e2e_<timestamp>.md` | Markdown |
| `--poll-timeout` | `30` | сек ожидания instance |
| `--poll-interval` | `0.5` | интервал poll |
| `--continue-on-fail` | off | не skip шаги после fail |

Exit code: `0` all green, `1` fail, `2` path/API unavailable.

## Контракт YAML

См. примеры в [`scenarios/courier/`](scenarios/courier/).

- `{{var}}` — подстановка в params / actor / expect
- `capture` — JSON-path (`data.pin`, `data.directions.0.id`)
- `wait_instance: true` — poll `instance_id` или все `instance_ids` до COMPLETED/FAILED
- `create_order` ставит `enqueues[]` `locker_reserve` на source/dest; дожидайтесь их перед open_cell


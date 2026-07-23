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
python -m tools.domain_e2e.runner scenarios/courier/
python -m tools.domain_e2e.runner scenarios/courier/ --report reports/run.md
```

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


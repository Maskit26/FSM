# FSM Platform

Автономная FSM Platform с доменами-картриджами. Норматив: [`fsm-platform-domain-requirements.md`](fsm-platform-domain-requirements.md).

## Структура (greenfield)

| Путь | Назначение |
|------|------------|
| `fsm_platform/core/` | Runtime декларативного FSM (§8; в спецификации — `fsm_core`) |
| `fsm_platform/host/` | Оболочка: engines, worker, side-effects, HTTP |
| `domains/` | Картриджи + `bootstrap.py` |
| `sql/platform/` | DDL platform DB |
| `sql/domain/` | Шаблон FSM-графа для domain DB |
| `main.py` | Entrypoint API (`uvicorn main:app`) |
| `fsm_worker.py` | Entrypoint worker |

Пакет назван `fsm_platform` (snake_case для import), не `FSM_Platform` — иначе конфликт с корнем репозитория и стилем Python.

## Быстрый старт

```bash
# schema
mysql … < sql/platform/001_platform_schema.sql

# env
set PLATFORM_DATABASE_URL=mysql+mysqlconnector://...
set FSM_DOMAINS=svc_demo=domains.demo.processes:register_all

# API
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# worker
python fsm_worker.py
```

## Тесты без БД

```bash
python -m pytest tests/test_fsm_platform_unit.py -q
```

# FSM Platform

Автономная FSM Platform с доменами-картриджами. Норматив: [`fsm-platform-domain-requirements.md`](fsm-platform-domain-requirements.md).

Метафора «приставка»:

| Путь | Роль |
|------|------|
| `input/` | Входящие интерфейсы (Telegram webhook, …) |
| `output/` | Исходящие интерфейсы (Telegram send, …) |
| `fsm_platform/` | Сама приставка (FSM runtime, worker, HTTP Public API) |
| `domains/` | Картриджи |

## Структура

| Путь | Назначение |
|------|------------|
| `fsm_platform/core/` | Runtime декларативного FSM |
| `fsm_platform/host/` | Engines, worker (+ outbox), side-effects, HTTP |
| `input/` | Controllers / adapters → Public API |
| `output/` | Доставка наружу из `platform_outbox` |
| `domains/` | Картриджи + `bootstrap.py` |
| `sql/platform/` | DDL platform DB |
| `sql/domain/` | Миграции / граф domain DB |
| `main.py` | Entrypoint API (`uvicorn main:app`) |
| `fsm_worker.py` | Worker: FSM instances + outbox delivery |

Пакет назван `fsm_platform` (snake_case для import), не `FSM_Platform`.

## Быстрый старт

```bash
# schema (platform DB)
mysql … < database/sql/platform/001_platform_schema.sql
# or additive upgrade on existing DB:
python database/apply_tenant_auth.py

# env
# platform: .env (см. .env.example) — TENANT_AUTH_SECRET, PLATFORM_ADMIN_TOKEN, …
# domain: domains/courier/.env (см. domains/courier/.env.example)
# tenant onboarding: register → login → DOMAIN_ADMIN_TOKEN → domains → secrets → connect

# domain service
uvicorn domains.courier.main:app --host 127.0.0.1 --port 8100

# platform API
uvicorn main:app --host 127.0.0.1 --port 8000

# worker (обычно поднимается через POST /v1/{service_id}/connect)
python fsm_worker.py
```

### Tenant auth (кратко)

1. `POST /v1/auth/register` → verify email → `POST /v1/auth/login`
2. `POST /v1/tenant/admin-tokens` (Bearer access) → raw `DOMAIN_ADMIN_TOKEN`
3. `POST /v1/tenant/domains` + `X-Admin-Token` → `service_id`
4. `PUT /v1/{service_id}/secrets` → `POST /v1/{service_id}/connect`
5. Live check: `python tools/tenant_e2e.py --contract-base-url …` (см. args)

### Telegram-уведомления

1. Фронт (после логина): `GET /input/telegram/{service_id}/link?user_id=<id>` → URL вида  
   `https://t.me/<bot>?start=u{id}_{sig}`
2. `setWebhook` бота → `POST /input/telegram/{service_id}/webhook`.
3. Пользователь открывает ссылку → бот получает `/start` с payload → пишется `telegram_chat_id`.
4. Прогресс заказа: effect → `platform_outbox` → `fsm_worker` → Bot API.
5. Шаблоны: `domains/courier/notifications.py`.  
   Секреты арендатора: `domain_secrets` (`TELEGRAM_BOT_TOKEN`, …).  
   Dev без сети: `TELEGRAM_DRY_RUN=1` (process-wide в platform `.env`).

## Тесты без БД

```bash
python -m unittest tests.test_tenant_auth -v
python -m pytest tests/test_fsm_platform_unit.py -q
```

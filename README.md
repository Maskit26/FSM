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
# schema
mysql … < sql/platform/001_platform_schema.sql

# env
set PLATFORM_DATABASE_URL=mysql+mysqlconnector://...
set FSM_DOMAINS=svc_courier_01=domains.courier.processes:register_all

# API
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# worker (FSM + outbox/Telegram)
python fsm_worker.py
```

### Telegram-уведомления

1. Фронт (после логина): `GET /input/telegram/{service_id}/link?user_id=<id>` → URL вида  
   `https://t.me/<bot>?start=u{id}_{sig}`
2. `setWebhook` бота → `POST /input/telegram/{service_id}/webhook`.
3. Пользователь открывает ссылку → бот получает `/start` с payload → пишется `telegram_chat_id`.
4. Прогресс заказа: effect → `platform_outbox` → `fsm_worker` → Bot API.
5. Шаблоны: `domains/courier/notifications.py`.  
   Секреты: `domain_secrets` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, опц. `TELEGRAM_LINK_SECRET`) или env fallback.  
   Dev без сети: `TELEGRAM_DRY_RUN=1`.

## Тесты без БД

```bash
python -m pytest tests/test_fsm_platform_unit.py -q
```

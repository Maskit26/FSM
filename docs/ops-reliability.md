# Reliability Matrix + DR runbook

Модель: dual-commit (domain → platform) + reconcile, dedicated worker на
`service_id`, outbox. Хостинг ориентир: Clever Cloud / похожий managed MySQL
(малый conn pool, бэкапы провайдера).

Цифры RPO/RTO ниже — **ориентиры под ваш текущий хостинг**, не контракт SLA.

| Обозначение | Смысл |
|-------------|--------|
| RPO | сколько данных можно потерять при restore из backup |
| RTO | за сколько поднять сервис после сбоя |

Типично для Clever MySQL + одно приложение Platform API:
- RPO ≈ интервал бэкапа провайдера (часто часы; уточнять в кабинете Clever);
- RTO API ≈ минуты (редеплой + boot);
- RTO worker ≈ минуты (`POST …/connect` / `…/worker/restart`).

---

## Reliability Matrix

| Сбой | Что теряется / зависает | Автовосстановление | Нужен человек | RPO / RTO (ориентир) |
|------|-------------------------|--------------------|---------------|----------------------|
| Рестарт Platform API | in-flight HTTP | клиент retry + Idempotency-Key на enqueue | обычно нет | RPO≈0; RTO≈1–5 мин |
| Убит / упал dedicated worker | PENDING не claim'ятся; PROCESSING зависает | после restart/provision: reclaim stale PROCESSING → PENDING, очередь догоняется | если worker не поднят снова | RPO≈0; RTO≈1–5 мин после provision |
| Dual-commit: domain ok, platform fail | рассинхрон до доката | reconcile worker | если DEAD / исчерпаны попытки | RPO≈0 при успешном reconcile; иначе ручной разбор |
| Рестарт outbox worker (тот же процесс) | intent в `platform_outbox` | retry / повтор доставки | если внешний API не идемпотентен или DEAD | зависит от внешнего SLA |
| Platform DB недоступна | запись/чтение platform | после восстановления DB | да при потере диска/коррупции | RPO≈backup lag; RTO≈восстановление DB + API |
| Domain service offline | invoke/query/Contract | после подъёма domain + reconnect/bootstrap | да, если упал надолго | RTO≈подъём domain |
| Потеря сайта / restore из backup | всё после точки backup | по DR runbook ниже | да | RPO≈backup; RTO≈часы |

Пороги «очередь протухла» для монитора ЛК: `WORKER_QUEUE_STALE_SECONDS`
(default 20). Reclaim PROCESSING: `WORKER_STALE_PROCESSING_SECONDS` (default 300).

---

## DR runbook — порядок подъёма

1. **Platform DB** — доступна (`SELECT 1`), при restore: дождаться recover MySQL.
2. **Domain DB** (graph + business) — доступна для каждого активного тенанта.
3. **Platform API** — процесс up; `GET /v1/health` → 200; `GET /v1/ready` → 200.
4. **Domain service** — Contract `/health`; затем platform `POST /v1/{service_id}/connect`
   (bootstrap + dedicated worker) или `…/worker/restart` если connect уже был.
5. **Проверки очередей**
   - `GET /v1/metrics` — PENDING / PROCESSING / failed_1h;
   - outbox `dead`, reconcile `dead` — если >0, разбор вручную;
   - `GET /v1/{service_id}/worker/status` — `health=ok`, очередь не stale.
6. **Контрольный вызов** — лёгкий query `invoke` + при необходимости `enqueue` и
   дождаться COMPLETED / события в `/events`.
7. **Tenant ready** — `GET /v1/{service_id}/ready` → 200.

### Если worker убит вручную / OOM

1. `GET …/worker/status` — not running / failed.
2. `POST …/worker/restart` (или `connect`).
3. Убедиться, что stale PROCESSING ушли в PENDING и доехали (метрики / status).
4. Автотест логики: `python -m unittest tests.test_worker_kill_recovery`.

### Если dual-commit застрял

1. Смотреть `platform_reconcile_queue` (pending/dead) в metrics.
2. Worker должен крутить reconcile в том же loop.
3. DEAD → человек: сверить domain vs `entity_fsm_state`, докатить или пометить.

### Restore из backup

1. Восстановить **platform DB** и **domain DB** на согласованную по времени пару
   (иначе рассинхрон FSM vs business).
2. Поднять API → connect/workers по списку active `domain_services`.
3. Не запускать массовый повтор enqueue «на всякий случай» — сначала metrics +
   выборочный invoke.

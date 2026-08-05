# Семантика конфликтов для клиентов (dual-commit)

Для авторов приложений домена и E2E. Код гонки FSM — **`STATE_MISMATCH`**
(не переименовываем).

## Классы ответов

| Класс | Пример | Что делать клиенту |
|-------|--------|-------------------|
| **Conflict / гонка** | `STATE_MISMATCH`, доменный `ALREADY_TAKEN` / «уже занято» | Перечитать карточку (Snapshot) или биржу; **не** долбить тот же take вслепую |
| **Business reject** | `DomainError`, guard reject (`NOT_STAGE_OWNER`, …) | Показать `reason` / `error_code`; обычно **без** auto-retry |
| **Transient** | 5xx, сеть, worker down, `EXTERNAL_API_TRANSIENT` | Retry с тем же `Idempotency-Key` и тем же `correlationId` |
| **Dual-commit в полёте** | domain ок, platform догоняет (reconcile) | **Не** создавать сущность второй раз; поллить `instance` / ждать event |

## Гонка двух курьеров на один заказ

1. Оба видят заказ в `list_courier_exchange`.
2. Оба жмут take → `take_courier_order` / `assign_executor` → FSM.
3. Победителя решает guard/effect/CAS на бэке:
   - первый — успех;
   - второй — `ALREADY_TAKEN` или `STATE_MISMATCH` (или аналог в DomainError).
4. UI после ответа / refresh списка показывает факт.

## HTTP-коды (ориентир)

| Ситуация | Типичный HTTP |
|----------|----------------|
| DomainError / business | 409 + `error_code` |
| FSM `STATE_MISMATCH` на worker | instance `FAILED`, event `fsm.instance.failed` |
| Auth | 401 / 403 |
| Domain not ready | 503 |
| Transient upstream | 502 / 5xx; клиент retry с idempotency |

## Dual-commit

Invoke command уже закоммитил domain, platform commit упал → reconcile.
Клиент, получивший успех domain-операции (или `pending_fsm`), при повторе
с тем же idempotency/correlation **не** создаёт дубликат сущности.

См. также: `docs/domain-app-realtime.md`, `docs/ops-reliability.md`.

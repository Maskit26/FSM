# Adapter checklist — внешние интеграции

Для каждой интеграции через `call_api` / outbox `http_external`
(не новый framework). Заполняй при подключении вендора.

## Чеклист

| # | Пункт | Что зафиксировать |
|---|--------|-------------------|
| 1 | **timeout** | Явный `timeout=` в `call_api` (сек). Default платформы: `EXTERNAL_API_TIMEOUT` (15). |
| 2 | **retry / backoff** | Кто ретраит: локально `max_attempts` в `call_api`, FSM (`EXTERNAL_API_TRANSIENT`), outbox (`OUTBOX_MAX_ATTEMPTS`). Не дублировать слепые ретраи на всех слоях. |
| 3 | **idempotency** | Ключ повтора: `idempotency_key=` → header `Idempotency-Key` (и/или поле вендора). Семантика: повтор того же ключа = тот же эффект. |
| 4 | **mapping ошибок** | HTTP/vendor → доменный код / `ExternalApiError` (`transient=True` только для 408/429/5xx/сеть). |
| 5 | **authentication** | Credential JSON в `domain_secrets` (`type`, `base_url`, …). Ключ = `credential_key`. |
| 6 | **correlation** | Цепочка из §2.4: `call_api` сам прокидывает `X-Correlation-Id` / `X-Command-Id` / `X-Causation-Id` из envelope. Не затирай их. |
| 7 | **недоступность** | Sync effect: fail → FSM retry/FAILED. Долгий/после commit: `notify[]` + `channel=http_external` → outbox → domain `/outbox/deliver`. |

## Runtime (платформа)

- `call_api(..., timeout=, idempotency_key=, max_attempts=)` — обязательный контракт вызова.
- Голый `requests` / `httpx` в обход `call_api` / outbox **не** использовать для vendor HTTP.
- Outbox `http_external`: payload сохраняет `correlation`; `destination` обычно = credential_key.

## Пример sync

```python
side_effects.call_api(
    "PARTNER_API",
    "POST",
    "/v1/orders",
    json_body={...},
    timeout=10.0,
    idempotency_key=f"partner:create:{order_id}",
)
```

## Пример async (после FSM commit)

```json
{
  "channel": "http_external",
  "destination": "PARTNER_API",
  "event_type": "partner.create_order",
  "payload": { "op": "create_order", "order_id": 1 }
}
```

Domain `outbox_handler` → снова `call_api` с тем же credential и timeout/idempotency.

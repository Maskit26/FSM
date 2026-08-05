# Realtime / reconnect для приложений домена

Для авторов мобильных/web-приложений домена (клиент, курьер, водитель).
Платформу как продукт end-user не видит — только API своего приложения.

---

## Два режима подписки (WS `/v1/{service_id}/ws/events`)

### 1. Карточка одной сущности

После обрыва связи:

1. Снова открыть WS (лучше с `after_id` = последний виденный `event.id`).
2. `subscribe` с `entity_type` + `entity_id` + actor (или end-user Bearer).
3. Сразу придёт Snapshot сущности.
4. Дальше — events только по этой сущности; при событии Snapshot обновляется.

Не нужно «додумывать» состояние на клиенте из старых events без Snapshot.

### 2. Биржа / списки (`list_courier_exchange`, «мои заказы»…)

Entity Snapshot здесь не используется.

После обрыва:

1. Снова открыть WS.
2. Тот же `subscribe` на operation (или обычный HTTP query).
3. Список перечитать целиком из ответа бэка.

Live-биржа: при каждом новом event платформа уже перезапрашивает подписанную
operation. Число заказов на экране — из свежего ответа, не «минус один» на фронте.

### Гонка двух курьеров на один заказ

Оба видят заказ в бирже → оба жмут «взять». Победителя решает command/guard на
бэке: один успех, второй отказ. UI после ответа (или после refresh списка)
просто показывает факт. Не угадывать победителя на клиенте.

---

## Auth для приложений end-user (без `DOMAIN_ADMIN_TOKEN`)

`DOMAIN_ADMIN_TOKEN` — только у бэкенда арендатора и ЛК (secrets, connect, worker…).

В приложение курьера/клиента его **не кладут**.

Рабочая схема:

1. Юзер логинится в домен (`login_user` и т.п.) через бэкенд арендатора или
   через Domain API с admin-токеном на стороне сервера.
2. Бэкенд арендатора (с `X-Admin-Token`) выпускает end-user токен:

   `POST /v1/{service_id}/end-user-tokens`  
   body: `{ "actor_type", "actor_id", "roles?", "ttl_seconds?" }`

3. Приложение ходит в Domain API так:

   `Authorization: Bearer eut1.…`  
   **без** `X-Admin-Token`.

Этим токеном можно: invoke, enqueue, status, snapshot, actions, history,
events, WS, catalog.

Нельзя: secrets, connect/reload, worker, graph/publish, webhooks/schedules,
выпуск новых end-user токенов.

Подпись токена — per-tenant секрет `end_user_token_secret` в `domain_secrets`
этого `service_id` (при первом выпуске создаётся сам). В platform `.env`
отдельного end-user секрета нет.

Альтернатива: BFF арендатора сам проксирует все вызовы с admin-токеном и
подставляет actor — приложение тогда вообще не знает про Platform API.
End-user токен — для случая, когда приложение ходит на платформу напрямую.

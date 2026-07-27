"""Публичный HTTP API платформы: /v1/{service_id}/…"""

from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from fsm_platform.host.auth import AuthError, auth_enabled, make_token, resolve_actor
from fsm_platform.host.boot import boot
from fsm_platform.host.http import request_runtime
from fsm_platform.host.http.events_ws import router as events_ws_router
from fsm_platform.host.operations import default_operation_registry
from fsm_platform.core.domain_errors import DomainError
from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.core.registry import default_process_registry
from fsm_platform.host.engines import domain_session, platform_session
from fsm_platform.host.graph_version import publish_graph_version

app = FastAPI(title="FSM Platform", version="0.1.0")
app.include_router(events_ws_router)


class Actor(BaseModel):
    """Кто вызвал API: тип, id и канал (api/mobile и т.п.)."""

    actor_type: str = "user"
    actor_id: Optional[str] = None
    channel: str = "api"


class InvokeBody(BaseModel):
    """Тело POST .../invoke: имя операции, params и actor."""

    operation: str
    params: dict[str, Any] = Field(default_factory=dict)
    actor: Optional[Actor] = None


class EnqueueBody(BaseModel):
    """Тело POST .../fsm/enqueue: какой процесс запустить для сущности."""

    process_name: str
    entity_type: str
    entity_id: int
    payload: dict[str, Any] = Field(default_factory=dict)
    actor: Optional[Actor] = None
    mode: str = "async"


def _http_actor(
    authorization: Optional[str],
    body_actor: Optional[Actor],
) -> dict[str, Any]:
    try:
        return resolve_actor(
            authorization=authorization,
            body_actor=body_actor.model_dump() if body_actor else None,
        )
    except AuthError as exc:
        code = 401 if exc.code in ("AUTH_REQUIRED", "AUTH_INVALID") else 400
        raise HTTPException(
            code, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc


@app.on_event("startup")
def _startup() -> None:
    """При старте API поднимает engines и регистрирует домены."""
    boot()


@app.get("/v1/health")
def health() -> dict[str, str]:
    """Проверка живости сервиса. Нужна для мониторинга и smoke."""
    return {"status": "ok"}


@app.get("/v1/auth/token")
def auth_token(
    actor_id: str,
    actor_type: str = "user",
) -> dict[str, Any]:
    """
    Dev-хелпер: выдаёт Bearer для локалки.
    Только если PLATFORM_AUTH_SECRET задан и PLATFORM_AUTH_DEV_TOKENS=1.
    """
    if not auth_enabled():
        raise HTTPException(400, detail="PLATFORM_AUTH_SECRET not set")
    if str(os.environ.get("PLATFORM_AUTH_DEV_TOKENS") or "").strip() not in (
        "1",
        "true",
        "yes",
    ):
        raise HTTPException(403, detail="PLATFORM_AUTH_DEV_TOKENS disabled")
    try:
        token = make_token(actor_type=actor_type, actor_id=actor_id)
    except AuthError as exc:
        raise HTTPException(400, detail=exc.code) from exc
    return {
        "authorization": f"Bearer {token}",
        "actor_type": actor_type,
        "actor_id": actor_id,
    }


@app.get("/v1/metrics")
def metrics() -> dict[str, Any]:
    """
    Снимок очередей platform: instances / outbox / reconcile / timers.
    Для алертов: pending lag, failed_1h, outbox.dead, reconcile.dead.
    """
    from fsm_platform.host.metrics import collect_platform_metrics

    try:
        return {"status": "ok", **collect_platform_metrics()}
    except Exception as exc:
        raise HTTPException(503, detail=f"METRICS_UNAVAILABLE: {exc}") from exc


@app.get("/v1/{service_id}/catalog")
def catalog(service_id: str) -> dict[str, Any]:
    """Каталог операций и процессов домена. Удобно смотреть, что доступно в Swagger."""
    ops = default_operation_registry.list(service_id)
    processes = default_process_registry.list_process_names(service_id)
    return {"service_id": service_id, "operations": ops, "processes": processes}


@app.post("/v1/{service_id}/invoke")
def invoke(
    service_id: str,
    body: InvokeBody,
    authorization: Optional[str] = Header(default=None),
) -> dict[str, Any]:
    """
    Синхронный вызов Command/Query домена.
    Ошибки домена отдаёт как 409 с error_code.
    """
    actor = _http_actor(authorization, body.actor)
    meta = default_operation_registry.get(service_id, body.operation)
    if meta is None:
        raise HTTPException(404, detail=f"UNKNOWN_OPERATION: {body.operation}")
    try:
        result = request_runtime.run_operation(
            service_id,
            meta["handler"],
            meta["kind"],
            body.params,
            actor,
        )
    except DomainError as exc:
        raise HTTPException(
            409,
            detail={"error_code": exc.code, "message": exc.message},
        ) from exc
    except KeyError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc

    return {
        "operation": body.operation,
        "data": result.get("data", result),
        "entity_type": result.get("entity_type"),
        "entity_id": result.get("entity_id"),
        "instance_id": result.get("instance_id"),
        "instance_ids": result.get("instance_ids"),
        "saga_id": result.get("saga_id"),
    }


@app.post("/v1/{service_id}/fsm/enqueue", status_code=202)
def enqueue(
    service_id: str,
    body: EnqueueBody,
    authorization: Optional[str] = Header(default=None),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """
    Ставит FSM-процесс в очередь для существующей сущности.
    Worker потом заберёт PENDING-инстанс и прогонит переход.
    """
    actor = _http_actor(authorization, body.actor)
    if not default_process_registry.has(service_id, body.process_name):
        raise HTTPException(400, detail=f"UNKNOWN_PROCESS: {body.process_name}")
    try:
        uid = int(actor["actor_id"]) if actor.get("actor_id") else None
        return request_runtime.enqueue_instance(
            service_id,
            process_name=body.process_name,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            payload=body.payload,
            actor_id=uid,
            idempotency_key=idempotency_key,
        )
    except LookupError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@app.get("/v1/{service_id}/fsm/instances/{instance_id}")
def instance_status(service_id: str, instance_id: int) -> dict[str, Any]:
    """Статус одного FSM-инстанса и текущее состояние сущности."""
    row = request_runtime.get_instance(service_id, instance_id)
    if row is None:
        raise HTTPException(404, detail="INSTANCE_NOT_FOUND")
    for k, v in list(row.items()):
        if hasattr(v, "isoformat"):
            row[k] = v.isoformat()
    return row


class ActionsBody(BaseModel):
    """Тело POST .../entities/.../actions: actor + опциональный payload для guards."""

    actor: Optional[Actor] = None
    payload: dict[str, Any] = Field(default_factory=dict)


@app.post("/v1/{service_id}/entities/{entity_type}/{entity_id}/actions")
def entity_actions(
    service_id: str,
    entity_type: str,
    entity_id: int,
    body: ActionsBody,
    authorization: Optional[str] = Header(default=None),
) -> dict[str, Any]:
    """
    Available actions: исходящие переходы + read-only прогон guards.
    Фронт рисует кнопки по allowed/reason, без дублирования правил.
    """
    actor = _http_actor(authorization, body.actor)
    try:
        return request_runtime.list_available_actions(
            service_id,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            payload=body.payload,
        )
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc


@app.get("/v1/{service_id}/entities/{entity_type}/{entity_id}/history")
def entity_history(
    service_id: str,
    entity_type: str,
    entity_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
) -> dict[str, Any]:
    """Таймлайн сущности из fsm_transition_logs (поддержка / аудит)."""
    return request_runtime.list_entity_history(
        service_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        before_id=before_id,
    )


@app.get("/v1/{service_id}/events")
def list_events(
    service_id: str,
    after_id: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    """Cursor-poll platform_events (id > after_id)."""
    return request_runtime.list_platform_events(
        service_id, after_id=after_id, limit=limit
    )


class WebhookBody(BaseModel):
    url: str
    secret: str
    event_types: Optional[list[str]] = None
    active: bool = True


@app.post("/v1/{service_id}/webhooks")
def create_webhook(service_id: str, body: WebhookBody) -> dict[str, Any]:
    """Регистрация outbound webhook (HMAC secret)."""
    url = (body.url or "").strip()
    secret = (body.secret or "").strip()
    if not url or not secret:
        raise HTTPException(400, detail="url and secret required")
    sp = platform_session()
    try:
        wid = default_db_layer.insert_webhook_subscription(
            sp,
            service_id=service_id,
            url=url,
            secret=secret,
            event_types=body.event_types,
            active=body.active,
        )
        sp.commit()
        return {
            "id": wid,
            "service_id": service_id,
            "url": url,
            "event_types": body.event_types,
            "active": body.active,
        }
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@app.get("/v1/{service_id}/webhooks")
def list_webhooks(service_id: str) -> dict[str, Any]:
    """Список webhook_subscriptions (secret не отдаём)."""
    sp = platform_session()
    try:
        rows = default_db_layer.list_webhook_subscriptions(
            sp, service_id=service_id, active_only=False
        )
        safe = []
        for r in rows:
            safe.append(
                {
                    "id": r["id"],
                    "service_id": r["service_id"],
                    "url": r["url"],
                    "event_types": r.get("event_types"),
                    "active": bool(r.get("active")),
                    "created_at": (
                        r["created_at"].isoformat()
                        if hasattr(r.get("created_at"), "isoformat")
                        else r.get("created_at")
                    ),
                }
            )
        return {"service_id": service_id, "webhooks": safe}
    finally:
        sp.close()


@app.post("/v1/{service_id}/webhooks/{subscription_id}/deactivate")
def deactivate_webhook(service_id: str, subscription_id: int) -> dict[str, Any]:
    sp = platform_session()
    try:
        ok = default_db_layer.set_webhook_subscription_active(
            sp,
            service_id=service_id,
            subscription_id=subscription_id,
            active=False,
        )
        if not ok:
            raise HTTPException(404, detail="WEBHOOK_NOT_FOUND")
        sp.commit()
        return {"id": subscription_id, "active": False}
    except HTTPException:
        sp.rollback()
        raise
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


class ScheduleBody(BaseModel):
    process_name: str
    interval_seconds: int
    entity_type: str = "schedule"
    entity_id: Optional[int] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    initial_state: str = "idle"


@app.post("/v1/{service_id}/schedules")
def create_schedule(service_id: str, body: ScheduleBody) -> dict[str, Any]:
    """
    Периодический процесс: каждые interval_seconds → enqueue process_name.
    Создаёт entity_fsm_state(schedule/{id}, idle) если entity_id не задан.
    """
    if body.interval_seconds < 1:
        raise HTTPException(400, detail="interval_seconds must be >= 1")
    if not default_process_registry.has(service_id, body.process_name):
        raise HTTPException(400, detail=f"UNKNOWN_PROCESS: {body.process_name}")
    sp = platform_session()
    try:
        # сначала schedule с entity_id=0, потом обновим на id если нужно
        sid = default_db_layer.insert_schedule(
            sp,
            service_id=service_id,
            process_name=body.process_name,
            interval_seconds=body.interval_seconds,
            entity_type=body.entity_type,
            entity_id=int(body.entity_id) if body.entity_id is not None else 0,
            payload=body.payload,
        )
        eid = int(body.entity_id) if body.entity_id is not None else sid
        if body.entity_id is None:
            # перезапишем entity_id = schedule id
            from sqlalchemy import text

            sp.execute(
                text(
                    """
                    UPDATE fsm_schedules
                    SET entity_id = :eid
                    WHERE id = :id
                    """
                ),
                {"eid": eid, "id": sid},
            )
        if default_db_layer.get_entity_state(
            sp, service_id, body.entity_type, eid
        ) is None:
            default_db_layer.insert_entity_state_initial(
                sp,
                service_id,
                body.entity_type,
                eid,
                str(body.initial_state or "idle"),
            )
        sp.commit()
        return {
            "id": sid,
            "service_id": service_id,
            "process_name": body.process_name,
            "interval_seconds": body.interval_seconds,
            "entity_type": body.entity_type,
            "entity_id": eid,
            "status": "ACTIVE",
        }
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@app.get("/v1/{service_id}/schedules")
def list_schedules(service_id: str) -> dict[str, Any]:
    sp = platform_session()
    try:
        rows = default_db_layer.list_schedules(sp, service_id=service_id)
        for r in rows:
            for k, v in list(r.items()):
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
        return {"service_id": service_id, "schedules": rows}
    finally:
        sp.close()


@app.post("/v1/{service_id}/schedules/{schedule_id}/pause")
def pause_schedule(service_id: str, schedule_id: int) -> dict[str, Any]:
    sp = platform_session()
    try:
        ok = default_db_layer.set_schedule_status(
            sp, service_id=service_id, schedule_id=schedule_id, status="PAUSED"
        )
        if not ok:
            raise HTTPException(404, detail="SCHEDULE_NOT_FOUND")
        sp.commit()
        return {"id": schedule_id, "status": "PAUSED"}
    except HTTPException:
        sp.rollback()
        raise
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@app.post("/v1/{service_id}/schedules/{schedule_id}/resume")
def resume_schedule(service_id: str, schedule_id: int) -> dict[str, Any]:
    sp = platform_session()
    try:
        ok = default_db_layer.set_schedule_status(
            sp, service_id=service_id, schedule_id=schedule_id, status="ACTIVE"
        )
        if not ok:
            raise HTTPException(404, detail="SCHEDULE_NOT_FOUND")
        sp.commit()
        return {"id": schedule_id, "status": "ACTIVE"}
    except HTTPException:
        sp.rollback()
        raise
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


@app.post("/v1/{service_id}/graph/publish")
def graph_publish(service_id: str) -> dict[str, Any]:
    """
    Копирует transitions current→current+1 и поднимает fsm_graph_meta.
    Летящие инстансы остаются на старой версии; новые берут новую.
    """
    sd = domain_session(service_id)
    try:
        nxt = publish_graph_version(sd)
        sd.commit()
        return {"service_id": service_id, "current_version": nxt}
    except Exception as exc:
        sd.rollback()
        raise HTTPException(400, detail=str(exc)) from exc
    finally:
        sd.close()


class SecretBody(BaseModel):
    key: str
    value: str


def _admin_or_raise(x_admin_token: Optional[str]) -> None:
    from fsm_platform.host.secrets import SecretsError, require_admin

    try:
        require_admin(x_admin_token)
    except SecretsError as exc:
        code = 403 if exc.code == "ADMIN_FORBIDDEN" else 503
        raise HTTPException(
            code, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc


@app.put("/v1/{service_id}/secrets")
def upsert_secret(
    service_id: str,
    body: SecretBody,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> dict[str, Any]:
    """
    Admin: upsert per-tenant secret (value хранится зашифрованным).
    Header: X-Admin-Token: <PLATFORM_ADMIN_TOKEN>
    """
    from fsm_platform.host.runtime_context import service_scope
    from fsm_platform.host.secrets import SecretsError, set_domain_secret

    _admin_or_raise(x_admin_token)
    try:
        with service_scope(service_id):
            set_domain_secret(body.key, body.value)
    except SecretsError as exc:
        raise HTTPException(
            400, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc
    return {"service_id": service_id, "key": body.key.strip(), "ok": True}


@app.get("/v1/{service_id}/secrets")
def list_secrets(
    service_id: str,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> dict[str, Any]:
    """Admin: список имён ключей (значения не отдаём)."""
    from fsm_platform.host.runtime_context import service_scope
    from fsm_platform.host.secrets import SecretsError, list_domain_secret_keys

    _admin_or_raise(x_admin_token)
    try:
        with service_scope(service_id):
            keys = list_domain_secret_keys()
    except SecretsError as exc:
        raise HTTPException(
            400, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc
    return {"service_id": service_id, "keys": keys}


@app.delete("/v1/{service_id}/secrets/{key}")
def delete_secret(
    service_id: str,
    key: str,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
) -> dict[str, Any]:
    """Admin: удалить секрет по имени ключа."""
    from fsm_platform.host.runtime_context import service_scope
    from fsm_platform.host.secrets import SecretsError, delete_domain_secret

    _admin_or_raise(x_admin_token)
    try:
        with service_scope(service_id):
            ok = delete_domain_secret(key)
    except SecretsError as exc:
        raise HTTPException(
            400, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc
    if not ok:
        raise HTTPException(404, detail="SECRET_NOT_FOUND")
    return {"service_id": service_id, "key": key, "deleted": True}


@app.post("/input/telegram/webhook")
def telegram_webhook(update: dict[str, Any]) -> dict[str, Any]:
    """
    Входящий Telegram Update (Bot webhook).
    /start u{user_id}_{sig} → users.telegram_chat_id.
    """
    from input.telegram.webhook import handle_telegram_update

    return handle_telegram_update(update)


@app.get("/input/telegram/link")
def telegram_link(user_id: int) -> dict[str, Any]:
    """
    Deep-link для фронта: пользователь открывает URL → /start в боте → bind chat_id.
    Нужны TELEGRAM_BOT_USERNAME и TELEGRAM_BOT_TOKEN (или TELEGRAM_LINK_SECRET).
    """
    from input.telegram.webhook import build_bot_start_url, make_start_payload

    try:
        url = build_bot_start_url(user_id)
        return {
            "user_id": user_id,
            "url": url,
            "payload": make_start_payload(user_id),
        }
    except RuntimeError as exc:
        raise HTTPException(400, detail=str(exc)) from exc

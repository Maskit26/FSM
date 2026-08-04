"""Публичный HTTP API платформы: /v1/{service_id}/…"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from fsm_platform.host.security.auth import AuthError, resolve_actor
from fsm_platform.host.http.auth_routes import router as auth_router
from fsm_platform.host.http.dependencies import (
    require_domain_service_access,
    require_platform_admin,
)
from fsm_platform.host.http.external_routes import router as external_router
from fsm_platform.host.tenant.domain_bootstrap import get_bootstrap_status, is_domain_ready
from fsm_platform.host.http import request_runtime
from fsm_platform.host.http.events_ws import router as events_ws_router
from fsm_platform.host.http.tenant_routes import router as tenant_router
from fsm_platform.host.tenant.hook_registry import (
    HookError,
    default_webhook_registry,
)
from fsm_platform.host.tenant.operations import default_operation_registry
from fsm_platform.core.domain_errors import DomainError
from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.core.registry import default_process_registry
from fsm_platform.host.runtime.engines import graph_write_session, platform_session
from fsm_platform.host.runtime.graph_version import publish_graph_version

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FSM Platform",
    version="0.2.0",
    openapi_tags=[
        {"name": "Public Auth", "description": "Tenant registration and sessions"},
        {"name": "Tenant Account", "description": "Tokens and domain registration"},
        {"name": "Platform Admin", "description": "Platform-wide operator API"},
        {"name": "Domain API", "description": "DOMAIN_ADMIN_TOKEN protected API"},
        {
            "name": "Domain Runtime",
            "description": "HMAC Contract reverse calls from domain process",
        },
        {"name": "Domain Input", "description": "Signed external integrations"},
    ],
)

_cors_origins = [
    o.strip()
    for o in str(
        os.environ.get("CORS_ORIGINS")
        or "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/debug/ok")
def debug_ok() -> dict[str, str]:
    """Локальная проверка, что процесс отвечает без DB."""
    return {"status": "ok", "v": "2"}


@app.get("/debug/pool")
def debug_pool() -> dict[str, Any]:
    """Снимок SQLAlchemy pool platform DB (без секретов)."""
    from fsm_platform.host.runtime.engines import get_platform_engine
    from sqlalchemy import text

    engine = get_platform_engine()
    pool = engine.pool
    info: dict[str, Any] = {
        "pool_class": type(pool).__name__,
        "status": pool.status() if hasattr(pool, "status") else None,
    }
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        info["select1"] = "ok"
    except Exception as exc:
        info["select1"] = f"{type(exc).__name__}: {exc}"[:300]
    return info


platform_router = APIRouter(
    tags=["Platform Admin"], dependencies=[Depends(require_platform_admin)]
)
domain_router = APIRouter(
    prefix="/v1/{service_id}",
    tags=["Domain API"],
    dependencies=[Depends(require_domain_service_access)],
)
input_router = APIRouter(tags=["Domain Input"])


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
    """Engines + best-effort domain bootstrap (не блокирует API при offline domain)."""
    from fsm_platform.host.tenant.boot import boot

    boot()


@platform_router.get("/v1/health")
def health() -> dict[str, Any]:
    """Живость platform API. Domain service может быть offline — это не ошибка health."""
    return {"status": "ok", "domains": get_bootstrap_status()}


@platform_router.get("/v1/metrics")
def metrics() -> dict[str, Any]:
    """
    Снимок очередей platform: instances / outbox / reconcile / timers.
    Для алертов: pending lag, failed_1h, outbox.dead, reconcile.dead.
    """
    from fsm_platform.host.runtime.metrics import collect_platform_metrics

    try:
        return {"status": "ok", **collect_platform_metrics()}
    except Exception as exc:
        raise HTTPException(503, detail=f"METRICS_UNAVAILABLE: {exc}") from exc


@domain_router.get("/catalog")
def catalog(service_id: str) -> dict[str, Any]:
    """Каталог операций, процессов и inbound hook channels домена."""
    domain_status = get_bootstrap_status(service_id)
    ops = default_operation_registry.list(service_id)
    processes = default_process_registry.list_process_names(service_id)
    hooks = default_webhook_registry.list_channels(service_id)
    return {
        "service_id": service_id,
        "domain_ready": is_domain_ready(service_id),
        "domain_bootstrap": domain_status,
        "operations": ops,
        "processes": processes,
        "hooks": hooks,
    }


@domain_router.post("/invoke")
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
        raise HTTPException(
            404,
            detail={
                "error_code": "UNKNOWN_OPERATION",
                "message": f"operation {body.operation!r} not registered",
                "domain_ready": is_domain_ready(service_id),
            },
        )
    if not is_domain_ready(service_id):
        raise HTTPException(
            503,
            detail={
                "error_code": "DOMAIN_NOT_READY",
                "message": "domain service catalog not loaded; tenant offline or misconfigured",
                "domain_bootstrap": get_bootstrap_status(service_id),
            },
        )
    try:
        result = request_runtime.run_operation(
            service_id,
            body.operation,
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


@domain_router.post("/fsm/enqueue", status_code=202)
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


@domain_router.get("/fsm/instances/{instance_id}")
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


@domain_router.post("/entities/{entity_type}/{entity_id}/actions")
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


class SnapshotBody(BaseModel):
    """Тело POST .../entities/.../snapshot: actor (+ опц. params)."""

    actor: Optional[Actor] = None
    params: dict[str, Any] = Field(default_factory=dict)
    include_actions: bool = True


@domain_router.post("/entities/{entity_type}/{entity_id}/snapshot")
def entity_snapshot(
    service_id: str,
    entity_type: str,
    entity_id: int,
    body: SnapshotBody,
    authorization: Optional[str] = Header(default=None),
) -> dict[str, Any]:
    """
    Entity Snapshot для фронта домена: Principal → access policy → snapshot.
    Admin-токен открывает Domain API; end-user identity — actor / Bearer.
    """
    from fsm_platform.host.security.auth import AuthError

    try:
        actor = _http_actor(authorization, body.actor)
    except AuthError as exc:
        raise HTTPException(401, detail={"error_code": exc.code, "message": str(exc)}) from exc
    try:
        return request_runtime.get_entity_snapshot(
            service_id,
            entity_type=entity_type,
            entity_id=entity_id,
            actor=actor,
            params=body.params,
            include_actions=bool(body.include_actions),
        )
    except request_runtime.EntityAccessDenied as exc:
        raise HTTPException(
            403,
            detail={"error_code": "FORBIDDEN", "message": exc.reason},
        ) from exc
    except request_runtime.EntityCapabilityMissing as exc:
        raise HTTPException(
            501,
            detail={"error_code": exc.code, "message": exc.message},
        ) from exc
    except AuthError as exc:
        raise HTTPException(401, detail={"error_code": exc.code, "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc


@domain_router.get("/entities/{entity_type}/{entity_id}/history")
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


@domain_router.get("/events")
def list_events(
    service_id: str,
    after_id: int = 0,
    limit: int = 100,
    newest: bool = False,
) -> dict[str, Any]:
    """Cursor-poll platform_events (id > after_id) или последние N при newest=true."""
    return request_runtime.list_platform_events(
        service_id, after_id=after_id, limit=limit, newest=newest
    )


class WebhookBody(BaseModel):
    url: str
    secret: str
    event_types: Optional[list[str]] = None
    active: bool = True


@domain_router.post("/webhooks")
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


@domain_router.get("/webhooks")
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


@domain_router.post("/webhooks/{subscription_id}/deactivate")
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


@domain_router.post("/schedules")
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


@domain_router.get("/schedules")
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


@domain_router.post("/schedules/{schedule_id}/pause")
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


@domain_router.post("/schedules/{schedule_id}/resume")
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


@domain_router.post("/graph/publish")
def graph_publish(service_id: str) -> dict[str, Any]:
    """
    Копирует transitions current→current+1 и поднимает fsm_graph_meta.
    Летящие инстансы остаются на старой версии; новые берут новую.
    """
    sd = graph_write_session(service_id)
    try:
        nxt = publish_graph_version(sd)
        sd.commit()
        return {"service_id": service_id, "current_version": nxt}
    except Exception as exc:
        sd.rollback()
        raise HTTPException(400, detail=str(exc)) from exc
    finally:
        sd.close()


@domain_router.post("/connect")
def connect_domain(service_id: str) -> dict[str, Any]:
    """Validate/bootstrap the configured domain and start its dedicated worker."""
    from fsm_platform.host.tenant.boot import configure_graph_engines
    from fsm_platform.host.tenant.domain_bootstrap import reload_domain
    from fsm_platform.host.tenant.domain_validator import DomainValidationError
    from fsm_platform.host.workers.worker_provisioner import provision_worker

    try:
        configure_graph_engines(service_id)
        bootstrap = reload_domain(service_id)
    except DomainValidationError as exc:
        sp = platform_session()
        try:
            default_db_layer.set_domain_service_status(
                sp,
                service_id=service_id,
                status="validation_failed",
                validation_report=json.dumps(exc.report.to_dict(), ensure_ascii=False),
            )
            sp.commit()
        finally:
            sp.close()
        raise HTTPException(
            422,
            detail={
                "error_code": "DOMAIN_VALIDATION_FAILED",
                "report": exc.report.to_dict(),
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            502,
            detail={
                "error_code": "DOMAIN_CONNECT_FAILED",
                "message": str(exc),
            },
        ) from exc

    sp = platform_session()
    try:
        default_db_layer.set_domain_service_status(
            sp,
            service_id=service_id,
            status="active",
            validation_report=json.dumps(bootstrap, ensure_ascii=False),
        )
        sp.commit()
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()
    try:
        worker = provision_worker(service_id)
    except Exception as exc:
        sp = platform_session()
        try:
            default_db_layer.set_domain_service_status(
                sp,
                service_id=service_id,
                status="worker_failed",
                validation_report=json.dumps(
                    {"bootstrap": bootstrap, "worker_error": str(exc)},
                    ensure_ascii=False,
                ),
            )
            sp.commit()
        finally:
            sp.close()
        raise HTTPException(
            502,
            detail={
                "error_code": "WORKER_PROVISION_FAILED",
                "message": str(exc),
            },
        ) from exc
    return {"service_id": service_id, "status": "active", "bootstrap": bootstrap, "worker": worker}


@domain_router.post("/reload")
def reload_tenant_domain(service_id: str) -> dict[str, Any]:
    """Reload catalog and validator state for one owned domain."""
    from fsm_platform.host.tenant.domain_bootstrap import reload_domain
    from fsm_platform.host.tenant.domain_validator import DomainValidationError

    try:
        return reload_domain(service_id)
    except DomainValidationError as exc:
        raise HTTPException(
            502,
            detail={
                "error_code": "DOMAIN_BOOTSTRAP_FAILED",
                "message": str(exc),
                "report": exc.report.to_dict(),
                "domain_bootstrap": get_bootstrap_status(service_id),
            },
        ) from exc


@domain_router.get("/worker/status")
def tenant_worker_status(service_id: str) -> dict[str, Any]:
    from fsm_platform.host.runtime.metrics import enrich_worker_status
    from fsm_platform.host.workers.worker_provisioner import worker_status

    return enrich_worker_status(service_id, worker_status(service_id))


@domain_router.post("/worker/restart")
def tenant_worker_restart(service_id: str) -> dict[str, Any]:
    from fsm_platform.host.workers.worker_provisioner import restart_worker

    try:
        return restart_worker(service_id)
    except Exception as exc:
        raise HTTPException(
            502,
            detail={"error_code": "WORKER_RESTART_FAILED", "message": str(exc)},
        ) from exc


@domain_router.post("/worker/stop")
def tenant_worker_stop(service_id: str) -> dict[str, Any]:
    from fsm_platform.host.workers.worker_provisioner import stop_worker

    return stop_worker(service_id)


class SecretBody(BaseModel):
    """Admin upsert: value — строка или JSON-объект (объект сериализуется в строку)."""

    key: str
    value: str

    @field_validator("value", mode="before")
    @classmethod
    def _coerce_value_to_str(cls, v: Any) -> str:
        if isinstance(v, str):
            return v
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
        if v is None:
            return ""
        return str(v)


@domain_router.put("/secrets")
def upsert_secret(
    service_id: str,
    body: SecretBody,
) -> dict[str, Any]:
    """
    Admin: upsert per-tenant secret (value хранится зашифрованным).
    Header: X-Admin-Token: <DOMAIN_ADMIN_TOKEN>
    """
    from fsm_platform.host.runtime.runtime_context import service_scope
    from fsm_platform.host.security.secrets import SecretsError, set_domain_secret

    try:
        with service_scope(service_id):
            set_domain_secret(body.key, body.value)
    except SecretsError as exc:
        raise HTTPException(
            400, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc
    return {"service_id": service_id, "key": body.key.strip(), "ok": True}


@domain_router.get("/secrets")
def list_secrets(service_id: str) -> dict[str, Any]:
    """Admin: список имён ключей (значения не отдаём)."""
    from fsm_platform.host.runtime.runtime_context import service_scope
    from fsm_platform.host.security.secrets import SecretsError, list_domain_secret_keys

    try:
        with service_scope(service_id):
            keys = list_domain_secret_keys()
    except SecretsError as exc:
        raise HTTPException(
            400, detail={"error_code": exc.code, "message": str(exc)}
        ) from exc
    return {"service_id": service_id, "keys": keys}


@domain_router.delete("/secrets/{key}")
def delete_secret(
    service_id: str,
    key: str,
) -> dict[str, Any]:
    """Admin: удалить секрет по имени ключа."""
    from fsm_platform.host.runtime.runtime_context import service_scope
    from fsm_platform.host.security.secrets import SecretsError, delete_domain_secret

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


@platform_router.post("/v1/admin/domains/{service_id}/reload")
def admin_reload_domain(service_id: str) -> dict[str, Any]:
    """
    Admin: повторный bootstrap catalog domain service без рестарта platform.
    Header: X-Admin-Token: <PLATFORM_ADMIN_TOKEN>
    """
    from fsm_platform.host.tenant.domain_bootstrap import get_bootstrap_status, reload_domain
    from fsm_platform.host.tenant.domain_validator import DomainValidationError

    try:
        return reload_domain(service_id)
    except DomainValidationError as exc:
        raise HTTPException(
            502,
            detail={
                "error_code": "DOMAIN_BOOTSTRAP_FAILED",
                "message": str(exc),
                "report": exc.report.to_dict(),
                "domain_bootstrap": get_bootstrap_status(service_id),
            },
        ) from exc


@input_router.post("/input/telegram/{service_id}/webhook")
def telegram_webhook_tenant(
    service_id: str, update: dict[str, Any]
) -> dict[str, Any]:
    """
    Multi-tenant Telegram Update.
    При онбординге: setWebhook → https://<host>/input/telegram/{service_id}/webhook
    Секреты бота: domain_secrets (TELEGRAM_BOT_TOKEN, …) или env fallback.
    """
    from input.telegram.webhook import handle_telegram_update

    return handle_telegram_update(update, service_id=service_id)


@input_router.get("/input/telegram/{service_id}/link")
def telegram_link_tenant(service_id: str, user_id: int) -> dict[str, Any]:
    """
    Deep-link для фронта арендатора.
    Нужны TELEGRAM_BOT_USERNAME + TOKEN/LINK_SECRET в domain_secrets или env.
    """
    from fsm_platform.host.runtime.runtime_context import service_scope
    from input.telegram.webhook import build_bot_start_url, make_start_payload

    try:
        with service_scope(service_id):
            url = build_bot_start_url(user_id)
            payload = make_start_payload(user_id)
        return {
            "service_id": service_id,
            "user_id": user_id,
            "url": url,
            "payload": payload,
        }
    except RuntimeError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@input_router.post("/input/generic/{service_id}/{channel}")
async def generic_inbound_webhook(
    service_id: str,
    channel: str,
    request: Request,
) -> dict[str, Any]:
    """
    Универсальный inbound (YooKassa / SMS / custom).

    Auth (один из вариантов):
    - Header ``X-Input-Secret`` = domain_secrets ``INPUT_HOOK_SECRET_<CHANNEL>``
      или fallback ``INPUT_HOOK_SECRET``;
    - HMAC: ``X-Input-Timestamp`` + ``X-Input-Signature``
      (hex hmac-sha256(secret, ``{ts}.{raw_body}``)).

    Канал должен быть объявлен в catalog (``hooks.register`` в домене).
    URL: ``POST /input/generic/{service_id}/{channel}``.
    """
    import json

    from input.generic.webhook import handle_generic_inbound

    raw = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}
    query = {k: v for k, v in request.query_params.multi_items()}
    body: Any
    if not raw:
        body = None
    else:
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = raw

    try:
        return handle_generic_inbound(
            service_id=service_id,
            channel=channel,
            body=body,
            headers=headers,
            query=query,
            raw_body=raw,
        )
    except HookError as exc:
        raise HTTPException(
            exc.status_code,
            detail={"error_code": exc.code, "message": str(exc)},
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            409,
            detail={"error_code": exc.code, "message": exc.message},
        ) from exc
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(platform_router)
app.include_router(domain_router)
app.include_router(external_router)
app.include_router(events_ws_router)
app.include_router(input_router)

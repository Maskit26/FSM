"""Public API /v1/{service_id}/…"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from fsm_host.boot import boot
from fsm_host.http import request_runtime
from fsm_host.operations import default_operation_registry
from fsm_platform.registry import default_process_registry

app = FastAPI(title="FSM Platform", version="0.1.0")


class Actor(BaseModel):
    actor_type: str = "user"
    actor_id: str
    channel: str = "api"


class InvokeBody(BaseModel):
    operation: str
    params: dict[str, Any] = Field(default_factory=dict)
    actor: Actor


class EnqueueBody(BaseModel):
    process_name: str
    entity_type: str
    entity_id: int
    payload: dict[str, Any] = Field(default_factory=dict)
    actor: Optional[Actor] = None
    mode: str = "async"


@app.on_event("startup")
def _startup() -> None:
    boot()


@app.get("/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/{service_id}/catalog")
def catalog(service_id: str) -> dict[str, Any]:
    ops = default_operation_registry.list(service_id)
    processes = default_process_registry.list_process_names(service_id)
    return {"service_id": service_id, "operations": ops, "processes": processes}


@app.post("/v1/{service_id}/invoke")
def invoke(service_id: str, body: InvokeBody) -> dict[str, Any]:
    meta = default_operation_registry.get(service_id, body.operation)
    if meta is None:
        raise HTTPException(404, detail=f"UNKNOWN_OPERATION: {body.operation}")
    try:
        result = request_runtime.run_operation(
            service_id,
            meta["handler"],
            meta["kind"],
            body.params,
            body.actor.model_dump(),
        )
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
    }


@app.post("/v1/{service_id}/fsm/enqueue", status_code=202)
def enqueue(
    service_id: str,
    body: EnqueueBody,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    _ = idempotency_key  # v1: store later
    if not default_process_registry.has(service_id, body.process_name):
        raise HTTPException(400, detail=f"UNKNOWN_PROCESS: {body.process_name}")
    try:
        uid = int(body.actor.actor_id) if body.actor else None
        return request_runtime.enqueue_instance(
            service_id,
            process_name=body.process_name,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            payload=body.payload,
            requested_by_user_id=uid,
        )
    except LookupError as exc:
        raise HTTPException(400, detail=str(exc)) from exc


@app.get("/v1/{service_id}/fsm/instances/{instance_id}")
def instance_status(service_id: str, instance_id: int) -> dict[str, Any]:
    row = request_runtime.get_instance(service_id, instance_id)
    if row is None:
        raise HTTPException(404, detail="INSTANCE_NOT_FOUND")
    # serialize datetimes
    for k, v in list(row.items()):
        if hasattr(v, "isoformat"):
            row[k] = v.isoformat()
    return row

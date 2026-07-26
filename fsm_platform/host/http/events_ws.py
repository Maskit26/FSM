"""
Универсальный WS платформы.

1) Стрим platform_events (FSM COMPLETED/FAILED …).
2) Опциональная подписка на domain operation (query/command read):
   клиент говорит operation + actor + params — платформа не знает «биржу».
   На новое событие (или refresh) — invoke и snapshot наружу.

Пример для фронта (биржа курьера — domain query):
  WS /v1/svc_courier_01/ws/events?after_id=0
  → {"op":"subscribe","operation":"list_courier_exchange",
     "actor":{"actor_type":"user","actor_id":"2","channel":"websocket"},
     "params":{}}
  ← {"type":"snapshot","operation":"list_courier_exchange","data":{...}}
  ← {"type":"event","item":{...}}  # FSM events
  # при новом event — снова snapshot подписанной operation
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.core.domain_errors import DomainError
from fsm_platform.host.auth import AuthError, auth_enabled, resolve_actor
from fsm_platform.host.engines import platform_session
from fsm_platform.host.http import request_runtime
from fsm_platform.host.operations import default_operation_registry

logger = logging.getLogger(__name__)

router = APIRouter()

_DEFAULT_INTERVAL = float(os.environ.get("EVENTS_WS_POLL_SECONDS", "1"))


def _fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fetch_events(
    service_id: str, after_id: int, limit: int = 100
) -> list[dict[str, Any]]:
    sp = platform_session()
    try:
        return default_db_layer.list_events_after(
            sp, service_id=service_id, after_id=after_id, limit=limit
        )
    finally:
        sp.close()


def _latest_event_id(service_id: str) -> int:
    sp = platform_session()
    try:
        return default_db_layer.latest_event_id(sp, service_id=service_id)
    finally:
        sp.close()


def _invoke_operation(
    *,
    service_id: str,
    operation: str,
    params: dict[str, Any],
    actor: dict[str, Any],
) -> dict[str, Any]:
    meta = default_operation_registry.get(service_id, operation)
    if meta is None:
        from fsm_platform.host.boot import boot

        boot()
        meta = default_operation_registry.get(service_id, operation)
    if meta is None:
        raise LookupError(f"UNKNOWN_OPERATION: {operation}")
    result = request_runtime.run_operation(
        service_id,
        meta["handler"],
        meta["kind"],
        params,
        actor,
    )
    data = result.get("data", result) if isinstance(result, dict) else result
    return {"operation": operation, "data": data}


@router.websocket("/v1/{service_id}/ws/events")
async def events_ws(
    websocket: WebSocket,
    service_id: str,
    after_id: int = 0,
    interval: Optional[float] = None,
) -> None:
    """
    Query:
      after_id — курсор platform_events (0 = с текущего хвоста при connect)
      interval — тик опроса курсора, default 1s

    Client → server:
      {"op":"subscribe","operation":"list_courier_exchange",
       "actor":{...},"params":{}}
      {"op":"unsubscribe"}
      {"op":"refresh"} | {"op":"ping"} | {"op":"close"}
      {"op":"seek","after_id":N}

    Server → client:
      {"type":"event","item":{...}}
      {"type":"snapshot","operation":"...","data":{...},"fp":"..."}
      {"type":"pong"} | {"type":"error","detail":"..."}
    """
    await websocket.accept()
    poll = float(interval) if interval is not None else _DEFAULT_INTERVAL
    if poll < 0.2:
        poll = 0.2

    # after_id=0 → не реплеим всю историю, стартуем с max(id)
    if int(after_id) <= 0:
        try:
            cursor = await run_in_threadpool(_latest_event_id, service_id)
        except Exception:
            cursor = 0
    else:
        cursor = int(after_id)

    sub_operation: Optional[str] = None
    sub_params: dict[str, Any] = {}
    sub_actor: dict[str, Any] = {}
    last_fp: Optional[str] = None

    async def push_snapshot(*, force: bool = False) -> None:
        nonlocal last_fp
        if not sub_operation:
            return
        try:
            bundle = await run_in_threadpool(
                _invoke_operation,
                service_id=service_id,
                operation=sub_operation,
                params=sub_params,
                actor=sub_actor,
            )
        except DomainError as exc:
            await websocket.send_json(
                {"type": "error", "error_code": exc.code, "detail": exc.message}
            )
            return
        except (ValueError, LookupError) as exc:
            await websocket.send_json({"type": "error", "detail": str(exc)})
            return
        except Exception as exc:
            logger.exception("events_ws snapshot failed")
            await websocket.send_json({"type": "error", "detail": str(exc)})
            return

        fp = _fingerprint(bundle["data"])
        if force or fp != last_fp:
            last_fp = fp
            await websocket.send_json(
                {
                    "type": "snapshot",
                    "operation": bundle["operation"],
                    "data": bundle["data"],
                    "fp": fp,
                }
            )

    try:
        while True:
            try:
                items = await run_in_threadpool(
                    _fetch_events, service_id, cursor, 100
                )
            except Exception as exc:
                logger.exception("events_ws fetch failed")
                await websocket.send_json({"type": "error", "detail": str(exc)})
                await asyncio.sleep(poll)
                continue

            had_events = bool(items)
            for item in items:
                cursor = int(item["id"])
                await websocket.send_json({"type": "event", "item": item})

            if had_events and sub_operation:
                await push_snapshot(force=False)

            try:
                raw = await asyncio.wait_for(
                    websocket.receive_text(), timeout=poll
                )
            except asyncio.TimeoutError:
                continue

            try:
                msg = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "detail": "invalid json"}
                )
                continue
            if not isinstance(msg, dict):
                continue

            op = str(msg.get("op") or "").strip().lower()
            if op == "ping":
                await websocket.send_json({"type": "pong"})
            elif op == "close":
                break
            elif op == "seek" and msg.get("after_id") is not None:
                cursor = int(msg["after_id"])
            elif op == "unsubscribe":
                sub_operation = None
                sub_params = {}
                sub_actor = {}
                last_fp = None
                await websocket.send_json({"type": "unsubscribed"})
            elif op == "subscribe":
                operation = str(msg.get("operation") or "").strip()
                if not operation:
                    await websocket.send_json(
                        {"type": "error", "detail": "operation required"}
                    )
                    continue
                actor = msg.get("actor") if isinstance(msg.get("actor"), dict) else None
                auth_header = (
                    websocket.headers.get("authorization")
                    or msg.get("authorization")
                )
                try:
                    if auth_enabled():
                        resolved = resolve_actor(
                            authorization=auth_header,
                            body_actor=actor,
                        )
                    else:
                        if not actor or not actor.get("actor_id"):
                            raise AuthError(
                                "ACTOR_REQUIRED", "actor.actor_id required"
                            )
                        resolved = {
                            "actor_type": str(actor.get("actor_type") or "user"),
                            "actor_id": str(actor["actor_id"]),
                            "channel": str(
                                actor.get("channel") or "websocket"
                            ),
                        }
                except AuthError as exc:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "detail": exc.code,
                            "message": str(exc),
                        }
                    )
                    continue
                resolved["channel"] = "websocket"
                params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
                sub_operation = operation
                sub_params = params
                sub_actor = resolved
                last_fp = None
                await push_snapshot(force=True)
            elif op in ("", "refresh"):
                await push_snapshot(force=True)
            else:
                await websocket.send_json(
                    {"type": "error", "detail": f"unknown op:{op}"}
                )
    except WebSocketDisconnect:
        return

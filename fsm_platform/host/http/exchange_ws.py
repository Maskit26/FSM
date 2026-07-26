"""
Пример realtime-биржи по WebSocket.

Источник правды — те же query, что и HTTP invoke:
  courier → list_courier_exchange
  driver  → list_driver_exchange

WS не заменяет queries.py: это транспорт + периодический snapshot
(серверный poll поверх query). Event-driven fan-out — следующий шаг (§10.10).
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

from fsm_platform.core.domain_errors import DomainError
from fsm_platform.host.http import request_runtime
from fsm_platform.host.operations import default_operation_registry

logger = logging.getLogger(__name__)

router = APIRouter()

_DEFAULT_INTERVAL = float(os.environ.get("EXCHANGE_WS_POLL_SECONDS", "3"))


def _fingerprint(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fetch_exchange(
    *,
    service_id: str,
    kind: str,
    actor_id: str,
    city: Optional[str],
) -> dict[str, Any]:
    """Синхронный вызов domain query через Request Runtime."""
    kind_n = kind.strip().lower()
    if kind_n == "courier":
        operation = "list_courier_exchange"
        params: dict[str, Any] = {}
    elif kind_n == "driver":
        operation = "list_driver_exchange"
        if not (city or "").strip():
            raise ValueError("city required for kind=driver")
        params = {"city": city.strip()}
    else:
        raise ValueError("kind must be courier or driver")

    meta = default_operation_registry.get(service_id, operation)
    if meta is None:
        # API без startup / тестовый клиент: дорегистрируем домены.
        from fsm_platform.host.boot import boot

        boot()
        meta = default_operation_registry.get(service_id, operation)
    if meta is None:
        raise LookupError(f"UNKNOWN_OPERATION: {operation}")

    actor = {"actor_type": "user", "actor_id": str(actor_id), "channel": "websocket"}
    result = request_runtime.run_operation(
        service_id,
        meta["handler"],
        meta["kind"],
        params,
        actor,
    )
    data = result.get("data", result) if isinstance(result, dict) else result
    return {"operation": operation, "data": data}


@router.websocket("/v1/{service_id}/ws/exchange")
async def exchange_ws(
    websocket: WebSocket,
    service_id: str,
    kind: str,
    actor_id: str,
    city: Optional[str] = None,
    interval: Optional[float] = None,
) -> None:
    """
    Биржа курьера/водителя по WebSocket.

    Query params:
      kind=courier|driver
      actor_id=<users.id>
      city=<город>          — обязателен для driver
      interval=<сек>        — опц., default EXCHANGE_WS_POLL_SECONDS (3)

    Server → client:
      {"type":"snapshot","operation":"...","data":{...},"fp":"..."}
      {"type":"error","detail":"..."}
      {"type":"pong"}

    Client → server (JSON):
      {"op":"refresh"} | {"op":"ping"} | {"op":"close"}
    """
    await websocket.accept()
    poll = float(interval) if interval is not None else _DEFAULT_INTERVAL
    if poll < 0.5:
        poll = 0.5

    last_fp: Optional[str] = None

    async def push_snapshot(*, force: bool = False) -> bool:
        nonlocal last_fp
        try:
            bundle = await run_in_threadpool(
                _fetch_exchange,
                service_id=service_id,
                kind=kind,
                actor_id=actor_id,
                city=city,
            )
        except DomainError as exc:
            await websocket.send_json(
                {"type": "error", "error_code": exc.code, "detail": exc.message}
            )
            return False
        except (ValueError, LookupError) as exc:
            await websocket.send_json({"type": "error", "detail": str(exc)})
            return False
        except Exception as exc:
            logger.exception("exchange_ws fetch failed")
            await websocket.send_json({"type": "error", "detail": str(exc)})
            return False

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
        return True

    try:
        ok = await push_snapshot(force=True)
        if not ok:
            await websocket.close(code=1008)
            return

        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=poll)
            except asyncio.TimeoutError:
                ok = await push_snapshot(force=False)
                if not ok:
                    break
                continue

            msg: dict[str, Any]
            try:
                parsed = json.loads(raw) if raw.strip() else {}
                msg = parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "invalid json"})
                continue

            op = str(msg.get("op") or "").strip().lower()
            if op in ("", "refresh"):
                await push_snapshot(force=True)
            elif op == "ping":
                await websocket.send_json({"type": "pong"})
            elif op == "close":
                break
            else:
                await websocket.send_json(
                    {"type": "error", "detail": f"unknown op: {op}"}
                )
    except WebSocketDisconnect:
        logger.debug(
            "exchange_ws disconnected service=%s kind=%s actor=%s",
            service_id,
            kind,
            actor_id,
        )
    finally:
        try:
            await websocket.close()
        except Exception:
            pass

"""Восстановление после FAILED domain-процессов (вызывается из ProcessDef.on_failed)."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fsm_platform.core.db_layer import default_db_layer

from domains.courier import db_layer

logger = logging.getLogger(__name__)


def _payload(instance: dict[str, Any]) -> dict[str, Any]:
    raw = instance.get("payload_json")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _cancel_sibling_locker_reserves(
    session_platform,
    *,
    service_id: str,
    request_id: int,
    except_instance_id: Optional[int],
) -> int:
    """Отменить PENDING locker_reserve с тем же request_id в payload."""
    rows = default_db_layer.list_pending_instances(
        session_platform,
        service_id=service_id,
        process_name="locker_reserve",
        limit=50,
    )
    cancelled = 0
    for row in rows:
        iid = int(row["id"])
        if except_instance_id is not None and iid == int(except_instance_id):
            continue
        p = _payload(row)
        try:
            rid = int(p.get("request_id") or 0)
        except (TypeError, ValueError):
            continue
        if rid != int(request_id):
            continue
        if default_db_layer.mark_instance_cancelled(
            session_platform,
            iid,
            last_error="SIBLING_RESERVE_FAILED",
        ):
            cancelled += 1
    return cancelled


def on_locker_reserve_failed(
    session_platform,
    session_domain,
    db,
    instance: dict[str, Any],
    last_error: str,
) -> None:
    """
    Провал locker_reserve под order_request:
    abort request (FAILED), free cells, cancel sibling PENDING.
    """
    _ = db
    err = str(last_error or "")
    payload = _payload(instance)
    service_id = str(instance.get("service_id") or "svc_courier_01")
    except_id = int(instance["id"]) if instance.get("id") else None

    raw = payload.get("request_id")
    if raw in (None, ""):
        logger.warning(
            "locker_reserve on_failed: no request_id instance=%s",
            instance.get("id"),
        )
        return
    request_id = int(raw)

    req = db_layer.get_order_request(session_domain, request_id)
    if req is None:
        _cancel_sibling_locker_reserves(
            session_platform,
            service_id=service_id,
            request_id=request_id,
            except_instance_id=except_id,
        )
        return

    released = db_layer.abort_order_request(
        session_domain,
        request_id,
        error_code="RESERVE_CELL_FAILED",
        error_message=err[:500],
    )
    for cell_id in released:
        default_db_layer.upsert_entity_state(
            session_platform,
            service_id,
            "locker",
            int(cell_id),
            "locker_free",
        )
    default_db_layer.upsert_entity_state(
        session_platform, service_id, "order_request", request_id, "FAILED"
    )
    cancelled = _cancel_sibling_locker_reserves(
        session_platform,
        service_id=service_id,
        request_id=request_id,
        except_instance_id=except_id,
    )
    logger.warning(
        "order_request reserve abort request_id=%s released=%s cancelled_siblings=%s err=%s",
        request_id,
        released,
        cancelled,
        err[:200],
    )

"""Recovery on_failed: domain DB + декларации platform side-effects в ответе."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

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


def on_locker_reserve_failed(
    session_platform,
    session_domain,
    db,
    instance: dict[str, Any],
    last_error: str,
) -> dict[str, Any]:
    """
    Провал locker_reserve под order_request:
    abort request (FAILED), free cells в domain DB;
    platform: entity_states + cancel sibling PENDING — через ответ.
    """
    _ = (db, session_platform)
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
        return {}
    request_id = int(raw)

    entity_states: list[dict[str, Any]] = []
    cancel_instances: list[dict[str, Any]] = [
        {
            "process_name": "locker_reserve",
            "payload_match": {"request_id": int(request_id)},
            "except_instance_id": except_id,
            "last_error": "SIBLING_RESERVE_FAILED",
        }
    ]

    req = db_layer.get_order_request(session_domain, request_id)
    if req is None:
        return {
            "cancel_instances": cancel_instances,
            "entity_states": entity_states,
        }

    released = db_layer.abort_order_request(
        session_domain,
        request_id,
        error_code="RESERVE_CELL_FAILED",
        error_message=err[:500],
    )
    for cell_id in released:
        entity_states.append(
            {
                "entity_type": "locker",
                "entity_id": int(cell_id),
                "state": "locker_free",
            }
        )
    entity_states.append(
        {
            "entity_type": "order_request",
            "entity_id": request_id,
            "state": "FAILED",
        }
    )
    logger.warning(
        "order_request reserve abort request_id=%s released=%s err=%s",
        request_id,
        released,
        err[:200],
    )
    return {
        "cancel_instances": cancel_instances,
        "entity_states": entity_states,
        "service_id": service_id,
    }

"""HTTP request sessions + invoke/create bootstrap (§4.10 / §4.12)."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Optional

from sqlalchemy import text

from fsm_platform.db_layer import default_db_layer
from fsm_host.engines import domain_session, platform_session

logger = logging.getLogger(__name__)


def run_operation(
    service_id: str,
    handler: Callable,
    kind: str,
    params: dict[str, Any],
    actor: dict[str, Any],
) -> dict[str, Any]:
    sp = platform_session()
    sd = domain_session(service_id)
    try:
        result = handler(sd, params, actor)
        if kind == "command" and isinstance(result, dict) and result.get("entity_type"):
            _bootstrap_and_maybe_enqueue(sp, service_id, result)
        sd.commit()
        sp.commit()
        return result if isinstance(result, dict) else {"data": result}
    except Exception:
        sd.rollback()
        sp.rollback()
        raise
    finally:
        sd.close()
        sp.close()


def _bootstrap_and_maybe_enqueue(
    sp,
    service_id: str,
    result: dict[str, Any],
) -> None:
    entity_type = str(result["entity_type"])
    entity_id = int(result["entity_id"])
    initial = result.get("initial_state")
    if not initial:
        raise ValueError("initial_state required for create command (legacy graph)")

    existing = default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)
    if existing is None:
        default_db_layer.insert_entity_state_initial(
            sp, service_id, entity_type, entity_id, str(initial)
        )

    enqueue = result.get("enqueue") or {}
    process_name = enqueue.get("process_name")
    if not process_name:
        raise ValueError("invoke-create must enqueue (missing enqueue.process_name)")

    payload = enqueue.get("payload") or {}
    inst = sp.execute(
        text(
            """
            INSERT INTO server_fsm_instances
                (service_id, process_name, entity_type, entity_id, status,
                 attempts, payload_json, created_at, updated_at)
            VALUES
                (:service_id, :process_name, :entity_type, :entity_id, 'PENDING',
                 0, :payload_json, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        ),
        {
            "service_id": service_id,
            "process_name": process_name,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload_json": json.dumps(payload),
        },
    )
    result["instance_id"] = int(inst.lastrowid)


def enqueue_instance(
    service_id: str,
    *,
    process_name: str,
    entity_type: str,
    entity_id: int,
    payload: Optional[dict[str, Any]] = None,
    requested_by_user_id: Optional[int] = None,
) -> dict[str, Any]:
    sp = platform_session()
    try:
        state = default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)
        if state is None:
            raise LookupError("ENTITY_STATE_NOT_FOUND")
        result = sp.execute(
            text(
                """
                INSERT INTO server_fsm_instances
                    (service_id, process_name, entity_type, entity_id, status,
                     attempts, payload_json, requested_by_user_id,
                     created_at, updated_at)
                VALUES
                    (:service_id, :process_name, :entity_type, :entity_id, 'PENDING',
                     0, :payload_json, :uid, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "process_name": process_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payload_json": json.dumps(payload or {}),
                "uid": requested_by_user_id,
            },
        )
        sp.commit()
        instance_id = int(result.lastrowid)
        return {
            "instance_id": instance_id,
            "status": "PENDING",
            "service_id": service_id,
            "status_url": f"/v1/{service_id}/fsm/instances/{instance_id}",
        }
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def get_instance(service_id: str, instance_id: int) -> Optional[dict[str, Any]]:
    sp = platform_session()
    try:
        row = sp.execute(
            text(
                """
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, last_error, payload_json,
                       created_at, started_at, finished_at
                FROM server_fsm_instances
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {"id": instance_id, "service_id": service_id},
        ).mappings().first()
        if row is None:
            return None
        data = dict(row)
        # enrich with entity_fsm_state
        st = default_db_layer.get_entity_state(
            sp, service_id, str(data["entity_type"]), int(data["entity_id"])
        )
        data["entity_fsm_state"] = st
        return data
    finally:
        sp.close()

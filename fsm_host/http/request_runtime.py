"""HTTP request runtime: сессии, invoke и bootstrap сущности.

SQL здесь нет — только вызовы fsm_platform.db_layer и владение сессиями.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

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
    """
    Выполняет invoke: открывает domain/platform сессии, вызывает handler, коммитит.
    Для create-command дополнительно пишет entity_fsm_state и опционально enqueue.
    """
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
    """
    После create: создаёт начальный entity_fsm_state.
    Если handler вернул enqueue.process_name — ставит задачу в server_fsm_instances.
    """
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
        return

    instance_id = default_db_layer.insert_fsm_instance(
        sp,
        service_id=service_id,
        process_name=str(process_name),
        entity_type=entity_type,
        entity_id=entity_id,
        payload=enqueue.get("payload") or {},
    )
    result["instance_id"] = instance_id


def enqueue_instance(
    service_id: str,
    *,
    process_name: str,
    entity_type: str,
    entity_id: int,
    payload: Optional[dict[str, Any]] = None,
    requested_by_user_id: Optional[int] = None,
) -> dict[str, Any]:
    """
    Кладёт PENDING-инстанс FSM в очередь для уже существующей сущности.
    Сущность должна уже иметь строку в entity_fsm_state.
    """
    sp = platform_session()
    try:
        state = default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)
        if state is None:
            raise LookupError("ENTITY_STATE_NOT_FOUND")
        instance_id = default_db_layer.insert_fsm_instance(
            sp,
            service_id=service_id,
            process_name=process_name,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
            requested_by_user_id=requested_by_user_id,
        )
        sp.commit()
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
    """
    Читает статус FSM-инстанса и текущий entity_fsm_state сущности.
    Нужен для GET .../fsm/instances/{id}.
    """
    sp = platform_session()
    try:
        data = default_db_layer.get_fsm_instance(sp, service_id, instance_id)
        if data is None:
            return None
        data["entity_fsm_state"] = default_db_layer.get_entity_state(
            sp, service_id, str(data["entity_type"]), int(data["entity_id"])
        )
        return data
    finally:
        sp.close()

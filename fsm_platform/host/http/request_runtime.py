"""HTTP request runtime: сессии, invoke и bootstrap сущности.

SQL здесь нет — только вызовы fsm_platform.core.db_layer и владение сессиями.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.engines import domain_session, platform_session

logger = logging.getLogger(__name__)


def _actor_id_from_actor(actor: Optional[dict[str, Any]]) -> Optional[int]:
    """Достаёт opaque actor_id из тела Public API. Не связан с именами колонок домена."""
    if not actor:
        return None
    raw = actor.get("actor_id")
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


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
            _bootstrap_and_maybe_enqueue(sp, service_id, result, actor=actor)
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
    *,
    actor: Optional[dict[str, Any]] = None,
) -> None:
    """
    Для command с entity_type: при необходимости создаёт entity_fsm_state.
    related_entities[] — доп. сущности (например locker cells для companions).
    Если handler вернул enqueue.process_name — ставит задачу; actor_id из HTTP actor.
    """
    entity_type = str(result["entity_type"])
    entity_id = int(result["entity_id"])
    initial = result.get("initial_state")

    existing = default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)
    if existing is None:
        if not initial:
            raise ValueError(
                "initial_state required when entity_fsm_state is missing"
            )
        default_db_layer.insert_entity_state_initial(
            sp, service_id, entity_type, entity_id, str(initial)
        )

    for related in result.get("related_entities") or []:
        if not isinstance(related, dict):
            raise ValueError("related_entities items must be objects")
        r_type = related.get("entity_type")
        r_id = related.get("entity_id")
        r_initial = related.get("initial_state")
        if not r_type or r_id is None:
            raise ValueError(
                "related_entities require entity_type and entity_id"
            )
        r_id_int = int(r_id)
        r_existing = default_db_layer.get_entity_state(
            sp, service_id, str(r_type), r_id_int
        )
        if r_existing is None:
            if not r_initial:
                raise ValueError(
                    "related_entities.initial_state required when "
                    "entity_fsm_state is missing"
                )
            default_db_layer.insert_entity_state_initial(
                sp, service_id, str(r_type), r_id_int, str(r_initial)
            )

    _apply_timers(sp, service_id, result)

    if result.get("saga"):
        _apply_saga(sp, service_id, result, actor=actor)
        return

    enqueues = result.get("enqueues")
    if isinstance(enqueues, list) and enqueues:
        instance_ids: list[int] = []
        for item in enqueues:
            if not isinstance(item, dict):
                raise ValueError("enqueues items must be objects")
            process_name = item.get("process_name")
            if not process_name:
                raise ValueError("enqueues[].process_name required")
            e_type = str(item.get("entity_type") or entity_type)
            e_id = int(item["entity_id"]) if item.get("entity_id") is not None else entity_id
            e_initial = item.get("initial_state")
            e_existing = default_db_layer.get_entity_state(
                sp, service_id, e_type, e_id
            )
            if e_existing is None:
                if not e_initial:
                    raise ValueError(
                        "enqueues[].initial_state required when "
                        "entity_fsm_state is missing"
                    )
                default_db_layer.insert_entity_state_initial(
                    sp, service_id, e_type, e_id, str(e_initial)
                )
            instance_ids.append(
                default_db_layer.insert_fsm_instance(
                    sp,
                    service_id=service_id,
                    process_name=str(process_name),
                    entity_type=e_type,
                    entity_id=e_id,
                    payload=item.get("payload") or {},
                    actor_id=_actor_id_from_actor(actor),
                )
            )
        result["instance_ids"] = instance_ids
        if instance_ids:
            result["instance_id"] = instance_ids[0]
        return

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
        actor_id=_actor_id_from_actor(actor),
    )
    result["instance_id"] = instance_id


def _apply_timers(sp, service_id: str, result: dict[str, Any]) -> None:
    """cancel_timers[] / timers[] из ответа command → fsm_timers."""
    from datetime import datetime

    from fsm_platform.host import side_effects

    for item in result.get("cancel_timers") or []:
        if not isinstance(item, dict):
            raise ValueError("cancel_timers items must be objects")
        key = item.get("idempotency_key")
        if not key:
            raise ValueError("cancel_timers[].idempotency_key required")
        default_db_layer.cancel_timer_by_idempotency_key(
            sp, service_id, str(key)
        )

    timer_ids: list[int] = []
    for item in result.get("timers") or []:
        if not isinstance(item, dict):
            raise ValueError("timers items must be objects")
        process_name = item.get("process_name")
        e_type = item.get("entity_type") or result.get("entity_type")
        e_id = item.get("entity_id")
        fire_at = item.get("fire_at")
        if not process_name or e_type is None or e_id is None or fire_at is None:
            raise ValueError(
                "timers[] require process_name, entity_type, entity_id, fire_at"
            )
        if isinstance(fire_at, str):
            fire_at = datetime.fromisoformat(
                fire_at.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        timer_ids.append(
            side_effects.schedule_timer(
                sp,
                service_id=service_id,
                entity_type=str(e_type),
                entity_id=int(e_id),
                process_name=str(process_name),
                fire_at=fire_at,
                payload=item.get("payload") or {},
                idempotency_key=item.get("idempotency_key"),
            )
        )
    if timer_ids:
        result["timer_ids"] = timer_ids


def _apply_saga(
    sp,
    service_id: str,
    result: dict[str, Any],
    *,
    actor: Optional[dict[str, Any]] = None,
) -> None:
    """result['saga'] → fsm_sagas + child instances."""
    from fsm_platform.host import side_effects

    raw = result.get("saga")
    if not isinstance(raw, dict):
        raise ValueError("saga must be an object")
    children = raw.get("children")
    if not isinstance(children, list) or not children:
        raise ValueError("saga.children required (non-empty list)")

    saga_id, instance_ids = side_effects.start_saga(
        sp,
        service_id=service_id,
        children=children,
        on_success=raw.get("on_success"),
        on_fail=raw.get("on_fail"),
        fail_policy=str(raw.get("fail_policy") or "fail_fast"),
        payload=raw.get("payload") or {},
        actor_id=_actor_id_from_actor(actor),
    )
    result["saga_id"] = saga_id
    result["instance_ids"] = instance_ids
    if instance_ids:
        result["instance_id"] = instance_ids[0]


def enqueue_instance(
    service_id: str,
    *,
    process_name: str,
    entity_type: str,
    entity_id: int,
    payload: Optional[dict[str, Any]] = None,
    actor_id: Optional[int] = None,
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
            actor_id=actor_id,
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

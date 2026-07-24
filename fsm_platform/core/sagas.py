"""Platform async saga: parent + N children + fan-in on_success / on_fail."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .db_layer import FsmDbLayer, SessionLike, default_db_layer

logger = logging.getLogger(__name__)

_TERMINAL_OK = "COMPLETED"
_TERMINAL_FAIL = "FAILED"
_CHILD_ACTIVE = frozenset({"PENDING", "RUNNING"})


def start_saga(
    session: SessionLike,
    *,
    service_id: str,
    children: list[dict[str, Any]],
    on_success: Optional[dict[str, Any]] = None,
    on_fail: Optional[dict[str, Any]] = None,
    fail_policy: str = "fail_fast",
    payload: Optional[dict[str, Any]] = None,
    actor_id: Optional[int] = None,
    db_layer: FsmDbLayer | None = None,
) -> tuple[int, list[int]]:
    """
    Создаёт RUNNING saga, bootstrap entity states при необходимости,
    INSERT child instances + fsm_saga_children.
    Возвращает (saga_id, child_instance_ids).
    """
    db = db_layer or default_db_layer
    if not children:
        raise ValueError("saga.children required (non-empty)")
    policy = (fail_policy or "fail_fast").strip().lower()
    if policy not in ("fail_fast", "wait_all"):
        raise ValueError(f"invalid fail_policy: {fail_policy}")

    saga_id = db.insert_saga(
        session,
        service_id=service_id,
        fail_policy=policy,
        on_success=on_success,
        on_fail=on_fail,
        payload=payload,
        actor_id=actor_id,
    )
    instance_ids: list[int] = []
    for item in children:
        if not isinstance(item, dict):
            raise ValueError("saga.children items must be objects")
        process_name = item.get("process_name")
        e_type = item.get("entity_type")
        e_id = item.get("entity_id")
        if not process_name or e_type is None or e_id is None:
            raise ValueError(
                "saga.children[] require process_name, entity_type, entity_id"
            )
        e_type_s = str(e_type)
        e_id_i = int(e_id)
        e_initial = item.get("initial_state")
        existing = db.get_entity_state(session, service_id, e_type_s, e_id_i)
        if existing is None:
            if not e_initial:
                raise ValueError(
                    "saga.children[].initial_state required when "
                    "entity_fsm_state is missing"
                )
            db.insert_entity_state_initial(
                session, service_id, e_type_s, e_id_i, str(e_initial)
            )
        iid = db.insert_fsm_instance(
            session,
            service_id=service_id,
            process_name=str(process_name),
            entity_type=e_type_s,
            entity_id=e_id_i,
            payload=item.get("payload") or {},
            actor_id=actor_id,
        )
        db.insert_saga_child(
            session,
            saga_id=saga_id,
            instance_id=iid,
            entity_type=e_type_s,
            entity_id=e_id_i,
            process_name=str(process_name),
        )
        instance_ids.append(iid)
    return saga_id, instance_ids


def _enqueue_finish(
    db: FsmDbLayer,
    session: SessionLike,
    *,
    service_id: str,
    spec: Optional[dict[str, Any]],
    actor_id: Optional[int],
    saga_id: int,
    kind: str,
) -> Optional[int]:
    if not spec or not isinstance(spec, dict):
        return None
    process_name = spec.get("process_name")
    e_type = spec.get("entity_type")
    e_id = spec.get("entity_id")
    if not process_name or e_type is None or e_id is None:
        logger.error(
            "saga %s finish %s missing process/entity saga_id=%s",
            kind,
            spec,
            saga_id,
        )
        return None
    e_type_s = str(e_type)
    e_id_i = int(e_id)
    e_initial = spec.get("initial_state")
    existing = db.get_entity_state(session, service_id, e_type_s, e_id_i)
    if existing is None:
        if not e_initial:
            logger.error(
                "saga %s finish entity state missing saga_id=%s %s/%s",
                kind,
                saga_id,
                e_type_s,
                e_id_i,
            )
            return None
        db.insert_entity_state_initial(
            session, service_id, e_type_s, e_id_i, str(e_initial)
        )
    payload = dict(spec.get("payload") or {})
    payload.setdefault("saga_id", saga_id)
    payload.setdefault("saga_finish", kind)
    return db.insert_fsm_instance(
        session,
        service_id=service_id,
        process_name=str(process_name),
        entity_type=e_type_s,
        entity_id=e_id_i,
        payload=payload,
        actor_id=actor_id if actor_id is not None else spec.get("actor_id"),
    )


def _heal_desynced_children(
    db: FsmDbLayer, session: SessionLike, saga_id: int
) -> None:
    """
    Подтягивает child-status из server_fsm_instances, если instance уже
    терминален, а child ещё PENDING/RUNNING (пропущенный fan-in).
    """
    for child in db.list_saga_children(session, saga_id):
        if str(child.get("status") or "") not in _CHILD_ACTIVE:
            continue
        inst = db.get_fsm_instance_by_id(session, int(child["instance_id"]))
        if inst is None:
            continue
        istatus = str(inst.get("status") or "").upper()
        if istatus == _TERMINAL_OK:
            db.mark_saga_child_terminal(
                session, int(child["instance_id"]), _TERMINAL_OK, None
            )
            logger.warning(
                "saga heal child COMPLETED saga_id=%s instance_id=%s",
                saga_id,
                child["instance_id"],
            )
        elif istatus == _TERMINAL_FAIL:
            db.mark_saga_child_terminal(
                session,
                int(child["instance_id"]),
                _TERMINAL_FAIL,
                inst.get("last_error"),
            )
            logger.warning(
                "saga heal child FAILED saga_id=%s instance_id=%s",
                saga_id,
                child["instance_id"],
            )


def on_child_terminal(
    session: SessionLike,
    *,
    instance_id: int,
    status: str,
    last_error: Optional[str] = None,
    db_layer: FsmDbLayer | None = None,
) -> Optional[dict[str, Any]]:
    """
    Fan-in после COMPLETED/FAILED child instance.
    Возвращает {saga_id, saga_status, finish_instance_id?} или None если не child.
    """
    db = db_layer or default_db_layer
    terminal = str(status).upper()
    if terminal not in (_TERMINAL_OK, _TERMINAL_FAIL):
        return None

    saga_id = db.mark_saga_child_terminal(
        session, instance_id, terminal, last_error
    )
    if saga_id is None:
        return None

    saga = db.get_saga(session, saga_id)
    if saga is None:
        return None
    if str(saga.get("status") or "") != "RUNNING":
        return {"saga_id": saga_id, "saga_status": saga.get("status")}

    # Heal: instance уже COMPLETED/FAILED, а child-row ещё PENDING
    # (старый воркер / rollback platform после domain commit).
    _heal_desynced_children(db, session, saga_id)

    children = db.list_saga_children(session, saga_id)
    policy = str(saga.get("fail_policy") or "fail_fast").lower()
    service_id = str(saga["service_id"])
    actor_id = saga.get("actor_id")
    if actor_id is not None:
        actor_id = int(actor_id)

    failed = [c for c in children if str(c.get("status")) == _TERMINAL_FAIL]
    completed = [c for c in children if str(c.get("status")) == _TERMINAL_OK]
    active = [c for c in children if str(c.get("status")) in _CHILD_ACTIVE]

    finish_iid: Optional[int] = None

    if policy == "fail_fast" and failed:
        if not db.cas_finish_saga(session, saga_id, "FAILED"):
            return {"saga_id": saga_id, "saga_status": "FAILED"}
        db.cancel_pending_saga_children(session, saga_id)
        finish_iid = _enqueue_finish(
            db,
            session,
            service_id=service_id,
            spec=saga.get("on_fail"),
            actor_id=actor_id,
            saga_id=saga_id,
            kind="on_fail",
        )
        logger.info(
            "saga FAILED fail_fast saga_id=%s failed_child=%s finish=%s",
            saga_id,
            instance_id,
            finish_iid,
        )
        return {
            "saga_id": saga_id,
            "saga_status": "FAILED",
            "finish_instance_id": finish_iid,
        }

    if active:
        return {"saga_id": saga_id, "saga_status": "RUNNING"}

    # no active children left
    if failed:
        if not db.cas_finish_saga(session, saga_id, "FAILED"):
            return {"saga_id": saga_id, "saga_status": "FAILED"}
        finish_iid = _enqueue_finish(
            db,
            session,
            service_id=service_id,
            spec=saga.get("on_fail"),
            actor_id=actor_id,
            saga_id=saga_id,
            kind="on_fail",
        )
        logger.info(
            "saga FAILED wait_all saga_id=%s finish=%s", saga_id, finish_iid
        )
        return {
            "saga_id": saga_id,
            "saga_status": "FAILED",
            "finish_instance_id": finish_iid,
        }

    if len(completed) == len(children) and children:
        if not db.cas_finish_saga(session, saga_id, "SUCCEEDED"):
            return {"saga_id": saga_id, "saga_status": "SUCCEEDED"}
        finish_iid = _enqueue_finish(
            db,
            session,
            service_id=service_id,
            spec=saga.get("on_success"),
            actor_id=actor_id,
            saga_id=saga_id,
            kind="on_success",
        )
        logger.info(
            "saga SUCCEEDED saga_id=%s children=%s finish=%s",
            saga_id,
            len(children),
            finish_iid,
        )
        return {
            "saga_id": saga_id,
            "saga_status": "SUCCEEDED",
            "finish_instance_id": finish_iid,
        }

    return {"saga_id": saga_id, "saga_status": "RUNNING"}

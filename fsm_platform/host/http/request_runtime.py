"""HTTP request runtime: сессии, invoke и bootstrap сущности.

SQL здесь нет — только вызовы fsm_platform.core.db_layer и владение сессиями.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.runtime.engines import graph_session, platform_session
from fsm_platform.host.runtime.graph_version import (
    current_graph_version,
    resolve_graph_version,
)

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
    operation: str,
    handler: Any,
    kind: str,
    params: dict[str, Any],
    actor: dict[str, Any],
) -> dict[str, Any]:
    """
    Invoke command/query через Contract API; platform commit + bootstrap/enqueue.
    Domain DB commit — на стороне domain service до ответа HTTP.
    При dual-commit сбое (domain ok / platform fail) — очередь reconcile.
    """
    from fsm_platform.core.remote import RemoteRef
    from fsm_platform.host.contract.contract_invoke import call_operation
    from fsm_platform.host.runtime.runtime_context import service_scope

    if not isinstance(handler, RemoteRef):
        raise TypeError("operation handler must be RemoteRef")

    sp = platform_session()
    sg = None
    result: Any = None
    domain_committed = False
    platform_committed = False
    try:
        with service_scope(service_id):
            result = call_operation(
                handler, kind=kind, params=params, actor=actor
            )
            domain_committed = True
            if (
                kind == "command"
                and isinstance(result, dict)
                and result.get("entity_type")
            ):
                sg = graph_session(service_id)
                _bootstrap_and_maybe_enqueue(
                    sp, sg, service_id, result, actor=actor
                )
            if kind == "command" and isinstance(result, dict):
                from fsm_platform.host.contract.contract_side_effects import apply_declared

                apply_declared(sp, service_id=service_id, data=result)
        sp.commit()
        platform_committed = True
        return result if isinstance(result, dict) else {"data": result}
    except Exception:
        sp.rollback()
        if (
            domain_committed
            and not platform_committed
            and kind == "command"
            and isinstance(result, dict)
            and _invoke_needs_reconcile(result)
        ):
            _enqueue_invoke_reconcile(
                service_id,
                operation=operation,
                result=result,
                actor=actor,
            )
        raise
    finally:
        if sg is not None:
            sg.close()
        sp.close()


def _invoke_needs_reconcile(result: dict[str, Any]) -> bool:
    """Есть platform-side эффекты, которые нужно докатить после сбоя commit."""
    if result.get("entity_type"):
        return True
    if result.get("enqueue") or result.get("enqueues") or result.get("saga"):
        return True
    if result.get("timers") or result.get("cancel_timers"):
        return True
    from fsm_platform.host.contract.contract_side_effects import extract_declared

    declared = extract_declared(result)
    if (
        declared["notify"]
        or declared["cancel_instances"]
        or declared["entity_states"]
    ):
        return True
    return False


def _invoke_reconcile_transition_id(
    service_id: str, operation: str, result: dict[str, Any]
) -> int:
    """Стабильный ключ для UNIQUE (instance_id, transition_id) invoke-reconcile."""
    import zlib

    from fsm_platform.host.contract.contract_side_effects import extract_declared

    entity_type = str(result.get("entity_type") or "")
    entity_id = int(result.get("entity_id") or 0)
    declared = extract_declared(result)
    se_fp = ",".join(
        f"{k}:{len(declared[k])}"
        for k in ("notify", "cancel_instances", "entity_states")
    )
    key = f"invoke:{service_id}:{operation}:{entity_type}:{entity_id}:{se_fp}"
    tid = zlib.crc32(key.encode("utf-8")) & 0x7FFFFFFF
    return tid or 1


def _enqueue_invoke_reconcile(
    service_id: str,
    *,
    operation: str,
    result: dict[str, Any],
    actor: dict[str, Any],
) -> None:
    """
    Domain command уже закоммичен; platform commit/bootstrap упали —
    ставим идемпотентный докат platform-части (§4.7.1, invoke).
    """
    entity_type = str(result.get("entity_type") or "_")
    entity_id = int(result.get("entity_id") or 0)
    instance_ids = result.get("instance_ids")
    instance_id = int(result.get("instance_id") or 0)
    if not instance_id and isinstance(instance_ids, list) and instance_ids:
        instance_id = int(instance_ids[0])
    transition_id = _invoke_reconcile_transition_id(service_id, operation, result)
    to_state = str(result.get("initial_state") or "bootstrap")
    payload = {
        "kind": "invoke_command",
        "operation": operation,
        "result": result,
        "actor": dict(actor or {}),
    }
    sp = platform_session()
    try:
        default_db_layer.enqueue_reconcile(
            sp,
            service_id=service_id,
            instance_id=instance_id,
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=None,
            to_state=to_state,
            event_name=operation,
            transition_id=transition_id,
            payload=payload,
        )
        sp.commit()
        logger.error(
            "DUAL_COMMIT_PLATFORM_FAILED invoke operation=%s entity=%s:%s "
            "queued reconcile transition_id=%s",
            operation,
            entity_type,
            entity_id,
            transition_id,
        )
    except Exception:
        sp.rollback()
        logger.exception(
            "invoke reconcile enqueue failed operation=%s entity=%s:%s",
            operation,
            entity_type,
            entity_id,
        )
        raise
    finally:
        sp.close()


def _bootstrap_and_maybe_enqueue(
    sp,
    sd,
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
    graph_version = resolve_graph_version(sd)

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
        if not r_initial:
            raise ValueError("related_entities.initial_state required")
        r_existing = default_db_layer.get_entity_state(
            sp, service_id, str(r_type), r_id_int
        )
        if r_existing is None:
            default_db_layer.insert_entity_state_initial(
                sp, service_id, str(r_type), r_id_int, str(r_initial)
            )
        elif str(r_existing) != str(r_initial):
            # Sync command уже изменил domain (напр. create_order bind / hold consume).
            default_db_layer.upsert_entity_state(
                sp, service_id, str(r_type), r_id_int, str(r_initial)
            )

    _apply_timers(sp, service_id, result)

    if result.get("saga"):
        _apply_saga(
            sp, service_id, result, actor=actor, graph_version=graph_version
        )
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
                    graph_version=graph_version,
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
        graph_version=graph_version,
    )
    result["instance_id"] = instance_id


def _apply_timers(sp, service_id: str, result: dict[str, Any]) -> None:
    """cancel_timers[] / timers[] из ответа command → fsm_timers."""
    from datetime import datetime

    from fsm_platform.host.runtime import side_effects

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
        owner = str(item.get("owner") or "domain").strip().lower()
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
                owner=owner,
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
    graph_version: Optional[int] = None,
) -> None:
    """result['saga'] → fsm_sagas + child instances."""
    from fsm_platform.host.runtime import side_effects

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
        graph_version=graph_version,
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
    idempotency_key: Optional[str] = None,
) -> dict[str, Any]:
    """
    Кладёт PENDING-инстанс FSM в очередь для уже существующей сущности.
    Сущность должна уже иметь строку в entity_fsm_state.
    При idempotency_key — повтор возвращает сохранённый ответ без второго instance.
    """
    sp = platform_session()
    try:
        key = (idempotency_key or "").strip() or None
        if key:
            existing = default_db_layer.get_idempotency(
                sp, service_id=service_id, scope="enqueue", key=key
            )
            if existing is not None:
                resp = existing.get("response") or {}
                if isinstance(resp, dict) and resp.get("instance_id") is not None:
                    return resp

        state = default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)
        if state is None:
            raise LookupError("ENTITY_STATE_NOT_FOUND")
        gv = None
        sg = None
        try:
            sg = graph_session(service_id)
            gv = resolve_graph_version(sg)
        finally:
            if sg is not None:
                sg.close()
        instance_id = default_db_layer.insert_fsm_instance(
            sp,
            service_id=service_id,
            process_name=process_name,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
            actor_id=actor_id,
            graph_version=gv,
        )
        response = {
            "instance_id": instance_id,
            "status": "PENDING",
            "service_id": service_id,
            "status_url": f"/v1/{service_id}/fsm/instances/{instance_id}",
        }
        if key:
            inserted = default_db_layer.put_idempotency(
                sp,
                service_id=service_id,
                scope="enqueue",
                key=key,
                response=response,
                instance_id=instance_id,
            )
            if not inserted:
                # Гонка: другой запрос успел записать ключ — отдаём его ответ.
                sp.rollback()
                again = default_db_layer.get_idempotency(
                    sp, service_id=service_id, scope="enqueue", key=key
                )
                if again and isinstance(again.get("response"), dict):
                    return again["response"]
                raise RuntimeError("IDEM_RACE_UNRESOLVED")
        sp.commit()
        return response
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


def list_entity_history(
    service_id: str,
    *,
    entity_type: str,
    entity_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
) -> dict[str, Any]:
    """Таймлайн сущности из fsm_transition_logs."""
    sp = platform_session()
    try:
        rows = default_db_layer.list_transition_logs(
            sp,
            service_id=service_id,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            before_id=before_id,
        )
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "items": rows,
        }
    finally:
        sp.close()


def list_platform_events(
    service_id: str,
    *,
    after_id: int = 0,
    limit: int = 100,
    newest: bool = False,
) -> dict[str, Any]:
    """Cursor-poll platform_events (id > after_id) или хвост newest=True."""
    sp = platform_session()
    try:
        items = default_db_layer.list_events_after(
            sp,
            service_id=service_id,
            after_id=after_id,
            limit=limit,
            newest=newest,
        )
        next_after = int(items[-1]["id"]) if items else int(after_id)
        return {
            "service_id": service_id,
            "after_id": int(after_id),
            "next_after_id": next_after,
            "newest": bool(newest),
            "items": items,
        }
    finally:
        sp.close()


def list_available_actions(
    service_id: str,
    *,
    entity_type: str,
    entity_id: int,
    actor: dict[str, Any],
    payload: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Исходящие переходы + read-only прогон guards (без apply/effect).
    Собирает domain context тем же context_builder, что и worker.
    """
    from fsm_platform.core.registry import (
        default_guard_registry,
        default_process_registry,
    )
    from fsm_platform.core.transition_repository import TransitionRepository
    from fsm_platform.core.types import normalize_guard_result

    try:
        actor_id = int((actor or {}).get("actor_id") or 0)
    except (TypeError, ValueError):
        actor_id = 0

    merged_payload = dict(payload or {})
    if actor_id and "executor_user_id" not in merged_payload:
        merged_payload.setdefault("executor_user_id", actor_id)
        merged_payload.setdefault("courier_user_id", actor_id)
        merged_payload.setdefault("driver_user_id", actor_id)

    from fsm_platform.host.runtime.runtime_context import service_scope

    repo = TransitionRepository()
    sp = platform_session()
    sg = graph_session(service_id)
    try:
        with service_scope(service_id):
            current = default_db_layer.get_entity_state(
                sp, service_id, entity_type, entity_id
            )
            if current is None:
                return {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "current_state": None,
                    "actions": [],
                    "error": "ENTITY_STATE_NOT_FOUND",
                }

            gv = current_graph_version(sg)
            outgoing = repo.list_outgoing(
                sg, entity_type, str(current), graph_version=gv
            )
            by_event: dict[str, list] = {}
            for p in default_process_registry.list_for_service(service_id):
                if str(p.entity_type or "") != entity_type:
                    continue
                by_event.setdefault(p.runtime_event_name, []).append(p)

            actions: list[dict[str, Any]] = []
            for edge in outgoing:
                procs = by_event.get(edge.event_name) or []
                process_name = procs[0].process_name if procs else None
                context_builder = procs[0].context_builder if procs else None

                instance: dict[str, Any] = {
                    "service_id": service_id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "actor_id": actor_id or None,
                    "payload_json": merged_payload,
                    "graph_version": gv,
                }

                domain_context: dict[str, Any] = {}
                context_error: Optional[str] = None
                if context_builder is not None:
                    try:
                        from fsm_platform.host.contract.contract_invoke import (
                            call_context_builder,
                        )

                        domain_context = call_context_builder(
                            context_builder, runtime_ctx={}, instance=instance
                        )
                    except Exception as exc:  # noqa: BLE001
                        context_error = f"CONTEXT_FAILED:{exc}"
                        logger.warning(
                            "available_actions context failed event=%s: %s",
                            edge.event_name,
                            exc,
                        )

                allowed = False
                reason: Optional[str] = None
                if context_error:
                    reason = context_error
                elif edge.guard_name is None or str(edge.guard_name).strip() == "":
                    allowed = True
                else:
                    guard_fn = default_guard_registry.get(
                        service_id, str(edge.guard_name)
                    )
                    if guard_fn is None:
                        reason = f"UNKNOWN_GUARD:{edge.guard_name}"
                    else:
                        try:
                            from fsm_platform.host.contract.contract_invoke import call_guard

                            gr = normalize_guard_result(
                                call_guard(
                                    guard_fn,
                                    context=domain_context,
                                    guard_params=edge.guard_params or {},
                                    instance=instance,
                                )
                            )
                            allowed = bool(gr.ok)
                            reason = gr.reason
                        except Exception as exc:  # noqa: BLE001
                            reason = f"GUARD_ERROR:{exc}"

                actions.append(
                    {
                        "transition_id": edge.id,
                        "event_name": edge.event_name,
                        "process_name": process_name,
                        "from_state": edge.from_state,
                        "to_state": edge.to_state,
                        "guard_name": edge.guard_name,
                        "priority": edge.priority,
                        "allowed": allowed,
                        "reason": reason,
                    }
                )

            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": str(current),
                "actor_id": actor_id or None,
                "actions": actions,
            }
    finally:
        sp.close()
        sg.close()


class EntityAccessDenied(Exception):
    def __init__(self, reason: str = "FORBIDDEN") -> None:
        self.reason = reason
        super().__init__(reason)


class EntityCapabilityMissing(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def get_entity_snapshot(
    service_id: str,
    *,
    entity_type: str,
    entity_id: int,
    actor: dict[str, Any],
    params: Optional[dict[str, Any]] = None,
    include_actions: bool = True,
) -> dict[str, Any]:
    """
    End-user entity Snapshot: Principal → access policy → domain snapshot.
    Optional platform availableActions (graph+guards).
    """
    from fsm_platform.core.registry import (
        default_access_registry,
        default_snapshot_registry,
    )
    from fsm_platform.host.contract.contract_invoke import call_access, call_snapshot
    from fsm_platform.host.security.principal import principal_from_actor

    et = str(entity_type or "").strip()
    eid = int(entity_id)
    principal = principal_from_actor(actor)
    principal_dict = principal.to_dict()
    merged_params = dict(params or {})

    access_ref = default_access_registry.get(service_id, et)
    snap_ref = default_snapshot_registry.get(service_id, et)
    if access_ref is None:
        raise EntityCapabilityMissing(
            "ACCESS_POLICY_NOT_REGISTERED",
            f"no access policy for entity_type={et!r}",
        )
    if snap_ref is None:
        raise EntityCapabilityMissing(
            "SNAPSHOT_NOT_REGISTERED",
            f"no snapshot builder for entity_type={et!r}",
        )

    gate = call_access(
        access_ref,
        entity_id=eid,
        principal=principal_dict,
        params=merged_params,
    )
    if not bool(gate.get("allowed")):
        raise EntityAccessDenied(str(gate.get("reason") or "FORBIDDEN"))

    data = call_snapshot(
        snap_ref,
        entity_id=eid,
        principal=principal_dict,
        params=merged_params,
    )
    out: dict[str, Any] = {
        "entity_type": et,
        "entity_id": eid,
        "principal": {
            "userId": principal.user_id,
            "roles": list(principal.roles),
            "actor_type": principal.actor_type,
        },
        "snapshot": data,
    }
    if include_actions:
        try:
            actions = list_available_actions(
                service_id,
                entity_type=et,
                entity_id=eid,
                actor=principal.as_actor(),
                payload=merged_params,
            )
            out["available_actions"] = actions.get("actions") or []
            out["current_state"] = actions.get("current_state")
        except Exception as exc:  # noqa: BLE001
            logger.warning("snapshot available_actions failed: %s", exc)
            out["available_actions"] = []
            out["available_actions_error"] = str(exc)
    return out

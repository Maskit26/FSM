"""Один декларативный шаг FSM: primary + companions (multi-entity)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .db_layer import SessionLike
from .errors import FsmErrorCodes
from .registry import EffectRegistry, GuardRegistry
from .state_store import EntityStateStore
from .transition_executor import TransitionApplyError, TransitionExecutor
from .transition_repository import TransitionRepository
from .types import (
    FsmResult,
    InstanceDict,
    ProcessDef,
    RuntimeContext,
    TransitionDef,
    normalize_effect_result,
    normalize_guard_result,
)

logger = logging.getLogger(__name__)


def _effect_params_for_call(params: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Копия effect_params без ключа companions (оркестрация — только runner)."""
    out = dict(params or {})
    out.pop("companions", None)
    return out


def _parse_companions(effect_params: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """Читает effect_params.companions; пусто/отсутствует → []."""
    raw = (effect_params or {}).get("companions")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("companions must be a list")
    return raw


class TransitionRunner:
    """
    Полный цикл одного process-step: primary entity, затем companions.
    Каждый entity: candidates → guards → apply → effect. Атомарность — у worker.
    """

    def __init__(
        self,
        guard_registry: GuardRegistry,
        effect_registry: EffectRegistry,
        state_store: EntityStateStore,
        transition_repository: TransitionRepository,
        transition_executor: TransitionExecutor,
    ) -> None:
        self._guards = guard_registry
        self._effects = effect_registry
        self._state_store = state_store
        self._repo = transition_repository
        self._executor = transition_executor

    def run(
        self,
        session_platform: SessionLike,
        session_domain: SessionLike,
        db: Any,
        runtime_ctx: RuntimeContext,
        instance: InstanceDict,
        process_def: ProcessDef,
        *,
        session_graph: Optional[SessionLike] = None,
    ) -> FsmResult:
        """Primary pipeline, затем companions из effect_params выбранного primary-ребра."""
        session_graph = session_graph or session_domain
        service_id = str(instance["service_id"])
        instance_id = instance.get("id")

        # 1. CONTEXT (один раз на process-step; companions делят тот же context)
        try:
            from fsm_platform.host.contract_invoke import call_context_builder

            domain_context = call_context_builder(
                process_def.context_builder,
                runtime_ctx=runtime_ctx,
                instance=instance,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("context_builder failed")
            return FsmResult(
                new_state="FAILED",
                last_error=f"{FsmErrorCodes.CONTEXT_BUILD_FAILED}: {exc}",
            )

        # 2. PRIMARY IDENTIFIERS
        entity_type = process_def.entity_type or instance.get("entity_type")
        entity_id = instance.get("entity_id")
        event_name = process_def.runtime_event_name
        user_id = instance.get("actor_id") or 0

        if not entity_type:
            return FsmResult(
                new_state="FAILED",
                last_error=FsmErrorCodes.MISSING_ENTITY_TYPE,
            )
        if entity_id is None:
            return FsmResult(
                new_state="FAILED",
                last_error=FsmErrorCodes.MISSING_ENTITY_ID,
            )
        entity_id = int(entity_id)

        primary = self._run_entity_step(
            session_platform=session_platform,
            session_domain=session_domain,
            session_graph=session_graph,
            db=db,
            domain_context=domain_context,
            instance=instance,
            service_id=service_id,
            entity_type=str(entity_type),
            entity_id=entity_id,
            event_name=event_name,
            user_id=int(user_id) if user_id else None,
            instance_id=int(instance_id) if instance_id is not None else None,
            role="primary",
        )
        if primary.get("error"):
            return FsmResult(new_state="FAILED", last_error=primary["error"])

        selected: TransitionDef = primary["selected"]
        domain_context = primary["domain_context"]
        effect_payload = primary["effect_payload"]
        side_effects = {
            "notify": list(primary.get("notify") or []),
            "cancel_instances": list(primary.get("cancel_instances") or []),
            "entity_states": list(primary.get("entity_states") or []),
        }

        # 3. COMPANIONS (effect_params выбранного primary-ребра)
        try:
            companions_spec = _parse_companions(selected.effect_params)
        except ValueError as exc:
            return FsmResult(
                new_state="FAILED",
                last_error=f"{FsmErrorCodes.INVALID_COMPANION}: {exc}",
            )

        companion_payloads: list[dict[str, Any]] = []
        for index, spec in enumerate(companions_spec):
            step = self._run_companion(
                session_platform=session_platform,
                session_domain=session_domain,
                session_graph=session_graph,
                db=db,
                domain_context=domain_context,
                instance=instance,
                service_id=service_id,
                user_id=int(user_id) if user_id else None,
                instance_id=int(instance_id) if instance_id is not None else None,
                spec=spec,
                index=index,
            )
            if step.get("error"):
                return FsmResult(new_state="FAILED", last_error=step["error"])
            domain_context = step["domain_context"]
            companion_payloads.append(step["payload"])
            for key in ("notify", "cancel_instances", "entity_states"):
                side_effects[key].extend(step.get(key) or [])

        payload: dict[str, Any] = {
            "transition_id": selected.id,
            "from_state": selected.from_state,
            "to_state": selected.to_state,
            "event_name": event_name,
            "entity_type": str(entity_type),
            "entity_id": entity_id,
            "effect": effect_payload,
            "companions": companion_payloads,
        }
        for key, vals in side_effects.items():
            if vals:
                payload[key] = vals

        return FsmResult(
            new_state="COMPLETED",
            attempts_increment=1,
            payload=payload,
        )

    def _run_companion(
        self,
        *,
        session_platform: SessionLike,
        session_domain: SessionLike,
        session_graph: SessionLike,
        db: Any,
        domain_context: dict[str, Any],
        instance: InstanceDict,
        service_id: str,
        user_id: Optional[int],
        instance_id: Optional[int],
        spec: Any,
        index: int,
    ) -> dict[str, Any]:
        if not isinstance(spec, dict):
            return {
                "error": (
                    f"{FsmErrorCodes.INVALID_COMPANION}: "
                    f"index={index} must be object"
                )
            }

        c_entity_type = spec.get("entity_type")
        c_event = spec.get("event_name")
        id_key = spec.get("entity_id_key")
        if not c_entity_type or not c_event or not id_key:
            return {
                "error": (
                    f"{FsmErrorCodes.INVALID_COMPANION}: "
                    f"index={index} requires entity_type, event_name, entity_id_key"
                )
            }

        raw_id = (domain_context or {}).get(str(id_key))
        if raw_id is None or str(raw_id).strip() == "":
            return {
                "error": (
                    f"{FsmErrorCodes.COMPANION_ENTITY_ID_MISSING}: "
                    f"index={index} key={id_key}"
                )
            }
        try:
            c_entity_id = int(raw_id)
        except (TypeError, ValueError):
            return {
                "error": (
                    f"{FsmErrorCodes.COMPANION_ENTITY_ID_MISSING}: "
                    f"index={index} key={id_key} invalid={raw_id!r}"
                )
            }

        result = self._run_entity_step(
            session_platform=session_platform,
            session_domain=session_domain,
            session_graph=session_graph,
            db=db,
            domain_context=domain_context,
            instance=instance,
            service_id=service_id,
            entity_type=str(c_entity_type),
            entity_id=c_entity_id,
            event_name=str(c_event),
            user_id=user_id,
            instance_id=instance_id,
            role=f"companion[{index}]",
        )
        if result.get("error"):
            return {
                "error": (
                    f"{FsmErrorCodes.COMPANION_FAILED}: "
                    f"index={index} {c_entity_type}/{c_entity_id}/{c_event}: "
                    f"{result['error']}"
                )
            }

        selected: TransitionDef = result["selected"]
        return {
            "domain_context": result["domain_context"],
            "payload": {
                "index": index,
                "entity_type": str(c_entity_type),
                "entity_id": c_entity_id,
                "transition_id": selected.id,
                "from_state": selected.from_state,
                "to_state": selected.to_state,
                "event_name": str(c_event),
                "effect": result["effect_payload"],
            },
            "notify": list(result.get("notify") or []),
            "cancel_instances": list(result.get("cancel_instances") or []),
            "entity_states": list(result.get("entity_states") or []),
        }

    def _run_entity_step(
        self,
        *,
        session_platform: SessionLike,
        session_domain: SessionLike,
        session_graph: SessionLike,
        db: Any,
        domain_context: dict[str, Any],
        instance: InstanceDict,
        service_id: str,
        entity_type: str,
        entity_id: int,
        event_name: str,
        user_id: Optional[int],
        instance_id: Optional[int],
        role: str,
    ) -> dict[str, Any]:
        """
        Один entity-pipeline: state → candidates → guards → apply → effect.
        Возвращает dict с selected / domain_context / effect_payload или error.
        """
        _ = role
        # FOR UPDATE: сериализация двух инстансов одной сущности до конца tx.
        current_state = self._state_store.get(
            session_platform,
            service_id,
            entity_type,
            entity_id,
            for_update=True,
        )
        if current_state is None:
            return {
                "error": (
                    f"{FsmErrorCodes.ENTITY_STATE_NOT_FOUND}: "
                    f"{entity_type}/{entity_id}"
                )
            }

        gv_raw = instance.get("graph_version")
        try:
            graph_version = int(gv_raw) if gv_raw is not None else None
        except (TypeError, ValueError):
            graph_version = None
        if graph_version is None:
            graph_version = self._repo.current_graph_version(session_graph)
        candidates = self._repo.list_candidates(
            session_graph,
            entity_type,
            current_state,
            event_name,
            graph_version=graph_version,
        )
        if not candidates:
            return {
                "error": (
                    f"{FsmErrorCodes.NO_CANDIDATE_TRANSITIONS}: "
                    f"{entity_type}/{current_state}/{event_name}"
                )
            }

        seen_priority: dict[int, int] = {}
        for c in candidates:
            if c.priority in seen_priority:
                return {
                    "error": (
                        f"{FsmErrorCodes.AMBIGUOUS_TRANSITION}: "
                        f"{entity_type}/{current_state}/{event_name}/"
                        f"priority={c.priority}"
                    )
                }
            seen_priority[c.priority] = c.id

        selected = None
        last_reason: Optional[str] = None
        for candidate in candidates:
            guard_name = candidate.guard_name
            if guard_name is None or str(guard_name).strip() == "":
                selected = candidate
                break
            guard_fn = self._guards.get(service_id, str(guard_name))
            if guard_fn is None:
                return {
                    "error": f"{FsmErrorCodes.UNKNOWN_GUARD}: {guard_name}"
                }
            from fsm_platform.host.contract_invoke import call_guard

            result = normalize_guard_result(
                call_guard(
                    guard_fn,
                    context=domain_context,
                    guard_params=candidate.guard_params or {},
                    instance=instance,
                )
            )
            if result.ok:
                selected = candidate
                break
            last_reason = result.reason
            logger.warning(
                "guard rejected transition_id=%s guard=%s reason=%s",
                candidate.id,
                guard_name,
                result.reason,
            )

        if selected is None:
            suffix = f" ({last_reason})" if last_reason else ""
            return {
                "error": (
                    f"{FsmErrorCodes.NO_GUARD_MATCHED}: "
                    f"{entity_type}/{current_state}/{event_name}{suffix}"
                )
            }

        try:
            self._executor.apply(
                session_platform,
                service_id=service_id,
                entity_type=entity_type,
                entity_id=entity_id,
                transition=selected,
                event_name=event_name,
                user_id=user_id,
                instance_id=instance_id,
            )
        except TransitionApplyError as exc:
            return {"error": f"{exc.code}: {exc}"}
        except Exception as exc:  # noqa: BLE001
            logger.exception("transition apply failed")
            return {"error": f"{FsmErrorCodes.APPLY_FAILED}: {exc}"}

        # Декларативный timeout нового state (граф fsm_states.timeout_*).
        try:
            from fsm_platform.host.state_timeouts import reschedule_after_transition

            reschedule_after_transition(
                session_platform,
                session_graph,
                service_id=service_id,
                entity_type=entity_type,
                entity_id=entity_id,
                to_state=selected.to_state,
                actor_id=user_id,
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "state timeout reschedule failed entity=%s/%s state=%s",
                entity_type,
                entity_id,
                selected.to_state,
            )

        domain_context = {
            **(domain_context or {}),
            "from_state": selected.from_state,
            "to_state": selected.to_state,
            "transition_id": selected.id,
            "event_name": event_name,
            "applied_entity_type": entity_type,
            "applied_entity_id": entity_id,
        }

        effect_payload = None
        notify: list = []
        cancel_instances: list = []
        entity_states: list = []
        if selected.effect_name:
            effect_fn = self._effects.get(service_id, selected.effect_name)
            if effect_fn is None:
                return {
                    "error": (
                        f"{FsmErrorCodes.UNKNOWN_EFFECT}: {selected.effect_name}"
                    )
                }
            try:
                from fsm_platform.host.contract_invoke import call_effect

                effect_result = normalize_effect_result(
                    call_effect(
                        effect_fn,
                        context=domain_context,
                        effect_params=_effect_params_for_call(selected.effect_params),
                        instance=instance,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("effect failed")
                return {"error": f"{FsmErrorCodes.EFFECT_FAILED}: {exc}"}
            if not effect_result.ok:
                return {
                    "error": (
                        f"{FsmErrorCodes.EFFECT_FAILED}: "
                        f"{effect_result.error or selected.effect_name}"
                    )
                }
            effect_payload = effect_result.payload
            notify = list(effect_result.notify or [])
            cancel_instances = list(effect_result.cancel_instances or [])
            entity_states = list(effect_result.entity_states or [])

        return {
            "selected": selected,
            "domain_context": domain_context,
            "effect_payload": effect_payload,
            "notify": notify,
            "cancel_instances": cancel_instances,
            "entity_states": entity_states,
        }

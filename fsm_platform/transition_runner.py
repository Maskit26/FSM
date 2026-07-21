"""Один декларативный шаг FSM: контекст → кандидаты → guards → apply → effect."""

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
    normalize_effect_result,
    normalize_guard_result,
)

logger = logging.getLogger(__name__)


class TransitionRunner:
    """Выполняет полный цикл одного перехода FSM для экземпляра процесса. Инкапсулирует выбор transition, guards, apply и effect."""

    def __init__(
        self,
        guard_registry: GuardRegistry,
        effect_registry: EffectRegistry,
        state_store: EntityStateStore,
        transition_repository: TransitionRepository,
        transition_executor: TransitionExecutor,
    ) -> None:
        """Собирает runner из реестров, хранилища состояния и исполнителя переходов. Зависимости передаются снаружи для тестов и кастомизации."""
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
    ) -> FsmResult:
        """Выполняет один шаг FSM и возвращает FsmResult с COMPLETED или FAILED. Вызывается воркером для каждого захваченного server_fsm_instances."""
        service_id = str(instance["service_id"])
        instance_id = instance.get("id")

        # 1. CONTEXT
        try:
            if process_def.context_builder is not None:
                domain_context = process_def.context_builder(
                    session_domain, db, runtime_ctx, instance
                )
            else:
                domain_context = {}
        except Exception as exc:  # noqa: BLE001 — boundary: return FAILED
            logger.exception("context_builder failed")
            return FsmResult(
                new_state="FAILED",
                last_error=f"{FsmErrorCodes.CONTEXT_BUILD_FAILED}: {exc}",
            )

        # 2. IDENTIFIERS
        entity_type = process_def.entity_type or instance.get("entity_type")
        entity_id = instance.get("entity_id")
        event_name = process_def.runtime_event_name
        user_id = instance.get("requested_by_user_id") or 0

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

        # 3. CURRENT STATE
        current_state = self._state_store.get(
            session_platform, service_id, str(entity_type), entity_id
        )
        if current_state is None:
            return FsmResult(
                new_state="FAILED",
                last_error=(
                    f"{FsmErrorCodes.ENTITY_STATE_NOT_FOUND}: "
                    f"{entity_type}/{entity_id}"
                ),
            )

        # 4. CANDIDATES
        candidates = self._repo.list_candidates(
            session_domain, str(entity_type), current_state, event_name
        )
        if not candidates:
            return FsmResult(
                new_state="FAILED",
                last_error=(
                    f"{FsmErrorCodes.NO_CANDIDATE_TRANSITIONS}: "
                    f"{entity_type}/{current_state}/{event_name}"
                ),
            )

        # 5. PRIORITY uniqueness
        seen_priority: dict[int, int] = {}
        for c in candidates:
            if c.priority in seen_priority:
                return FsmResult(
                    new_state="FAILED",
                    last_error=(
                        f"{FsmErrorCodes.AMBIGUOUS_TRANSITION}: "
                        f"{entity_type}/{current_state}/{event_name}/priority={c.priority}"
                    ),
                )
            seen_priority[c.priority] = c.id

        # 6. SELECT (guards) — §4.4
        selected = None
        last_reason: Optional[str] = None
        for candidate in candidates:
            guard_name = candidate.guard_name
            if guard_name is None or str(guard_name).strip() == "":
                selected = candidate
                break
            guard_fn = self._guards.get(service_id, str(guard_name))
            if guard_fn is None:
                return FsmResult(
                    new_state="FAILED",
                    last_error=f"{FsmErrorCodes.UNKNOWN_GUARD}: {guard_name}",
                )
            result = normalize_guard_result(
                guard_fn(
                    session_domain,
                    db,
                    domain_context,
                    instance,
                    candidate.guard_params or {},
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
            return FsmResult(
                new_state="FAILED",
                last_error=(
                    f"{FsmErrorCodes.NO_GUARD_MATCHED}: "
                    f"{entity_type}/{current_state}/{event_name}{suffix}"
                ),
            )

        # 7. SQL TRANSITION (platform)
        try:
            self._executor.apply(
                session_platform,
                service_id=service_id,
                entity_type=str(entity_type),
                entity_id=entity_id,
                transition=selected,
                event_name=event_name,
                user_id=int(user_id) if user_id else None,
                instance_id=int(instance_id) if instance_id is not None else None,
            )
        except TransitionApplyError as exc:
            return FsmResult(
                new_state="FAILED",
                last_error=f"{exc.code}: {exc}",
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("transition apply failed")
            return FsmResult(
                new_state="FAILED",
                last_error=f"{FsmErrorCodes.APPLY_FAILED}: {exc}",
            )

        # 8. EFFECT
        effect_payload = None
        if selected.effect_name:
            effect_fn = self._effects.get(service_id, selected.effect_name)
            if effect_fn is None:
                return FsmResult(
                    new_state="FAILED",
                    last_error=f"{FsmErrorCodes.UNKNOWN_EFFECT}: {selected.effect_name}",
                )
            try:
                effect_result = normalize_effect_result(
                    effect_fn(
                        session_domain,
                        db,
                        domain_context,
                        instance,
                        selected.effect_params or {},
                    )
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("effect failed")
                return FsmResult(
                    new_state="FAILED",
                    last_error=f"{FsmErrorCodes.EFFECT_FAILED}: {exc}",
                )
            if not effect_result.ok:
                return FsmResult(
                    new_state="FAILED",
                    last_error=(
                        f"{FsmErrorCodes.EFFECT_FAILED}: "
                        f"{effect_result.error or selected.effect_name}"
                    ),
                )
            effect_payload = effect_result.payload

        # 9. SUCCESS
        return FsmResult(
            new_state="COMPLETED",
            attempts_increment=1,
            payload={
                "transition_id": selected.id,
                "from_state": selected.from_state,
                "to_state": selected.to_state,
                "event_name": event_name,
                "effect": effect_payload,
            },
        )

"""Точка входа воркера: разрешение ProcessDef и один шаг TransitionRunner."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .db_layer import SessionLike
from .errors import FsmErrorCodes
from .registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from .state_store import EntityStateStore
from .transition_executor import TransitionExecutor
from .transition_repository import TransitionRepository
from .transition_runner import TransitionRunner
from .types import FsmResult, InstanceDict, RuntimeContext

logger = logging.getLogger(__name__)

_ALLOWED_INSTANCE_STATES = frozenset({"COMPLETED", "FAILED"})


def run_instance(
    session_platform: SessionLike,
    session_domain: Optional[SessionLike],
    db: Any,
    runtime_ctx: RuntimeContext,
    instance: InstanceDict,
    *,
    process_registry: Optional[ProcessRegistry] = None,
    guard_registry: Optional[GuardRegistry] = None,
    effect_registry: Optional[EffectRegistry] = None,
    state_store: Optional[EntityStateStore] = None,
    transition_repository: Optional[TransitionRepository] = None,
    transition_executor: Optional[TransitionExecutor] = None,
    session_graph: Optional[SessionLike] = None,
) -> FsmResult:
    """Запускает один шаг FSM для server_fsm_instances и возвращает FsmResult. Главная функция движка, вызываемая воркером после claim_pending_instance."""
    process_registry = process_registry or default_process_registry
    guard_registry = guard_registry or default_guard_registry
    effect_registry = effect_registry or default_effect_registry

    service_id = instance.get("service_id")
    process_name = instance.get("process_name")

    if not process_name:
        return FsmResult(
            new_state="FAILED",
            last_error=FsmErrorCodes.MISSING_PROCESS_NAME,
        )
    if not service_id:
        return FsmResult(
            new_state="FAILED",
            last_error=f"{FsmErrorCodes.UNKNOWN_PROCESS}: missing service_id",
        )

    process_def = process_registry.get(str(service_id), str(process_name))
    if process_def is None:
        logger.error("unknown process %s/%s", service_id, process_name)
        return FsmResult(
            new_state="FAILED",
            last_error=f"{FsmErrorCodes.UNKNOWN_PROCESS}: {service_id}/{process_name}",
        )

    runner = TransitionRunner(
        guard_registry=guard_registry,
        effect_registry=effect_registry,
        state_store=state_store or EntityStateStore(),
        transition_repository=transition_repository or TransitionRepository(),
        transition_executor=transition_executor or TransitionExecutor(),
    )

    from fsm_platform.host.runtime_context import service_scope

    with service_scope(str(service_id)):
        result = runner.run(
            session_platform,
            session_domain,
            db,
            runtime_ctx,
            instance,
            process_def,
            session_graph=session_graph,
        )

    if result.new_state not in _ALLOWED_INSTANCE_STATES:
        return FsmResult(
            new_state="FAILED",
            last_error=result.last_error or FsmErrorCodes.INVALID_STATE_RETURNED,
            attempts_increment=result.attempts_increment,
            payload=result.payload,
        )
    return result

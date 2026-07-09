from __future__ import annotations

from typing import Any, Dict

from fsm_core.registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from fsm_core.types import ProcessDef
from fsm_engine import PROCESS_DEFS

from .context import build_courier_context
from .effects import noop_effect
from .guards import always_allow

SERVICE_NAME = "courier"


def _legacy_process_handler(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
) -> Any:
    process_name = instance["process_name"]
    fsm_state = instance["fsm_state"]
    process_handlers = PROCESS_DEFS.get(process_name)
    if not process_handlers:
        raise RuntimeError(f"UNKNOWN_PROCESS: {process_name}")
    handler = process_handlers.get(fsm_state)
    if not handler:
        raise RuntimeError(f"NO_HANDLER_FOR_STATE_{fsm_state}_IN_{process_name}")
    return handler(db, session, context, instance)


def register_all(
    process_registry: ProcessRegistry = default_process_registry,
    guard_registry: GuardRegistry = default_guard_registry,
    effect_registry: EffectRegistry = default_effect_registry,
) -> ProcessRegistry:
    guard_registry.register("always_allow", always_allow)
    effect_registry.register("noop_effect", noop_effect)

    for process_name in sorted(PROCESS_DEFS):
        process_registry.register(
            ProcessDef(
                service=SERVICE_NAME,
                process_name=process_name,
                event_name=process_name,
                context_builder=build_courier_context,
                handler=_legacy_process_handler,
                metadata={"compatibility": "fsm_engine.PROCESS_DEFS"},
            )
        )

    return process_registry


register_all()

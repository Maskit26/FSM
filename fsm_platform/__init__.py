"""
FSM Platform — продукт целиком.

- ``fsm_platform.core`` — декларативный FSM runtime (в спецификации — fsm_core):
  без HTTP, без импортов домена, без commit.
- ``fsm_platform.host`` — оболочка: engines, worker, boot, OperationRegistry, HTTP.

Публичный API ядра реэкспортируется здесь для коротких импортов доменов:
``from fsm_platform import ProcessDef``.
"""

from fsm_platform.core import (
    EffectRegistry,
    EffectResult,
    EntityStateStore,
    FsmDbLayer,
    FsmErrorCodes,
    FsmResult,
    GuardRegistry,
    GuardResult,
    ProcessDef,
    ProcessRegistry,
    TransitionDef,
    TransitionExecutor,
    TransitionRepository,
    TransitionRunner,
    cancel_timer,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
    run_instance,
    schedule_timer,
)

__all__ = [
    "run_instance",
    "FsmErrorCodes",
    "ProcessRegistry",
    "GuardRegistry",
    "EffectRegistry",
    "default_process_registry",
    "default_guard_registry",
    "default_effect_registry",
    "FsmDbLayer",
    "EntityStateStore",
    "TransitionRepository",
    "TransitionExecutor",
    "TransitionRunner",
    "schedule_timer",
    "cancel_timer",
    "FsmResult",
    "GuardResult",
    "EffectResult",
    "ProcessDef",
    "TransitionDef",
]

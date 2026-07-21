"""
fsm_platform — декларативный FSM runtime (в спецификации — fsm_core).

Только для воркера: без HTTP, без импортов домена и без commit.
"""

from .engine import run_instance
from .errors import FsmErrorCodes
from .registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from .db_layer import FsmDbLayer
from .state_store import EntityStateStore
from .timers import cancel_timer, schedule_timer
from .transition_executor import TransitionExecutor
from .transition_repository import TransitionRepository
from .transition_runner import TransitionRunner
from .types import (
    EffectResult,
    FsmResult,
    GuardResult,
    ProcessDef,
    TransitionDef,
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

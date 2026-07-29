"""
fsm_platform.core — декларативный FSM runtime (в спецификации — fsm_core).

Только для воркера: без HTTP, без импортов домена и без commit.
"""

from .engine import run_instance
from .errors import FsmErrorCodes
from .http_client import ApiResponse, ExternalApiError, call_api
from .registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from .db_layer import FsmDbLayer
from .sagas import on_child_terminal, start_saga
from .state_store import EntityStateStore
from .timers import schedule_timer
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
    "ApiResponse",
    "ExternalApiError",
    "call_api",
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
    "start_saga",
    "on_child_terminal",
    "FsmResult",
    "GuardResult",
    "EffectResult",
    "ProcessDef",
    "TransitionDef",
]

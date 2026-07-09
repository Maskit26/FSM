"""Shared FSM runtime package."""

from .engine import run_instance
from .registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from .types import EffectResult, FsmResult, GuardResult, ProcessDef, TransitionDef

__all__ = [
    "EffectRegistry",
    "EffectResult",
    "FsmResult",
    "GuardRegistry",
    "GuardResult",
    "ProcessDef",
    "ProcessRegistry",
    "TransitionDef",
    "default_effect_registry",
    "default_guard_registry",
    "default_process_registry",
    "run_instance",
]

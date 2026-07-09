from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional


RuntimeContext = Dict[str, Any]
InstanceDict = Dict[str, Any]
ContextBuilder = Callable[[Any, Any, RuntimeContext, InstanceDict], Dict[str, Any]]
ProcessHandler = Callable[[Any, Any, Dict[str, Any], InstanceDict], Any]
GuardFunction = Callable[[Any, Any, Dict[str, Any], InstanceDict, Dict[str, Any]], Any]
EffectFunction = Callable[[Any, Any, Dict[str, Any], InstanceDict, Dict[str, Any]], Any]


@dataclass
class FsmResult:
    """Runtime result returned to the worker boundary."""

    new_state: str
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1
    payload: Optional[Dict[str, Any]] = None

    @classmethod
    def from_legacy(cls, result: Any) -> "FsmResult":
        """Adapt the old fsm_engine.FsmStepResult without importing legacy code."""

        if isinstance(result, cls):
            return result
        return cls(
            new_state=getattr(result, "new_state", "FAILED"),
            last_error=getattr(result, "last_error", None),
            next_timer_at=getattr(result, "next_timer_at", None),
            attempts_increment=getattr(result, "attempts_increment", 1),
            payload=getattr(result, "payload", None),
        )


@dataclass
class GuardResult:
    ok: bool
    reason: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


@dataclass
class EffectResult:
    ok: bool = True
    error: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


@dataclass
class ProcessDef:
    service: str
    process_name: str
    entity_type: Optional[str] = None
    event_name: Optional[str] = None
    context_builder: Optional[ContextBuilder] = None
    handler: Optional[ProcessHandler] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def runtime_event_name(self) -> str:
        return self.event_name or self.process_name


@dataclass
class TransitionDef:
    id: int
    entity_type: str
    from_state: str
    to_state: str
    event_name: str
    guard_name: Optional[str] = None
    guard_params: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    effect_name: Optional[str] = None
    effect_params: Dict[str, Any] = field(default_factory=dict)

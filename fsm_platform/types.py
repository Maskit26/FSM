"""Контракты между воркером, fsm_platform и доменом (без I/O)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional


RuntimeContext = dict[str, Any]
InstanceDict = dict[str, Any]

# session_domain, db facade, runtime_ctx, instance → context
ContextBuilder = Callable[[Any, Any, RuntimeContext, InstanceDict], dict[str, Any]]
# session_domain, db, context, instance, params → result
GuardFunction = Callable[[Any, Any, dict[str, Any], InstanceDict, dict[str, Any]], Any]
EffectFunction = Callable[[Any, Any, dict[str, Any], InstanceDict, dict[str, Any]], Any]


@dataclass
class FsmResult:
    """Результат шага FSM для воркера: COMPLETED или FAILED (WAITING в v1 не используется)."""

    new_state: str
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1
    payload: Optional[dict[str, Any]] = None


@dataclass
class GuardResult:
    """Нормализованный ответ guard: допущен ли переход и причина отказа."""

    ok: bool
    reason: Optional[str] = None
    payload: Optional[dict[str, Any]] = None


@dataclass
class EffectResult:
    """Нормализованный ответ effect после успешного apply перехода."""

    ok: bool = True
    error: Optional[str] = None
    payload: Optional[dict[str, Any]] = None


@dataclass
class ProcessDef:
    """Декларация FSM-процесса: привязка к service_id, сущности, событию и context_builder."""

    service_id: str
    process_name: str
    entity_type: Optional[str] = None
    event_name: Optional[str] = None
    context_builder: Optional[ContextBuilder] = None
    initial_state: Optional[str] = None

    @property
    def runtime_event_name(self) -> str:
        """Возвращает имя события для поиска transition: event_name или process_name по умолчанию."""
        return self.event_name or self.process_name


@dataclass
class TransitionDef:
    """Описание одного перехода из доменного графа FSM с guard и effect."""

    id: int
    entity_type: str
    from_state: str
    to_state: str
    event_name: str
    guard_name: Optional[str] = None
    guard_params: dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    effect_name: Optional[str] = None
    effect_params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: Any) -> TransitionDef:
        """Собирает TransitionDef из строки SQL (mapping или dict) с известными ключами."""
        data = dict(row) if not isinstance(row, dict) else row

        def _get(*keys: str, default: Any = None) -> Any:
            """Возвращает первое непустое значение из row по списку ключей. Упрощает маппинг разных имён колонок SQL."""
            for k in keys:
                if k in data and data[k] is not None:
                    return data[k]
            return default

        guard_params = _get("guard_params") or {}
        effect_params = _get("effect_params") or {}
        if isinstance(guard_params, str):
            import json

            guard_params = json.loads(guard_params) if guard_params else {}
        if isinstance(effect_params, str):
            import json

            effect_params = json.loads(effect_params) if effect_params else {}

        return cls(
            id=int(_get("id")),
            entity_type=str(_get("entity_type")),
            from_state=str(_get("from_state")),
            to_state=str(_get("to_state")),
            event_name=str(_get("event_name")),
            guard_name=_get("guard_name"),
            guard_params=dict(guard_params or {}),
            priority=int(_get("priority", default=100)),
            effect_name=_get("effect_name"),
            effect_params=dict(effect_params or {}),
        )


def normalize_guard_result(value: Any) -> GuardResult:
    """Приводит произвольный возврат guard к GuardResult. Поддерживает bool, tuple, dict и GuardResult."""
    if isinstance(value, GuardResult):
        return value
    if isinstance(value, bool):
        return GuardResult(ok=value, reason=None if value else "guard_returned_false")
    if isinstance(value, tuple) and len(value) >= 1:
        ok = bool(value[0])
        reason = value[1] if len(value) > 1 else None
        return GuardResult(ok=ok, reason=str(reason) if reason is not None else None)
    if isinstance(value, dict):
        return GuardResult(
            ok=bool(value.get("ok")),
            reason=value.get("reason"),
            payload=value.get("payload"),
        )
    return GuardResult(ok=False, reason="invalid_guard_result")


def normalize_effect_result(value: Any) -> EffectResult:
    """Приводит произвольный возврат effect к EffectResult. Поддерживает bool, dict и EffectResult."""
    if isinstance(value, EffectResult):
        return value
    if isinstance(value, bool):
        return EffectResult(ok=value, error=None if value else "effect_returned_false")
    if isinstance(value, dict):
        return EffectResult(
            ok=bool(value.get("ok", True)),
            error=value.get("error"),
            payload=value.get("payload"),
        )
    return EffectResult(ok=True)

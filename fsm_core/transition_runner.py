from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

from .registry import EffectRegistry, GuardRegistry
from .types import EffectResult, FsmResult, GuardResult, ProcessDef, TransitionDef

logger = logging.getLogger(__name__)


class TransitionRunner:
    """RFC-pipeline для одного server_fsm_instance (без знания о доменах)."""

    def __init__(
        self,
        guard_registry: GuardRegistry,
        effect_registry: EffectRegistry,
    ) -> None:
        self.guard_registry = guard_registry
        self.effect_registry = effect_registry

    def run(
        self,
        session: Any,
        db: Any,
        runtime_ctx: Dict[str, Any],
        instance: Dict[str, Any],
        process_def: ProcessDef,
    ) -> FsmResult:
        """Один шаг FSM: context → candidates → guards → SQL transition → effect."""
        domain_context: Dict[str, Any] = {}
        if process_def.context_builder:
            domain_context = process_def.context_builder(session, db, runtime_ctx, instance)

        entity_type = process_def.entity_type or instance.get("entity_type")
        entity_id = instance.get("entity_id")
        user_id = instance.get("requested_by_user_id") or 0
        event_name = process_def.runtime_event_name

        if not entity_type:
            return self._failed("MISSING_ENTITY_TYPE")
        if entity_id is None:
            return self._failed("MISSING_ENTITY_ID")

        current_state = db.get_entity_current_state(session, entity_type, entity_id)
        if not current_state:
            return self._failed(f"ENTITY_STATE_NOT_FOUND: {entity_type}/{entity_id}")

        candidates = [
            self._transition_from_row(row)
            for row in db.get_candidate_transitions(
                session=session,
                entity_type=entity_type,
                current_state=current_state,
                event_name=event_name,
            )
        ]
        if not candidates:
            return self._failed(
                f"NO_CANDIDATE_TRANSITIONS: {entity_type}/{current_state}/{event_name}"
            )

        ambiguous_priority = self._find_ambiguous_priority(candidates)
        if ambiguous_priority is not None:
            return self._failed(
                f"AMBIGUOUS_TRANSITION: {entity_type}/{current_state}/{event_name}/priority={ambiguous_priority}"
            )

        selected = self._select_transition(session, db, domain_context, instance, candidates)
        if isinstance(selected, FsmResult):
            return selected
        if selected is None:
            return self._failed(
                f"NO_GUARD_MATCHED: {entity_type}/{current_state}/{event_name}"
            )

        db.perform_transition(
            session=session,
            entity_type=entity_type,
            entity_id=entity_id,
            transition_id=selected.id,
            event_name=event_name,
            user_id=user_id,
        )

        effect_payload: Optional[Dict[str, Any]] = None
        if selected.effect_name:
            effect = self.effect_registry.get(selected.effect_name)
            if not effect:
                return self._failed(f"UNKNOWN_EFFECT: {selected.effect_name}")
            effect_result = self._normalize_effect_result(
                effect(
                    session,
                    db,
                    domain_context,
                    instance,
                    selected.effect_params,
                )
            )
            if not effect_result.ok:
                return self._failed(effect_result.error or f"EFFECT_FAILED: {selected.effect_name}")
            effect_payload = effect_result.payload

        return FsmResult(
            new_state="COMPLETED",
            attempts_increment=1,
            payload={
                "transition_id": selected.id,
                "from_state": selected.from_state,
                "to_state": selected.to_state,
                "event_name": selected.event_name,
                "effect": effect_payload,
            },
        )

    def _select_transition(
        self,
        session: Any,
        db: Any,
        domain_context: Dict[str, Any],
        instance: Dict[str, Any],
        candidates: Iterable[TransitionDef],
    ) -> Optional[TransitionDef | FsmResult]:
        """Выбрать один transition из candidates (по priority и guards)."""
        last_reason: Optional[str] = None
        for transition in candidates:
            if not transition.guard_name:
                return transition

            guard = self.guard_registry.get(transition.guard_name)
            if not guard:
                return self._failed(f"UNKNOWN_GUARD: {transition.guard_name}")

            guard_result = self._normalize_guard_result(
                guard(
                    session,
                    db,
                    domain_context,
                    instance,
                    transition.guard_params,
                )
            )
            if guard_result.ok:
                return transition
            logger.warning(
                "[FSM_CORE] guard declined transition_id=%s guard=%s reason=%s",
                transition.id,
                transition.guard_name,
                guard_result.reason,
            )
            last_reason = guard_result.reason
        if last_reason:
            return self._failed(f"NO_GUARD_MATCHED: {last_reason}")
        return None

    def _transition_from_row(self, row: Dict[str, Any]) -> TransitionDef:
        """Строка из get_candidate_transitions → TransitionDef."""
        return TransitionDef(
            id=row["id"],
            entity_type=row["entity_type"],
            from_state=row["from_state"],
            to_state=row["to_state"],
            event_name=row["event_name"],
            guard_name=row.get("guard_name"),
            guard_params=row.get("guard_params") or {},
            priority=row.get("priority") or 100,
            effect_name=row.get("effect_name"),
            effect_params=row.get("effect_params") or {},
        )

    def _find_ambiguous_priority(self, candidates: Iterable[TransitionDef]) -> Optional[int]:
        """Вернуть priority, если он повторяется у двух candidates (иначе None)."""
        seen: set[int] = set()
        for transition in candidates:
            if transition.priority in seen:
                return transition.priority
            seen.add(transition.priority)
        return None

    def _normalize_guard_result(self, value: Any) -> GuardResult:
        """Привести ответ guard к GuardResult (bool/tuple тоже допускаются)."""
        if isinstance(value, GuardResult):
            return value
        if isinstance(value, bool):
            return GuardResult(ok=value)
        if isinstance(value, tuple):
            ok = bool(value[0]) if value else False
            reason = str(value[1]) if len(value) > 1 and value[1] else None
            return GuardResult(ok=ok, reason=reason)
        return GuardResult(ok=bool(value))

    def _normalize_effect_result(self, value: Any) -> EffectResult:
        """Привести ответ effect к EffectResult (bool/tuple/dict тоже допускаются)."""
        if isinstance(value, EffectResult):
            return value
        if isinstance(value, bool):
            return EffectResult(ok=value)
        if isinstance(value, tuple):
            ok = bool(value[0]) if value else False
            error = str(value[1]) if len(value) > 1 and value[1] else None
            return EffectResult(ok=ok, error=error)
        return EffectResult(ok=True, payload=value if isinstance(value, dict) else None)

    def _failed(self, error: str) -> FsmResult:
        """Штатная ошибка шага; worker обработает FAILED и last_error."""
        return FsmResult(
            new_state="FAILED",
            last_error=error,
            attempts_increment=1,
        )

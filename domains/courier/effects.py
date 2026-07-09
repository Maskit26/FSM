from __future__ import annotations

from typing import Any, Dict

from fsm_core.types import EffectResult


def noop_effect(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    return EffectResult(ok=True)

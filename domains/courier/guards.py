from __future__ import annotations

from typing import Any, Dict

from fsm_core.types import GuardResult


def always_allow(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> GuardResult:
    return GuardResult(ok=True)

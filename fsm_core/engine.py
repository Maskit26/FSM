from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .registry import (
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from .transition_runner import TransitionRunner
from .types import FsmResult

logger = logging.getLogger(__name__)


def run_instance(
    session: Any,
    db: Any,
    runtime_ctx: Dict[str, Any],
    instance: Dict[str, Any],
    registry: Optional[ProcessRegistry] = None,
) -> FsmResult:
    process_registry = registry or default_process_registry
    service = instance.get("service") or "courier"
    process_name = instance.get("process_name")

    if not process_name:
        return FsmResult(
            new_state="FAILED",
            last_error="MISSING_PROCESS_NAME",
            attempts_increment=1,
        )

    process_def = process_registry.get(service, process_name)
    if not process_def:
        logger.error("[FSM_CORE] unknown process service=%s process=%s", service, process_name)
        return FsmResult(
            new_state="FAILED",
            last_error=f"UNKNOWN_PROCESS: {service}/{process_name}",
            attempts_increment=1,
        )

    runner = TransitionRunner(
        guard_registry=default_guard_registry,
        effect_registry=default_effect_registry,
    )
    result = runner.run(session, db, runtime_ctx, instance, process_def)

    if result.new_state not in ("COMPLETED", "FAILED", "WAITING", "PROCESSING", "PENDING"):
        logger.warning("[FSM_CORE] invalid result state=%s", result.new_state)
        result.new_state = "FAILED"
        result.last_error = result.last_error or "INVALID_STATE_RETURNED"

    return result

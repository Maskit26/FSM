from __future__ import annotations

from typing import Any, Dict

from adapter.core_adapter import CoreAdapter
from fsm_engine import build_actions_context


def build_courier_context(
    session: Any,
    db: Any,
    runtime_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> Dict[str, Any]:
    """Build legacy action context for the courier domain.

    The MVP keeps existing action classes intact while moving process lookup to
    the platform registry.
    """

    core_adapter = runtime_ctx.get("core_adapter")
    if core_adapter is None:
        core_adapter = CoreAdapter(core_url="", core_api_key="", core_timeout=5)
    return build_actions_context(db, core_adapter)

from __future__ import annotations

from typing import Any, Dict


def build_courier_context(
    session: Any,
    db: Any,
    runtime_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> Dict[str, Any]:
    """Собрать domain context для guards/effects courier-домена."""
    return {}

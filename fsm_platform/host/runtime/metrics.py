"""Снимки очередей platform для /v1/metrics (через db_layer)."""

from __future__ import annotations

from typing import Any

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.runtime.engines import platform_session


def collect_platform_metrics() -> dict[str, Any]:
    """Агрегаты по instances / outbox / reconcile / timers."""
    sp = platform_session()
    try:
        return default_db_layer.collect_platform_queue_metrics(sp)
    finally:
        sp.close()

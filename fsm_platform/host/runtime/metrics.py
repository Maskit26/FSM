"""Снимки очередей platform для /v1/metrics (через db_layer)."""

from __future__ import annotations

import os
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


def collect_tenant_metrics(service_id: str) -> dict[str, Any]:
    """Ops-снимок одного service_id."""
    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id required")
    sp = platform_session()
    try:
        return default_db_layer.collect_tenant_queue_metrics(sp, sid)
    finally:
        sp.close()


def _stale_pending_seconds() -> int:
    raw = (os.environ.get("WORKER_QUEUE_STALE_SECONDS") or "20").strip()
    try:
        return max(5, int(raw))
    except ValueError:
        return 20


def enrich_worker_status(service_id: str, process: dict[str, Any]) -> dict[str, Any]:
    """
    Добавляет queue snapshot, полный metrics и health для ЛК-монитора.
    failed: процесс не running, либо due PENDING старше порога (воркер не claim'ит).
    """
    out = dict(process)
    sid = str(service_id or "").strip()
    process_status = str(out.get("status") or "unknown")
    queue: dict[str, Any] = {
        "pending": 0,
        "processing": 0,
        "oldest_due_pending_age_seconds": None,
    }
    metrics: dict[str, Any] | None = None
    try:
        sp = platform_session()
        try:
            metrics = default_db_layer.collect_tenant_queue_metrics(sp, sid)
            inst = metrics.get("instances") or {}
            queue = {
                "pending": int(inst.get("pending") or 0),
                "processing": int(inst.get("processing") or 0),
                "oldest_due_pending_age_seconds": inst.get(
                    "oldest_due_pending_age_seconds"
                ),
                "failed_1h": int(inst.get("failed_1h") or 0),
            }
        finally:
            sp.close()
    except Exception as exc:
        out["queue_error"] = str(exc)
        out["health"] = "failed"
        out["ok"] = False
        out["reason"] = "queue_unavailable"
        out["display_status"] = "failed"
        out["queue"] = queue
        return out

    out["queue"] = queue
    out["metrics"] = metrics
    pending = int(queue.get("pending") or 0)
    age = queue.get("oldest_due_pending_age_seconds")
    stale_after = _stale_pending_seconds()
    queue_stale = (
        pending > 0 and age is not None and int(age) >= stale_after
    )

    if process_status not in ("running", "started"):
        out["health"] = "failed"
        out["ok"] = False
        out["reason"] = "not_running"
        out["display_status"] = "failed"
    elif queue_stale:
        out["health"] = "failed"
        out["ok"] = False
        out["reason"] = "queue_stale"
        out["display_status"] = "failed"
    else:
        out["health"] = "ok"
        out["ok"] = True
        out["reason"] = None
        out["display_status"] = "running"
    return out

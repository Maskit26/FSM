"""Platform readiness probes (≠ liveness /health)."""

from __future__ import annotations

import os
from typing import Any, Optional

from sqlalchemy import text

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.runtime.engines import platform_session
from fsm_platform.host.tenant.domain_bootstrap import is_domain_ready


def _optional_nonneg_env(name: str) -> Optional[int]:
    """None = check disabled (env unset/empty)."""
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return max(0, int(raw))
    except ValueError:
        return None


def _pending_age_limit() -> Optional[int]:
    """Default 300s when unset. Set READY_MAX_PENDING_AGE_SECONDS=0 to disable."""
    raw = (os.environ.get("READY_MAX_PENDING_AGE_SECONDS") or "").strip()
    if raw == "":
        return 300
    try:
        v = int(raw)
    except ValueError:
        return 300
    return None if v <= 0 else v


def check_platform_ready() -> dict[str, Any]:
    """
    Liveness не трогаем. Ready = можно пускать трафик на Platform API.
    200 если ok=True, иначе 503.
    """
    checks: dict[str, Any] = {}
    ok = True

    try:
        sp = platform_session()
        try:
            sp.execute(text("SELECT 1"))
            checks["platform_db"] = {"ok": True}
            metrics = default_db_layer.collect_platform_queue_metrics(sp)
        finally:
            sp.close()
    except Exception as exc:
        return {
            "status": "not_ready",
            "ok": False,
            "checks": {
                "platform_db": {"ok": False, "error": str(exc)},
            },
        }

    inst = metrics.get("instances") or {}
    outbox = metrics.get("outbox") or {}
    reconcile = metrics.get("reconcile") or {}

    age = inst.get("oldest_due_pending_age_seconds")
    age_limit = _pending_age_limit()
    if age_limit is None:
        checks["pending_age"] = {
            "ok": True,
            "skipped": True,
            "oldest_due_pending_age_seconds": age,
            "pending": int(inst.get("pending") or 0),
        }
    else:
        age_ok = age is None or int(age) <= age_limit
        if not age_ok:
            ok = False
        checks["pending_age"] = {
            "ok": age_ok,
            "oldest_due_pending_age_seconds": age,
            "limit_seconds": age_limit,
            "pending": int(inst.get("pending") or 0),
        }

    outbox_limit = _optional_nonneg_env("READY_MAX_OUTBOX_DEAD")
    dead_outbox = int(outbox.get("dead") or 0)
    if outbox_limit is None:
        checks["outbox_dead"] = {
            "ok": True,
            "skipped": True,
            "dead": dead_outbox,
        }
    else:
        outbox_ok = dead_outbox <= outbox_limit
        if not outbox_ok:
            ok = False
        checks["outbox_dead"] = {
            "ok": outbox_ok,
            "dead": dead_outbox,
            "limit": outbox_limit,
        }

    rec_limit = _optional_nonneg_env("READY_MAX_RECONCILE_DEAD")
    dead_rec = int(reconcile.get("dead") or 0)
    if rec_limit is None:
        checks["reconcile_dead"] = {
            "ok": True,
            "skipped": True,
            "dead": dead_rec,
        }
    else:
        rec_ok = dead_rec <= rec_limit
        if not rec_ok:
            ok = False
        checks["reconcile_dead"] = {
            "ok": rec_ok,
            "dead": dead_rec,
            "limit": rec_limit,
        }

    return {
        "status": "ready" if ok else "not_ready",
        "ok": ok,
        "checks": checks,
    }


def check_tenant_ready(service_id: str) -> dict[str, Any]:
    """
    Tenant probe: domain catalog + worker process + очередь instances.
    """
    sid = str(service_id or "").strip()
    checks: dict[str, Any] = {}
    ok = True

    domain_ok = is_domain_ready(sid)
    checks["domain"] = {"ok": domain_ok, "ready": domain_ok}
    if not domain_ok:
        ok = False

    try:
        from fsm_platform.host.runtime.metrics import enrich_worker_status
        from fsm_platform.host.workers.worker_provisioner import worker_status

        worker = enrich_worker_status(sid, worker_status(sid))
    except Exception as exc:
        worker = {
            "status": "unknown",
            "health": "failed",
            "ok": False,
            "reason": str(exc),
        }
    worker_ok = bool(worker.get("ok"))
    checks["worker"] = {
        "ok": worker_ok,
        "status": worker.get("status"),
        "health": worker.get("health"),
        "reason": worker.get("reason"),
        "queue": worker.get("queue"),
    }
    if not worker_ok:
        ok = False

    try:
        sp = platform_session()
        try:
            sp.execute(text("SELECT 1"))
            checks["platform_db"] = {"ok": True}
        finally:
            sp.close()
    except Exception as exc:
        checks["platform_db"] = {"ok": False, "error": str(exc)}
        ok = False

    return {
        "service_id": sid,
        "status": "ready" if ok else "not_ready",
        "ok": ok,
        "checks": checks,
    }

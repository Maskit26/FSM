"""Снимки очередей platform для /v1/metrics."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from fsm_platform.host.engines import platform_session


def collect_platform_metrics() -> dict[str, Any]:
    """Агрегаты по instances / outbox / reconcile / timers."""
    sp = platform_session()
    try:
        instances = {
            str(r["status"]): int(r["n"])
            for r in sp.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM server_fsm_instances
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        oldest_pending = sp.execute(
            text(
                """
                SELECT TIMESTAMPDIFF(SECOND, MIN(created_at), UTC_TIMESTAMP()) AS age_s
                FROM server_fsm_instances
                WHERE status = 'PENDING'
                  AND (next_attempt_at IS NULL
                       OR next_attempt_at <= UTC_TIMESTAMP())
                """
            )
        ).scalar()
        failed_1h = sp.execute(
            text(
                """
                SELECT COUNT(*) FROM server_fsm_instances
                WHERE status = 'FAILED'
                  AND finished_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 HOUR)
                """
            )
        ).scalar()
        outbox = {
            str(r["status"]): int(r["n"])
            for r in sp.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM platform_outbox
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        oldest_outbox = sp.execute(
            text(
                """
                SELECT TIMESTAMPDIFF(SECOND, MIN(created_at), UTC_TIMESTAMP()) AS age_s
                FROM platform_outbox
                WHERE status = 'PENDING'
                  AND next_attempt_at <= UTC_TIMESTAMP()
                """
            )
        ).scalar()
        reconcile = {
            str(r["status"]): int(r["n"])
            for r in sp.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM platform_reconcile_queue
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        timers_due = sp.execute(
            text(
                """
                SELECT COUNT(*) FROM fsm_timers
                WHERE status = 'SCHEDULED'
                  AND fire_at <= UTC_TIMESTAMP()
                """
            )
        ).scalar()
        return {
            "instances": {
                "by_status": instances,
                "pending": int(instances.get("PENDING") or 0),
                "processing": int(instances.get("PROCESSING") or 0),
                "failed_1h": int(failed_1h or 0),
                "oldest_due_pending_age_seconds": int(oldest_pending or 0)
                if oldest_pending is not None
                else None,
            },
            "outbox": {
                "by_status": outbox,
                "pending": int(outbox.get("PENDING") or 0),
                "dead": int(outbox.get("DEAD") or 0),
                "oldest_due_pending_age_seconds": int(oldest_outbox or 0)
                if oldest_outbox is not None
                else None,
            },
            "reconcile": {
                "by_status": reconcile,
                "pending": int(reconcile.get("PENDING") or 0),
                "dead": int(reconcile.get("DEAD") or 0),
            },
            "timers": {"due_scheduled": int(timers_due or 0)},
        }
    finally:
        sp.close()

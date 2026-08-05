"""Kill worker → stale PROCESSING reclaim → очередь снова claim'ится."""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

from fsm_platform.host.workers import worker as worker_mod
from fsm_platform.host.workers import worker_provisioner as wp


class StaleProcessingReclaimTests(unittest.TestCase):
    def setUp(self) -> None:
        worker_mod._last_stale_reclaim_at = 0.0

    def test_reclaim_sql_called_with_service_scope(self) -> None:
        session = MagicMock()
        result = MagicMock()
        result.rowcount = 2
        session.execute.return_value = result

        n = worker_mod.default_db_layer.reclaim_stale_processing_instances(
            session,
            older_than_seconds=120,
            service_id="svc_test",
            limit=50,
        )
        self.assertEqual(n, 2)
        self.assertTrue(session.execute.called)
        kwargs = session.execute.call_args[0][1]
        self.assertEqual(kwargs["service_id"], "svc_test")
        self.assertEqual(kwargs["age"], 120)
        self.assertEqual(kwargs["limit"], 50)

    def test_reclaim_runs_then_claim_sees_pending(self) -> None:
        """Симуляция: после kill остался PROCESSING → reclaim → claim."""
        worker_mod._last_stale_reclaim_at = 0.0
        sp = MagicMock()

        with patch.object(worker_mod, "platform_session", return_value=sp), patch.object(
            worker_mod.default_db_layer,
            "reclaim_stale_processing_instances",
            return_value=1,
        ) as reclaim, patch.object(
            worker_mod, "_fire_due_timers", return_value=False
        ), patch.object(
            worker_mod, "_fire_due_schedules", return_value=False
        ), patch.object(
            worker_mod.default_db_layer,
            "claim_pending_instance",
            return_value=None,
        ):
            worked = worker_mod.process_one(service_id="svc_x")

        self.assertFalse(worked)
        reclaim.assert_called_once()
        self.assertEqual(
            reclaim.call_args.kwargs.get("service_id")
            or reclaim.call_args[1].get("service_id"),
            "svc_x",
        )
        sp.commit.assert_called()

    def test_kill_then_restart_provisioner(self) -> None:
        """stop → not running; restart = stop + provision."""
        wp._backends.clear()
        backend = MagicMock()
        backend.stop.return_value = {
            "service_id": "svc_x",
            "status": "stopped",
        }
        backend.status.return_value = {
            "service_id": "svc_x",
            "status": "stopped",
        }
        backend.provision.return_value = {
            "service_id": "svc_x",
            "status": "started",
            "pid": 4242,
        }

        with patch.object(wp, "_get_backend", return_value=backend):
            stopped = wp.stop_worker("svc_x")
            self.assertEqual(stopped["status"], "stopped")
            st = wp.worker_status("svc_x")
            self.assertEqual(st["status"], "stopped")
            started = wp.restart_worker("svc_x")
            self.assertEqual(started["status"], "started")
            backend.stop.assert_called()
            backend.provision.assert_called_with("svc_x")


class ReadyProbeUnitTests(unittest.TestCase):
    def test_ready_db_down(self) -> None:
        from fsm_platform.host.runtime import readiness

        with patch.object(
            readiness, "platform_session", side_effect=RuntimeError("db down")
        ):
            body = readiness.check_platform_ready()
        self.assertFalse(body["ok"])
        self.assertEqual(body["status"], "not_ready")
        self.assertFalse(body["checks"]["platform_db"]["ok"])

    def test_ready_ok_when_db_and_fresh_queue(self) -> None:
        from fsm_platform.host.runtime import readiness

        sp = MagicMock()
        metrics = {
            "instances": {
                "pending": 1,
                "oldest_due_pending_age_seconds": 5,
            },
            "outbox": {"dead": 0},
            "reconcile": {"dead": 0},
        }
        with patch.dict(os.environ, {"READY_MAX_PENDING_AGE_SECONDS": "300"}, clear=False), patch.object(
            readiness, "platform_session", return_value=sp
        ), patch.object(
            readiness.default_db_layer,
            "collect_platform_queue_metrics",
            return_value=metrics,
        ):
            body = readiness.check_platform_ready()
        self.assertTrue(body["ok"])
        self.assertEqual(body["status"], "ready")

    def test_ready_fails_on_stale_pending(self) -> None:
        from fsm_platform.host.runtime import readiness

        sp = MagicMock()
        metrics = {
            "instances": {
                "pending": 3,
                "oldest_due_pending_age_seconds": 999,
            },
            "outbox": {"dead": 0},
            "reconcile": {"dead": 0},
        }
        with patch.dict(os.environ, {"READY_MAX_PENDING_AGE_SECONDS": "300"}, clear=False), patch.object(
            readiness, "platform_session", return_value=sp
        ), patch.object(
            readiness.default_db_layer,
            "collect_platform_queue_metrics",
            return_value=metrics,
        ):
            body = readiness.check_platform_ready()
        self.assertFalse(body["ok"])
        self.assertFalse(body["checks"]["pending_age"]["ok"])


if __name__ == "__main__":
    unittest.main()

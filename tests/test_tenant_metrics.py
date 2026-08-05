"""Tenant metrics snapshot shape."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from fsm_platform.core.db_layer import FsmDbLayer


class TenantMetricsTests(unittest.TestCase):
    def test_collect_tenant_queue_metrics_shape(self) -> None:
        layer = FsmDbLayer()
        session = MagicMock()
        calls: list[str] = []

        def execute(stmt, params=None):
            sql = " ".join(str(stmt).split())
            calls.append(sql)
            mock = MagicMock()
            if "FROM server_fsm_instances" in sql and "GROUP BY status" in sql:
                mock.mappings.return_value = [
                    {"status": "PENDING", "n": 2},
                    {"status": "PROCESSING", "n": 1},
                ]
            elif (
                "FROM server_fsm_instances" in sql
                and "TIMESTAMPDIFF" in sql
                and "PENDING" in sql
            ):
                mock.scalar.return_value = 15
            elif "FROM server_fsm_instances" in sql and "FAILED" in sql:
                mock.scalar.return_value = 3
            elif "FROM platform_outbox" in sql and "GROUP BY status" in sql:
                mock.mappings.return_value = [
                    {"status": "PENDING", "n": 4},
                    {"status": "DEAD", "n": 1},
                ]
            elif "FROM platform_outbox" in sql and "attempts > 0" in sql:
                mock.scalar.return_value = 1
            elif "FROM platform_outbox" in sql and "attempts = 0" in sql:
                mock.scalar.return_value = 3
            elif "FROM fsm_timers" in sql and "INTERVAL 60 SECOND" in sql:
                mock.scalar.return_value = 1
            elif "FROM fsm_timers" in sql:
                mock.scalar.return_value = 2
            elif "FROM platform_reconcile_queue" in sql:
                mock.mappings.return_value = [{"status": "PENDING", "n": 0}]
            else:
                mock.scalar.return_value = 0
                mock.mappings.return_value = []
            return mock

        session.execute.side_effect = execute
        out = layer.collect_tenant_queue_metrics(session, "svc_x")
        self.assertEqual(out["service_id"], "svc_x")
        self.assertEqual(out["instances"]["pending"], 2)
        self.assertEqual(out["instances"]["processing"], 1)
        self.assertEqual(out["instances"]["failed_1h"], 3)
        self.assertEqual(out["instances"]["oldest_due_pending_age_seconds"], 15)
        self.assertEqual(out["outbox"]["dead"], 1)
        self.assertEqual(out["outbox"]["retry"], 1)
        self.assertEqual(out["outbox"]["pending"], 3)
        self.assertEqual(out["timers"]["due"], 2)
        self.assertEqual(out["timers"]["overdue"], 1)
        self.assertGreaterEqual(len(calls), 8)


if __name__ == "__main__":
    unittest.main()

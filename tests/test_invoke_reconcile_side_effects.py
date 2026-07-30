"""Invoke reconcile gate for side-effects-only commands."""

from __future__ import annotations

import unittest

from fsm_platform.host.http.request_runtime import (
    _invoke_needs_reconcile,
    _invoke_reconcile_transition_id,
)


class InvokeReconcileGateTests(unittest.TestCase):
    def test_notify_only_needs_reconcile(self) -> None:
        self.assertTrue(
            _invoke_needs_reconcile({"notify": [{"channel": "telegram", "destination": "1"}]})
        )

    def test_cancel_instances_needs_reconcile(self) -> None:
        self.assertTrue(
            _invoke_needs_reconcile({"cancel_instances": [{"instance_id": 1}]})
        )

    def test_entity_states_needs_reconcile(self) -> None:
        self.assertTrue(
            _invoke_needs_reconcile(
                {"entity_states": [{"entity_type": "order", "entity_id": 1, "state": "x"}]}
            )
        )

    def test_empty_result_does_not(self) -> None:
        self.assertFalse(_invoke_needs_reconcile({"data": {"ok": True}}))

    def test_transition_id_stable_for_side_effects(self) -> None:
        result = {"notify": [{"channel": "telegram"}]}
        a = _invoke_reconcile_transition_id("svc", "ping", result)
        b = _invoke_reconcile_transition_id("svc", "ping", result)
        self.assertEqual(a, b)
        c = _invoke_reconcile_transition_id(
            "svc", "ping", {"notify": [{"channel": "telegram"}, {"channel": "x"}]}
        )
        self.assertNotEqual(a, c)


if __name__ == "__main__":
    unittest.main()

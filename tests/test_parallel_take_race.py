"""Parallel take / CAS race → one win, one STATE_MISMATCH or ALREADY_TAKEN."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from domains.courier.guards import can_assign_executor
from fsm_platform.core.errors import FsmErrorCodes
from fsm_platform.core.transition_executor import (
    TransitionApplyError,
    TransitionExecutor,
)
from fsm_platform.core.types import TransitionDef


def _transition(
    *,
    from_state: str = "order_created",
    to_state: str = "order_courier1_assigned",
) -> TransitionDef:
    return TransitionDef(
        id=1,
        entity_type="order",
        from_state=from_state,
        to_state=to_state,
        event_name="assign_executor",
    )


class ParallelTakeRaceTests(unittest.TestCase):
    def test_second_apply_raises_state_mismatch(self) -> None:
        """Два take: первый CAS ок, второй — STATE_MISMATCH."""
        db = MagicMock()
        states = {"order": "order_created"}

        def get_state(_session, _sid, _et, _eid):
            return states["order"]

        def cas(_session, _sid, _et, _eid, *, from_state, to_state):
            if states["order"] != from_state:
                return False
            states["order"] = to_state
            return True

        db.get_entity_state.side_effect = get_state
        db.cas_entity_state.side_effect = cas
        db.insert_transition_log = MagicMock()

        ex = TransitionExecutor(db_layer=db)
        session = MagicMock()
        tr = _transition()

        ex.apply(
            session,
            service_id="svc_x",
            entity_type="order",
            entity_id=42,
            transition=tr,
            event_name="assign_executor",
            instance_id=1,
        )
        self.assertEqual(states["order"], "order_courier1_assigned")

        with self.assertRaises(TransitionApplyError) as ctx:
            ex.apply(
                session,
                service_id="svc_x",
                entity_type="order",
                entity_id=42,
                transition=tr,
                event_name="assign_executor",
                instance_id=2,
            )
        self.assertEqual(ctx.exception.code, FsmErrorCodes.STATE_MISMATCH)

    def test_cas_lost_race_state_mismatch(self) -> None:
        """current ещё from_state, CAS False (параллельный UPDATE)."""
        db = MagicMock()
        db.get_entity_state.side_effect = [
            "order_created",
            "order_courier1_assigned",
        ]
        db.cas_entity_state.return_value = False
        ex = TransitionExecutor(db_layer=db)
        with self.assertRaises(TransitionApplyError) as ctx:
            ex.apply(
                MagicMock(),
                service_id="svc_x",
                entity_type="order",
                entity_id=7,
                transition=_transition(),
                event_name="assign_executor",
                instance_id=9,
            )
        self.assertEqual(ctx.exception.code, FsmErrorCodes.STATE_MISMATCH)

    def test_assign_guard_already_taken(self) -> None:
        """Слот stage занят → ALREADY_TAKEN (второй курьер на бирже)."""
        ctx = {
            "leg": "pickup",
            "order_id": 10,
            "executor_id": 2,
            "executor": {"role_name": "courier"},
            "executor_city": "msk",
            "locker_city": "msk",
            "cell_id": 5,
            "order": {
                "status": "order_created",
                "pickup_type": "courier",
            },
        }
        params = {
            "leg": "pickup",
            "user_role": "courier",
            "required_status": "order_created",
            "type_field": "pickup_type",
            "type_value": "courier",
            "stage_must_be": "free",
            "require_cell": True,
            "require_city": True,
        }
        with patch(
            "domains.courier.guards.db_layer.is_stage_slot_free",
            return_value=False,
        ):
            result = can_assign_executor(
                MagicMock(), None, ctx, {"entity_id": 10}, params
            )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "ALREADY_TAKEN")


class CallApiTraceHeaderTests(unittest.TestCase):
    def test_timeout_must_be_positive(self) -> None:
        from fsm_platform.core.http_client import ExternalApiError, _resolve_timeout

        self.assertGreater(_resolve_timeout(None), 0)
        with self.assertRaises(ExternalApiError) as ctx:
            _resolve_timeout(0)
        self.assertEqual(ctx.exception.code, "TIMEOUT_INVALID")

    def test_merge_correlation_and_idempotency(self) -> None:
        from fsm_platform.core.http_client import _merge_trace_headers
        from fsm_platform.host.runtime.correlation import (
            CorrelationEnvelope,
            bind_envelope,
            reset_envelope,
        )

        env = CorrelationEnvelope(
            command_id="cmd-1",
            correlation_id="corr-9",
            causation_id="cause-2",
        )
        token = bind_envelope(env)
        try:
            headers = _merge_trace_headers(
                {"Accept": "application/json"},
                idempotency_key="idem-77",
            )
            self.assertEqual(headers["X-Correlation-Id"], "corr-9")
            self.assertEqual(headers["X-Command-Id"], "cmd-1")
            self.assertEqual(headers["X-Causation-Id"], "cause-2")
            self.assertEqual(headers["Idempotency-Key"], "idem-77")
            self.assertEqual(headers["Accept"], "application/json")
        finally:
            reset_envelope(token)


if __name__ == "__main__":
    unittest.main()

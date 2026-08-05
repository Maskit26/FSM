"""Correlation envelope resolve / payload / idempotency link."""

from __future__ import annotations

import unittest

from fsm_platform.host.runtime.correlation import (
    PAYLOAD_KEY,
    attach_to_payload,
    bind_envelope,
    envelope_from_payload,
    event_ids_from_envelope,
    merge_into_dict,
    reset_envelope,
    resolve_envelope,
)


class CorrelationEnvelopeTests(unittest.TestCase):
    def test_generate_when_missing(self) -> None:
        env = resolve_envelope()
        self.assertTrue(env.command_id)
        self.assertEqual(env.correlation_id, env.command_id)
        self.assertIsNone(env.causation_id)

    def test_headers_and_body(self) -> None:
        env = resolve_envelope(
            headers={
                "X-Command-Id": "cmd-1",
                "X-Correlation-Id": "corr-9",
                "X-Causation-Id": "cause-2",
            },
            body={"operation": "x"},
        )
        self.assertEqual(env.command_id, "cmd-1")
        self.assertEqual(env.correlation_id, "corr-9")
        self.assertEqual(env.causation_id, "cause-2")

    def test_idempotency_becomes_command_id(self) -> None:
        env = resolve_envelope(idempotency_key="idem-abc")
        self.assertEqual(env.command_id, "idem-abc")
        self.assertEqual(env.correlation_id, "idem-abc")
        self.assertEqual(env.idempotency_key, "idem-abc")

    def test_payload_roundtrip(self) -> None:
        env = resolve_envelope(
            body={"commandId": "c1", "correlationId": "r1", "causationId": "a1"}
        )
        token = bind_envelope(env)
        try:
            payload = attach_to_payload({"leg": "pickup"})
            self.assertIn(PAYLOAD_KEY, payload)
            self.assertEqual(payload["leg"], "pickup")
            back = envelope_from_payload(payload)
            self.assertIsNotNone(back)
            assert back is not None
            self.assertEqual(back.command_id, "c1")
            self.assertEqual(back.correlation_id, "r1")
            self.assertEqual(back.causation_id, "a1")
            pub = merge_into_dict({"ok": True})
            self.assertEqual(pub["correlation"]["commandId"], "c1")
            corr, cmd = event_ids_from_envelope(back)
            self.assertEqual(corr, "r1")
            self.assertEqual(cmd, "c1")
        finally:
            reset_envelope(token)


if __name__ == "__main__":
    unittest.main()

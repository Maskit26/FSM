"""Scoped secret broker unit tests."""

from __future__ import annotations

import base64
import os
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet

from fsm_platform.host.security.secret_broker import (
    SecretBrokerError,
    unwrap,
    wrap,
)


def _valid_master() -> str:
    return Fernet.generate_key().decode("utf-8")


class SecretBrokerTests(unittest.TestCase):
    def test_wrap_unwrap_roundtrip(self) -> None:
        master = _valid_master()
        with patch.dict(os.environ, {"PLATFORM_SECRETS_KEY": master, "WORKER_SERVICE_ID": ""}, clear=False):
            os.environ.pop("WORKER_SERVICE_ID", None)
            enc = wrap("svc_a", "hello-secret")
            self.assertTrue(enc.startswith("v2.svc_a."))
            self.assertEqual(unwrap("svc_a", enc), "hello-secret")

    def test_wrong_service_cannot_unwrap_v2(self) -> None:
        master = _valid_master()
        with patch.dict(os.environ, {"PLATFORM_SECRETS_KEY": master}, clear=False):
            os.environ.pop("WORKER_SERVICE_ID", None)
            enc = wrap("svc_a", "hello-secret")
            with self.assertRaises(SecretBrokerError) as ctx:
                unwrap("svc_b", enc)
            self.assertEqual(ctx.exception.code, "SECRETS_SERVICE_MISMATCH")

    def test_worker_scope_denied(self) -> None:
        master = _valid_master()
        with patch.dict(
            os.environ,
            {"PLATFORM_SECRETS_KEY": master, "WORKER_SERVICE_ID": "svc_worker"},
            clear=False,
        ):
            with self.assertRaises(SecretBrokerError) as ctx:
                unwrap("svc_other", "v2.svc_other.dummy")
            self.assertEqual(ctx.exception.code, "SECRETS_SCOPE_DENIED")

    def test_non_v2_cipher_rejected(self) -> None:
        master = _valid_master()
        legacy = Fernet(master.encode("utf-8")).encrypt(b"legacy-value").decode("utf-8")
        with patch.dict(os.environ, {"PLATFORM_SECRETS_KEY": master}, clear=False):
            os.environ.pop("WORKER_SERVICE_ID", None)
            with self.assertRaises(SecretBrokerError) as ctx:
                unwrap("svc_any", legacy)
            self.assertEqual(ctx.exception.code, "SECRETS_CIPHER_INVALID")

    def test_worker_can_unwrap_own_tenant(self) -> None:
        master = _valid_master()
        with patch.dict(os.environ, {"PLATFORM_SECRETS_KEY": master}, clear=False):
            os.environ.pop("WORKER_SERVICE_ID", None)
            enc = wrap("svc_worker", "own")
        with patch.dict(
            os.environ,
            {"PLATFORM_SECRETS_KEY": master, "WORKER_SERVICE_ID": "svc_worker"},
            clear=False,
        ):
            self.assertEqual(unwrap("svc_worker", enc), "own")


if __name__ == "__main__":
    unittest.main()

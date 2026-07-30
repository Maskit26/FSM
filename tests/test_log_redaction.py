"""Tests for log redaction and hide_parameters."""

from __future__ import annotations

import logging
import os
import unittest
from unittest.mock import patch

from fsm_platform.host.log_redaction import (
    RedactingFilter,
    install_log_redaction,
    redact_text,
    safe_db_url,
)


class LogRedactionTests(unittest.TestCase):
    def test_redact_uri_password(self) -> None:
        text = (
            "Lost connection at "
            "mysql+mysqlconnector://u9lv:SecretPass99@host.example:3306/db"
        )
        out = redact_text(text)
        self.assertNotIn("SecretPass99", out)
        self.assertIn("***", out)
        self.assertIn("u9lv:", out)

    def test_redact_env_values(self) -> None:
        env = {
            "PLATFORM_SECRETS_KEY": "super-secret-fernet-key-value",
            "PLATFORM_DATABASE_URL": (
                "mysql+mysqlconnector://user:dbpass123@db.example/platform"
            ),
        }
        with patch.dict(os.environ, env, clear=False):
            out = redact_text(
                "key=super-secret-fernet-key-value url="
                "mysql+mysqlconnector://user:dbpass123@db.example/platform"
            )
        self.assertNotIn("super-secret-fernet-key-value", out)
        self.assertNotIn("dbpass123", out)

    def test_redact_token_kv(self) -> None:
        out = redact_text("PLATFORM_ADMIN_TOKEN=abc123XYZ999TOKEN")
        self.assertNotIn("abc123XYZ999TOKEN", out)
        self.assertIn("PLATFORM_ADMIN_TOKEN=", out)

    def test_safe_db_url_hides_password(self) -> None:
        url = "mysql+mysqlconnector://alice:hunter2@localhost:3306/app"
        safe = safe_db_url(url)
        self.assertNotIn("hunter2", safe)
        self.assertIn("alice", safe)

    def test_filter_on_logger(self) -> None:
        logger = logging.getLogger("test.redaction.filter")
        logger.handlers.clear()
        logger.filters.clear()
        logger.setLevel(logging.INFO)
        logger.propagate = False
        buf: list[str] = []

        class Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                buf.append(record.getMessage())

        handler = Capture()
        logger.addHandler(handler)
        install_log_redaction(logger)
        with patch.dict(
            os.environ,
            {"PLATFORM_SECRETS_KEY": "filter-secret-value-xyz"},
            clear=False,
        ):
            # Rebuild filter env snapshot by calling redact via filter
            logger.addFilter(RedactingFilter())
            logger.info("leak filter-secret-value-xyz here")
        self.assertTrue(buf)
        self.assertNotIn("filter-secret-value-xyz", buf[0])

    def test_engine_kwargs_include_hide_parameters(self) -> None:
        from fsm_platform.host.engines import _default_engine_kwargs

        self.assertTrue(_default_engine_kwargs().get("hide_parameters"))


if __name__ == "__main__":
    unittest.main()

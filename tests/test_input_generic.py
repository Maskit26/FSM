"""Unit tests for input/generic auth."""

from __future__ import annotations

import hashlib
import hmac
import time
from unittest import mock

from input.generic.webhook import (
    hook_secret_key,
    verify_input_auth,
)


def test_hook_secret_key_normalizes_channel() -> None:
    assert hook_secret_key("payment") == "INPUT_HOOK_SECRET_PAYMENT"
    assert hook_secret_key("sms-gw") == "INPUT_HOOK_SECRET_SMS_GW"


def test_verify_plain_secret_ok() -> None:
    with mock.patch(
        "input.generic.webhook.resolve_hook_secret", return_value="s3cret"
    ):
        err = verify_input_auth(
            channel="payment",
            headers={"X-Input-Secret": "s3cret"},
            raw_body=b"{}",
        )
    assert err is None


def test_verify_plain_secret_bad() -> None:
    with mock.patch(
        "input.generic.webhook.resolve_hook_secret", return_value="s3cret"
    ):
        err = verify_input_auth(
            channel="payment",
            headers={"X-Input-Secret": "wrong"},
            raw_body=b"{}",
        )
    assert err == "INPUT_AUTH_FAILED"


def test_verify_hmac_ok() -> None:
    secret = "s3cret"
    body = b'{"ok":true}'
    ts = str(int(time.time()))
    sig = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.".encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()
    with mock.patch(
        "input.generic.webhook.resolve_hook_secret", return_value=secret
    ):
        err = verify_input_auth(
            channel="payment",
            headers={
                "X-Input-Timestamp": ts,
                "X-Input-Signature": sig,
            },
            raw_body=body,
        )
    assert err is None


def test_verify_missing_secret_config() -> None:
    with mock.patch(
        "input.generic.webhook.resolve_hook_secret", return_value=""
    ):
        err = verify_input_auth(
            channel="payment",
            headers={"X-Input-Secret": "x"},
            raw_body=b"{}",
        )
    assert err == "INPUT_HOOK_SECRET_MISSING"


def test_verify_auth_required_when_no_headers() -> None:
    with mock.patch(
        "input.generic.webhook.resolve_hook_secret", return_value="s3cret"
    ):
        err = verify_input_auth(
            channel="payment",
            headers={},
            raw_body=b"{}",
        )
    assert err == "INPUT_AUTH_REQUIRED"

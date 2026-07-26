"""Outbound webhook: POST JSON + HMAC-SHA256 signature."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def deliver_webhook(
    *,
    url: str,
    secret: str,
    body: dict[str, Any],
    event_type: str,
    timeout: float = 10.0,
) -> None:
    """
    POST body as JSON. Header X-FSM-Signature = hex(HMAC-SHA256(secret, raw_body)).
    Raises on non-2xx.
    """
    dest = (url or "").strip()
    if not dest:
        raise RuntimeError("WEBHOOK_URL_EMPTY")
    raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(
        (secret or "").encode("utf-8"), raw, hashlib.sha256
    ).hexdigest()
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-FSM-Signature": sig,
        "X-FSM-Event-Type": str(event_type or ""),
        "User-Agent": "fsm-platform-webhook/1",
    }
    resp = requests.post(dest, data=raw, headers=headers, timeout=timeout)
    if resp.status_code < 200 or resp.status_code >= 300:
        raise RuntimeError(
            f"WEBHOOK_HTTP_{resp.status_code}:{(resp.text or '')[:300]}"
        )
    logger.info("webhook delivered url=%s event=%s", dest[:80], event_type)

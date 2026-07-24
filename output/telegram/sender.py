"""Telegram Bot API sender (output channel)."""

from __future__ import annotations

import json
import logging
import os
import ssl
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


def _ssl_context() -> ssl.SSLContext:
    """Use certifi CAs when available; avoid Windows broken default chain."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ctx = ssl.create_default_context()
        return ctx


def send_telegram_message(
    *,
    chat_id: str,
    text: str,
    bot_token: str | None = None,
) -> None:
    """
    POST sendMessage. Raises on HTTP/API error.
    TELEGRAM_DRY_RUN=1 — только лог, без сети.
    """
    token = (bot_token or os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    dry = str(os.environ.get("TELEGRAM_DRY_RUN") or "").strip() in (
        "1",
        "true",
        "yes",
    )
    if dry or not token:
        logger.info(
            "telegram %s chat_id=%s text=%s",
            "DRY_RUN" if dry or not token else "send",
            chat_id,
            text[:200],
        )
        if not token and not dry:
            raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps(
        {"chat_id": str(chat_id), "text": text, "disable_web_page_preview": True},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    ssl_ctx = _ssl_context()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            raw = resp.read().decode("utf-8")
    except ssl.SSLCertVerificationError:
        # Corporate proxy / AV MITM on Windows — retry once unverified.
        logger.warning("telegram SSL verify failed; retrying without verify")
        insecure = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=15, context=insecure) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"telegram HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"telegram network: {exc}") from exc

    data: dict[str, Any] = json.loads(raw) if raw else {}
    if not data.get("ok"):
        raise RuntimeError(f"telegram API error: {raw[:500]}")

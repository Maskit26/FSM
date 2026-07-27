"""
Per-tenant Telegram settings.

Порядок: domain_secrets (если service_id bound) → fallback os.environ (миграция / dev).
Ключи: TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_LINK_SECRET.
TELEGRAM_DRY_RUN остаётся process-wide в .env (не секрет арендатора).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def telegram_setting(key: str) -> str:
    """Значение настройки Telegram для текущего арендатора (или env fallback)."""
    k = str(key or "").strip()
    if not k:
        return ""

    from fsm_platform.host.runtime_context import peek_service_id

    if peek_service_id():
        try:
            from fsm_platform.host.secrets import get_domain_secret

            val = get_domain_secret(k)
            if val is not None and str(val).strip():
                return str(val).strip()
        except Exception as exc:  # noqa: BLE001
            logger.debug("telegram_setting %s from secrets failed: %s", k, exc)

    return (os.environ.get(k) or "").strip()


def telegram_bot_token() -> str:
    return telegram_setting("TELEGRAM_BOT_TOKEN")


def telegram_bot_username() -> str:
    return telegram_setting("TELEGRAM_BOT_USERNAME").lstrip("@")


def telegram_link_secret() -> str:
    """Подпись deep-link: LINK_SECRET или BOT_TOKEN."""
    return telegram_setting("TELEGRAM_LINK_SECRET") or telegram_bot_token()


def telegram_dry_run() -> bool:
    return str(os.environ.get("TELEGRAM_DRY_RUN") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

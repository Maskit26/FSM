"""Обработка Telegram Update: /start <signed payload> → bind chat_id."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
from typing import Any, Optional
from urllib.parse import quote

from output.telegram.sender import send_telegram_message

logger = logging.getLogger(__name__)

_START_RE = re.compile(r"^/start(?:@\w+)?(?:\s+(.+))?$", re.IGNORECASE)


def _link_secret() -> str:
    return (
        os.environ.get("TELEGRAM_LINK_SECRET")
        or os.environ.get("TELEGRAM_BOT_TOKEN")
        or ""
    ).strip()


def make_start_payload(user_id: int) -> str:
    """Payload для deep-link: u{user_id}_{sig12}."""
    secret = _link_secret()
    if not secret:
        raise RuntimeError("TELEGRAM_LINK_SECRET or TELEGRAM_BOT_TOKEN required")
    sig = hmac.new(
        secret.encode("utf-8"),
        str(int(user_id)).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:12]
    return f"u{int(user_id)}_{sig}"


def verify_start_payload(payload: str) -> Optional[int]:
    """Проверяет подпись deep-link. None если невалидно."""
    raw = str(payload or "").strip()
    if not raw.startswith("u"):
        return None
    body = raw[1:]
    if "_" not in body:
        return None
    uid_s, sig = body.rsplit("_", 1)
    try:
        user_id = int(uid_s)
    except ValueError:
        return None
    secret = _link_secret()
    if not secret:
        return None
    expected = hmac.new(
        secret.encode("utf-8"),
        str(user_id).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:12]
    if not hmac.compare_digest(expected, sig):
        return None
    return user_id


def build_bot_start_url(user_id: int, bot_username: Optional[str] = None) -> str:
    """https://t.me/<bot>?start=<payload>."""
    bot = (
        bot_username
        or os.environ.get("TELEGRAM_BOT_USERNAME")
        or ""
    ).strip().lstrip("@")
    if not bot:
        raise RuntimeError("TELEGRAM_BOT_USERNAME required")
    payload = make_start_payload(user_id)
    return f"https://t.me/{bot}?start={quote(payload)}"


def handle_telegram_update(update: dict[str, Any]) -> dict[str, Any]:
    """
    /start u{user_id}_{sig} → users.telegram_chat_id = chat.id
    Ссылку фронт берёт из build_bot_start_url / GET /input/telegram/link.
    """
    message = update.get("message") or update.get("edited_message") or {}
    if not isinstance(message, dict):
        return {"ok": True, "handled": False}

    text = str(message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    m = _START_RE.match(text)
    if not m:
        return {"ok": True, "handled": False}

    if chat_id is None:
        return {"ok": False, "error": "NO_CHAT_ID"}

    payload = (m.group(1) or "").strip()
    if not payload:
        _reply(
            str(chat_id),
            "Откройте бота по ссылке из приложения "
            "(кнопка «Подключить Telegram»), чтобы привязать уведомления.",
        )
        return {"ok": True, "handled": True, "bound": False, "reason": "NO_PAYLOAD"}

    user_id = verify_start_payload(payload)
    if user_id is None:
        _reply(
            str(chat_id),
            "Ссылка недействительна или устарела. "
            "Откройте новую из приложения.",
        )
        return {"ok": True, "handled": True, "bound": False, "reason": "BAD_PAYLOAD"}

    from fsm_platform.host.engines import domain_session
    from domains.courier import db_layer

    service_id = os.environ.get("SERVICE_ID", "svc_courier_01").strip()
    sd = domain_session(service_id)
    try:
        user = db_layer.get_user(sd, user_id)
        if user is None:
            _reply(str(chat_id), "Пользователь не найден.")
            sd.rollback()
            return {
                "ok": True,
                "handled": True,
                "bound": False,
                "reason": "USER_NOT_FOUND",
                "user_id": user_id,
            }

        db_layer.bind_telegram_chat_id(sd, user_id, str(chat_id))
        sd.commit()
        name = str(user.get("name") or f"#{user_id}")
        _reply(
            str(chat_id),
            f"Готово! Аккаунт «{name}» привязан. "
            "Вы будете получать уведомления о заказах.",
        )
        logger.info(
            "telegram bound user_id=%s chat_id=%s",
            user_id,
            chat_id,
        )
        return {
            "ok": True,
            "handled": True,
            "bound": True,
            "user_id": user_id,
            "chat_id": str(chat_id),
        }
    except Exception:
        sd.rollback()
        logger.exception("telegram /start failed")
        _reply(str(chat_id), "Ошибка привязки. Попробуйте позже.")
        return {"ok": False, "error": "BIND_FAILED"}
    finally:
        sd.close()


def _reply(chat_id: str, text: str) -> None:
    try:
        send_telegram_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("telegram reply failed chat_id=%s", chat_id)

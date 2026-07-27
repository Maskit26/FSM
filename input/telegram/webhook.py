"""Обработка Telegram Update: /start <signed payload> → bind chat_id."""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
from typing import Any, Optional
from urllib.parse import quote

from output.telegram.sender import send_telegram_message
from output.telegram.settings import (
    telegram_bot_username,
    telegram_link_secret,
)

logger = logging.getLogger(__name__)

_START_RE = re.compile(r"^/start(?:@\w+)?(?:\s+(.+))?$", re.IGNORECASE)


def make_start_payload(user_id: int) -> str:
    """Payload для deep-link: u{user_id}_{sig12}."""
    secret = telegram_link_secret()
    if not secret:
        raise RuntimeError(
            "TELEGRAM_LINK_SECRET or TELEGRAM_BOT_TOKEN required "
            "(domain_secrets or env)"
        )
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
    secret = telegram_link_secret()
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


def build_bot_start_url(
    user_id: int, bot_username: Optional[str] = None
) -> str:
    """https://t.me/<bot>?start=<payload>. Нужен service_scope или env."""
    bot = (bot_username or telegram_bot_username() or "").strip().lstrip("@")
    if not bot:
        raise RuntimeError(
            "TELEGRAM_BOT_USERNAME required (domain_secrets or env)"
        )
    payload = make_start_payload(user_id)
    return f"https://t.me/{bot}?start={quote(payload)}"


def handle_telegram_update(
    update: dict[str, Any],
    *,
    service_id: str,
) -> dict[str, Any]:
    """
    /start u{user_id}_{sig} → users.telegram_chat_id = chat.id

    service_id — из URL /input/telegram/{service_id}/webhook (обязателен).
    Вызывать внутри service_scope(service_id) или функция сама биндит.
    """
    from fsm_platform.host.runtime_context import peek_service_id, service_scope

    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id required")

    if peek_service_id() == sid:
        return _handle_telegram_update_bound(update, service_id=sid)

    with service_scope(sid):
        return _handle_telegram_update_bound(update, service_id=sid)


def _handle_telegram_update_bound(
    update: dict[str, Any], *, service_id: str
) -> dict[str, Any]:
    """Внутри уже bound service_scope."""
    message = update.get("message") or update.get("edited_message") or {}
    if not isinstance(message, dict):
        return {"ok": True, "handled": False, "service_id": service_id}

    text = str(message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    m = _START_RE.match(text)
    if not m:
        return {"ok": True, "handled": False, "service_id": service_id}

    if chat_id is None:
        return {"ok": False, "error": "NO_CHAT_ID", "service_id": service_id}

    payload = (m.group(1) or "").strip()
    if not payload:
        _reply(
            str(chat_id),
            "Откройте бота по ссылке из приложения "
            "(кнопка «Подключить Telegram»), чтобы привязать уведомления.",
        )
        return {
            "ok": True,
            "handled": True,
            "bound": False,
            "reason": "NO_PAYLOAD",
            "service_id": service_id,
        }

    user_id = verify_start_payload(payload)
    if user_id is None:
        _reply(
            str(chat_id),
            "Ссылка недействительна или устарела. "
            "Откройте новую из приложения.",
        )
        return {
            "ok": True,
            "handled": True,
            "bound": False,
            "reason": "BAD_PAYLOAD",
            "service_id": service_id,
        }

    from domains.courier import db_layer
    from fsm_platform.host.engines import domain_session

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
                "service_id": service_id,
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
            "telegram bound service_id=%s user_id=%s chat_id=%s",
            service_id,
            user_id,
            chat_id,
        )
        return {
            "ok": True,
            "handled": True,
            "bound": True,
            "user_id": user_id,
            "chat_id": str(chat_id),
            "service_id": service_id,
        }
    except Exception:
        sd.rollback()
        logger.exception("telegram /start failed service_id=%s", service_id)
        _reply(str(chat_id), "Ошибка привязки. Попробуйте позже.")
        return {"ok": False, "error": "BIND_FAILED", "service_id": service_id}
    finally:
        sd.close()


def _reply(chat_id: str, text: str) -> None:
    try:
        send_telegram_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("telegram reply failed chat_id=%s", chat_id)

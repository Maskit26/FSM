"""Обработка Telegram Update: deep-link + bind (I/O платформы)."""

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
            "(domain_secrets)"
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
    """https://t.me/<bot>?start=<payload>. Нужен service_scope."""
    bot = (bot_username or telegram_bot_username() or "").strip().lstrip("@")
    if not bot:
        raise RuntimeError("TELEGRAM_BOT_USERNAME required (domain_secrets)")
    payload = make_start_payload(user_id)
    return f"https://t.me/{bot}?start={quote(payload)}"


def _reply(chat_id: str, text: str) -> None:
    try:
        send_telegram_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("telegram reply failed chat_id=%s", chat_id)


def handle_telegram_update(
    update: dict[str, Any],
    *,
    service_id: str,
) -> dict[str, Any]:
    """
    Platform I/O: парсит Update, проверяет deep-link, шлёт ответы.
    Запись users.telegram_chat_id — domain command bind_telegram (invoke).
    Арендатор не пишет webhook/hooks.py.
    """
    from fsm_platform.core.domain_errors import DomainError
    from fsm_platform.host.contract.contract_client import get_contract_client
    from fsm_platform.host.runtime.runtime_context import peek_service_id, service_scope

    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id required")

    def _run() -> dict[str, Any]:
        message = update.get("message") or update.get("edited_message") or {}
        if not isinstance(message, dict):
            return {"ok": True, "handled": False, "service_id": sid}

        text = str(message.get("text") or "").strip()
        chat = message.get("chat") or {}
        chat_id = chat.get("id")

        m = _START_RE.match(text)
        if not m:
            return {"ok": True, "handled": False, "service_id": sid}

        if chat_id is None:
            return {"ok": False, "error": "NO_CHAT_ID", "service_id": sid}

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
                "service_id": sid,
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
                "service_id": sid,
            }

        try:
            result = get_contract_client(sid).call_command(
                "bind_telegram",
                params={"user_id": user_id, "chat_id": str(chat_id)},
                actor={
                    "actor_type": "user",
                    "actor_id": str(user_id),
                    "channel": "telegram",
                },
            )
        except DomainError as exc:
            if exc.code == "USER_NOT_FOUND":
                _reply(str(chat_id), "Пользователь не найден.")
                return {
                    "ok": True,
                    "handled": True,
                    "bound": False,
                    "reason": "USER_NOT_FOUND",
                    "user_id": user_id,
                    "service_id": sid,
                }
            logger.warning(
                "bind_telegram failed service_id=%s code=%s", sid, exc.code
            )
            _reply(str(chat_id), "Не удалось привязать аккаунт. Попробуйте позже.")
            return {
                "ok": False,
                "error": exc.code,
                "message": str(exc),
                "service_id": sid,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("bind_telegram transport failed service_id=%s", sid)
            _reply(str(chat_id), "Сервис временно недоступен. Попробуйте позже.")
            return {
                "ok": False,
                "error": "CONTRACT_ERROR",
                "message": str(exc),
                "service_id": sid,
            }

        data = result.get("data") if isinstance(result, dict) else None
        if not isinstance(data, dict):
            data = result if isinstance(result, dict) else {}
        name = str(data.get("name") or f"#{user_id}")
        _reply(
            str(chat_id),
            f"Готово! Аккаунт «{name}» привязан. "
            "Вы будете получать уведомления о заказах.",
        )
        logger.info(
            "telegram bound service_id=%s user_id=%s chat_id=%s",
            sid,
            user_id,
            chat_id,
        )
        return {
            "ok": True,
            "handled": True,
            "bound": True,
            "user_id": user_id,
            "chat_id": str(chat_id),
            "service_id": sid,
        }

    if peek_service_id() == sid:
        return _run()
    with service_scope(sid):
        return _run()

"""
Текущий service_id для доменного кода (contextvars).

Платформа вызывает bind/service_scope перед effect/command/guard/on_failed/outbox.
Домен читает секреты через get_domain_secret(key) без параметра service_id —
подставить чужой арендатор через сигнатуру нельзя.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Iterator, Optional

_current_service_id: ContextVar[Optional[str]] = ContextVar(
    "current_service_id", default=None
)


class RuntimeContextError(RuntimeError):
    """Нет bound service_id или некорректный bind."""


def bind_service_id(service_id: str) -> Token:
    """Привязывает service_id к текущему контексту. Возвращает token для reset."""
    sid = str(service_id or "").strip()
    if not sid:
        raise RuntimeContextError("service_id required")
    return _current_service_id.set(sid)


def reset_service_id(token: Token) -> None:
    """Сбрасывает bind после выхода из платформенного entry-point."""
    _current_service_id.reset(token)


def current_service_id() -> str:
    """
    service_id текущего арендатора.
    LookupError/RuntimeContextError, если вызвали вне service_scope.
    """
    sid = _current_service_id.get()
    if not sid:
        raise RuntimeContextError(
            "no service_id bound — call only inside platform domain entry"
        )
    return sid


def peek_service_id() -> Optional[str]:
    """Текущий service_id или None (для диагностики)."""
    return _current_service_id.get()


@contextmanager
def service_scope(service_id: str) -> Iterator[str]:
    """with service_scope(sid): … — bind на время блока."""
    token = bind_service_id(service_id)
    try:
        yield str(service_id).strip()
    finally:
        reset_service_id(token)

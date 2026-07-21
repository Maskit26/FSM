"""Бизнес-ошибки из доменных Command handlers → HTTP 4xx."""

from __future__ import annotations


class DomainError(Exception):
    """Доменная ошибка с кодом и сообщением для маппинга в HTTP 4xx. Не относится к сбоям FSM-воркера."""

    def __init__(self, code: str, message: str) -> None:
        """Сохраняет code и message и формирует текст исключения. HTTP-слой читает code для выбора статуса."""
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

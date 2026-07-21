"""Business errors from domain Command handlers → HTTP 4xx."""

from __future__ import annotations


class DomainError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

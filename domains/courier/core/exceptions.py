"""Ошибки интеграции с ibronevik Core."""

from __future__ import annotations


class CoreError(Exception):
    """Базовая ошибка Core."""

    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


class CoreAuthError(CoreError):
    def __init__(self, message: str = "CORE_AUTH") -> None:
        super().__init__("CORE_AUTH", message)


class CoreValidationError(CoreError):
    def __init__(self, message: str = "CORE_VALIDATION") -> None:
        super().__init__("CORE_VALIDATION", message)


class CoreUnavailableError(CoreError):
    def __init__(self, message: str = "CORE_UNAVAILABLE") -> None:
        super().__init__("CORE_UNAVAILABLE", message)


class CoreMappingError(CoreError):
    def __init__(self, message: str = "CORE_MAPPING") -> None:
        super().__init__("CORE_MAPPING", message)

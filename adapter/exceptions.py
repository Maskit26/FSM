"""
Исключения адаптера Core.
"""


class CoreAdapterError(Exception):
    """Базовое исключение адаптера"""
    pass


class CoreUnavailableError(CoreAdapterError):
    """Core не отвечает — нужно откатывать транзакцию"""
    pass


class CoreMappingError(CoreAdapterError):
    """Ошибка создания/получения mapping"""
    pass


class CoreValidationError(CoreAdapterError):
    """Core вернул 400 (валидация)"""
    pass


class CoreAuthError(CoreAdapterError):
    """Core вернул 401 (авторизация)"""
    pass
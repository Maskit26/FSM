"""
Пакет интеграции с Core API.
CoreAdapter — единая точка входа. UserMapping — оркестратор.
"""
from .core_adapter import CoreAdapter
from .user_mapping import UserMapping
from .core_client import CoreClient
from .exceptions import (
    CoreUnavailableError,
    CoreMappingError,
    CoreValidationError,
    CoreAuthError,
    CoreAdapterError
)

__all__ = [
    "CoreAdapter",
    "UserMapping",
    "CoreClient",
    "CoreUnavailableError",
    "CoreMappingError",
    "CoreValidationError",
    "CoreAuthError",
    "CoreAdapterError",
]
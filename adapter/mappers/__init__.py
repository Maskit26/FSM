"""
Мапперы данных между Delivery и Core.
"""
from .user import to_core_register, from_core_register, ROLE_TO_CORE

__all__ = [
    "to_core_register",
    "from_core_register",
    "ROLE_TO_CORE",
]
"""
Мапперы данных между Delivery и Core.
"""
from .user import to_core_register, from_core_register, to_core_login, from_core_login, ROLE_TO_CORE

__all__ = [
    "to_core_register",
    "from_core_register",
    "to_core_login", 
    "from_core_login",
    "ROLE_TO_CORE",
]
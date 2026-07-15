"""
Thin Domain adapter implementing Platform Integration Contract.

This package wraps the existing FastAPI Domain API / DatabaseLayer.
It does not replace FSM internals.
"""

from .adapter import DomainIntegrationAdapter
from .mapping import OPERATION_MAP, OperationMapping

__all__ = [
    "DomainIntegrationAdapter",
    "OPERATION_MAP",
    "OperationMapping",
]

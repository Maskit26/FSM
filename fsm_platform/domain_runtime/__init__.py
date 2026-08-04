"""
Domain runtime — общий Contract API server для любого картриджа.

Арендатор пишет только доменный код + register_all + main.py:

    from fsm_platform.domain_runtime import create_app
    app = create_app(entry="domains.courier.processes:register_all")
"""

from __future__ import annotations

from fsm_platform.domain_runtime.app import create_app
from fsm_platform.domain_runtime.registry import (
    DomainProcessDef,
    access_policies,
    effects,
    guards,
    hooks,
    operations,
    processes,
    set_outbox_handler,
    snapshots,
)

__all__ = [
    "create_app",
    "DomainProcessDef",
    "operations",
    "guards",
    "effects",
    "processes",
    "hooks",
    "access_policies",
    "snapshots",
    "set_outbox_handler",
]

"""
Boot active domains: load package → register_all(service_id) → RAM registries.

v1: domains listed in FSM_DOMAINS env (comma-separated cartridge module paths)
     plus optional Domain Registry rows (status=active) when DB is configured.
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Callable

logger = logging.getLogger(__name__)


def _load_register_all(entry: str) -> Callable[[str], None]:
    """
    entry formats:
      domains.demo.processes:register_all
      domains.demo
    """
    if ":" in entry:
        module_name, attr = entry.split(":", 1)
    else:
        module_name, attr = entry, "register_all"
    module = importlib.import_module(module_name)
    fn = getattr(module, attr)
    if not callable(fn):
        raise TypeError(f"{entry} is not callable")
    return fn  # type: ignore[return-value]


def bootstrap_from_env() -> None:
    """
    FSM_DOMAINS example:
      demo_svc=domains.demo.processes:register_all
    Multiple entries separated by semicolon.
    """
    raw = os.environ.get("FSM_DOMAINS", "").strip()
    if not raw:
        logger.warning("FSM_DOMAINS empty — no domains registered")
        return

    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(
                f"FSM_DOMAINS item must be service_id=module:register_all, got {item!r}"
            )
        service_id, entry = item.split("=", 1)
        service_id = service_id.strip()
        entry = entry.strip()
        register_all = _load_register_all(entry)
        logger.info("register_all service_id=%s entry=%s", service_id, entry)
        register_all(service_id)

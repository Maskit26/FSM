"""Загрузка entry point домена и регистрация в локальные реестры."""

from __future__ import annotations

import importlib
import logging
import os
from typing import Callable, Optional

from fsm_platform.domain_runtime.registry import clear_all

logger = logging.getLogger(__name__)


def resolve_entry(entry: str) -> Callable[[str], None]:
    """domains.courier.processes:register_all → callable(service_id)."""
    mod_name, _, attr = entry.partition(":")
    if not mod_name or not attr:
        raise ValueError(f"invalid entry {entry!r}; expected module:attr")
    module = importlib.import_module(mod_name.strip())
    fn = getattr(module, attr.strip(), None)
    if not callable(fn):
        raise TypeError(f"entry {entry!r} is not callable")
    return fn


def bootstrap_domain(*, entry: str, service_id: Optional[str] = None) -> str:
    """
    Очищает локальные реестры, вызывает register_all(service_id).
    Возвращает service_id.
    """
    sid = (service_id or os.environ.get("SERVICE_ID", "")).strip()
    if not sid:
        raise RuntimeError("SERVICE_ID is required (env or argument)")

    clear_all()

    register_all = resolve_entry(entry)
    logger.info("domain_runtime bootstrap entry=%s service_id=%s", entry, sid)
    register_all(sid)
    return sid

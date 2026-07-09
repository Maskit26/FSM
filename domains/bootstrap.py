"""Подключение доменов к fsm_core registry (единая точка для worker и API)."""

from __future__ import annotations

import importlib
import os


def _domain_names() -> list[str]:
    raw = os.getenv("FSM_DOMAINS", "courier")
    return [name.strip() for name in raw.split(",") if name.strip()]


def register_domains() -> None:
    """Загрузить domains/<name>/processes.py и вызвать register_all()."""
    for domain_name in _domain_names():
        module = importlib.import_module(f"domains.{domain_name}.processes")
        register = getattr(module, "register_all", None)
        if register is None:
            raise RuntimeError(f"domains.{domain_name}.processes has no register_all()")
        register()

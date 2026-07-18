"""RAM registries: ProcessDef / guards / effects keyed by service_id."""

from __future__ import annotations

from typing import Optional

from .types import EffectFunction, GuardFunction, ProcessDef


class ProcessRegistry:
    def __init__(self) -> None:
        self._processes: dict[tuple[str, str], ProcessDef] = {}

    def register(self, process_def: ProcessDef) -> ProcessDef:
        key = (process_def.service_id, process_def.process_name)
        self._processes[key] = process_def
        return process_def

    def get(self, service_id: str, process_name: str) -> Optional[ProcessDef]:
        return self._processes.get((service_id, process_name))

    def has(self, service_id: str, process_name: str) -> bool:
        return (service_id, process_name) in self._processes

    def list_process_names(self, service_id: Optional[str] = None) -> list[str]:
        if service_id is None:
            return sorted({p.process_name for p in self._processes.values()})
        return sorted(
            p.process_name for (sid, _), p in self._processes.items() if sid == service_id
        )

    def list_processes(self) -> list[ProcessDef]:
        return list(self._processes.values())

    def clear(self) -> None:
        self._processes.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._processes if k[0] == service_id]:
            del self._processes[key]


class GuardRegistry:
    def __init__(self) -> None:
        self._guards: dict[tuple[str, str], GuardFunction] = {}

    def register(self, service_id: str, name: str, fn: GuardFunction) -> None:
        self._guards[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[GuardFunction]:
        return self._guards.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._guards if sid == service_id)

    def clear(self) -> None:
        self._guards.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._guards if k[0] == service_id]:
            del self._guards[key]


class EffectRegistry:
    def __init__(self) -> None:
        self._effects: dict[tuple[str, str], EffectFunction] = {}

    def register(self, service_id: str, name: str, fn: EffectFunction) -> None:
        self._effects[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[EffectFunction]:
        return self._effects.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._effects if sid == service_id)

    def clear(self) -> None:
        self._effects.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._effects if k[0] == service_id]:
            del self._effects[key]


default_process_registry = ProcessRegistry()
default_guard_registry = GuardRegistry()
default_effect_registry = EffectRegistry()

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from .types import EffectFunction, GuardFunction, ProcessDef


class ProcessRegistry:
    def __init__(self) -> None:
        self._processes: Dict[Tuple[str, str], ProcessDef] = {}

    def register(self, process_def: ProcessDef) -> ProcessDef:
        key = (process_def.service, process_def.process_name)
        self._processes[key] = process_def
        return process_def

    def get(self, service: str, process_name: str) -> Optional[ProcessDef]:
        return self._processes.get((service, process_name))

    def has(self, service: str, process_name: str) -> bool:
        return (service, process_name) in self._processes

    def list_process_names(self, service: Optional[str] = None) -> List[str]:
        names = [
            process_name
            for registered_service, process_name in self._processes
            if service is None or registered_service == service
        ]
        return sorted(names)

    def list_processes(self) -> List[ProcessDef]:
        return [self._processes[key] for key in sorted(self._processes)]


class GuardRegistry:
    def __init__(self) -> None:
        self._guards: Dict[str, GuardFunction] = {}

    def register(self, name: str, guard: GuardFunction) -> GuardFunction:
        self._guards[name] = guard
        return guard

    def get(self, name: str) -> Optional[GuardFunction]:
        return self._guards.get(name)

    def names(self) -> List[str]:
        return sorted(self._guards)


class EffectRegistry:
    def __init__(self) -> None:
        self._effects: Dict[str, EffectFunction] = {}

    def register(self, name: str, effect: EffectFunction) -> EffectFunction:
        self._effects[name] = effect
        return effect

    def get(self, name: str) -> Optional[EffectFunction]:
        return self._effects.get(name)

    def names(self) -> List[str]:
        return sorted(self._effects)


default_process_registry = ProcessRegistry()
default_guard_registry = GuardRegistry()
default_effect_registry = EffectRegistry()

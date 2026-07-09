from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from .types import EffectFunction, GuardFunction, ProcessDef


class ProcessRegistry:
    """Справочник ProcessDef: (service, process_name) -> описание процесса."""

    def __init__(self) -> None:
        self._processes: Dict[Tuple[str, str], ProcessDef] = {}

    def register(self, process_def: ProcessDef) -> ProcessDef:
        """Добавить или заменить ProcessDef в registry."""
        key = (process_def.service, process_def.process_name)
        self._processes[key] = process_def
        return process_def

    def get(self, service: str, process_name: str) -> Optional[ProcessDef]:
        """Найти ProcessDef по service и process_name из server_fsm_instance."""
        return self._processes.get((service, process_name))

    def has(self, service: str, process_name: str) -> bool:
        """Проверить, зарегистрирован ли процесс."""
        return (service, process_name) in self._processes

    def list_process_names(self, service: Optional[str] = None) -> List[str]:
        """Список process_name (для валидации API enqueue)."""
        names = [
            process_name
            for registered_service, process_name in self._processes
            if service is None or registered_service == service
        ]
        return sorted(names)

    def list_processes(self) -> List[ProcessDef]:
        """Все зарегистрированные ProcessDef."""
        return [self._processes[key] for key in sorted(self._processes)]


class GuardRegistry:
    """Имена guard из fsm_transitions.guard_name -> Python-функции домена."""

    def __init__(self) -> None:
        self._guards: Dict[str, GuardFunction] = {}

    def register(self, name: str, guard: GuardFunction) -> GuardFunction:
        """Зарегистрировать guard по строковому имени из БД."""
        self._guards[name] = guard
        return guard

    def get(self, name: str) -> Optional[GuardFunction]:
        """Получить guard по имени или None."""
        return self._guards.get(name)

    def names(self) -> List[str]:
        """Список зарегистрированных guard_name."""
        return sorted(self._guards)


class EffectRegistry:
    """Имена effect из fsm_transitions.effect_name -> Python-функции домена."""

    def __init__(self) -> None:
        self._effects: Dict[str, EffectFunction] = {}

    def register(self, name: str, effect: EffectFunction) -> EffectFunction:
        """Зарегистрировать effect по строковому имени из БД."""
        self._effects[name] = effect
        return effect

    def get(self, name: str) -> Optional[EffectFunction]:
        """Получить effect по имени или None."""
        return self._effects.get(name)

    def names(self) -> List[str]:
        """Список зарегистрированных effect_name."""
        return sorted(self._effects)


default_process_registry = ProcessRegistry()
default_guard_registry = GuardRegistry()
default_effect_registry = EffectRegistry()

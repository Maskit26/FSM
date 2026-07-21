"""RAM-реестры: ProcessDef, guards и effects с ключом service_id."""

from __future__ import annotations

from typing import Optional

from .types import EffectFunction, GuardFunction, ProcessDef


class ProcessRegistry:
    """Хранит зарегистрированные ProcessDef в памяти по паре (service_id, process_name). Наполняется доменами при bootstrap."""

    def __init__(self) -> None:
        """Создаёт пустой реестр процессов. Вызывается один раз на приложение или в тестах."""
        self._processes: dict[tuple[str, str], ProcessDef] = {}

    def register(self, process_def: ProcessDef) -> ProcessDef:
        """Регистрирует или перезаписывает ProcessDef и возвращает его. Вызывается из register_all доменного картриджа."""
        key = (process_def.service_id, process_def.process_name)
        self._processes[key] = process_def
        return process_def

    def get(self, service_id: str, process_name: str) -> Optional[ProcessDef]:
        """Возвращает ProcessDef по service_id и имени процесса. Используется run_instance для разрешения экземпляра."""
        return self._processes.get((service_id, process_name))

    def has(self, service_id: str, process_name: str) -> bool:
        """Проверяет, зарегистрирован ли процесс. Удобно для валидации команд до постановки в очередь."""
        return (service_id, process_name) in self._processes

    def list_process_names(self, service_id: Optional[str] = None) -> list[str]:
        """Возвращает отсортированные имена процессов, опционально только для одного service_id. Нужен для introspection и админки."""
        if service_id is None:
            return sorted({p.process_name for p in self._processes.values()})
        return sorted(
            p.process_name for (sid, _), p in self._processes.items() if sid == service_id
        )

    def list_processes(self) -> list[ProcessDef]:
        """Возвращает все зарегистрированные ProcessDef. Используется при диагностике и перечислении картриджей."""
        return list(self._processes.values())

    def clear(self) -> None:
        """Очищает весь реестр процессов. Применяется в тестах и при hot-reload доменов."""
        self._processes.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все процессы указанного service_id. Вызывается при выгрузке доменного картриджа."""
        for key in [k for k in self._processes if k[0] == service_id]:
            del self._processes[key]


class GuardRegistry:
    """Реестр guard-функций по (service_id, name). Guards выбирают допустимый transition среди кандидатов."""

    def __init__(self) -> None:
        """Создаёт пустой реестр guards. Инициализируется при старте приложения."""
        self._guards: dict[tuple[str, str], GuardFunction] = {}

    def register(self, service_id: str, name: str, fn: GuardFunction) -> None:
        """Регистрирует guard под именем для service_id. Вызывается доменом при register_all."""
        self._guards[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[GuardFunction]:
        """Возвращает guard-функцию или None. TransitionRunner вызывает её при выборе transition."""
        return self._guards.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        """Возвращает отсортированные имена guards для service_id. Полезно для документации и отладки графа."""
        return sorted(n for (sid, n) in self._guards if sid == service_id)

    def clear(self) -> None:
        """Очищает все guards. Используется в тестах."""
        self._guards.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все guards указанного service_id. Сопровождает выгрузку домена."""
        for key in [k for k in self._guards if k[0] == service_id]:
            del self._guards[key]


class EffectRegistry:
    """Реестр effect-функций по (service_id, name). Effects выполняют доменную логику после успешного apply."""

    def __init__(self) -> None:
        """Создаёт пустой реестр effects. Инициализируется при старте приложения."""
        self._effects: dict[tuple[str, str], EffectFunction] = {}

    def register(self, service_id: str, name: str, fn: EffectFunction) -> None:
        """Регистрирует effect под именем для service_id. Вызывается доменом при register_all."""
        self._effects[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[EffectFunction]:
        """Возвращает effect-функцию или None. TransitionRunner вызывает её после apply перехода."""
        return self._effects.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        """Возвращает отсортированные имена effects для service_id. Нужен для introspection и валидации графа."""
        return sorted(n for (sid, n) in self._effects if sid == service_id)

    def clear(self) -> None:
        """Очищает все effects. Используется в тестах."""
        self._effects.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все effects указанного service_id. Сопровождает выгрузку домена."""
        for key in [k for k in self._effects if k[0] == service_id]:
            del self._effects[key]


default_process_registry = ProcessRegistry()
default_guard_registry = GuardRegistry()
default_effect_registry = EffectRegistry()

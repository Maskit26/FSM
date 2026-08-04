"""RAM-реестры: ProcessDef, guards и effects с ключом service_id."""

from __future__ import annotations

from typing import Optional

from fsm_platform.core.remote import RemoteRef

from .types import ProcessDef


class ProcessRegistry:
    """Хранит зарегистрированные ProcessDef в памяти по паре (service_id, process_name). Наполняется при bootstrap catalog."""

    def __init__(self) -> None:
        """Создаёт пустой реестр процессов. Вызывается один раз на приложение или в тестах."""
        self._processes: dict[tuple[str, str], ProcessDef] = {}

    def register(self, process_def: ProcessDef) -> ProcessDef:
        """Регистрирует или перезаписывает ProcessDef и возвращает его."""
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

    def list_for_service(self, service_id: str) -> list[ProcessDef]:
        """ProcessDef одного service_id — для Domain Validator и catalog."""
        return [
            p for (sid, _), p in self._processes.items() if sid == service_id
        ]

    def clear(self) -> None:
        """Очищает весь реестр процессов. Применяется в тестах и при hot-reload доменов."""
        self._processes.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все процессы указанного service_id."""
        for key in [k for k in self._processes if k[0] == service_id]:
            del self._processes[key]


class GuardRegistry:
    """Реестр guards по (service_id, name) — RemoteRef на Contract API."""

    def __init__(self) -> None:
        self._guards: dict[tuple[str, str], RemoteRef] = {}

    def register(self, service_id: str, name: str, ref: RemoteRef) -> None:
        if ref.kind != "guard":
            raise ValueError(f"RemoteRef kind must be guard, got {ref.kind!r}")
        self._guards[(service_id, name)] = ref

    def get(self, service_id: str, name: str) -> Optional[RemoteRef]:
        return self._guards.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._guards if sid == service_id)

    def clear(self) -> None:
        self._guards.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._guards if k[0] == service_id]:
            del self._guards[key]


class EffectRegistry:
    """Реестр effects по (service_id, name) — RemoteRef на Contract API."""

    def __init__(self) -> None:
        self._effects: dict[tuple[str, str], RemoteRef] = {}

    def register(self, service_id: str, name: str, ref: RemoteRef) -> None:
        if ref.kind != "effect":
            raise ValueError(f"RemoteRef kind must be effect, got {ref.kind!r}")
        self._effects[(service_id, name)] = ref

    def get(self, service_id: str, name: str) -> Optional[RemoteRef]:
        return self._effects.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._effects if sid == service_id)

    def clear(self) -> None:
        self._effects.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._effects if k[0] == service_id]:
            del self._effects[key]


class EntityAccessRegistry:
    """Access policy по (service_id, entity_type)."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, str], RemoteRef] = {}

    def register(self, service_id: str, entity_type: str, ref: RemoteRef) -> None:
        if ref.kind != "access":
            raise ValueError(f"RemoteRef kind must be access, got {ref.kind!r}")
        et = str(entity_type or "").strip()
        if not et:
            raise ValueError("entity_type required")
        self._items[(service_id, et)] = ref

    def get(self, service_id: str, entity_type: str) -> Optional[RemoteRef]:
        return self._items.get((service_id, str(entity_type or "").strip()))

    def list_entity_types(self, service_id: str) -> list[str]:
        return sorted(et for (sid, et) in self._items if sid == service_id)

    def clear(self) -> None:
        self._items.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._items if k[0] == service_id]:
            del self._items[key]


class EntitySnapshotRegistry:
    """Snapshot builder по (service_id, entity_type)."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, str], RemoteRef] = {}

    def register(self, service_id: str, entity_type: str, ref: RemoteRef) -> None:
        if ref.kind != "snapshot":
            raise ValueError(f"RemoteRef kind must be snapshot, got {ref.kind!r}")
        et = str(entity_type or "").strip()
        if not et:
            raise ValueError("entity_type required")
        self._items[(service_id, et)] = ref

    def get(self, service_id: str, entity_type: str) -> Optional[RemoteRef]:
        return self._items.get((service_id, str(entity_type or "").strip()))

    def list_entity_types(self, service_id: str) -> list[str]:
        return sorted(et for (sid, et) in self._items if sid == service_id)

    def clear(self) -> None:
        self._items.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._items if k[0] == service_id]:
            del self._items[key]


default_process_registry = ProcessRegistry()
default_guard_registry = GuardRegistry()
default_effect_registry = EffectRegistry()
default_access_registry = EntityAccessRegistry()
default_snapshot_registry = EntitySnapshotRegistry()

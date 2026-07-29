"""Локальные реестры Callables внутри domain service (не RemoteRef платформы)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

Kind = Literal["query", "command"]


@dataclass
class DomainProcessDef:
    """ProcessDef на стороне domain service: Callables, не RemoteRef."""

    service_id: str
    process_name: str
    entity_type: Optional[str] = None
    event_name: Optional[str] = None
    context_builder: Optional[Callable[..., dict[str, Any]]] = None
    initial_state: Optional[str] = None
    on_failed: Optional[Callable[..., Any]] = None

    @property
    def runtime_event_name(self) -> str:
        return self.event_name or self.process_name

    @property
    def context_builder_name(self) -> Optional[str]:
        if self.context_builder is None:
            return None
        return getattr(self.context_builder, "__name__", None) or None


class LocalOperationRegistry:
    def __init__(self) -> None:
        self._ops: dict[tuple[str, str], dict[str, Any]] = {}

    def register(
        self,
        service_id: str,
        operation: str,
        kind: Kind,
        handler: Callable[..., Any],
    ) -> None:
        if kind not in ("query", "command"):
            raise ValueError(f"kind must be query|command, got {kind!r}")
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._ops[(service_id, operation)] = {"kind": kind, "handler": handler}

    def get(self, service_id: str, operation: str) -> Optional[dict[str, Any]]:
        return self._ops.get((service_id, operation))

    def list(self, service_id: str) -> list[dict[str, str]]:
        return [
            {"operation": op, "kind": meta["kind"]}
            for (sid, op), meta in sorted(self._ops.items())
            if sid == service_id
        ]

    def clear(self) -> None:
        self._ops.clear()


class LocalGuardRegistry:
    def __init__(self) -> None:
        self._guards: dict[tuple[str, str], Callable[..., Any]] = {}

    def register(self, service_id: str, name: str, fn: Callable[..., Any]) -> None:
        if not callable(fn):
            raise TypeError("guard must be callable")
        self._guards[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[Callable[..., Any]]:
        return self._guards.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._guards if sid == service_id)

    def clear(self) -> None:
        self._guards.clear()


class LocalEffectRegistry:
    def __init__(self) -> None:
        self._effects: dict[tuple[str, str], Callable[..., Any]] = {}

    def register(self, service_id: str, name: str, fn: Callable[..., Any]) -> None:
        if not callable(fn):
            raise TypeError("effect must be callable")
        self._effects[(service_id, name)] = fn

    def get(self, service_id: str, name: str) -> Optional[Callable[..., Any]]:
        return self._effects.get((service_id, name))

    def list_names(self, service_id: str) -> list[str]:
        return sorted(n for (sid, n) in self._effects if sid == service_id)

    def clear(self) -> None:
        self._effects.clear()


class LocalProcessRegistry:
    def __init__(self) -> None:
        self._processes: dict[tuple[str, str], DomainProcessDef] = {}

    def register(self, process_def: DomainProcessDef) -> DomainProcessDef:
        key = (process_def.service_id, process_def.process_name)
        self._processes[key] = process_def
        return process_def

    def get(self, service_id: str, process_name: str) -> Optional[DomainProcessDef]:
        return self._processes.get((service_id, process_name))

    def list_for_service(self, service_id: str) -> list[DomainProcessDef]:
        return [
            p for (sid, _), p in self._processes.items() if sid == service_id
        ]

    def clear(self) -> None:
        self._processes.clear()


class LocalHookRegistry:
    def __init__(self) -> None:
        self._channels: dict[tuple[str, str], Optional[Callable[..., Any]]] = {}

    def register(
        self,
        service_id: str,
        channel: str,
        handler: Callable[..., Any],
    ) -> None:
        sid = str(service_id or "").strip()
        ch = str(channel or "").strip().lower()
        if not sid or not ch:
            raise ValueError("service_id and channel required")
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._channels[(sid, ch)] = handler

    def register_channel(
        self,
        service_id: str,
        channel: str,
        handler: Optional[Callable[..., Any]] = None,
    ) -> None:
        sid = str(service_id or "").strip()
        ch = str(channel or "").strip().lower()
        if not sid or not ch:
            raise ValueError("service_id and channel required")
        self._channels[(sid, ch)] = handler

    def get(
        self, service_id: str, channel: str
    ) -> Optional[Callable[..., Any]]:
        return self._channels.get(
            (str(service_id).strip(), str(channel or "").strip().lower())
        )

    def has(self, service_id: str, channel: str) -> bool:
        key = (str(service_id).strip(), str(channel or "").strip().lower())
        return key in self._channels

    def list_channels(self, service_id: str) -> list[str]:
        sid = str(service_id).strip()
        return sorted(ch for (s, ch) in self._channels if s == sid)

    def clear(self) -> None:
        self._channels.clear()


# Process-wide defaults for one domain service process
operations = LocalOperationRegistry()
guards = LocalGuardRegistry()
effects = LocalEffectRegistry()
processes = LocalProcessRegistry()
hooks = LocalHookRegistry()
_outbox_handler: Optional[Callable[..., Any]] = None


def set_outbox_handler(fn: Callable[..., Any]) -> None:
    global _outbox_handler
    if not callable(fn):
        raise TypeError("outbox handler must be callable")
    _outbox_handler = fn


def get_outbox_handler() -> Optional[Callable[..., Any]]:
    return _outbox_handler


def clear_all() -> None:
    global _outbox_handler
    operations.clear()
    guards.clear()
    effects.clear()
    processes.clear()
    hooks.clear()
    _outbox_handler = None
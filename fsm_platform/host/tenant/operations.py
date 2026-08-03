"""OperationRegistry — реестр sync invoke-операций (RemoteRef → Contract API)."""

from __future__ import annotations

from typing import Any, Literal, Optional

from fsm_platform.core.remote import RemoteRef

Kind = Literal["query", "command"]


class OperationRegistry:
    """Хранит (service_id, operation) → RemoteRef с kind query|command."""

    def __init__(self) -> None:
        self._ops: dict[tuple[str, str], dict[str, Any]] = {}

    def register(
        self,
        service_id: str,
        operation: str,
        kind: Kind,
        handler: RemoteRef,
    ) -> None:
        if kind not in ("query", "command"):
            raise ValueError(f"kind must be query|command, got {kind!r}")
        expected = "query" if kind == "query" else "command"
        if handler.kind != expected:
            raise ValueError(
                f"RemoteRef kind must be {expected!r}, got {handler.kind!r}"
            )
        self._ops[(service_id, operation)] = {"kind": kind, "handler": handler}

    def get(self, service_id: str, operation: str) -> Optional[dict[str, Any]]:
        return self._ops.get((service_id, operation))

    def list(self, service_id: str) -> list[dict[str, str]]:
        return [
            {"operation": op, "kind": meta["kind"]}
            for (sid, op), meta in sorted(self._ops.items())
            if sid == service_id
        ]

    def items(self, service_id: str) -> list[dict[str, Any]]:
        return [
            {
                "operation": op,
                "kind": meta["kind"],
                "handler": meta["handler"],
            }
            for (sid, op), meta in sorted(self._ops.items())
            if sid == service_id
        ]

    def clear(self) -> None:
        self._ops.clear()

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._ops if k[0] == service_id]:
            del self._ops[key]


default_operation_registry = OperationRegistry()

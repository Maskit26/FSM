"""OperationRegistry — sync invoke handlers (§6.4.1)."""

from __future__ import annotations

from typing import Any, Callable, Literal, Optional

Kind = Literal["query", "command"]
Handler = Callable[..., Any]


class OperationRegistry:
    def __init__(self) -> None:
        self._ops: dict[tuple[str, str], dict[str, Any]] = {}

    def register(
        self,
        service_id: str,
        operation: str,
        kind: Kind,
        handler: Handler,
    ) -> None:
        if kind not in ("query", "command"):
            raise ValueError(f"kind must be query|command, got {kind!r}")
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

    def unregister(self, service_id: str) -> None:
        for key in [k for k in self._ops if k[0] == service_id]:
            del self._ops[key]


default_operation_registry = OperationRegistry()

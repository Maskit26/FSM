"""OperationRegistry — реестр синхронных invoke-обработчиков домена."""

from __future__ import annotations

from typing import Any, Callable, Literal, Optional

Kind = Literal["query", "command"]
Handler = Callable[..., Any]


class OperationRegistry:
    """Хранит (service_id, operation) → handler с kind query|command."""

    def __init__(self) -> None:
        """Создаёт пустой реестр операций в памяти процесса."""
        self._ops: dict[tuple[str, str], dict[str, Any]] = {}

    def register(
        self,
        service_id: str,
        operation: str,
        kind: Kind,
        handler: Handler,
    ) -> None:
        """Регистрирует операцию домена для Public API invoke."""
        if kind not in ("query", "command"):
            raise ValueError(f"kind must be query|command, got {kind!r}")
        self._ops[(service_id, operation)] = {"kind": kind, "handler": handler}

    def get(self, service_id: str, operation: str) -> Optional[dict[str, Any]]:
        """Ищет handler операции. None, если операция не зарегистрирована."""
        return self._ops.get((service_id, operation))

    def list(self, service_id: str) -> list[dict[str, str]]:
        """Список операций сервиса для catalog API."""
        return [
            {"operation": op, "kind": meta["kind"]}
            for (sid, op), meta in sorted(self._ops.items())
            if sid == service_id
        ]

    def items(self, service_id: str) -> list[dict[str, Any]]:
        """Операции с handler'ами — для Domain Validator."""
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
        """Полностью очищает реестр (тесты / hot-reload)."""
        self._ops.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все операции одного service_id."""
        for key in [k for k in self._ops if k[0] == service_id]:
            del self._ops[key]


default_operation_registry = OperationRegistry()

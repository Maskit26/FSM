"""Remote Contract API descriptors (platform-side)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RemoteKind = Literal["guard", "effect", "context", "command", "query", "on_failed"]


@dataclass(frozen=True)
class RemoteRef:
    """Handler на доменном Contract API."""

    service_id: str
    name: str
    kind: RemoteKind


def remote_guard(service_id: str, name: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=name, kind="guard")


def remote_effect(service_id: str, name: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=name, kind="effect")


def remote_context(service_id: str, name: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=name, kind="context")


def remote_command(service_id: str, operation: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=operation, kind="command")


def remote_query(service_id: str, operation: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=operation, kind="query")


def remote_on_failed(service_id: str, process_name: str) -> RemoteRef:
    return RemoteRef(service_id=service_id, name=process_name, kind="on_failed")

"""
Platform Integration Contract — Python interface (normative shapes).

Implementations live in `contract/` (Domain adapter).
Consumers: Scenario Runner (separate repo), any Python client.
Platform Interactive typically uses the TypeScript twin.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Protocol, Union


class ObjectType(str, Enum):
    ORDER = "order"
    TRIP = "trip"
    LOCKER = "locker"  # cell id in current Domain
    DRIVER_RESERVATION = "driver_reservation"
    DIRECTION = "direction"
    USER = "user"


@dataclass(frozen=True)
class ObjectRef:
    type: ObjectType
    id: int


@dataclass
class Session:
    """Opaque Domain session. Adapter defines how it is authenticated."""

    session_id: str
    user_id: int
    role: Optional[str] = None
    # Adapter-private fields (Core tokens, etc.) MUST NOT be required by clients.
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationResult:
    accepted: bool
    operation: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    job_id: Optional[Union[str, int]] = None
    objects: List[ObjectRef] = field(default_factory=list)
    correlation_id: Optional[str] = None


@dataclass
class Snapshot:
    object: ObjectRef
    state: str
    participants: Dict[str, Any] = field(default_factory=dict)
    related: List[ObjectRef] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    updated_at: Optional[str] = None


@dataclass
class ActionDescriptor:
    operation: str
    enabled: bool
    params_schema: Dict[str, Any]
    requires_object: bool = True
    label: Optional[str] = None
    reason_disabled: Optional[str] = None


@dataclass
class ChangeEvent:
    event_id: str
    timestamp: str
    source: str  # "operation" | "system" | "job"
    object: Optional[ObjectRef] = None
    job_id: Optional[Union[str, int]] = None
    operation: Optional[str] = None
    accepted: Optional[bool] = None
    state: Optional[str] = None
    snapshot: Optional[Snapshot] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    message: Optional[str] = None


@dataclass
class Credentials:
    login: str
    password: str
    type: str = "phone"


class IntegrationContract(Protocol):
    """Normative contract surface. Same for PI and Scenario Runner."""

    def login(self, credentials: Credentials) -> Session:
        ...

    def logout(self, session: Session) -> None:
        ...

    def perform(
        self,
        session: Session,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        object: Optional[ObjectRef] = None,
    ) -> OperationResult:
        ...

    def snapshot(self, session: Session, object: ObjectRef) -> Snapshot:
        ...

    def available_actions(
        self, session: Session, object: ObjectRef
    ) -> List[ActionDescriptor]:
        ...

    def observe(
        self,
        session: Session,
        *,
        object: Optional[ObjectRef] = None,
        job_id: Optional[Union[str, int]] = None,
    ) -> AsyncIterator[ChangeEvent]:
        """SSE-backed async iterator of ChangeEvent. Exactly one of object/job_id."""
        ...

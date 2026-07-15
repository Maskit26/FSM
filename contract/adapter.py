"""
DomainIntegrationAdapter — skeleton implementation of IntegrationContract.

MVP status:
- perform / login / logout / snapshot / available_actions: wired to existing API patterns
- observe: SSE skeleton (job stream exists; entity stream to be completed)

Not a full production adapter yet — intentional thin skeleton for contract review.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from interfaces.IntegrationContract import (
    ActionDescriptor,
    ChangeEvent,
    Credentials,
    ObjectRef,
    ObjectType,
    OperationResult,
    Session,
    Snapshot,
)

from .mapping import (
    BUTTON_TO_OPERATION,
    OPERATION_MAP,
    default_params_schema,
    resolve,
)

logger = logging.getLogger(__name__)


class ContractError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class DomainIntegrationAdapter:
    """
    Thin adapter over DatabaseLayer + existing HTTP semantics.

    `db` is the existing DatabaseLayer instance.
    `http_client` is optional; when None, adapter calls db methods directly where possible.
    """

    def __init__(self, db: Any, core_adapter: Any = None):
        self.db = db
        self.core_adapter = core_adapter

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def login(self, credentials: Credentials) -> Session:
        """
        Establish Session via Domain login (Core-backed).

        Implementation note: wire to UserMapping / POST /api/users/login.
        """
        # Skeleton: expects db helper or raises until wired.
        if not hasattr(self.db, "login_user"):
            raise ContractError(
                "CONTRACT_NOT_IMPLEMENTED",
                "login_user is not wired on DatabaseLayer; connect UserMapping here",
            )
        result = self.db.login_user(
            login=credentials.login,
            password=credentials.password,
            auth_type=credentials.type,
        )
        if not result or not result.get("success"):
            raise ContractError(
                "DOMAIN_AUTH_FAILED",
                (result or {}).get("message", "login failed"),
            )
        return Session(
            session_id=result.get("token") or str(uuid.uuid4()),
            user_id=int(result["user_id"]),
            role=result.get("role"),
            attributes={
                "core_user_id": result.get("core_user_id"),
                "token": result.get("token"),
            },
        )

    def logout(self, session: Session) -> None:
        if hasattr(self.db, "logout_user"):
            self.db.logout_user(session.user_id)
        return None

    # ------------------------------------------------------------------
    # perform
    # ------------------------------------------------------------------

    def perform(
        self,
        session: Session,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        object: Optional[ObjectRef] = None,
    ) -> OperationResult:
        params = params or {}
        correlation_id = str(uuid.uuid4())

        try:
            mapping = resolve(operation)
        except KeyError:
            return OperationResult(
                accepted=False,
                operation=operation,
                error_code="CONTRACT_UNKNOWN_OPERATION",
                error_message=f"Unknown operation: {operation}",
                correlation_id=correlation_id,
            )

        if mapping.kind == "session":
            return OperationResult(
                accepted=False,
                operation=operation,
                error_code="CONTRACT_USE_SESSION_API",
                error_message="Use login()/logout() for session operations in this adapter",
                correlation_id=correlation_id,
            )

        if mapping.default_object_type and object is None and mapping.kind == "async_process":
            if operation != "CREATE_ORDER":
                return OperationResult(
                    accepted=False,
                    operation=operation,
                    error_code="CONTRACT_OBJECT_REQUIRED",
                    error_message=f"Operation {operation} requires object",
                    correlation_id=correlation_id,
                )

        try:
            if mapping.kind == "async_process":
                return self._perform_async(session, mapping, params, object, correlation_id)
            if mapping.kind == "rest":
                return self._perform_rest(session, mapping, params, object, correlation_id)
            return OperationResult(
                accepted=False,
                operation=operation,
                error_code="CONTRACT_NOT_IMPLEMENTED",
                error_message=f"Kind {mapping.kind} not implemented",
                correlation_id=correlation_id,
            )
        except ContractError as exc:
            return OperationResult(
                accepted=False,
                operation=operation,
                error_code=exc.code,
                error_message=exc.message,
                correlation_id=correlation_id,
            )
        except Exception as exc:  # noqa: BLE001 — boundary adapter
            logger.exception("perform failed: %s", operation)
            return OperationResult(
                accepted=False,
                operation=operation,
                error_code="DOMAIN_INTERNAL_ERROR",
                error_message=str(exc),
                correlation_id=correlation_id,
            )

    def _perform_async(
        self,
        session: Session,
        mapping: Any,
        params: Dict[str, Any],
        object: Optional[ObjectRef],
        correlation_id: str,
    ) -> OperationResult:
        """
        Maps to enqueue_fsm_instance / create_order_request patterns.

        Full wiring is intentionally incomplete in skeleton — see TODOs.
        """
        process_name = mapping.process_name
        if not process_name:
            raise ContractError("CONTRACT_INVALID_MAPPING", "async_process without process_name")

        # CREATE_ORDER uses order_request pipeline (entity is request id initially)
        if mapping.public == "CREATE_ORDER":
            # TODO: call db.create_order_request_and_fsm(...) with session.user_id + params
            raise ContractError(
                "CONTRACT_NOT_IMPLEMENTED",
                "CREATE_ORDER wiring: use create_order_request_and_fsm; "
                "return job_id and eventually ObjectRef(order, id) via observe/result",
            )

        if object is None:
            raise ContractError("CONTRACT_OBJECT_REQUIRED", "object is required")

        entity_type = object.type.value
        entity_id = object.id
        metadata = dict(params)

        target_user_id = metadata.pop("target_user_id", None)
        target_role = metadata.pop("target_role", None)

        if not hasattr(self.db, "enqueue_fsm_instance"):
            raise ContractError(
                "CONTRACT_NOT_IMPLEMENTED",
                "enqueue_fsm_instance missing on DatabaseLayer",
            )

        # TODO: obtain SQLAlchemy session from db factory used by API layer
        raise ContractError(
            "CONTRACT_NOT_IMPLEMENTED",
            f"Enqueue {process_name} for {entity_type}/{entity_id} "
            f"(user={session.user_id}, target={target_user_id}, role={target_role}, "
            f"metadata={metadata}, correlation={correlation_id})",
        )

    def _perform_rest(
        self,
        session: Session,
        mapping: Any,
        params: Dict[str, Any],
        object: Optional[ObjectRef],
        correlation_id: str,
    ) -> OperationResult:
        raise ContractError(
            "CONTRACT_NOT_IMPLEMENTED",
            f"REST mapping {mapping.rest_key} not wired yet ({correlation_id})",
        )

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------

    def snapshot(self, session: Session, object: ObjectRef) -> Snapshot:
        _ = session  # auth checks to be added
        if object.type == ObjectType.ORDER:
            row = self._get_order(object.id)
            return Snapshot(
                object=object,
                state=row.get("status") or row.get("state") or "unknown",
                participants={
                    "client_user_id": row.get("client_user_id"),
                    "recipient_user_id": row.get("recipient_user_id"),
                },
                related=self._order_related(row),
                data=row,
                updated_at=self._now(),
            )
        if object.type == ObjectType.TRIP:
            row = self._get_trip(object.id)
            return Snapshot(
                object=object,
                state=row.get("status") or "unknown",
                participants={"driver_user_id": row.get("driver_user_id")},
                data=row,
                updated_at=self._now(),
            )
        if object.type == ObjectType.LOCKER:
            row = self._get_cell(object.id)
            return Snapshot(
                object=object,
                state=row.get("status") or "unknown",
                related=(
                    [ObjectRef(ObjectType.ORDER, int(row["current_order_id"]))]
                    if row.get("current_order_id")
                    else []
                ),
                data=row,
                updated_at=self._now(),
            )
        raise ContractError(
            "CONTRACT_UNSUPPORTED_OBJECT_TYPE",
            f"snapshot not implemented for {object.type}",
        )

    # ------------------------------------------------------------------
    # availableActions
    # ------------------------------------------------------------------

    def available_actions(
        self, session: Session, object: ObjectRef
    ) -> List[ActionDescriptor]:
        """
        Prefer role-aware buttons, map to public Operations + params_schema.

        Falls back to catalog defaults when button API is unavailable.
        """
        role = session.role or self._role_for(session.user_id)
        buttons: List[Dict[str, Any]] = []
        if hasattr(self.db, "get_buttons_for_entity"):
            buttons = self.db.get_buttons_for_entity(
                user_role=role,
                entity_type=object.type.value,
                entity_id=object.id,
            ) or []

        descriptors: List[ActionDescriptor] = []
        seen = set()
        for btn in buttons:
            name = btn.get("button_name")
            op = BUTTON_TO_OPERATION.get(name or "")
            if not op or op in seen:
                continue
            seen.add(op)
            descriptors.append(
                ActionDescriptor(
                    operation=op,
                    enabled=bool(btn.get("is_enabled")),
                    params_schema=default_params_schema(op),
                    requires_object=True,
                    label=name,
                )
            )

        # Ensure creating-order style ops are not inferred from buttons alone.
        return descriptors

    # ------------------------------------------------------------------
    # observe (SSE skeleton)
    # ------------------------------------------------------------------

    async def observe(
        self,
        session: Session,
        *,
        object: Optional[ObjectRef] = None,
        job_id: Optional[Union[str, int]] = None,
    ) -> AsyncIterator[ChangeEvent]:
        """
        MVP: job observation can wrap GET /api/fsm/instance/{id}/stream.
        Entity-level SSE is TODO — until then clients may poll snapshot().
        """
        _ = session
        if (object is None) == (job_id is None):
            raise ContractError(
                "CONTRACT_OBSERVE_TARGET",
                "Provide exactly one of object or job_id",
            )

        if job_id is not None:
            # TODO: bridge existing SSE job stream into ChangeEvent
            yield ChangeEvent(
                event_id=str(uuid.uuid4()),
                timestamp=self._now(),
                source="job",
                job_id=job_id,
                message="observe(job) skeleton — wire to /api/fsm/instance/{id}/stream",
            )
            return

        # TODO: entity subscription (poll fsm_action_logs or dedicated SSE)
        assert object is not None
        snap = self.snapshot(session, object)
        yield ChangeEvent(
            event_id=str(uuid.uuid4()),
            timestamp=self._now(),
            source="system",
            object=object,
            state=snap.state,
            snapshot=snap,
            message="observe(object) skeleton — replace with entity SSE",
        )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _get_order(self, order_id: int) -> Dict[str, Any]:
        if hasattr(self.db, "get_order"):
            row = self.db.get_order(order_id)
            if row:
                return dict(row)
        raise ContractError("DOMAIN_NOT_FOUND", f"order {order_id} not found")

    def _get_trip(self, trip_id: int) -> Dict[str, Any]:
        if hasattr(self.db, "get_trip"):
            row = self.db.get_trip(trip_id)
            if row:
                return dict(row)
        raise ContractError("DOMAIN_NOT_FOUND", f"trip {trip_id} not found")

    def _get_cell(self, cell_id: int) -> Dict[str, Any]:
        if hasattr(self.db, "get_cell"):
            row = self.db.get_cell(cell_id)
            if row:
                return dict(row)
        raise ContractError("DOMAIN_NOT_FOUND", f"locker/cell {cell_id} not found")

    def _order_related(self, row: Dict[str, Any]) -> List[ObjectRef]:
        related: List[ObjectRef] = []
        for key, typ in (
            ("source_cell_id", ObjectType.LOCKER),
            ("dest_cell_id", ObjectType.LOCKER),
        ):
            if row.get(key):
                related.append(ObjectRef(typ, int(row[key])))
        return related

    def _role_for(self, user_id: int) -> str:
        if hasattr(self.db, "get_user_role"):
            return self.db.get_user_role(user_id) or "client"
        return "client"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()


def known_operations() -> List[str]:
    return sorted(OPERATION_MAP.keys())

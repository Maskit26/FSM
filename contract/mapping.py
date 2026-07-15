"""
Public Operation → internal Domain mechanism.

Clients never import this module; only the adapter uses it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


Kind = Literal["async_process", "rest", "session", "internal_only"]


@dataclass(frozen=True)
class OperationMapping:
    public: str
    kind: Kind
    """Worker process_name when kind == async_process."""
    process_name: Optional[str] = None
    """Logical REST route key when kind == rest | session."""
    rest_key: Optional[str] = None
    """Default ObjectRef.type when a target is required."""
    default_object_type: Optional[str] = None
    notes: str = ""


# Catalog aligned with specs/operations-catalog.md
OPERATION_MAP: Dict[str, OperationMapping] = {
    # Session / Core-backed identity
    "LOGIN": OperationMapping("LOGIN", "session", rest_key="users.login"),
    "LOGOUT": OperationMapping("LOGOUT", "session", rest_key="users.logout"),
    "CREATE_USER": OperationMapping("CREATE_USER", "rest", rest_key="users.register"),
    "CREATE_CAR": OperationMapping(
        "CREATE_CAR", "rest", rest_key="users.car_create", default_object_type="user"
    ),
    "VERIFY_USER": OperationMapping(
        "VERIFY_USER", "rest", rest_key="users.verify_state", default_object_type="user"
    ),
    # Orders
    "CREATE_ORDER": OperationMapping(
        "CREATE_ORDER",
        "async_process",
        process_name="order_creation",
        rest_key="client.create_order_request",
        notes="Creates order via order_request pipeline; return ObjectRef(order) in result.objects",
    ),
    "CANCEL_ORDER": OperationMapping(
        "CANCEL_ORDER",
        "async_process",
        process_name="cancel_order",
        default_object_type="order",
    ),
    "ASSIGN_COURIER": OperationMapping(
        "ASSIGN_COURIER",
        "async_process",
        process_name="assign_executor",
        default_object_type="order",
        notes="params: target_user_id, leg=pickup|delivery",
    ),
    "REMOVE_COURIER": OperationMapping(
        "REMOVE_COURIER",
        "async_process",
        process_name="remove_executor",
        default_object_type="order",
    ),
    "CONFIRM_COURIER2_DELIVERY": OperationMapping(
        "CONFIRM_COURIER2_DELIVERY",
        "async_process",
        process_name="confirm_courier2_delivery",
        default_object_type="order",
    ),
    "CONFIRM_PICKUP": OperationMapping(
        "CONFIRM_PICKUP",
        "rest",
        rest_key="order.recipient_confirmed",
        default_object_type="order",
        notes="Maps to db.order_recipient_confirmed / FSM action order_recipient_confirmed",
    ),
    "BIND_ORDER_TO_TRIP": OperationMapping(
        "BIND_ORDER_TO_TRIP",
        "async_process",
        process_name="bind_order_to_trip",
        default_object_type="order",
    ),
    "REPORT_ERROR": OperationMapping(
        "REPORT_ERROR",
        "async_process",
        process_name="report_error",
    ),
    # Lockers / cells
    "OPEN_CELL": OperationMapping(
        "OPEN_CELL",
        "async_process",
        process_name="open_cell",
        default_object_type="locker",
        notes="PIN resolved by Domain when omitted (SR); may be supplied by PI",
    ),
    "CLOSE_CELL": OperationMapping(
        "CLOSE_CELL",
        "async_process",
        process_name="close_cell",
        default_object_type="locker",
    ),
    "REQUEST_LOCKER_ACCESS_CODE": OperationMapping(
        "REQUEST_LOCKER_ACCESS_CODE",
        "async_process",
        process_name="request_locker_access_code",
    ),
    "REPORT_LOCKER_ERROR": OperationMapping(
        "REPORT_LOCKER_ERROR",
        "async_process",
        process_name="locker_error",
        default_object_type="locker",
    ),
    # Trips / driver exchange
    "START_TRIP": OperationMapping(
        "START_TRIP", "async_process", process_name="start_trip", default_object_type="trip"
    ),
    "ARRIVE_AT_DESTINATION": OperationMapping(
        "ARRIVE_AT_DESTINATION",
        "async_process",
        process_name="arrive_at_destination",
        default_object_type="trip",
    ),
    "COMPLETE_TRIP": OperationMapping(
        "COMPLETE_TRIP",
        "async_process",
        process_name="complete_trip",
        default_object_type="trip",
    ),
    "CANCEL_TRIP": OperationMapping(
        "CANCEL_TRIP", "async_process", process_name="cancel_trip", default_object_type="trip"
    ),
    "RESERVE_DIRECTION_SLOT": OperationMapping(
        "RESERVE_DIRECTION_SLOT",
        "async_process",
        process_name="direction_reserve_slot",
        default_object_type="direction",
    ),
    "START_LOADING": OperationMapping(
        "START_LOADING",
        "async_process",
        process_name="driver_reservation_start_loading",
        default_object_type="driver_reservation",
    ),
    "COMPLETE_LOADING": OperationMapping(
        "COMPLETE_LOADING",
        "async_process",
        process_name="direction_complete_loading",
        default_object_type="direction",
    ),
    "CANCEL_RESERVATION": OperationMapping(
        "CANCEL_RESERVATION",
        "async_process",
        process_name="driver_reservation_cancel",
        default_object_type="driver_reservation",
    ),
}


# UI button_name → public Operation (partial; extend as button_states evolve)
BUTTON_TO_OPERATION: Dict[str, str] = {
    "open_cell": "OPEN_CELL",
    "close_cell": "CLOSE_CELL",
    "take_order": "ASSIGN_COURIER",
    "assign_courier": "ASSIGN_COURIER",
    "cancel_order": "CANCEL_ORDER",
    "reserve_slot": "RESERVE_DIRECTION_SLOT",
    "start_loading": "START_LOADING",
    "complete_loading": "COMPLETE_LOADING",
    "request_access_code": "REQUEST_LOCKER_ACCESS_CODE",
    "report_error": "REPORT_ERROR",
    "confirm_pickup": "CONFIRM_PICKUP",
    "confirm_delivery_with_code": "CONFIRM_COURIER2_DELIVERY",
}


def resolve(operation: str) -> OperationMapping:
    mapping = OPERATION_MAP.get(operation)
    if mapping is None:
        raise KeyError(operation)
    return mapping


def default_params_schema(operation: str) -> Dict[str, Any]:
    """Minimal JSON Schema stubs; refine per Operation as adapter matures."""
    common: Dict[str, Any] = {
        "type": "object",
        "additionalProperties": True,
        "properties": {},
        "required": [],
    }
    schemas: Dict[str, Dict[str, Any]] = {
        "CREATE_ORDER": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "recipient_user_id": {"type": "integer"},
                "parcel_type": {"type": "string"},
                "cell_size": {"type": "string"},
                "sender_delivery": {"type": "string", "enum": ["self", "courier"]},
                "recipient_delivery": {"type": "string", "enum": ["self", "courier"]},
            },
            "required": [
                "recipient_user_id",
                "parcel_type",
                "cell_size",
                "sender_delivery",
                "recipient_delivery",
            ],
        },
        "ASSIGN_COURIER": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "target_user_id": {"type": "integer"},
                "leg": {"type": "string", "enum": ["pickup", "delivery"]},
            },
            "required": ["target_user_id", "leg"],
        },
        "OPEN_CELL": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "pin": {"type": "string", "minLength": 4, "maxLength": 8},
                "leg": {"type": "string", "enum": ["pickup", "delivery"]},
            },
            "required": [],
        },
        "LOGIN": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "login": {"type": "string"},
                "password": {"type": "string"},
                "type": {"type": "string"},
            },
            "required": ["login", "password"],
        },
    }
    return schemas.get(operation, common)

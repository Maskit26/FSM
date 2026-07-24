"""Регистрация картриджа courier: операции, процессы и effects."""

from __future__ import annotations

from fsm_platform import ProcessDef
from fsm_platform.core.registry import (
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from fsm_platform.host.operations import default_operation_registry

from domains.courier.commands import (
    assign_executor,
    cancel_courier_order,
    cancel_reservation,
    close_cell,
    complete_loading,
    create_order,
    open_cell,
    remove_executor,
    request_locker_access_code,
    reserve_direction_slot,
    start_loading,
    start_trip,
    take_courier_order,
)
from domains.courier.context import (
    build_locker_context,
    build_order_context,
    build_reservation_context,
    build_trip_context,
)
from domains.courier.effects import (
    assign_executor_effect,
    cancel_reservation_effect,
    close_cell_effect,
    open_cell_effect,
    remove_executor_effect,
    reserve_locker_cell_effect,
    sync_locker_cell_status,
    sync_order_status,
    sync_reservation_status,
    sync_trip_status,
)
from domains.courier.guards import (
    can_assign_executor,
    can_cancel_reservation,
    can_close_cell,
    can_complete_loading,
    can_create_trip,
    can_expire_reservation,
    can_open_cell,
    can_remove_executor,
    can_reserve_direction_slot,
    can_reserve_locker_cell,
    can_start_loading,
    can_start_order_transit,
    can_start_trip,
)
from domains.courier.queries import (
    list_client_orders,
    list_courier_exchange,
    list_courier_orders,
    list_driver_exchange,
    list_driver_trips,
    view_locker_access_code,
)


def register_all(service_id: str) -> None:
    """
    Подключает операции и FSM-процессы домена к service_id.
    Назначение/снятие/открытие/закрытие — процессы assign/remove/open/close_cell;
    цепочки задаются guard_params на рёбрах графа.
    """
    default_operation_registry.register(
        service_id, "create_order", "command", create_order
    )
    default_operation_registry.register(
        service_id, "assign_executor", "command", assign_executor
    )
    default_operation_registry.register(
        service_id, "take_courier_order", "command", take_courier_order
    )
    default_operation_registry.register(
        service_id, "remove_executor", "command", remove_executor
    )
    default_operation_registry.register(
        service_id, "cancel_courier_order", "command", cancel_courier_order
    )
    default_operation_registry.register(
        service_id, "open_cell", "command", open_cell
    )
    default_operation_registry.register(
        service_id, "close_cell", "command", close_cell
    )
    default_operation_registry.register(
        service_id,
        "request_locker_access_code",
        "command",
        request_locker_access_code,
    )
    default_operation_registry.register(
        service_id, "reserve_direction_slot", "command", reserve_direction_slot
    )
    default_operation_registry.register(
        service_id, "start_loading", "command", start_loading
    )
    default_operation_registry.register(
        service_id, "cancel_reservation", "command", cancel_reservation
    )
    default_operation_registry.register(
        service_id, "complete_loading", "command", complete_loading
    )
    default_operation_registry.register(
        service_id, "start_trip", "command", start_trip
    )
    default_operation_registry.register(
        service_id, "list_client_orders", "query", list_client_orders
    )
    default_operation_registry.register(
        service_id, "list_courier_exchange", "query", list_courier_exchange
    )
    default_operation_registry.register(
        service_id, "list_courier_orders", "query", list_courier_orders
    )
    default_operation_registry.register(
        service_id, "list_driver_exchange", "query", list_driver_exchange
    )
    default_operation_registry.register(
        service_id, "list_driver_trips", "query", list_driver_trips
    )
    default_operation_registry.register(
        service_id, "view_locker_access_code", "query", view_locker_access_code
    )

    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="assign_executor",
            entity_type="order",
            event_name="assign_executor",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="remove_executor",
            entity_type="order",
            event_name="remove_executor",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="open_cell",
            entity_type="order",
            event_name="open_cell",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="close_cell",
            entity_type="order",
            event_name="close_cell",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="start_loading",
            entity_type="driver_reservations",
            event_name="start_loading",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="complete_loading",
            entity_type="driver_reservations",
            event_name="complete_loading",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="cancel_reservation",
            entity_type="driver_reservations",
            event_name="cancel_reservation",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="expire_reservation",
            entity_type="driver_reservations",
            event_name="expire_reservation",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="locker_reserve",
            entity_type="locker",
            event_name="locker_reserve_cell",
            context_builder=build_locker_context,
            initial_state="locker_free",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="start_trip",
            entity_type="trip",
            event_name="start_trip",
            context_builder=build_trip_context,
            initial_state="trip_assigned",
        )
    )
    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="start_order_transit",
            entity_type="order",
            event_name="start_order_transit",
            context_builder=build_order_context,
            initial_state="order_picked_up_from_post1",
        )
    )

    default_guard_registry.register(
        service_id, "can_assign_executor", can_assign_executor
    )
    default_guard_registry.register(
        service_id, "can_remove_executor", can_remove_executor
    )
    default_guard_registry.register(service_id, "can_open_cell", can_open_cell)
    default_guard_registry.register(service_id, "can_close_cell", can_close_cell)
    default_guard_registry.register(
        service_id, "can_start_loading", can_start_loading
    )
    default_guard_registry.register(
        service_id, "can_complete_loading", can_complete_loading
    )
    default_guard_registry.register(
        service_id, "can_cancel_reservation", can_cancel_reservation
    )
    default_guard_registry.register(
        service_id, "can_expire_reservation", can_expire_reservation
    )
    default_guard_registry.register(
        service_id, "can_reserve_locker_cell", can_reserve_locker_cell
    )
    default_guard_registry.register(
        service_id, "can_reserve_direction_slot", can_reserve_direction_slot
    )
    default_guard_registry.register(service_id, "can_create_trip", can_create_trip)
    default_guard_registry.register(service_id, "can_start_trip", can_start_trip)
    default_guard_registry.register(
        service_id, "can_start_order_transit", can_start_order_transit
    )
    default_effect_registry.register(
        service_id, "assign_executor_effect", assign_executor_effect
    )
    default_effect_registry.register(
        service_id, "remove_executor_effect", remove_executor_effect
    )
    default_effect_registry.register(
        service_id, "open_cell_effect", open_cell_effect
    )
    default_effect_registry.register(
        service_id, "close_cell_effect", close_cell_effect
    )
    default_effect_registry.register(
        service_id, "sync_locker_cell_status", sync_locker_cell_status
    )
    default_effect_registry.register(
        service_id, "reserve_locker_cell_effect", reserve_locker_cell_effect
    )
    default_effect_registry.register(
        service_id, "sync_reservation_status", sync_reservation_status
    )
    default_effect_registry.register(
        service_id, "cancel_reservation_effect", cancel_reservation_effect
    )
    default_effect_registry.register(
        service_id, "sync_trip_status", sync_trip_status
    )
    default_effect_registry.register(
        service_id, "sync_order_status", sync_order_status
    )

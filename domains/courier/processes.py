"""Регистрация картриджа courier: операции, процессы, guards, effects."""

from __future__ import annotations

from fsm_platform.domain_runtime import (
    DomainProcessDef,
    effects as effect_registry,
    guards as guard_registry,
    operations as operation_registry,
    processes as process_registry,
    set_outbox_handler,
)

from domains.courier.commands import (
    assign_executor,
    bind_telegram,
    cancel_courier_order,
    cancel_reservation,
    close_cell,
    complete_loading,
    complete_trip,
    confirm_courier2_delivery,
    create_car,
    create_order,
    create_order_request,
    login_user,
    logout_user,
    open_cell,
    register_user,
    remove_executor,
    request_locker_access_code,
    reserve_direction_slot,
    start_loading,
    start_trip,
    take_courier_order,
    verify_user,
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
    confirm_courier2_delivery_effect,
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
    can_complete_trip,
    can_confirm_courier2_delivery,
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
    Вызывается domain_runtime при старте domain service.
    """
    operation_registry.register(
        service_id, "create_order_request", "command", create_order_request
    )
    operation_registry.register(
        service_id, "create_order", "command", create_order
    )
    operation_registry.register(
        service_id, "register_user", "command", register_user
    )
    operation_registry.register(
        service_id, "bind_telegram", "command", bind_telegram
    )
    operation_registry.register(
        service_id, "login_user", "command", login_user
    )
    operation_registry.register(
        service_id, "logout_user", "command", logout_user
    )
    operation_registry.register(service_id, "create_car", "command", create_car)
    operation_registry.register(
        service_id, "verify_user", "command", verify_user
    )
    operation_registry.register(
        service_id, "assign_executor", "command", assign_executor
    )
    operation_registry.register(
        service_id, "take_courier_order", "command", take_courier_order
    )
    operation_registry.register(
        service_id, "remove_executor", "command", remove_executor
    )
    operation_registry.register(
        service_id, "cancel_courier_order", "command", cancel_courier_order
    )
    operation_registry.register(service_id, "open_cell", "command", open_cell)
    operation_registry.register(service_id, "close_cell", "command", close_cell)
    operation_registry.register(
        service_id,
        "request_locker_access_code",
        "command",
        request_locker_access_code,
    )
    operation_registry.register(
        service_id, "reserve_direction_slot", "command", reserve_direction_slot
    )
    operation_registry.register(
        service_id, "start_loading", "command", start_loading
    )
    operation_registry.register(
        service_id, "cancel_reservation", "command", cancel_reservation
    )
    operation_registry.register(
        service_id, "complete_loading", "command", complete_loading
    )
    operation_registry.register(
        service_id, "start_trip", "command", start_trip
    )
    operation_registry.register(
        service_id, "complete_trip", "command", complete_trip
    )
    operation_registry.register(
        service_id,
        "confirm_courier2_delivery",
        "command",
        confirm_courier2_delivery,
    )
    operation_registry.register(
        service_id, "list_client_orders", "query", list_client_orders
    )
    operation_registry.register(
        service_id, "list_courier_exchange", "query", list_courier_exchange
    )
    operation_registry.register(
        service_id, "list_courier_orders", "query", list_courier_orders
    )
    operation_registry.register(
        service_id, "list_driver_exchange", "query", list_driver_exchange
    )
    operation_registry.register(
        service_id, "list_driver_trips", "query", list_driver_trips
    )
    operation_registry.register(
        service_id, "view_locker_access_code", "query", view_locker_access_code
    )

    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="assign_executor",
            entity_type="order",
            event_name="assign_executor",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="remove_executor",
            entity_type="order",
            event_name="remove_executor",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="open_cell",
            entity_type="order",
            event_name="open_cell",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="close_cell",
            entity_type="order",
            event_name="close_cell",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="start_loading",
            entity_type="driver_reservations",
            event_name="start_loading",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="complete_loading",
            entity_type="driver_reservations",
            event_name="complete_loading",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="cancel_reservation",
            entity_type="driver_reservations",
            event_name="cancel_reservation",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="expire_reservation",
            entity_type="driver_reservations",
            event_name="expire_reservation",
            context_builder=build_reservation_context,
            initial_state="reservation_active",
        )
    )
    from domains.courier.recovery import on_locker_reserve_failed

    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="locker_reserve",
            entity_type="locker",
            event_name="locker_reserve_cell",
            context_builder=build_locker_context,
            initial_state="locker_free",
            on_failed=on_locker_reserve_failed,
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="start_trip",
            entity_type="trip",
            event_name="start_trip",
            context_builder=build_trip_context,
            initial_state="trip_assigned",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="complete_trip",
            entity_type="trip",
            event_name="complete_trip",
            context_builder=build_trip_context,
            initial_state="trip_in_progress",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="confirm_courier2_delivery",
            entity_type="order",
            event_name="confirm_courier2_delivery",
            context_builder=build_order_context,
            initial_state="order_courier2_parcel_delivered",
        )
    )
    process_registry.register(
        DomainProcessDef(
            service_id=service_id,
            process_name="start_order_transit",
            entity_type="order",
            event_name="start_order_transit",
            context_builder=build_order_context,
            initial_state="order_picked_up_from_post1",
        )
    )

    guard_registry.register(service_id, "can_assign_executor", can_assign_executor)
    guard_registry.register(service_id, "can_remove_executor", can_remove_executor)
    guard_registry.register(service_id, "can_open_cell", can_open_cell)
    guard_registry.register(service_id, "can_close_cell", can_close_cell)
    guard_registry.register(
        service_id, "can_confirm_courier2_delivery", can_confirm_courier2_delivery
    )
    guard_registry.register(service_id, "can_start_loading", can_start_loading)
    guard_registry.register(
        service_id, "can_complete_loading", can_complete_loading
    )
    guard_registry.register(
        service_id, "can_cancel_reservation", can_cancel_reservation
    )
    guard_registry.register(
        service_id, "can_expire_reservation", can_expire_reservation
    )
    guard_registry.register(
        service_id, "can_reserve_locker_cell", can_reserve_locker_cell
    )
    guard_registry.register(
        service_id, "can_reserve_direction_slot", can_reserve_direction_slot
    )
    guard_registry.register(service_id, "can_create_trip", can_create_trip)
    guard_registry.register(service_id, "can_start_trip", can_start_trip)
    guard_registry.register(service_id, "can_complete_trip", can_complete_trip)
    guard_registry.register(
        service_id, "can_start_order_transit", can_start_order_transit
    )

    effect_registry.register(
        service_id, "assign_executor_effect", assign_executor_effect
    )
    effect_registry.register(
        service_id, "remove_executor_effect", remove_executor_effect
    )
    effect_registry.register(service_id, "open_cell_effect", open_cell_effect)
    effect_registry.register(service_id, "close_cell_effect", close_cell_effect)
    effect_registry.register(
        service_id, "sync_locker_cell_status", sync_locker_cell_status
    )
    effect_registry.register(
        service_id, "reserve_locker_cell_effect", reserve_locker_cell_effect
    )
    effect_registry.register(
        service_id, "sync_reservation_status", sync_reservation_status
    )
    effect_registry.register(
        service_id, "cancel_reservation_effect", cancel_reservation_effect
    )
    effect_registry.register(service_id, "sync_trip_status", sync_trip_status)
    effect_registry.register(service_id, "sync_order_status", sync_order_status)
    effect_registry.register(
        service_id,
        "confirm_courier2_delivery_effect",
        confirm_courier2_delivery_effect,
    )

    from domains.courier.core.deliver import handle_core_outbox

    set_outbox_handler(handle_core_outbox)

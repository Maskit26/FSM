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
    create_order,
    remove_executor,
    take_courier_order,
)
from domains.courier.context import build_order_context
from domains.courier.effects import assign_executor_effect, remove_executor_effect
from domains.courier.guards import can_assign_executor, can_remove_executor
from domains.courier.queries import (
    list_client_orders,
    list_courier_exchange,
    list_courier_orders,
)


def register_all(service_id: str) -> None:
    """
    Подключает операции и FSM-процессы домена к service_id.
    Назначение/снятие исполнителя — процессы assign_executor / remove_executor;
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
        service_id, "list_client_orders", "query", list_client_orders
    )
    default_operation_registry.register(
        service_id, "list_courier_exchange", "query", list_courier_exchange
    )
    default_operation_registry.register(
        service_id, "list_courier_orders", "query", list_courier_orders
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

    default_guard_registry.register(
        service_id, "can_assign_executor", can_assign_executor
    )
    default_guard_registry.register(
        service_id, "can_remove_executor", can_remove_executor
    )
    default_effect_registry.register(
        service_id, "assign_executor_effect", assign_executor_effect
    )
    default_effect_registry.register(
        service_id, "remove_executor_effect", remove_executor_effect
    )

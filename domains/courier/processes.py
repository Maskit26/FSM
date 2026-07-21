"""Регистрация картриджа courier: операции, процессы и effects."""

from __future__ import annotations

from fsm_platform import ProcessDef
from fsm_platform.registry import (
    default_effect_registry,
    default_process_registry,
)
from fsm_host.operations import default_operation_registry

from domains.courier.commands import create_order
from domains.courier.context import build_order_context
from domains.courier.effects import assign_courier1_effect
from domains.courier.queries import list_client_orders, list_courier_exchange


def register_all(service_id: str) -> None:
    """
    Подключает все операции и FSM-процессы домена к указанному service_id.
    Вызывается один раз при boot платформы.
    """
    default_operation_registry.register(
        service_id, "create_order", "command", create_order
    )
    default_operation_registry.register(
        service_id, "list_client_orders", "query", list_client_orders
    )
    default_operation_registry.register(
        service_id, "list_courier_exchange", "query", list_courier_exchange
    )

    default_process_registry.register(
        ProcessDef(
            service_id=service_id,
            process_name="order_assign_courier1",
            entity_type="order",
            event_name="order_assign_courier1_to_order",
            context_builder=build_order_context,
            initial_state="order_created",
        )
    )

    default_effect_registry.register(
        service_id, "assign_courier1_effect", assign_courier1_effect
    )

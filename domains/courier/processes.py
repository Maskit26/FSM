from __future__ import annotations

from fsm_core.registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from fsm_core.types import ProcessDef

from .context import build_courier_context
from .effects import noop_effect, release_orders_on_reservation_cancel
from .guards import always_allow, can_cancel_driver_reservation, is_driver

SERVICE_NAME = "courier"


def register_all(
    process_registry: ProcessRegistry = default_process_registry,
    guard_registry: GuardRegistry = default_guard_registry,
    effect_registry: EffectRegistry = default_effect_registry,
) -> ProcessRegistry:
    """Регистрация guards, effects и ProcessDef courier в platform registry."""
    guard_registry.register("always_allow", always_allow)
    guard_registry.register("is_driver", is_driver)
    guard_registry.register("can_cancel_driver_reservation", can_cancel_driver_reservation)

    effect_registry.register("noop_effect", noop_effect)
    effect_registry.register(
        "release_orders_on_reservation_cancel",
        release_orders_on_reservation_cancel,
    )

    process_registry.register(
        ProcessDef(
            service=SERVICE_NAME,
            process_name="driver_reservation_cancel",
            entity_type="driver_reservations",
            event_name="driver_reservation_cancel",
            context_builder=build_courier_context,
        )
    )

    return process_registry


register_all()

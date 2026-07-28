"""Вызовы доменной логики платформы — только через Contract API."""

from __future__ import annotations

from typing import Any, Optional

from fsm_platform.core.remote import RemoteRef
from fsm_platform.core.types import InstanceDict, RuntimeContext


def instance_to_contract(instance: InstanceDict) -> dict[str, Any]:
    """Snapshot instance для тела Contract API (FsmInstance)."""
    payload = instance.get("payload_json")
    if payload is None:
        payload = {}
    out: dict[str, Any] = {
        "service_id": str(instance.get("service_id") or ""),
        "payload_json": payload if isinstance(payload, dict) else {},
    }
    for key in (
        "id",
        "process_name",
        "entity_type",
        "entity_id",
        "actor_id",
        "graph_version",
        "status",
        "attempts",
    ):
        if key in instance and instance[key] is not None:
            out[key] = instance[key]
    return out


def call_context_builder(
    ref: Optional[RemoteRef],
    *,
    runtime_ctx: RuntimeContext,
    instance: InstanceDict,
) -> dict[str, Any]:
    if ref is None:
        return {}
    from fsm_platform.host.contract_client import get_contract_client

    return get_contract_client(ref.service_id).call_context(
        ref.name,
        runtime_ctx=dict(runtime_ctx or {}),
        instance=instance_to_contract(instance),
    )


def call_guard(
    ref: RemoteRef,
    *,
    context: dict[str, Any],
    guard_params: dict[str, Any],
    instance: InstanceDict,
) -> dict[str, Any]:
    from fsm_platform.host.contract_client import get_contract_client

    return get_contract_client(ref.service_id).call_guard(
        ref.name,
        context=dict(context or {}),
        guard_params=dict(guard_params or {}),
        instance=instance_to_contract(instance),
    )


def call_effect(
    ref: RemoteRef,
    *,
    context: dict[str, Any],
    effect_params: dict[str, Any],
    instance: InstanceDict,
) -> dict[str, Any]:
    from fsm_platform.host.contract_client import get_contract_client

    return get_contract_client(ref.service_id).call_effect(
        ref.name,
        context=dict(context or {}),
        effect_params=dict(effect_params or {}),
        instance=instance_to_contract(instance),
    )


def call_operation(
    ref: RemoteRef,
    *,
    kind: str,
    params: dict[str, Any],
    actor: dict[str, Any],
) -> dict[str, Any]:
    from fsm_platform.host.contract_client import get_contract_client

    client = get_contract_client(ref.service_id)
    actor_body = dict(actor or {})
    params_body = dict(params or {})
    if ref.kind == "query" or kind == "query":
        return client.call_query(ref.name, params=params_body, actor=actor_body)
    return client.call_command(ref.name, params=params_body, actor=actor_body)


def call_on_failed(
    ref: RemoteRef,
    *,
    instance: InstanceDict,
    last_error: str,
    process_name: str,
) -> None:
    from fsm_platform.host.contract_client import get_contract_client

    get_contract_client(ref.service_id).call_on_failed(
        process_name,
        instance=instance_to_contract(instance),
        last_error=last_error or "",
    )

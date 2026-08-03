"""
Применение декларативных platform side-effects из ответа Contract API.

Домен возвращает notify / cancel_instances / entity_states.
Платформа пишет в свою DB в рамках своей транзакции.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from fsm_platform.core.db_layer import SessionLike, default_db_layer
from fsm_platform.host.runtime import side_effects

_SIDE_KEYS = ("notify", "cancel_instances", "entity_states")


def extract_declared(data: Optional[dict[str, Any]]) -> dict[str, list[Any]]:
    """Достаёт side-effect поля из ответа effect/command/on-failed."""
    out: dict[str, list[Any]] = {
        "notify": [],
        "cancel_instances": [],
        "entity_states": [],
    }
    if not isinstance(data, dict):
        return out
    for key in _SIDE_KEYS:
        raw = data.get(key)
        if isinstance(raw, list):
            out[key].extend(raw)
    return out


def apply_declared(
    session_platform: SessionLike,
    *,
    service_id: str,
    data: Optional[dict[str, Any]] = None,
    notify: Optional[list[Any]] = None,
    cancel_instances: Optional[list[Any]] = None,
    entity_states: Optional[list[Any]] = None,
) -> dict[str, Any]:
    """
    Применяет декларации в текущей platform-транзакции.
    Возвращает краткий отчёт (для логов / диагностики).
    """
    declared = extract_declared(data)
    if notify:
        declared["notify"].extend(notify)
    if cancel_instances:
        declared["cancel_instances"].extend(cancel_instances)
    if entity_states:
        declared["entity_states"].extend(entity_states)

    stats = {
        "notify": 0,
        "cancel_instances": 0,
        "entity_states": 0,
    }

    for item in declared["entity_states"]:
        if not isinstance(item, dict):
            continue
        et = str(item.get("entity_type") or "").strip()
        state = str(item.get("state") or "").strip()
        eid = item.get("entity_id")
        if not et or eid is None or not state:
            raise ValueError("entity_states[] require entity_type, entity_id, state")
        default_db_layer.upsert_entity_state(
            session_platform, service_id, et, int(eid), state
        )
        stats["entity_states"] += 1

    for item in declared["cancel_instances"]:
        if not isinstance(item, dict):
            continue
        cancelled = _cancel_pending(
            session_platform,
            service_id=service_id,
            process_name=str(item.get("process_name") or "").strip(),
            payload_match=item.get("payload_match")
            if isinstance(item.get("payload_match"), dict)
            else {},
            except_instance_id=item.get("except_instance_id"),
            last_error=str(item.get("last_error") or "CANCELLED_BY_DOMAIN"),
        )
        stats["cancel_instances"] += len(cancelled)

    for item in declared["notify"]:
        if not isinstance(item, dict):
            continue
        channel = str(item.get("channel") or "").strip()
        destination = str(item.get("destination") or "").strip()
        event_type = str(item.get("event_type") or "").strip()
        if not channel or not destination or not event_type:
            raise ValueError(
                "notify[] require channel, destination, event_type"
            )
        side_effects.notify(
            session_platform,
            service_id=service_id,
            channel=channel,
            destination=destination,
            event_type=event_type,
            payload=item.get("payload")
            if isinstance(item.get("payload"), dict)
            else {},
            idempotency_key=(str(item.get("idempotency_key") or "").strip() or None),
        )
        stats["notify"] += 1

    return stats


def _cancel_pending(
    session_platform: SessionLike,
    *,
    service_id: str,
    process_name: str,
    payload_match: dict[str, Any],
    except_instance_id: Optional[Any],
    last_error: str,
) -> list[int]:
    if not process_name:
        raise ValueError("cancel_instances[].process_name required")
    except_id = (
        int(except_instance_id) if except_instance_id is not None else None
    )
    rows = default_db_layer.list_pending_instances(
        session_platform,
        service_id=service_id,
        process_name=process_name,
        limit=100,
    )
    cancelled: list[int] = []
    for row in rows:
        iid = int(row["id"])
        if except_id is not None and iid == except_id:
            continue
        payload = row.get("payload_json") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        if not isinstance(payload, dict):
            payload = {}
        match = True
        for k, v in payload_match.items():
            if payload.get(k) != v:
                match = False
                break
        if not match:
            continue
        if default_db_layer.mark_instance_cancelled(
            session_platform, iid, last_error=last_error
        ):
            cancelled.append(iid)
    return cancelled

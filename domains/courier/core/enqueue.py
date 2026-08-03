"""Core outbox notify[] builder (платформа применяет из ответа Contract API)."""

from __future__ import annotations

from typing import Any, Optional

from fsm_platform.host.runtime.runtime_context import current_service_id


def core_notify(
    *,
    op: str,
    payload: dict[str, Any],
    idempotency_key: str,
    service_id: Optional[str] = None,
) -> dict[str, Any]:
    """Один элемент notify[]: channel=core → outbox_worker → deliver.handle."""
    sid = (service_id or "").strip() or current_service_id()
    body = dict(payload)
    body["op"] = op
    body.setdefault("service_id", sid)
    return {
        "channel": "core",
        "destination": "CORE",
        "event_type": f"core.{op}",
        "payload": body,
        "idempotency_key": idempotency_key,
    }


# legacy alias — код должен использовать core_notify
def enqueue_core(*_a: Any, **_k: Any) -> int:
    raise RuntimeError(
        "enqueue_core removed: return notify=[core_notify(...)] in effect/command"
    )


def platform_available(_db: Any = None) -> bool:
    """Всегда True: platform side-effects идут декларативно в ответе."""
    return True

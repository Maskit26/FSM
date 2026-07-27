"""Enqueue Core ops into platform_outbox (channel=core)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fsm_platform.host import side_effects
from fsm_platform.host.runtime_context import current_service_id

logger = logging.getLogger(__name__)


def _platform_session(db: Any):
    if isinstance(db, dict):
        return db.get("platform")
    return None


def enqueue_core(
    db: Any,
    *,
    op: str,
    payload: dict[str, Any],
    idempotency_key: str,
    platform_session: Any = None,
    service_id: Optional[str] = None,
) -> int:
    """
    platform.notify(channel=core) → outbox_worker → deliver.handle.
    Raises ValueError если нет platform session.
    """
    sp = platform_session or _platform_session(db)
    if sp is None:
        raise ValueError("PLATFORM_SESSION_REQUIRED_FOR_CORE")

    sid = (service_id or "").strip() or current_service_id()
    body = dict(payload)
    body["op"] = op
    body.setdefault("service_id", sid)

    outbox_id = side_effects.notify(
        sp,
        service_id=sid,
        channel="core",
        destination="CORE",
        event_type=f"core.{op}",
        payload=body,
        idempotency_key=idempotency_key,
    )
    logger.info("core outbox enqueued op=%s id=%s key=%s", op, outbox_id, idempotency_key)
    return int(outbox_id)

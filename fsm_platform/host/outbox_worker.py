"""Outbox worker: доставка platform_outbox после commit FSM."""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Optional

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.engines import platform_session

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = int(os.environ.get("OUTBOX_MAX_ATTEMPTS", "8"))


def _payload_dict(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _backoff_seconds(attempts: int) -> int:
    # 5s, 15s, 45s, … cap 15m
    return min(900, 5 * (3 ** max(0, attempts - 1)))


def deliver_one(row: dict[str, Any]) -> None:
    """Синхронная доставка одной строки. Raises → retry."""
    from fsm_platform.host.runtime_context import service_scope

    channel = str(row.get("channel") or "").strip().lower()
    destination = str(row.get("destination") or "").strip()
    payload = _payload_dict(row.get("payload_json"))
    text = str(payload.get("text") or "").strip()
    if not text:
        text = json.dumps(payload, ensure_ascii=False)[:3500]

    service_id = str(row.get("service_id") or payload.get("service_id") or "").strip()

    def _deliver() -> None:
        if channel == "telegram":
            from output.telegram.sender import send_telegram_message

            send_telegram_message(chat_id=destination, text=text)
            return

        if channel in ("log", "dry_run"):
            logger.info(
                "outbox log channel=%s dest=%s text=%s",
                channel,
                destination,
                text[:300],
            )
            return

        if channel == "webhook":
            from output.webhook.sender import deliver_webhook

            secret = ""
            sub_id = payload.get("subscription_id")
            if sub_id is not None:
                sp_sec = platform_session()
                try:
                    sub = default_db_layer.get_webhook_subscription(
                        sp_sec,
                        service_id=service_id,
                        subscription_id=int(sub_id),
                    )
                    if sub:
                        secret = str(sub.get("secret") or "")
                finally:
                    sp_sec.close()
            body = {
                "event_id": payload.get("event_id"),
                "event_type": row.get("event_type") or payload.get("event_type"),
                "service_id": service_id or payload.get("service_id"),
                "instance_id": payload.get("instance_id"),
                "entity_type": payload.get("entity_type"),
                "entity_id": payload.get("entity_id"),
                "payload": payload.get("payload") or {},
            }
            deliver_webhook(
                url=destination,
                secret=secret,
                body=body,
                event_type=str(row.get("event_type") or ""),
            )
            return

        if channel in ("core", "http_external"):
            # Vendor-семантика в домене; platform только роутит outbox.
            # destination = credential key hint (CORE); payload.op обязателен.
            from domains.courier.core.deliver import handle_core_outbox

            body = dict(payload)
            if destination and not body.get("credential_key"):
                body["credential_key"] = destination
            handle_core_outbox(body)
            return

        raise RuntimeError(f"UNSUPPORTED_CHANNEL:{channel}")

    if service_id:
        with service_scope(service_id):
            _deliver()
    else:
        _deliver()


def process_one(*, batch_size: int = 10, service_id: Optional[str] = None) -> bool:
    """
    Claim + deliver batch. True если была хотя бы одна строка.
    Каждая доставка — отдельный commit после успеха/ошибки строки.
    service_id — опциональный фильтр тенанта.
    """
    sp = platform_session()
    claimed: list[dict[str, Any]] = []
    try:
        claimed = default_db_layer.claim_pending_outbox(
            sp, limit=batch_size, service_id=service_id
        )
        sp.commit()
    except Exception:
        sp.rollback()
        logger.exception("outbox claim failed")
        return False
    finally:
        sp.close()

    if not claimed:
        return False

    for row in claimed:
        oid = int(row["id"])
        attempts = int(row.get("attempts") or 1)
        sp2 = platform_session()
        try:
            deliver_one(row)
            default_db_layer.mark_outbox_sent(sp2, oid)
            sp2.commit()
            logger.info(
                "outbox SENT id=%s channel=%s dest=%s",
                oid,
                row.get("channel"),
                row.get("destination"),
            )
        except Exception as exc:
            sp2.rollback()
            sp3 = platform_session()
            try:
                dead = attempts >= _MAX_ATTEMPTS
                default_db_layer.mark_outbox_retry(
                    sp3,
                    oid,
                    error=str(exc),
                    backoff_seconds=_backoff_seconds(attempts),
                    dead=dead,
                )
                sp3.commit()
                logger.warning(
                    "outbox %s id=%s attempts=%s err=%s",
                    "DEAD" if dead else "RETRY",
                    oid,
                    attempts,
                    exc,
                )
            except Exception:
                sp3.rollback()
                logger.exception("outbox mark retry failed id=%s", oid)
            finally:
                sp3.close()
        finally:
            sp2.close()
    return True


def run_loop(
    poll_seconds: float = 1.0, *, service_id: Optional[str] = None
) -> None:
    """Опциональный standalone-цикл outbox (обычно вызывается из fsm_worker)."""
    logger.info(
        "outbox-only loop started%s",
        f" service_id={service_id}" if service_id else "",
    )
    while True:
        worked = process_one(service_id=service_id)
        if not worked:
            time.sleep(poll_seconds)

"""
FSM worker: claim instance → run_instance → dual-DB commit (§4.7 / §4.7.1).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

from sqlalchemy import text

from fsm_platform import run_instance
from fsm_platform.types import FsmResult
from fsm_host import side_effects
from fsm_host.engines import domain_session, platform_session

logger = logging.getLogger(__name__)


def _claim_one(session_platform) -> Optional[dict[str, Any]]:
    row = session_platform.execute(
        text(
            """
            SELECT id, service_id, process_name, entity_type, entity_id,
                   status, attempts, payload_json, requested_by_user_id
            FROM server_fsm_instances
            WHERE status = 'PENDING'
            ORDER BY id ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """
        )
    ).mappings().first()
    if row is None:
        return None
    session_platform.execute(
        text(
            """
            UPDATE server_fsm_instances
            SET status = 'PROCESSING', started_at = UTC_TIMESTAMP(), updated_at = UTC_TIMESTAMP()
            WHERE id = :id
            """
        ),
        {"id": row["id"]},
    )
    return dict(row)


def _mark_completed(session_platform, instance_id: int) -> None:
    session_platform.execute(
        text(
            """
            UPDATE server_fsm_instances
            SET status = 'COMPLETED', finished_at = UTC_TIMESTAMP(),
                updated_at = UTC_TIMESTAMP(), last_error = NULL
            WHERE id = :id
            """
        ),
        {"id": instance_id},
    )


def _failed_short_tx(instance: dict[str, Any], last_error: str) -> None:
    """§4.7 FAILED notify in a separate short platform transaction."""
    sp = platform_session()
    try:
        sp.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'FAILED', last_error = :err,
                    finished_at = UTC_TIMESTAMP(), updated_at = UTC_TIMESTAMP(),
                    attempts = attempts + 1
                WHERE id = :id
                """
            ),
            {"id": instance["id"], "err": (last_error or "")[:2000]},
        )
        side_effects.emit_event(
            sp,
            service_id=str(instance["service_id"]),
            event_type="fsm.instance.failed",
            instance_id=int(instance["id"]),
            entity_type=instance.get("entity_type"),
            entity_id=instance.get("entity_id"),
            payload={"last_error": last_error},
        )
        sp.commit()
    except Exception:
        sp.rollback()
        logger.exception("FAILED short tx failed instance_id=%s", instance.get("id"))
        raise
    finally:
        sp.close()


def _enqueue_reconcile(
    instance: dict[str, Any],
    result: FsmResult,
) -> None:
    """Domain committed, platform commit failed — §4.7.1."""
    payload = result.payload or {}
    sp = platform_session()
    try:
        sp.execute(
            text(
                """
                INSERT INTO platform_reconcile_queue
                    (service_id, instance_id, entity_type, entity_id,
                     from_state, to_state, event_name, transition_id,
                     payload_json, status, attempts, created_at, updated_at)
                VALUES
                    (:service_id, :instance_id, :entity_type, :entity_id,
                     :from_state, :to_state, :event_name, :transition_id,
                     :payload_json, 'PENDING', 0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    status = IF(status = 'DONE', status, 'PENDING'),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": instance["service_id"],
                "instance_id": instance["id"],
                "entity_type": instance.get("entity_type"),
                "entity_id": instance.get("entity_id"),
                "from_state": payload.get("from_state"),
                "to_state": payload.get("to_state"),
                "event_name": payload.get("event_name"),
                "transition_id": payload.get("transition_id"),
                "payload_json": json.dumps(payload),
            },
        )
        sp.commit()
        logger.error(
            "DUAL_COMMIT_PLATFORM_FAILED instance_id=%s queued reconcile",
            instance["id"],
        )
    except Exception:
        sp.rollback()
        logger.exception("reconcile enqueue failed instance_id=%s", instance.get("id"))
        raise
    finally:
        sp.close()


def process_one() -> bool:
    """Claim and process one PENDING instance. Returns True if work was done."""
    sp = platform_session()
    instance: Optional[dict[str, Any]] = None
    sd = None
    try:
        instance = _claim_one(sp)
        if instance is None:
            sp.rollback()
            return False
        sp.commit()  # release claim lock; instance is PROCESSING
    except Exception:
        sp.rollback()
        logger.exception("claim failed")
        return False
    finally:
        if instance is None:
            sp.close()

    assert instance is not None
    service_id = str(instance["service_id"])
    sp = platform_session()
    try:
        sd = domain_session(service_id)
        runtime_ctx: dict[str, Any] = {}
        db = {"platform": sp, "domain": sd}

        result = run_instance(sp, sd, db, runtime_ctx, instance)

        if result.new_state == "COMPLETED":
            side_effects.emit_event(
                sp,
                service_id=service_id,
                event_type="fsm.instance.completed",
                instance_id=int(instance["id"]),
                entity_type=instance.get("entity_type"),
                entity_id=instance.get("entity_id"),
                payload=result.payload,
            )
            _mark_completed(sp, int(instance["id"]))
            try:
                sd.commit()
            except Exception:
                sd.rollback()
                sp.rollback()
                logger.exception("domain commit failed instance_id=%s", instance["id"])
                _failed_short_tx(instance, "DOMAIN_COMMIT_FAILED")
                return True
            try:
                sp.commit()
            except Exception:
                sp.rollback()
                logger.exception(
                    "platform commit failed after domain ok instance_id=%s",
                    instance["id"],
                )
                _enqueue_reconcile(instance, result)
                return True
            return True

        # FAILED path: rollback both, then short tx
        sd.rollback()
        sp.rollback()
        _failed_short_tx(instance, result.last_error or "FAILED")
        return True
    except Exception as exc:
        logger.exception("process_one crashed instance_id=%s", instance.get("id"))
        try:
            if sd is not None:
                sd.rollback()
            sp.rollback()
        except Exception:
            pass
        _failed_short_tx(instance, f"WORKER_CRASH: {exc}")
        return True
    finally:
        if sd is not None:
            sd.close()
        sp.close()


def run_loop(poll_seconds: float = 1.0) -> None:
    logger.info("fsm worker loop started")
    while True:
        worked = process_one()
        if not worked:
            time.sleep(poll_seconds)

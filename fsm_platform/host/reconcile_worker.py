"""Reconcile worker: докат platform после domain ok / platform commit fail (§4.7.1)."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.core.sagas import on_child_terminal
from fsm_platform.host.engines import platform_session
from fsm_platform.host.webhooks import emit_event_with_webhooks

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = int(os.environ.get("RECONCILE_MAX_ATTEMPTS", "8"))


def _payload_dict(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("payload")
    if isinstance(raw, dict):
        return raw
    return {}


def dock_platform(row: dict[str, Any]) -> None:
    """
    Идемпотентный докат только platform-части.
    Запрещено: domain effects / guards / run_instance.
    """
    service_id = str(row["service_id"])
    instance_id = int(row["instance_id"])
    entity_type = str(row["entity_type"])
    entity_id = int(row["entity_id"])
    from_state = str(row["from_state"] or "")
    to_state = str(row["to_state"] or "")
    event_name = str(row.get("event_name") or "")
    transition_id = int(row["transition_id"])
    payload = _payload_dict(row)

    sp = platform_session()
    try:
        current = default_db_layer.get_entity_state(
            sp, service_id, entity_type, entity_id, for_update=True
        )
        if current is None:
            default_db_layer.insert_entity_state_initial(
                sp, service_id, entity_type, entity_id, to_state
            )
        elif current != to_state:
            if from_state and current == from_state:
                ok = default_db_layer.cas_entity_state(
                    sp,
                    service_id,
                    entity_type,
                    entity_id,
                    from_state=from_state,
                    to_state=to_state,
                )
                if not ok:
                    raise RuntimeError(
                        f"RECONCILE_CAS_FAILED actual="
                        f"{default_db_layer.get_entity_state(sp, service_id, entity_type, entity_id)}"
                    )
            else:
                # Неожиданный drift — форсируем to_state (domain уже закоммичен).
                logger.warning(
                    "reconcile force state instance=%s expected_from=%s actual=%s → %s",
                    instance_id,
                    from_state,
                    current,
                    to_state,
                )
                default_db_layer.upsert_entity_state(
                    sp, service_id, entity_type, entity_id, to_state
                )

        default_db_layer.insert_transition_log_idempotent(
            sp,
            service_id=service_id,
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state or to_state,
            to_state=to_state,
            event_name=event_name,
            transition_id=transition_id,
            instance_id=instance_id,
            user_id=payload.get("actor_id"),
        )

        inst = default_db_layer.get_fsm_instance_by_id(sp, instance_id)
        if inst is not None and str(inst.get("status")) != "COMPLETED":
            default_db_layer.mark_instance_completed(sp, instance_id)

        emit_event_with_webhooks(
            sp,
            service_id=service_id,
            event_type="fsm.instance.completed",
            instance_id=instance_id,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {
                "reconcile": True,
                "transition_id": transition_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
            },
            correlation_id=f"reconcile:{instance_id}:{transition_id}",
        )

        on_child_terminal(sp, instance_id=instance_id, status="COMPLETED")
        sp.commit()
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def process_one(*, batch_size: int = 10, service_id: Optional[str] = None) -> bool:
    """Claim + dock batch. True если была хотя бы одна строка.
    service_id — опциональный фильтр тенанта.
    """
    sp = platform_session()
    claimed: list[dict[str, Any]] = []
    try:
        claimed = default_db_layer.claim_pending_reconcile(
            sp, limit=batch_size, service_id=service_id
        )
        sp.commit()
    except Exception:
        sp.rollback()
        logger.exception("reconcile claim failed")
        return False
    finally:
        sp.close()

    if not claimed:
        return False

    for row in claimed:
        rid = int(row["id"])
        attempts = int(row.get("attempts") or 1)
        try:
            dock_platform(row)
            sp2 = platform_session()
            try:
                default_db_layer.mark_reconcile_done(sp2, rid)
                sp2.commit()
                logger.info(
                    "reconcile DONE id=%s instance_id=%s",
                    rid,
                    row.get("instance_id"),
                )
            except Exception:
                sp2.rollback()
                raise
            finally:
                sp2.close()
        except Exception as exc:
            sp3 = platform_session()
            try:
                dead = attempts >= _MAX_ATTEMPTS
                default_db_layer.mark_reconcile_retry(
                    sp3, rid, error=str(exc), dead=dead
                )
                sp3.commit()
                logger.warning(
                    "reconcile %s id=%s attempts=%s err=%s",
                    "DEAD" if dead else "RETRY",
                    rid,
                    attempts,
                    exc,
                )
            except Exception:
                sp3.rollback()
                logger.exception("reconcile mark retry failed id=%s", rid)
            finally:
                sp3.close()
    return True

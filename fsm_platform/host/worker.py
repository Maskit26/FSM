"""
FSM worker: claim инстанса → run_instance → dual-DB commit.

SQL нет — записи в platform идут через fsm_platform.core.db_layer.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from fsm_platform import run_instance
from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.core.registry import default_process_registry
from fsm_platform.core.sagas import on_child_terminal
from fsm_platform.core.types import FsmResult
from fsm_platform.host import side_effects
from fsm_platform.host.engines import domain_session, platform_session
from fsm_platform.host.retry_policy import backoff_seconds, should_retry

logger = logging.getLogger(__name__)


def _fire_due_timers(*, limit: int = 20) -> bool:
    """
    SCHEDULED timers с fire_at<=now → enqueue process + FIRED.
    True если хотя бы один таймер обработан.
    """
    sp = platform_session()
    try:
        due = default_db_layer.claim_due_timers(sp, limit=limit)
        if not due:
            sp.rollback()
            return False
        for timer in due:
            payload = timer.get("payload") or {}
            actor_raw = (
                payload.get("executor_user_id")
                or payload.get("driver_user_id")
                or payload.get("actor_id")
            )
            actor_id = int(actor_raw) if actor_raw is not None else None
            default_db_layer.insert_fsm_instance(
                sp,
                service_id=str(timer["service_id"]),
                process_name=str(timer["process_name"]),
                entity_type=str(timer["entity_type"]),
                entity_id=int(timer["entity_id"]),
                payload=payload,
                actor_id=actor_id,
            )
            logger.info(
                "timer fired id=%s process=%s entity=%s/%s",
                timer.get("id"),
                timer.get("process_name"),
                timer.get("entity_type"),
                timer.get("entity_id"),
            )
        sp.commit()
        return True
    except Exception:
        sp.rollback()
        logger.exception("fire_due_timers failed")
        return False
    finally:
        sp.close()


def _call_on_failed(instance: dict[str, Any], last_error: str) -> None:
    """ProcessDef.on_failed — domain recovery после терминального FAILED."""
    service_id = str(instance["service_id"])
    process_name = str(instance.get("process_name") or "")
    process_def = default_process_registry.get(service_id, process_name)
    if process_def is None or process_def.on_failed is None:
        return

    sp = platform_session()
    sd = None
    try:
        sd = domain_session(service_id)
        db = {"platform": sp, "domain": sd}
        process_def.on_failed(sp, sd, db, instance, last_error or "")
        sd.commit()
        sp.commit()
    except Exception:
        if sd is not None:
            try:
                sd.rollback()
            except Exception:
                pass
        try:
            sp.rollback()
        except Exception:
            pass
        logger.exception(
            "on_failed handler crashed process=%s instance_id=%s",
            process_name,
            instance.get("id"),
        )
    finally:
        if sd is not None:
            sd.close()
        sp.close()


def _finish_failure(instance: dict[str, Any], last_error: str) -> None:
    """
    Retry (PENDING + backoff) или терминальный FAILED + event + on_failed.
    Domain/platform рабочие tx уже откачены.
    """
    err = last_error or "FAILED"
    attempts_after = int(instance.get("attempts") or 0) + 1

    if should_retry(err, attempts_after=attempts_after):
        delay = backoff_seconds(attempts_after)
        sp = platform_session()
        try:
            default_db_layer.mark_instance_retry(
                sp,
                int(instance["id"]),
                last_error=err,
                attempts=attempts_after,
                backoff_seconds=delay,
            )
            sp.commit()
            logger.warning(
                "instance RETRY id=%s attempts=%s backoff=%ss err=%s",
                instance.get("id"),
                attempts_after,
                delay,
                err[:300],
            )
        except Exception:
            sp.rollback()
            logger.exception(
                "mark_instance_retry failed instance_id=%s", instance.get("id")
            )
            raise
        finally:
            sp.close()
        return

    sp = platform_session()
    try:
        default_db_layer.mark_instance_failed(
            sp, int(instance["id"]), err, attempts=attempts_after
        )
        side_effects.emit_event(
            sp,
            service_id=str(instance["service_id"]),
            event_type="fsm.instance.failed",
            instance_id=int(instance["id"]),
            entity_type=instance.get("entity_type"),
            entity_id=instance.get("entity_id"),
            payload={"last_error": err, "attempts": attempts_after},
        )
        on_child_terminal(
            sp,
            instance_id=int(instance["id"]),
            status="FAILED",
            last_error=err,
        )
        sp.commit()
    except Exception:
        sp.rollback()
        logger.exception("FAILED short tx failed instance_id=%s", instance.get("id"))
        raise
    finally:
        sp.close()

    _call_on_failed(instance, err)


def _enqueue_reconcile(
    instance: dict[str, Any],
    result: FsmResult,
) -> None:
    """
    Domain уже закоммичен, а platform commit упал — кладём задачу reconcile.
    Дальше отдельный процесс догоняет platform-состояние.
    """
    payload = result.payload or {}
    sp = platform_session()
    try:
        default_db_layer.enqueue_reconcile(
            sp,
            service_id=str(instance["service_id"]),
            instance_id=int(instance["id"]),
            entity_type=instance.get("entity_type"),
            entity_id=instance.get("entity_id"),
            from_state=payload.get("from_state"),
            to_state=payload.get("to_state"),
            event_name=payload.get("event_name"),
            transition_id=payload.get("transition_id"),
            payload=payload,
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
    """
    Берёт один PENDING-инстанс и прогоняет FSM до COMPLETED или FAILED.
    Возвращает True, если была работа; False, если очередь пуста.
    """
    if _fire_due_timers():
        return True

    sp = platform_session()
    instance: Optional[dict[str, Any]] = None
    sd = None
    try:
        instance = default_db_layer.claim_pending_instance(sp)
        if instance is None:
            sp.rollback()
            return False
        sp.commit()
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
            default_db_layer.mark_instance_completed(sp, int(instance["id"]))
            on_child_terminal(
                sp,
                instance_id=int(instance["id"]),
                status="COMPLETED",
            )
            try:
                sd.commit()
            except Exception:
                sd.rollback()
                sp.rollback()
                logger.exception("domain commit failed instance_id=%s", instance["id"])
                _finish_failure(instance, "DOMAIN_COMMIT_FAILED")
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

        sd.rollback()
        sp.rollback()
        _finish_failure(instance, result.last_error or "FAILED")
        return True
    except Exception as exc:
        logger.exception("process_one crashed instance_id=%s", instance.get("id"))
        try:
            if sd is not None:
                sd.rollback()
            sp.rollback()
        except Exception:
            pass
        _finish_failure(instance, f"WORKER_CRASH: {exc}")
        return True
    finally:
        if sd is not None:
            sd.close()
        sp.close()


def run_loop(poll_seconds: float = 1.0) -> None:
    """Бесконечный цикл: FSM instances + outbox + reconcile."""
    logger.info("fsm worker loop started (fsm + outbox + reconcile)")
    while True:
        fsm_worked = process_one()
        outbox_worked = False
        reconcile_worked = False
        try:
            from fsm_platform.host.outbox_worker import process_one as process_outbox

            outbox_worked = process_outbox()
        except Exception:
            logger.exception("outbox process_one failed")
        try:
            from fsm_platform.host.reconcile_worker import (
                process_one as process_reconcile,
            )

            reconcile_worked = process_reconcile()
        except Exception:
            logger.exception("reconcile process_one failed")
        if not fsm_worked and not outbox_worked and not reconcile_worked:
            time.sleep(poll_seconds)

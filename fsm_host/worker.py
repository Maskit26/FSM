"""
FSM worker: claim инстанса → run_instance → dual-DB commit.

SQL нет — записи в platform идут через fsm_platform.db_layer.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from fsm_platform import run_instance
from fsm_platform.db_layer import default_db_layer
from fsm_platform.types import FsmResult
from fsm_host import side_effects
from fsm_host.engines import domain_session, platform_session

logger = logging.getLogger(__name__)


def _failed_short_tx(instance: dict[str, Any], last_error: str) -> None:
    """
    Короткая отдельная транзакция при FAILED: помечает инстанс и пишет событие.
    Нужна, чтобы ошибка зафиксировалась даже после rollback основной работы.
    """
    sp = platform_session()
    try:
        default_db_layer.mark_instance_failed(
            sp, int(instance["id"]), last_error or ""
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
    """Бесконечный цикл воркера: process_one, при пустой очереди — sleep."""
    logger.info("fsm worker loop started")
    while True:
        worked = process_one()
        if not worked:
            time.sleep(poll_seconds)

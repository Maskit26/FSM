# fsm_worker.py
"""FSM worker: claim instance → run_instance → commit/rollback."""

from __future__ import annotations

import json
import logging
import os
import socket
import time
from contextlib import contextmanager
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from db_layer import DatabaseLayer, DbLayerError
from domains.bootstrap import register_domains
from fsm_core.engine import run_instance
from fsm_core.registry import default_process_registry
from fsm_core.types import FsmResult

load_dotenv()

POLL_INTERVAL_SECONDS = int(os.getenv("FSM_POLL_INTERVAL_SECONDS", "5"))
BATCH_SIZE = int(os.getenv("FSM_BATCH_SIZE", "20"))
MAX_ATTEMPTS = int(os.getenv("FSM_MAX_ATTEMPTS", "5"))
STUCK_THRESHOLD_MINUTES = int(os.getenv("FSM_STUCK_THRESHOLD_MINUTES", "60"))
WORKER_ID = os.getenv("FSM_WORKER_ID", socket.gethostname())


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DB_HOST = get_required_env("DB_HOST")
DB_PORT = get_required_env("DB_PORT")
DB_NAME = get_required_env("DB_NAME")
DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "REQUIRED").upper().replace("-", "_")
DB_SSL_CA = os.getenv("DB_SSL_CA")

DATABASE_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
    query={"charset": "utf8mb4"},
)

connect_args: Dict[str, Any] = {}
if DB_SSL_MODE in {"REQUIRED", "PREFERRED", "VERIFY_CA", "VERIFY_IDENTITY"}:
    connect_args["ssl_disabled"] = False
    if DB_SSL_CA:
        connect_args["ssl_ca"] = DB_SSL_CA
    if DB_SSL_MODE in {"VERIFY_CA", "VERIFY_IDENTITY"}:
        connect_args["ssl_verify_cert"] = True
    if DB_SSL_MODE == "VERIFY_IDENTITY":
        connect_args["ssl_verify_identity"] = True
elif DB_SSL_MODE == "DISABLED":
    connect_args["ssl_disabled"] = True

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@contextmanager
def session_scope() -> Session:
    """Transaction boundary воркера: commit при успехе, rollback при exception."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def row_to_instance_dict(row: Tuple[Any, ...]) -> Dict[str, Any]:
    """Строка server_fsm_instances → dict для run_instance."""
    instance = {
        "id": row[0],
        "entity_type": row[1],
        "entity_id": row[2],
        "process_name": row[3],
        "fsm_state": row[4],
        "next_timer_at": row[5],
        "attempts_count": row[6],
        "last_error": row[7],
        "requested_by_user_id": row[8],
        "requested_user_role": row[9],
        "target_user_id": row[10],
        "target_role": row[11],
        "metadata_json": row[12],
        "service": row[13] if len(row) > 13 and row[13] else "courier",
    }
    try:
        instance["metadata"] = (
            json.loads(instance["metadata_json"]) if instance.get("metadata_json") else {}
        )
    except (ValueError, TypeError, json.JSONDecodeError):
        logger.warning(
            "[FSM] invalid metadata_json instance_id=%s",
            instance["id"],
        )
        instance["metadata"] = {}
    return instance


def _log_error_independently(db: DatabaseLayer, instance: Dict[str, Any], error: str) -> None:
    """Записать ошибку в fsm_errors_log отдельной короткой транзакцией."""
    with session_scope() as log_session:
        db.log_error_to_db(
            session=log_session,
            error_message=error,
            entity_type=instance.get("entity_type"),
            entity_id=instance.get("entity_id"),
            action_name=instance.get("process_name"),
            user_id=instance.get("requested_by_user_id"),
        )


def _mark_instance_failed(
    db: DatabaseLayer,
    instance_id: int,
    error: str,
    attempts_increment: int = 1,
) -> None:
    """Пометить инстанс FAILED в отдельной транзакции (после rollback основной)."""
    with session_scope() as fail_session:
        db.update_fsm_instance(
            session=fail_session,
            instance_id=instance_id,
            new_state="FAILED",
            last_error=error,
            attempts_increment=attempts_increment,
        )


def process_instance(db: DatabaseLayer, instance_id: int) -> None:
    """Один инстанс = одна транзакция: claim → run_instance → сохранить результат."""
    with session_scope() as session:
        row = db.try_claim_fsm_instance(session, instance_id)
        if row is None:
            return

        instance = row_to_instance_dict(row)
        runtime_ctx = {"worker_id": WORKER_ID}

        logger.info(
            "[FSM] start id=%s service=%s process=%s attempts=%s worker=%s",
            instance["id"],
            instance["service"],
            instance["process_name"],
            instance["attempts_count"],
            WORKER_ID,
        )

        if instance["attempts_count"] >= MAX_ATTEMPTS:
            logger.warning("[FSM] max attempts id=%s", instance["id"])
            db.update_fsm_instance(
                session=session,
                instance_id=instance["id"],
                new_state="FAILED",
                last_error="MAX_ATTEMPTS_EXCEEDED",
                attempts_increment=0,
            )
            return

        try:
            result: FsmResult = run_instance(
                session=session,
                db=db,
                runtime_ctx=runtime_ctx,
                instance=instance,
            )
        except Exception as step_error:
            logger.exception("[FSM] exception id=%s", instance["id"])
            session.rollback()
            _log_error_independently(db, instance, str(step_error))
            _mark_instance_failed(
                db,
                instance_id=instance["id"],
                error=str(step_error),
                attempts_increment=1,
            )
            return

        if result.new_state == "FAILED":
            logger.warning(
                "[FSM] failed id=%s err=%s",
                instance["id"],
                result.last_error,
            )
            session.rollback()
            _log_error_independently(db, instance, result.last_error or "FSM_FAILED")
            _mark_instance_failed(
                db,
                instance_id=instance["id"],
                error=result.last_error or "FSM_FAILED",
                attempts_increment=result.attempts_increment or 1,
            )
            return

        db.update_fsm_instance(
            session=session,
            instance_id=instance["id"],
            new_state=result.new_state,
            last_error=result.last_error,
            next_timer_at=result.next_timer_at,
            attempts_increment=result.attempts_increment or 0,
        )
        logger.info("[FSM] done id=%s → %s", instance["id"], result.new_state)


def check_stuck_instances(db: DatabaseLayer) -> int:
    """PROCESSING дольше порога → FAILED (STUCK_TIMEOUT)."""
    with session_scope() as session:
        stuck_ids = db.get_stuck_fsm_instances(
            session=session,
            threshold_minutes=STUCK_THRESHOLD_MINUTES,
        )
        for instance_id in stuck_ids:
            db.update_fsm_instance(
                session=session,
                instance_id=instance_id,
                new_state="FAILED",
                last_error="STUCK_TIMEOUT",
                attempts_increment=0,
            )
        if stuck_ids:
            logger.warning("[FSM] stuck failed count=%s", len(stuck_ids))
        return len(stuck_ids)


def poll_once(db: DatabaseLayer) -> int:
    """Один цикл: список ready → claim/process каждого → stuck check."""
    with session_scope() as session:
        instance_ids = db.list_ready_fsm_instance_ids(session, limit=BATCH_SIZE)

    processed = 0
    for instance_id in instance_ids:
        process_instance(db, instance_id)
        processed += 1

    check_stuck_instances(db)
    return processed


def main() -> None:
    db = DatabaseLayer()
    register_domains()
    logger.info("[FSM] worker started worker_id=%s db=%s", WORKER_ID, DB_NAME)
    logger.info(
        "[FSM] registered processes: %s",
        default_process_registry.list_process_names(),
    )

    while True:
        try:
            count = poll_once(db)
            if count == 0:
                time.sleep(POLL_INTERVAL_SECONDS)
        except DbLayerError:
            logger.exception("[FSM] DbLayerError")
            time.sleep(POLL_INTERVAL_SECONDS)
        except Exception:
            logger.exception("[FSM] unexpected error")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

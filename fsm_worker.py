# fsm_worker.py

import time
import logging
import os
from typing import Any, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

from db_layer import DatabaseLayer, DbLayerError
from fsm_engine import (
    build_actions_context,
    run_fsm_step,
    FsmStepResult,
    PROCESS_DEFS,
)

load_dotenv()

# ================== CONFIG ==================

POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 20
MAX_ATTEMPTS = 5
STUCK_THRESHOLD_MINUTES = 60
MAX_WORKERS = 1

# ================== DB SETUP ==================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "fsm")
DB_PASSWORD = os.getenv("DB_PASSWORD", "6eF1zb")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ================== LOGGING ==================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

logger = logging.getLogger(__name__)

# ================== CONTEXT MANAGER ==================

@contextmanager
def get_db_session() -> Session:
    """Контекст для сессии в воркере (всегда write)."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ================== HELPERS ==================

def row_to_instance_dict(row: Tuple[Any, ...]) -> Dict[str, Any]:
    # row — это tuple из fetchall(), поэтому индексируем по позиции
    return {
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
    }

# ================== CORE ==================

def process_instance(
    db: DatabaseLayer,
    instance_row: Any,
) -> None:
    """
    ОДИН FSM instance = ОДНА транзакция.
    Сессия создаётся и управляется внутри этого вызова.
    """
    with get_db_session() as session:
        try:
            instance = row_to_instance_dict(instance_row)
            actions_ctx = build_actions_context(db)

            logger.info(
                "[FSM] start instance_id=%s process=%s state=%s attempts=%s",
                instance["id"],
                instance["process_name"],
                instance["fsm_state"],
                instance["attempts_count"],
            )

            # ================= MAX ATTEMPTS =================
            if instance["attempts_count"] >= MAX_ATTEMPTS:
                logger.warning("[FSM] max attempts exceeded id=%s", instance["id"])

                db.update_fsm_instance(
                    session=session,
                    instance_id=instance["id"],
                    new_state="FAILED",
                    last_error="MAX_ATTEMPTS_EXCEEDED",
                    attempts_increment=0,
                )

                if instance["process_name"] == "order_creation":
                    db.mark_request_failed(
                        session=session,
                        request_id=instance["entity_id"],
                        error_code="MAX_ATTEMPTS",
                        error_message="FSM attempts exceeded",
                    )
                return

            # ================= RUN STEP =================
            try:
                result: FsmStepResult = run_fsm_step(
                    session=session,
                    db=db,
                    actions_ctx=actions_ctx,
                    instance=instance,
                )

                if result is None:
                    raise RuntimeError("run_fsm_step returned None")

            except Exception as step_error:
                logger.exception("[FSM] step error instance_id=%s", instance["id"])
                result = FsmStepResult(
                    new_state="FAILED",
                    last_error=str(step_error),
                    attempts_increment=1,
                    payload=None,
                )

            # ================= UPDATE INSTANCE =================
            db.update_fsm_instance(
                session=session,
                instance_id=instance["id"],
                new_state=result.new_state,
                last_error=result.last_error,
                next_timer_at=result.next_timer_at,
                attempts_increment=result.attempts_increment or 0,
            )

            # ================= HANDLE ORDER REQUEST =================
            if instance["process_name"] == "order_creation":
                if result.new_state == "COMPLETED":
                    order_id = result.payload.get("order_id") if result.payload else None
                    logger.info(
                        "[FSM] order_creation COMPLETED request_id=%s order_id=%s",
                        instance["entity_id"],
                        order_id,
                    )
                    db.mark_request_completed(
                        session=session,
                        request_id=instance["entity_id"],
                        order_id=order_id,
                    )

                elif result.new_state == "FAILED":
                    logger.warning(
                        "[FSM] order_creation FAILED request_id=%s err=%s",
                        instance["entity_id"],
                        result.last_error,
                    )
                    db.mark_request_failed(
                        session=session,
                        request_id=instance["entity_id"],
                        error_code=result.last_error or "FSM_FAILED",
                        error_message=result.last_error or "FSM failed",
                    )

            logger.info("[FSM] done instance_id=%s → %s", instance["id"], result.new_state)

        except Exception:
            logger.exception("[FSM] CRITICAL ERROR instance_id=%s", instance["id"])
            raise  # чтобы rollback сработал

# ================== STUCK CHECK ==================

def check_stuck_instances(db: DatabaseLayer) -> int:
    with get_db_session() as session:
        try:
            stuck_ids = db.get_stuck_fsm_instances(
                session=session,
                threshold_minutes=STUCK_THRESHOLD_MINUTES,
            )

            if not stuck_ids:
                return 0

            for instance_id in stuck_ids:
                db.update_fsm_instance(
                    session=session,
                    instance_id=instance_id,
                    new_state="FAILED",
                    last_error="STUCK_TIMEOUT",
                    attempts_increment=0,
                )

            logger.warning("[FSM] stuck failed count=%s", len(stuck_ids))
            return len(stuck_ids)

        except Exception:
            logger.exception("[FSM] stuck check failed")
            raise

# ================== MAIN LOOP ==================

def main():
    db = DatabaseLayer()  # ← stateless, без параметров!

    logger.info("[FSM] worker started")
    logger.info("[FSM] processes: %s", list(PROCESS_DEFS.keys()))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            try:
                # Получаем готовые инстансы
                with get_db_session() as session:
                    rows = db.fetch_ready_fsm_instances(
                        session=session,
                        limit=BATCH_SIZE,
                    )

                if not rows:
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # Обрабатываем каждый инстанс в отдельной транзакции
                futures = [
                    executor.submit(process_instance, db, row)
                    for row in rows
                ]

                for f in as_completed(futures):
                    f.result()  # проброс исключений

                # Проверяем зависшие инстансы
                check_stuck_instances(db)

            except DbLayerError:
                logger.exception("[FSM] DbLayerError")
                time.sleep(POLL_INTERVAL_SECONDS)
            except Exception:
                logger.exception("[FSM] unexpected error")
                time.sleep(POLL_INTERVAL_SECONDS)

# ================== ENTRY ==================

if __name__ == "__main__":
    main()
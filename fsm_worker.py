# fsm_worker.py

import time
import logging
import os
import json
from typing import Any, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

from db_layer import DatabaseLayer, DbLayerError
from adapter.core_adapter import CoreAdapter
import domains.courier.processes  # noqa: F401 - registers courier processes
from fsm_core.engine import run_instance
from fsm_core.registry import default_process_registry
from fsm_core.types import FsmResult

load_dotenv()

# ================== CONFIG ==================

POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 20
MAX_ATTEMPTS = 5
STUCK_THRESHOLD_MINUTES = 60
MAX_WORKERS = 1
LOCKER_CLEANUP_INTERVAL_SECONDS = 300
_last_cleanup_check = 0

# ================== DB SETUP ==================

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

# ================== LOGGING ==================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

logger = logging.getLogger(__name__)

# ================== CORE ADAPTER ====================
core_adapter = CoreAdapter(
    core_url=os.getenv("CORE_URL", "https://ibronevik.ru/taxi/c/postamat/"),
    core_api_key=os.getenv("CORE_API_KEY", ""),
    core_timeout=5
)

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
    }
    instance["service"] = row[13] if len(row) > 13 and row[13] else "courier"
    return instance

# ================== CORE ==================

def process_instance(
    db: DatabaseLayer,
    core_adapter: CoreAdapter,
    instance_row: Any,
) -> None:
    """
    ОДИН FSM instance = ОДНА транзакция.
    Сессия создаётся и управляется внутри этого вызова.
    """
    with get_db_session() as session:
        try:
            instance = row_to_instance_dict(instance_row)
            # ДЕСЕРИАЛИЗАЦИЯ METADATA
            try:
                instance["metadata"] = json.loads(instance["metadata_json"]) if instance.get("metadata_json") else {}
            except (ValueError, TypeError, json.JSONDecodeError):
                logger.warning(
                    "[FSM] invalid metadata_json for instance_id=%s: %s",
                    instance["id"],
                    instance.get("metadata_json")
                )
                instance["metadata"] = {}

            runtime_ctx = {"core_adapter": core_adapter}

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
                result: FsmResult = run_instance(
                    session=session,
                    db=db,
                    runtime_ctx=runtime_ctx,
                    instance=instance,
                )
            except Exception as step_error:
                logger.exception("[FSM] step error instance_id=%s", instance["id"])               

                result = FsmResult(
                    new_state="FAILED",
                    last_error=str(step_error),
                    attempts_increment=1,
                    payload=None,
                )            

            # ================= UPDATE INSTANCE =================
            if result.new_state == "FAILED":
                logger.warning("[FSM] Step failed. Rolling back everything for instance %s", instance["id"])
                
                with SessionLocal() as log_session:
                    try:
                        db.log_error_to_db(
                            session=log_session,
                            error_message=result.last_error,
                            entity_type=instance["entity_type"],
                            entity_id=instance["entity_id"],
                            action_name=instance["process_name"],
                            user_id=instance["requested_by_user_id"]
                        )
                        log_session.commit()
                        logger.info("[FSM] Error log saved independently")
                    except Exception as log_e:
                        log_session.rollback()
                        logger.error("[FSM] Failed to save log_error_to_db: %s", log_e)
                session.rollback() 
                
                # записать ошибку в НОВОЙ транзакции
                db.update_fsm_instance(
                    session=session,
                    instance_id=instance["id"],
                    new_state="FAILED",
                    last_error=result.last_error,
                    attempts_increment=result.attempts_increment or 0,
                )
                return 
            
            # Если всё SUCCESS
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
            raise

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
    db = DatabaseLayer()
    global _last_cleanup_check
    logger.info("[FSM] worker started")
    logger.info("[FSM] processes: %s", default_process_registry.list_process_names("courier"))
    last_reservation_expire_check = 0    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            try: 
                # === ПРОВЕРКА ПРОСРОЧЕННЫХ РЕЗЕРВОВ (каждые 5 минут) ===
                now = time.time()
                if now - last_reservation_expire_check >= 300: 
                    with get_db_session() as session_inner:
                        expired = db.get_expired_reservations(session_inner)
                        
                        for res in expired:
                            logger.info(
                                "[AUTO_EXPIRE] Истёк резерв reservation_id=%s, driver=%s, direction=%s",
                                res["reservation_id"], res["driver_user_id"], res["direction_id"]
                            )
                            try:                                
                                released = db.expire_reservation_direct(
                                    session_inner,
                                    res["reservation_id"],
                                    999999  # системный пользователь
                                )
                                logger.info(
                                    "[AUTO_EXPIRE] reservation_id=%s: released=%d заказов, статус=reservation_expired",
                                    res["reservation_id"], released
                                )
                                
                            except Exception as e:
                                session_inner.rollback()
                                logger.exception(
                                    "[AUTO_EXPIRE] failed reservation_id=%s: %s",
                                    res["reservation_id"], e
                                )
                                continue
                        session_inner.commit()
                        
                    if expired:
                        logger.info("[AUTO_EXPIRE] Обработано %d просроченных резервов", len(expired))
                    
                    last_reservation_expire_check = now

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
                    executor.submit(process_instance, db, core_adapter, row)
                    for row in rows
                ]

                for f in as_completed(futures):
                    f.result()  # проброс исключений

                # Проверяем зависшие инстансы
                check_stuck_instances(db)                  

                # ================= Создаём инстанс locker_cleanup периодически =================
                current_time = time.time()
                if current_time - _last_cleanup_check >= LOCKER_CLEANUP_INTERVAL_SECONDS:
                    try:
                        with get_db_session() as session:
                            db.ensure_locker_cleanup_instance(
                                session=session,
                                threshold_minutes=30
                            )                           
                        
                        _last_cleanup_check = current_time
                        
                    except Exception as e:
                        logger.error(f"[FSM] Ошибка создания locker_cleanup: {e}")             

            except DbLayerError:
                logger.exception("[FSM] DbLayerError")
                time.sleep(POLL_INTERVAL_SECONDS)
            except Exception:
                logger.exception("[FSM] unexpected error")
                time.sleep(POLL_INTERVAL_SECONDS)

# ================== ENTRY ==================

if __name__ == "__main__":
    main()
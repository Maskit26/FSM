# fsm_worker.py
import time
import logging
from typing import Any, Dict, List
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from dotenv import load_dotenv

from db_layer import DatabaseLayer, DbLayerError
from fsm_engine import (
    build_actions_context,
    run_fsm_step,
    FsmStepResult,
    PROCESS_DEFS,
)

load_dotenv()

POLL_INTERVAL_SECONDS = 5  # Интервал поллинга
BATCH_SIZE = 20  # Увеличили батч
TRIP_ACTIVATION_INTERVAL = 30  # Секунды между проверками трипов
MAX_ATTEMPTS = 5  # Макс. попыток перед FAILED
STUCK_THRESHOLD_MINUTES = 60  # Застрявшие заявки > 60 мин → FAILED
MAX_WORKERS = 1  # Макс. потоков для параллельной обработки

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("/var/log/fsm_worker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_ready_instances(db: DatabaseLayer) -> List[Any]:
    """
    Выбирает готовые к обработке заявки из server_fsm_instances.
    """
    session = db.session
    rows = session.execute(
        text("""
            SELECT
                id,
                entity_type,
                entity_id,
                process_name,
                fsm_state,
                next_timer_at,
                attempts_count,
                last_error,
                requested_by_user_id,
                requested_user_role,
                target_user_id,
                target_role  
            FROM server_fsm_instances
            WHERE fsm_state NOT IN ('COMPLETED', 'FAILED')
              AND (next_timer_at IS NULL OR next_timer_at <= NOW())
            ORDER BY id
            LIMIT :limit
        """),
        {"limit": BATCH_SIZE},
    ).fetchall()
    return rows

def row_to_instance_dict(row: Any) -> Dict[str, Any]:
    """
    Преобразует строку БД в словарь для fsm_engine.
    """
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

def apply_fsm_result(
    db: DatabaseLayer,
    instance: Dict[str, Any],
    result: FsmStepResult,
):
    """
    Обновляет server_fsm_instances по результату FSM-шага.
    """
    session = db.session
    new_attempts = instance["attempts_count"] + (result.attempts_increment or 0)
    if result.new_state == "FAILED":
        logger.error(
            f"FAILED: instance_id={instance['id']}, "
            f"process={instance['process_name']}, "
            f"entity={instance['entity_type']}/{instance['entity_id']}, "
            f"user_id={instance['requested_by_user_id']}, "
            f"error: {result.last_error}"
        )
    else:
        logger.info(
            f"{result.new_state}: instance_id={instance['id']}, "
            f"process={instance['process_name']}, "
            f"entity={instance['entity_type']}/{instance['entity_id']}"
        )
    session.execute(
        text("""
            UPDATE server_fsm_instances
            SET fsm_state = :new_state,
                last_error = :last_error,
                next_timer_at = :next_timer_at,
                attempts_count = :attempts,
                updated_at = NOW()
            WHERE id = :id
        """),
        {
            "id": instance["id"],
            "new_state": result.new_state,
            "last_error": result.last_error,
            "next_timer_at": result.next_timer_at,
            "attempts": new_attempts,
        },
    )
    session.commit()

def process_instance(db: DatabaseLayer, actions_ctx: Dict[str, Any], instance: Dict[str, Any]) -> None:
    """
    Обработка одного инстанса в отдельном потоке.
    """
    try:
        logger.info(
            f"Обработка: instance_id={instance['id']}, "
            f"process={instance['process_name']}, "
            f"state={instance['fsm_state']}, "
            f"attempts={instance['attempts_count']}"
        )

        # Проверка лимита попыток (защита от бесконечного цикла)
        if instance["attempts_count"] >= MAX_ATTEMPTS:
            logger.warning(f"Превышен лимит попыток → FAILED: instance_id={instance['id']}")
            apply_fsm_result(db, instance, FsmStepResult(
                new_state="FAILED",
                last_error="MAX_ATTEMPTS_EXCEEDED",
                attempts_increment=0
            ))
            return

        try:
            result = run_fsm_step(db, actions_ctx, instance)

            # Проверка, вернул ли run_fsm_step результат
            if result is None:
                logger.error(f"run_fsm_step вернул None! instance_id={instance['id']}")
                # Обрабатываем как ошибку FSM шага
                raise RuntimeError("run_fsm_step returned None")

        except Exception as fsm_step_error:
            # Обработка ошибки, возникшей внутри run_fsm_step (или в db_layer, fsm_actions и т.п.)
            logger.error(f"Ошибка выполнения FSM шага для instance_id={instance['id']}: {fsm_step_error}", exc_info=True)
            # Формируем результат ошибки FSM шага
            result = FsmStepResult(
                new_state="FAILED",
                last_error=str(fsm_step_error),
                attempts_increment=1
            )

        apply_fsm_result(db, instance, result)
        
        if result.new_state in ("COMPLETED", "FAILED"):
            logger.info(f"Завершено: instance_id={instance['id']}, new_state={result.new_state}")
        else:
            logger.info(f"Продолжение: instance_id={instance['id']}, new_state={result.new_state}")

    except Exception as e:
        logger.error(f"Критическая ошибка обработки instance_id={instance['id']}: {e}", exc_info=True)
        db.session.rollback()

def check_stuck_instances(db: DatabaseLayer) -> int:
    """
    Проверяет и фейлит застрявшие PENDING-заявки (> STUCK_THRESHOLD_MINUTES).
    """
    session = db.session    
    rows = session.execute(
        text("""
            SELECT id, attempts_count, created_at, TIMESTAMPDIFF(MINUTE, created_at, NOW()) AS diff_min
            FROM server_fsm_instances
            WHERE fsm_state = 'PENDING'
            AND TIMESTAMPDIFF(MINUTE, created_at, NOW()) > :threshold
        """),
        {"threshold": STUCK_THRESHOLD_MINUTES},
    ).fetchall()

    stuck_count = 0
    for row in rows:
        instance_id, attempts, created_at, diff_min = row
        logger.warning(f"Застрявшая заявка: instance_id={instance_id}, attempts={attempts}, created_at={created_at}, diff_min={diff_min}")

        session.execute(
            text("""
                UPDATE server_fsm_instances
                SET fsm_state = 'FAILED',
                    last_error = 'STUCK_TIMEOUT',
                    updated_at = NOW()
                WHERE id = :id
            """),
            {"id": instance_id},
        )
        stuck_count += 1

    if stuck_count > 0:
        session.commit()
        logger.info(f"Обработано застрявших заявок: {stuck_count}")

    return stuck_count

def main():
    db = DatabaseLayer(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "testdb"),
        user=os.getenv("DB_USER", "fsm"),
        password=os.getenv("DB_PASSWORD", "6eF1zb"),
        echo=False,
    )

    actions_ctx = build_actions_context(db)
    logger.info("[WORKER] FSM worker started")
    logger.info(f"[WORKER] Loaded process definitions: {list(PROCESS_DEFS.keys())}")

    last_trip_check = 0
    last_stuck_check = 0  # Счётчик проверки застрявших

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            try:
                current_time = time.time()

                # Периодическая активация рейсов
                if current_time - last_trip_check >= TRIP_ACTIVATION_INTERVAL:
                    try:
                        activated = db.update_trip_active_flags(max_orders=5, wait_hours=24)
                        if activated > 0:
                            logger.info(f"Активировано рейсов: {activated}")
                        last_trip_check = current_time
                    except Exception as e:
                        logger.error(f"Ошибка активации рейсов: {e}")

                # Периодическая проверка застрявших
                if current_time - last_stuck_check >= 300:  # Каждые 5 мин
                    try:
                        stuck = check_stuck_instances(db)
                        if stuck > 0:
                            logger.info(f"Фейл застрявших: {stuck}")
                        last_stuck_check = current_time
                    except Exception as e:
                        logger.error(f"Ошибка проверки застрявших: {e}")

                rows = fetch_ready_instances(db)
                logger.debug(f"Получено готовых инстансов: {len(rows)} шт")
                if rows:
                    for row in rows:
                        logger.info(f"  - instance_id={row[0]}, process={row[3]}, state={row[4]}, next_timer_at={row[5]}")
                else:
                    logger.debug("Нет готовых инстансов. Проверяем PENDING:")
                    pending = db.session.execute(
                        text("SELECT COUNT(*) FROM server_fsm_instances WHERE fsm_state = 'PENDING'")
                    ).scalar()
                    logger.debug(f"Всего PENDING в базе: {pending}")
                if not rows:
                    db.session.commit()
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                # Параллельная обработка батча
                futures = [
                    executor.submit(process_instance, db, actions_ctx, row_to_instance_dict(row))
                    for row in rows
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Ошибка в потоке: {e}")

            except DbLayerError as e:
                logger.error(f"DbLayerError: {e}")
                db.session.rollback()
                time.sleep(POLL_INTERVAL_SECONDS)
            except Exception as e:
                import traceback
                logger.error(f"Unexpected error: {e}")
                traceback.print_exc()
                db.session.rollback()
                time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
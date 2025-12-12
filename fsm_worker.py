# fsm_worker.py

import time
from typing import Any, Dict

from sqlalchemy import text
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

POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 10


def fetch_ready_instances(db: DatabaseLayer):
    """
    Универсальный выбор процессов, готовых к обработке.
    Пока берём только не завершённые процессы с next_timer_at <= NOW().
    """
    session = db.session
    rows = session.execute(
        text(
            """
            SELECT
                id,
                entity_type,
                entity_id,
                process_name,
                fsm_state,
                next_timer_at,
                attempts_count,
                last_error
            FROM server_fsm_instances
            WHERE fsm_state NOT IN ('COMPLETED', 'FAILED')
              AND (next_timer_at IS NULL OR next_timer_at <= NOW())
            ORDER BY id
            LIMIT :limit
            """
        ),
        {"limit": BATCH_SIZE},
    ).fetchall()
    return rows


def row_to_instance_dict(row: Any) -> Dict[str, Any]:
    """
    Преобразует строку server_fsm_instances в dict, чтобы удобно передавать в движок.
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
    }


def apply_fsm_result(
    db: DatabaseLayer,
    instance: Dict[str, Any],
    result: FsmStepResult,
):
    """
    Универсально обновляет server_fsm_instances по результату шага.
    """
    session = db.session

    new_attempts = instance["attempts_count"] + (result.attempts_increment or 0)

    session.execute(
        text(
            """
            UPDATE server_fsm_instances
            SET fsm_state = :new_state,
                last_error = :last_error,
                next_timer_at = :next_timer_at,
                attempts_count = :attempts,
                updated_at = NOW()
            WHERE id = :id
            """
        ),
        {
            "id": instance["id"],
            "new_state": result.new_state,
            "last_error": result.last_error,
            "next_timer_at": result.next_timer_at,
            "attempts": new_attempts,
        },
    )
    session.commit()    

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

    print("[WORKER] FSM worker started")
    print(f"[WORKER] Loaded process definitions: {list(PROCESS_DEFS.keys())}")

    while True:
        try:            
            rows = fetch_ready_instances(db)            
            if not rows:
                db.session.commit()
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            for row in rows:
                instance = row_to_instance_dict(row)

                print(
                    f"[WORKER] instance_id={instance['id']}, "
                    f"process={instance['process_name']}, "
                    f"state={instance['fsm_state']}, "
                    f"attempts={instance['attempts_count']}"
                )

                result = run_fsm_step(db, actions_ctx, instance)
                if result is None:
                    # Нет обработчика – просто пропускаем
                    print(
                        f"[WORKER] No handler for process={instance['process_name']} "
                        f"state={instance['fsm_state']}"
                        f"new_state={getattr(result, 'new_state', None)},",
                        f"last_error={getattr(result, 'last_error', None)}",
                    )
                    continue

                apply_fsm_result(db, instance, result)

        except DbLayerError as e:
            print(f"[WORKER] DbLayerError: {e}")
            db.session.rollback()
            time.sleep(POLL_INTERVAL_SECONDS)
        except Exception as e:
            print(f"[WORKER] Unexpected error: {e}")
            db.session.rollback()
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

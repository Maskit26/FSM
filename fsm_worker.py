# fsm_worker.py

import time
from typing import Any

from sqlalchemy import text

from db_layer import DatabaseLayer, DbLayerError
from fsm_actions import OrderCreationActions


POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 10


def fetch_ready_instances(db: DatabaseLayer):
    """
    Универсальный выбор процессов, готовых к обработке.
    Сейчас: только WAITING_FOR_RESERVATION.
    """
    session = db.session
    rows = session.execute(
        text(
            """
            SELECT id, entity_type, entity_id, process_name, fsm_state, attempts_count
            FROM server_fsm_instances
            WHERE fsm_state = 'WAITING_FOR_RESERVATION'
              AND (next_timer_at IS NULL OR next_timer_at <= NOW())
            ORDER BY id
            LIMIT :limit
            """
        ),
        {"limit": BATCH_SIZE},
    ).fetchall()
    return rows


def process_fsm_instance(
    db: DatabaseLayer,
    order_actions: OrderCreationActions,
    row: Any,
):
    """
    Диспетчер: выбирает обработчик по process_name / fsm_state.
    """
    fsm_id = row[0]
    entity_type = row[1]
    entity_id = row[2]
    process_name = row[3]
    fsm_state = row[4]
    attempts_count = row[5]

    print(
        f"[WORKER] instance_id={fsm_id}, "
        f"entity_type={entity_type}, entity_id={entity_id}, "
        f"process_name={process_name}, state={fsm_state}, attempts={attempts_count}"
    )

    if process_name == "order_creation" and fsm_state == "WAITING_FOR_RESERVATION":
        handle_order_creation(db, order_actions, fsm_id, entity_id, attempts_count)
    else:
        print(f"[WORKER] Нет обработчика для process={process_name}, state={fsm_state}")


def handle_order_creation(
    db: DatabaseLayer,
    actions: OrderCreationActions,
    fsm_id: int,
    request_id: int,
    attempts_count: int,
):
    """
    Обработчик процесса 'order_creation' на уровне движка:
    - вызывает 2 action'а (поиск ячеек, создание заказа);
    - по результату обновляет server_fsm_instances.
    Все изменения в order_requests / orders / locker_cells делает actions.
    """
    session = db.session

    try:
        # 1. Поиск ячеек
        ok, src_id, dst_id, code = actions.find_cells_for_request(request_id)
        if not ok:
            # Процесс упал на этапе поиска ячеек
            session.execute(
                text(
                    """
                    UPDATE server_fsm_instances
                    SET fsm_state = 'FAILED',
                        last_error = :err,
                        attempts_count = :attempts
                    WHERE id = :fsm_id
                    """
                ),
                {
                    "fsm_id": fsm_id,
                    "err": code or "CELLS_ERROR",
                    "attempts": attempts_count + 1,
                },
            )
            session.commit()
            print(
                f"[WORKER] order_creation FAILED on find_cells: "
                f"request_id={request_id}, error={code}"
            )
            return

        # 2. Создание заказа из заявки
        ok, order_id, code = actions.create_order_from_request(request_id, src_id, dst_id)
        if not ok:
            session.execute(
                text(
                    """
                    UPDATE server_fsm_instances
                    SET fsm_state = 'FAILED',
                        last_error = :err,
                        attempts_count = :attempts
                    WHERE id = :fsm_id
                    """
                ),
                {
                    "fsm_id": fsm_id,
                    "err": code or "ORDER_ERROR",
                    "attempts": attempts_count + 1,
                },
            )
            session.commit()
            print(
                f"[WORKER] order_creation FAILED on create_order: "
                f"request_id={request_id}, error={code}"
            )
            return

        # 3. Всё прошло успешно → помечаем процесс COMPLETED
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET fsm_state = 'COMPLETED',
                    last_error = NULL,
                    attempts_count = :attempts
                WHERE id = :fsm_id
                """
            ),
            {
                "fsm_id": fsm_id,
                "attempts": attempts_count + 1,
            },
        )
        session.commit()
        print(
            f"[WORKER] order_creation COMPLETED: "
            f"request_id={request_id}, order_id={order_id}"
        )

    except Exception as e:
        session.rollback()
        print(f"[WORKER] Ошибка в handle_order_creation: {e}")


def main():
    # Подключаемся теми же параметрами, что и main.py
    db = DatabaseLayer(
        host="localhost",
        port=3307,
        database="testdb",
        user="root",
        password="root",
        echo=False,
    )
    order_actions = OrderCreationActions(db)

    print("[WORKER] FSM worker started")
    while True:
        try:
            rows = fetch_ready_instances(db)
            if not rows:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            for row in rows:
                process_fsm_instance(db, order_actions, row)

        except DbLayerError as e:
            print(f"[WORKER] DbLayerError: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
        except Exception as e:
            print(f"[WORKER] Unexpected error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

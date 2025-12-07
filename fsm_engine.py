# fsm_engine.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Any, Optional

from db_layer import DatabaseLayer, DbLayerError
from fsm_actions import OrderCreationActions


@dataclass
class FsmStepResult:
    """
    Результат одного шага серверного FSM-процесса.
    new_state: во что переводим fsm_state.
    last_error: текст/код ошибки (None, если успех).
    next_timer_at: когда запускать процесс следующий раз (если нужен отложенный запуск).
    attempts_increment: на сколько увеличить attempts_count.
    """
    new_state: str
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1


# Тип обработчика шага процесса:
# на вход: db, actions-контекст, данные инстанса FSM
FsmStateHandler = Callable[[DatabaseLayer, Dict[str, Any], Dict[str, Any]], FsmStepResult]


def _handle_order_creation_waiting(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """
    Обработчик состояния WAITING_FOR_RESERVATION для процесса 'order_creation'.
    Вызывает два action'а: поиск ячеек и создание заказа.
    """
    actions: OrderCreationActions = ctx["order_creation_actions"]
    fsm_id = instance["id"]
    request_id = instance["entity_id"]
    attempts = instance["attempts_count"]

    # 1. Поиск ячеек
    ok, src_id, dst_id, code = actions.find_cells_for_request(request_id)
    if not ok:
        # Ошибка на этапе поиска ячеек
        return FsmStepResult(
            new_state="FAILED",
            last_error=code or "CELLS_ERROR",
            attempts_increment=1,
        )

    # 2. Создание заказа из заявки
    ok, order_id, code = actions.create_order_from_request(request_id, src_id, dst_id)
    if not ok:
        return FsmStepResult(
            new_state="FAILED",
            last_error=code or "ORDER_ERROR",
            attempts_increment=1,
        )

    print(
        f"[FSM] order_creation COMPLETED: "
        f"fsm_id={fsm_id}, request_id={request_id}, order_id={order_id}"
    )

    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1,
    )


# Реестр процессов и состояний.
# Здесь описывается "оркестрационный FSM-граф" в коде.
PROCESS_DEFS: Dict[str, Dict[str, FsmStateHandler]] = {
    "order_creation": {
        "WAITING_FOR_RESERVATION": _handle_order_creation_waiting,
        # потом можно добавить другие состояния этого процесса
        # "SOMETHING_ELSE": handler_fn,
    },
    # другие процессы будут добавляться сюда:
    # "trip_auto_activate": { ... },
    # "timeout_handler": { ... },
}


def build_actions_context(db: DatabaseLayer) -> Dict[str, Any]:
    """
    Собирает actions-контексты для всех процессов.
    Это точка расширения: добавишь новые классы действий - зарегистрируешь их тут.
    """
    return {
        "order_creation_actions": OrderCreationActions(db),
        # "trip_actions": TripActions(db),
        # и т.д.
    }


def run_fsm_step(
    db: DatabaseLayer,
    actions_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> Optional[FsmStepResult]:
    """
    Универсальный запуск одного шага FSM-процесса.
    На вход: одна строка server_fsm_instances (как dict).
    Находит handler по process_name + fsm_state и вызывает его.
    Если handler не найден - возвращает None.
    """
    process_name = instance["process_name"]
    fsm_state = instance["fsm_state"]

    process_def = PROCESS_DEFS.get(process_name)
    if not process_def:
        print(f"[FSM] Нет определения процесса: {process_name}")
        return None

    handler = process_def.get(fsm_state)
    if not handler:
        print(
            f"[FSM] Нет обработчика состояния: process={process_name}, state={fsm_state}"
        )
        return None

    return handler(db, actions_ctx, instance)

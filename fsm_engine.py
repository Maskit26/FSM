# fsm_engine.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional
from db_layer import DatabaseLayer, DbLayerError
import logging
logger = logging.getLogger(__name__)
from fsm_actions import (
    OrderCreationActions,
    AssignmentActions,
    CourierActions,
    OperatorActions,
    ClientActions,
    RecipientActions,
    DriverActions,
)

@dataclass
class FsmStepResult:
    """Результат одного шага серверного FSM-процесса."""
    new_state: str
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1

FsmStateHandler = Callable[[DatabaseLayer, Dict[str, Any], Dict[str, Any]], FsmStepResult]


# ==================== ORDER CREATION ====================
def _handle_order_creation_pending(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Обработчик состояния PENDING для процесса 'order_creation'."""
    actions: OrderCreationActions = ctx["order_creation_actions"]
    fsm_id = instance["id"]
    request_id = instance["entity_id"]
    # 1. Поиск ячеек
    ok, src_id, dst_id, code = actions.find_cells_for_request(request_id)
    if not ok:
        return FsmStepResult(
            new_state="FAILED",
            last_error=code or "CELLS_ERROR",
            attempts_increment=1,
        )
    # 2. Создание заказа
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


# ==================== УНИВЕРСАЛЬНОЕ НАЗНАЧЕНИЕ ====================
def _handle_assign_executor_pending(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """
    Обработчик назначения исполнителя.
    target_user_id ВСЕГДА должен быть задан (конкретный исполнитель).
    НЕТ автоматического выбора исполнителя.
    Работает для процессов:
    - order_assign_courier1
    - order_assign_courier2
    - trip_assign_driver
    """
    actions: AssignmentActions = ctx["assignment_actions"]
    entity_type = instance["entity_type"]  # "order" или "trip"
    entity_id = instance["entity_id"]
    target_user_id = instance.get("target_user_id", 0)
    process_name = instance["process_name"]
    # Проверка: target_user_id ОБЯЗАТЕЛЬНО должен быть задан
    if not target_user_id or target_user_id <= 0:
        return FsmStepResult(
            new_state="FAILED",
            last_error="TARGET_USER_ID_NOT_SET",
            attempts_increment=1,
        )
    # Определяем роль исполнителя из process_name
    if "courier1" in process_name:
        role = "courier1"
    elif "courier2" in process_name:
        role = "courier2"
    elif "driver" in process_name:
        role = "driver"
    else:
        return FsmStepResult(
            new_state="FAILED",
            last_error="UNKNOWN_PROCESS_TYPE",
            attempts_increment=1,
        )
    executor_id = target_user_id
    print(
        f"[FSM] Назначение исполнителя: "
        f"entity={entity_type}:{entity_id}, executor={executor_id}, role={role}"
    )
    # Назначаем исполнителя через двухэтапный процесс
    if entity_type == "order":
        success = actions.assign_to_order(entity_id, executor_id, role)
    elif entity_type == "trip":
        success = actions.assign_to_trip(entity_id, executor_id, role)
    else:
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"UNKNOWN_ENTITY_TYPE_{entity_type}",
            attempts_increment=1,
        )
    if not success:
        return FsmStepResult(
            new_state="FAILED",
            last_error="ASSIGNMENT_FAILED",
            attempts_increment=1,
        )
    print(
        f"[FSM] ✅ assign_executor COMPLETED: "
        f"entity={entity_type}:{entity_id}, executor={executor_id}, role={role}"
    )
    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1,
    )


# ==================== УНИВЕРСАЛЬНОЕ ОТКРЫТИЕ ЯЧЕЙКИ ====================
def _handle_open_cell(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """
    Универсальный обработчик открытия ячейки.
    entity_type может быть:
      - "order" → открываем ячейку, привязанную к заказу
      - "locker" → открываем ячейку напрямую (для водителя)
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    if entity_type == "order":
        order_id = entity_id
        if user_role == "client":
            success, error = ctx["client_actions"].open_cell_for_client(order_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].open_cell_for_recipient(order_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].open_cell(order_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].open_cell_for_operator(order_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"ROLE_NOT_SUPPORTED_{user_role}")
    elif entity_type == "locker":
        cell_id = entity_id
        if user_role == "driver":
            success, error = ctx["driver_actions"].open_cell_for_driver(cell_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ACCESS_DENIED_FOR_{user_role}")
    else:
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error or "OPEN_FAILED")
    return FsmStepResult(new_state="COMPLETED")


# ==================== УНИВЕРСАЛЬНОЕ ЗАКРЫТИЕ ЯЧЕЙКИ ====================
def _handle_close_cell(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Универсальный обработчик закрытия ячейки."""
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    if entity_type == "order":
        order_id = entity_id
        if user_role == "client":
            success, error = ctx["client_actions"].close_cell_for_client(order_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].close_cell_for_recipient(order_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].close_cell(order_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].close_cell_for_operator(order_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"ROLE_NOT_SUPPORTED_{user_role}")
    elif entity_type == "locker":
        cell_id = entity_id
        if user_role == "driver":
            success, error = ctx["driver_actions"].close_cell_for_driver(cell_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ACCESS_DENIED_FOR_{user_role}")
    else:
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error or "CLOSE_FAILED")
    return FsmStepResult(new_state="COMPLETED")


# ==================== УНИВЕРСАЛЬНАЯ ОТМЕНА ЗАКАЗА ====================
def _handle_cancel_order(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Универсальный обработчик отмены заказа."""
    user_role = instance["requested_user_role"]
    order_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    if user_role == "client":
        success, error = ctx["client_actions"].cancel_order(order_id, user_id)
    elif user_role == "courier":
        success, error = ctx["courier_actions"].cancel_order(order_id, user_id)
    elif user_role == "operator":
        success, error = ctx["operator_actions"].force_cancel_order(order_id, user_id)
    else:
        return FsmStepResult(new_state="FAILED", last_error=f"CANCEL_NOT_ALLOWED_FOR_{user_role}")

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    return FsmStepResult(new_state="COMPLETED")


# ==================== УНИВЕРСАЛЬНАЯ ОШИБКА ЯЧЕЙКИ ====================
def _handle_locker_error(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Универсальный обработчик ошибки ячейки (не открылась / не закрылась)."""
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    if entity_type == "order":
        order_id = entity_id
        if user_role == "client":
            success, error = ctx["client_actions"].report_locker_error(order_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].report_locker_error(order_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].locker_error(order_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].report_locker_error(order_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ERROR_NOT_ALLOWED_{user_role}")
    elif entity_type == "locker":
        cell_id = entity_id
        if user_role == "driver":
            success, error = ctx["driver_actions"].report_locker_error_cell(cell_id, user_id)
        else:
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ERROR_NOT_ALLOWED_{user_role}")
    else:
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    return FsmStepResult(new_state="COMPLETED")

# ==================== КНОПКИ ВОДИТЕЛЯ ====================
def _handle_start_trip(db: DatabaseLayer, ctx: Dict[str, Any], instance: Dict[str, Any]) -> FsmStepResult:
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")
    success, error = ctx["driver_actions"].start_trip(trip_id, user_id)
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    return FsmStepResult(new_state="COMPLETED")

def _handle_arrive_at_destination(db: DatabaseLayer, ctx: Dict[str, Any], instance: Dict[str, Any]) -> FsmStepResult:
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")
    success, error = ctx["driver_actions"].arrive_at_destination(trip_id, user_id)
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    return FsmStepResult(new_state="COMPLETED")

def _handle_cancel_trip(db: DatabaseLayer, ctx: Dict[str, Any], instance: Dict[str, Any]) -> FsmStepResult:
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")
    success, error = ctx["driver_actions"].cancel_trip(trip_id, user_id)
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    return FsmStepResult(new_state="COMPLETED")

# ==================== РЕЕСТР ПРОЦЕССОВ ====================
PROCESS_DEFS: Dict[str, Dict[str, FsmStateHandler]] = {
    "order_creation": {
        "PENDING": _handle_order_creation_pending,
    },
    "order_assign_courier1": {
        "PENDING": _handle_assign_executor_pending,
    },
    "order_assign_courier2": {
        "PENDING": _handle_assign_executor_pending,
    },
    "trip_assign_driver": {
        "PENDING": _handle_assign_executor_pending,
    },
    "start_trip": {
        "PENDING": _handle_start_trip,
    },
    "arrive_at_destination": {
        "PENDING": _handle_arrive_at_destination,
    },
    "cancel_trip": {
        "PENDING": _handle_cancel_trip,
    },
    # Универсальные действия
    "open_cell": {"PENDING": _handle_open_cell},
    "close_cell": {"PENDING": _handle_close_cell},
    "cancel_order": {"PENDING": _handle_cancel_order},
    "locker_error": {"PENDING": _handle_locker_error},
}


def build_actions_context(db: DatabaseLayer) -> Dict[str, Any]:
    """Собирает actions-контексты для всех процессов."""
    return {
        "order_creation_actions": OrderCreationActions(db),
        "assignment_actions": AssignmentActions(db),
        "courier_actions": CourierActions(db),        
        "operator_actions": OperatorActions(db),
        "client_actions": ClientActions(db),
        "recipient_actions": RecipientActions(db),
        "driver_actions": DriverActions(db),
    }


def run_fsm_step(
    db: DatabaseLayer,
    actions_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:  # ← убрал Optional, теперь всегда возвращаем результат
    """Универсальный запуск одного шага FSM-процесса."""
    process_name = instance["process_name"]
    fsm_state = instance["fsm_state"]

    if process_name not in PROCESS_DEFS:
        logger.error(f"Неизвестный процесс: {process_name}")
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"UNKNOWN_PROCESS: {process_name}",
            attempts_increment=1
        )

    process_def = PROCESS_DEFS[process_name]
    handler = process_def.get(fsm_state)

    if not handler:
        logger.warning(f"Нет обработчика состояния {fsm_state} для процесса {process_name}")
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"NO_HANDLER_FOR_STATE_{fsm_state}_IN_{process_name}",
            attempts_increment=1
        )

    return handler(db, actions_ctx, instance)
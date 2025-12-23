# fsm_engine.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional

from db_layer import DatabaseLayer, DbLayerError
from fsm_actions import (
    OrderCreationActions, 
    AssignmentActions, 
    CourierCellActions,
    CourierErrorActions, 
    OperatorActions
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

# ==================== РАБОТА С ПОСТАМАТОМ =================

def _handle_courier_open_cell(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """
    Курьер открывает ячейку (single-step процесс).
    """
    actions: CourierCellActions = ctx["courier_cell_actions"]
    
    order_id = instance["entity_id"]
    courier_id = instance["requested_by_user_id"]
    
    success, error = actions.open_cell(order_id, courier_id)
    
    if not success:
        return FsmStepResult(
            new_state="FAILED",
            last_error=error or "OPEN_FAILED",
        )    
    
    print(f"[FSM] ✅ courier_open_cell COMPLETED: order={order_id}, courier={courier_id}")
    return FsmStepResult(new_state="COMPLETED")

def _handle_courier_close_cell(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """
    Курьер закрывает ячейку (универсальный handler).
    """
    actions: CourierCellActions = ctx["courier_cell_actions"]
    
    order_id = instance["entity_id"]
    courier_id = instance["requested_by_user_id"]
    
    success, error = actions.close_cell(order_id, courier_id)
    
    if not success:
        return FsmStepResult(
            new_state="FAILED",
            last_error=error or "CLOSE_FAILED",
        )
    
    return FsmStepResult(new_state="COMPLETED")


# ==================== КУРЬЕРЫ: Ошибки и отмена ====================

def _handle_courier_cancel_order(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Курьер отменяет заказ."""
    actions: CourierErrorActions = ctx["courier_error_actions"]
    
    order_id = instance["entity_id"]
    courier_id = instance["requested_by_user_id"]
    
    success, error = actions.cancel_order(order_id, courier_id)
    
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    return FsmStepResult(new_state="COMPLETED")


def _handle_courier_locker_error(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Курьер сообщает об ошибке с ячейкой."""
    actions: CourierErrorActions = ctx["courier_error_actions"]
    
    order_id = instance["entity_id"]
    courier_id = instance["requested_by_user_id"]
    
    success, error = actions.locker_error(order_id, courier_id)
    
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    return FsmStepResult(new_state="COMPLETED")

# ==================== РАБОТА ОПЕРАТОРА ====================

def _handle_operator_reset_locker(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Оператор сбрасывает ячейку в locker_free."""
    actions: OperatorActions = ctx["operator_actions"]
    
    cell_id = instance["entity_id"]
    operator_id = instance["requested_by_user_id"]
    
    success, error = actions.reset_locker(cell_id, operator_id)
    
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    return FsmStepResult(new_state="COMPLETED")


def _handle_operator_set_maintenance(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Оператор переводит ячейку в обслуживание."""
    actions: OperatorActions = ctx["operator_actions"]
    
    cell_id = instance["entity_id"]
    operator_id = instance["requested_by_user_id"]
    
    success, error = actions.set_locker_maintenance(cell_id, operator_id)
    
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
    "courier_open_cell": {
    "PENDING": _handle_courier_open_cell,
    },
    "courier_close_cell": {
        "PENDING": _handle_courier_close_cell,
    },
    "courier_cancel_order": {
        "PENDING": _handle_courier_cancel_order,
    },
    "courier_locker_error": {
        "PENDING": _handle_courier_locker_error,
    },
    "operator_reset_locker": {
        "PENDING": _handle_operator_reset_locker,
    },
    "operator_set_maintenance": {
        "PENDING": _handle_operator_set_maintenance,
    },
}


def build_actions_context(db: DatabaseLayer) -> Dict[str, Any]:
    """Собирает actions-контексты для всех процессов."""
    return {
        "order_creation_actions": OrderCreationActions(db),
        "assignment_actions": AssignmentActions(db),
        "courier_cell_actions": CourierCellActions(db),
        "courier_error_actions": CourierErrorActions(db),
        "operator_actions": OperatorActions(db),
    }


def run_fsm_step(
    db: DatabaseLayer,
    actions_ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> Optional[FsmStepResult]:
    """Универсальный запуск одного шага FSM-процесса."""
    process_name = instance["process_name"]
    fsm_state = instance["fsm_state"]
    
    process_def = PROCESS_DEFS.get(process_name)
    if not process_def:
        print(f"[FSM] ❌ Нет определения процесса: {process_name}")
        return None
    
    handler = process_def.get(fsm_state)
    if not handler:
        print(
            f"[FSM] ❌ Нет обработчика состояния: "
            f"process={process_name}, state={fsm_state}"
        )
        return None
    
    return handler(db, actions_ctx, instance)

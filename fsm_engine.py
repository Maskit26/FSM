# fsm_engine.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Any, Optional

from db_layer import DatabaseLayer, DbLayerError
from fsm_actions import OrderCreationActions, AssignmentActions


@dataclass
class FsmStepResult:
    """Результат одного шага серверного FSM-процесса."""
    new_state: str
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1


FsmStateHandler = Callable[[DatabaseLayer, Dict[str, Any], Dict[str, Any]], FsmStepResult]


# ==================== ORDER CREATION ====================

def _handle_order_creation_waiting(
    db: DatabaseLayer,
    ctx: Dict[str, Any],
    instance: Dict[str, Any],
) -> FsmStepResult:
    """Обработчик состояния WAITING_FOR_RESERVATION для процесса 'order_creation'."""
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


# ==================== РЕЕСТР ПРОЦЕССОВ ====================

PROCESS_DEFS: Dict[str, Dict[str, FsmStateHandler]] = {
    "order_creation": {
        "WAITING_FOR_RESERVATION": _handle_order_creation_waiting,
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
}


def build_actions_context(db: DatabaseLayer) -> Dict[str, Any]:
    """Собирает actions-контексты для всех процессов."""
    return {
        "order_creation_actions": OrderCreationActions(db),
        "assignment_actions": AssignmentActions(db),
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

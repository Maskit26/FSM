# fsm_engine.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from db_layer import DatabaseLayer, DbLayerError
from fsm_actions import (
    OrderCreationActions,
    AssignmentActions,
    CourierActions,
    OperatorActions,
    ClientActions,
    RecipientActions,
    DriverActions,
)

logger = logging.getLogger(__name__)

@dataclass
class FsmStepResult:
    """Результат одного шага FSM-процесса."""
    new_state: str  # всегда "COMPLETED" или "FAILED"
    last_error: Optional[str] = None
    next_timer_at: Optional[datetime] = None
    attempts_increment: int = 1
    payload: Optional[Dict[str, Any]] = None

FsmStateHandler = Callable[[DatabaseLayer, Session, Dict[str, Any], Dict[str, Any]], FsmStepResult]


# ==================== ORDER CREATION ====================
def _handle_order_creation_pending(
    db: DatabaseLayer,
    session: Session,          
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик состояния PENDING для процесса 'order_creation'.
    Создаёт заказ из заявки и резервирует ячейки.
    Если ячейки не найдены или заказ не создан → FAILED.
    """
    actions: OrderCreationActions = ctx["order_creation_actions"]
    fsm_id = instance["id"]
    request_id = instance["entity_id"]

    logger.info(f"[FSM] order_creation PENDING: fsm_id={fsm_id}, request_id={request_id}")

    # Единственный вызов — создание заказа (включает поиск и резерв ячеек)
    ok, order_id, code = actions.create_order_from_request(session, request_id)  
    if not ok:
        error_code = code or "ORDER_CREATION_FAILED"
        logger.error(f"[FSM] create_order_from_request FAILED: request_id={request_id}, code={error_code}")
        return FsmStepResult(new_state="FAILED", last_error=error_code, attempts_increment=1)

    logger.info(f"[FSM] order_creation COMPLETED: fsm_id={fsm_id}, request_id={request_id}, order_id={order_id}")
    return FsmStepResult(
        new_state="COMPLETED", 
        last_error=None, 
        attempts_increment=1,
        payload={"order_id": order_id}  
    )


# ==================== ASSIGN EXECUTOR ====================
def _handle_assign_executor_pending(
    db: DatabaseLayer,
    session: Session,          
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик назначения исполнителя.
    target_user_id ВСЕГДА должен быть задан (конкретный исполнитель).
    НЕ автоматического выбора исполнителя.
    Работает для процессов:
    - order_assign_courier1
    - order_assign_courier2
    - trip_assign_driver
    """
    actions: AssignmentActions = ctx["assignment_actions"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    target_user_id = instance.get("target_user_id", 0)
    process_name = instance["process_name"]

    if not target_user_id or target_user_id <= 0:
        return FsmStepResult(new_state="FAILED", last_error="TARGET_USER_ID_NOT_SET", attempts_increment=1)

    # Определяем роль исполнителя
    if "courier1" in process_name:
        role = "courier1"
    elif "courier2" in process_name:
        role = "courier2"
    elif "driver" in process_name:
        role = "driver"
    else:
        return FsmStepResult(new_state="FAILED", last_error="UNKNOWN_PROCESS_TYPE", attempts_increment=1)

    executor_id = target_user_id

    logger.info(f"[FSM] assign_executor: entity={entity_type}:{entity_id}, executor={executor_id}, role={role}")

    # Назначение через actions 
    if entity_type == "order":
        success = actions.assign_to_order(session, entity_id, executor_id, role)  
    elif entity_type == "trip":
        success = actions.assign_to_trip(session, entity_id, executor_id, role)    
    else:
        return FsmStepResult(new_state="FAILED", last_error=f"UNKNOWN_ENTITY_TYPE_{entity_type}", attempts_increment=1)

    if not success:
        return FsmStepResult(new_state="FAILED", last_error="ASSIGNMENT_FAILED", attempts_increment=1)

    logger.info(f"[FSM] assign_executor COMPLETED: entity={entity_type}:{entity_id}, executor={executor_id}, role={role}")
    return FsmStepResult(new_state="COMPLETED", last_error=None, attempts_increment=1)


# ==================== OPEN/CLOSE CELL ====================
def _handle_open_cell(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальный обработчик открытия ячейки.
    Поддерживаемые роли: client, recipient, courier, operator, driver.
    entity_type: "order" или "locker".
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] open_cell: role={user_role}, entity={entity_type}:{entity_id}, user={user_id}")

    if entity_type == "order":
        if user_role == "client":
            success, error = ctx["client_actions"].open_cell_for_client(session, entity_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].open_cell_for_recipient(session, entity_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].open_cell(session, entity_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].open_cell_for_operator(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] open_cell: unsupported role {user_role} for order")
            return FsmStepResult(new_state="FAILED", last_error=f"ROLE_NOT_SUPPORTED_{user_role}")
    elif entity_type == "locker":
        if user_role == "driver":
            success, error = ctx["driver_actions"].open_cell_for_driver(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] open_cell: locker access denied for role {user_role}")
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ACCESS_DENIED_FOR_{user_role}")
    else:
        logger.error(f"[FSM] open_cell: unsupported entity_type {entity_type}")
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        logger.error(f"[FSM] open_cell FAILED: entity={entity_type}:{entity_id}, error={error or 'OPEN_FAILED'}")
        return FsmStepResult(new_state="FAILED", last_error=error or "OPEN_FAILED")
    
    logger.info(f"[FSM] open_cell COMPLETED: entity={entity_type}:{entity_id}")
    return FsmStepResult(new_state="COMPLETED")


def _handle_close_cell(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальный обработчик закрытия ячейки.
    Поддерживаемые роли: client, recipient, courier, operator, driver.
    entity_type: "order" или "locker".
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] close_cell: role={user_role}, entity={entity_type}:{entity_id}, user={user_id}")

    if entity_type == "order":
        if user_role == "client":
            success, error = ctx["client_actions"].close_cell_for_client(session, entity_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].close_cell_for_recipient(session, entity_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].close_cell(session, entity_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].close_cell_for_operator(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] close_cell: unsupported role {user_role} for order")
            return FsmStepResult(new_state="FAILED", last_error=f"ROLE_NOT_SUPPORTED_{user_role}")
    elif entity_type == "locker":
        if user_role == "driver":
            success, error = ctx["driver_actions"].close_cell_for_driver(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] close_cell: locker access denied for role {user_role}")
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ACCESS_DENIED_FOR_{user_role}")
    else:
        logger.error(f"[FSM] close_cell: unsupported entity_type {entity_type}")
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        logger.error(f"[FSM] close_cell FAILED: entity={entity_type}:{entity_id}, error={error or 'CLOSE_FAILED'}")
        return FsmStepResult(new_state="FAILED", last_error=error or "CLOSE_FAILED")
    
    logger.info(f"[FSM] close_cell COMPLETED: entity={entity_type}:{entity_id}")
    return FsmStepResult(new_state="COMPLETED")


# ==================== CANCEL ORDER ====================
def _handle_cancel_order(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальная отмена заказа.
    Роли: client, courier, operator.
    """
    user_role = instance["requested_user_role"]
    order_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] cancel_order: role={user_role}, order_id={order_id}, user_id={user_id}")

    if user_role == "client":
        success, error = ctx["client_actions"].cancel_order(session, order_id, user_id)
    elif user_role == "courier":
        success, error = ctx["courier_actions"].cancel_order(session, order_id, user_id)
    elif user_role == "operator":
        success, error = ctx["operator_actions"].force_cancel_order(session, order_id, user_id)
    else:
        logger.warning(f"[FSM] cancel_order: not allowed for role {user_role}")
        return FsmStepResult(new_state="FAILED", last_error=f"CANCEL_NOT_ALLOWED_FOR_{user_role}")

    if not success:
        logger.error(f"[FSM] cancel_order FAILED: order_id={order_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    logger.info(f"[FSM] cancel_order COMPLETED: order_id={order_id}")
    return FsmStepResult(new_state="COMPLETED")


# ==================== LOCKER ERROR ====================
def _handle_locker_error(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальный обработчик ошибки ячейки (не открылось / не закрылось).
    Поддерживаемые роли: client, recipient, courier, operator, driver.
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] locker_error: role={user_role}, entity={entity_type}:{entity_id}, user={user_id}")

    if entity_type == "order":
        if user_role == "client":
            success, error = ctx["client_actions"].report_locker_error(session, entity_id, user_id)
        elif user_role == "recipient":
            success, error = ctx["recipient_actions"].report_locker_error(session, entity_id, user_id)
        elif user_role == "courier":
            success, error = ctx["courier_actions"].locker_error(session, entity_id, user_id)
        elif user_role == "operator":
            success, error = ctx["operator_actions"].report_locker_error(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] locker_error: not allowed for role {user_role}")
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ERROR_NOT_ALLOWED_{user_role}")
    elif entity_type == "locker":
        if user_role == "driver":
            success, error = ctx["driver_actions"].report_locker_error_cell(session, entity_id, user_id)
        else:
            logger.warning(f"[FSM] locker_error: not allowed for role {user_role}")
            return FsmStepResult(new_state="FAILED", last_error=f"LOCKER_ERROR_NOT_ALLOWED_{user_role}")
    else:
        logger.error(f"[FSM] locker_error: unsupported entity_type {entity_type}")
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not success:
        logger.error(f"[FSM] locker_error FAILED: entity={entity_type}:{entity_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    logger.info(f"[FSM] locker_error COMPLETED: entity={entity_type}:{entity_id}")
    return FsmStepResult(new_state="COMPLETED")


# ==================== DRIVER BUTTONS ====================
def _handle_start_trip(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Начало поездки водителем.
    Только роль driver разрешена.
    """
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] start_trip: role={user_role}, trip_id={trip_id}, user_id={user_id}")

    if user_role != "driver":
        logger.warning(f"[FSM] start_trip: not allowed for role {user_role}")
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    success, error = ctx["driver_actions"].start_trip(session, trip_id, user_id)
    if not success:
        logger.error(f"[FSM] start_trip FAILED: trip_id={trip_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    logger.info(f"[FSM] start_trip COMPLETED: trip_id={trip_id}")
    return FsmStepResult(new_state="COMPLETED")


def _handle_arrive_at_destination(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Прибытие водителя в пункт назначения.
    Только роль driver разрешена.
    """
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] arrive_at_destination: role={user_role}, trip_id={trip_id}, user_id={user_id}")

    if user_role != "driver":
        logger.warning(f"[FSM] arrive_at_destination: not allowed for role {user_role}")
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    success, error = ctx["driver_actions"].arrive_at_destination(session, trip_id, user_id)
    if not success:
        logger.error(f"[FSM] arrive_at_destination FAILED: trip_id={trip_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    logger.info(f"[FSM] arrive_at_destination COMPLETED: trip_id={trip_id}")
    return FsmStepResult(new_state="COMPLETED")


def _handle_cancel_trip(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Отмена поездки водителем.
    Только роль driver разрешена.
    """
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info(f"[FSM] cancel_trip: role={user_role}, trip_id={trip_id}, user_id={user_id}")

    if user_role != "driver":
        logger.warning(f"[FSM] cancel_trip: not allowed for role {user_role}")
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    success, error = ctx["driver_actions"].cancel_trip(session, trip_id, user_id)
    if not success:
        logger.error(f"[FSM] cancel_trip FAILED: trip_id={trip_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)
    
    logger.info(f"[FSM] cancel_trip COMPLETED: trip_id={trip_id}")
    return FsmStepResult(new_state="COMPLETED")


# ==================== PROCESS REGISTRY ====================
PROCESS_DEFS: Dict[str, Dict[str, FsmStateHandler]] = {
    "order_creation": {"PENDING": _handle_order_creation_pending},
    "order_assign_courier1": {"PENDING": _handle_assign_executor_pending},
    "order_assign_courier2": {"PENDING": _handle_assign_executor_pending},
    "trip_assign_driver": {"PENDING": _handle_assign_executor_pending},
    "start_trip": {"PENDING": _handle_start_trip},
    "arrive_at_destination": {"PENDING": _handle_arrive_at_destination},
    "cancel_trip": {"PENDING": _handle_cancel_trip},
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
    session: Session,
    db: DatabaseLayer,
    actions_ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальный запуск одного шага FSM.
    Всегда возвращает FsmStepResult с new_state="COMPLETED" или "FAILED".
    """
    process_name = instance["process_name"]
    fsm_state = instance["fsm_state"]

    if process_name not in PROCESS_DEFS:
        logger.error(f"Неизвестный процесс: {process_name}")
        return FsmStepResult(new_state="FAILED", last_error=f"UNKNOWN_PROCESS: {process_name}", attempts_increment=1)

    process_def = PROCESS_DEFS[process_name]
    handler = process_def.get(fsm_state)

    if not handler:
        logger.warning(f"Нет обработчика состояния {fsm_state} для процесса {process_name}")
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"NO_HANDLER_FOR_STATE_{fsm_state}_IN_{process_name}",
            attempts_increment=1
        )

    result = handler(db, session, actions_ctx, instance)  

    # защита: new_state только COMPLETED/FAILED
    if result.new_state not in ("COMPLETED", "FAILED"):
        logger.warning(f"Некорректное new_state={result.new_state} в {process_name}")
        result.new_state = "FAILED"
        if not result.last_error:
            result.last_error = "INVALID_STATE_RETURNED"

    return result

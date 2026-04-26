# fsm_engine.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import logging

from db_layer import DatabaseLayer, DbLayerError
from adapter.order_mapping import OrderMapping
from fsm_actions import (
    OrderCreationActions,
    AssignmentActions,
    CourierActions,
    OperatorActions,
    ClientActions,
    RecipientActions,
    DriverActions,
    AccessCodeActions,
    TripActions,
    LockerActions,
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
def _handle_order_creation_pending(db, session, ctx, instance):
    request_id = instance["entity_id"]
    actions = ctx["order_creation_actions"]
    ok, src_id, dst_id, client_id, recipient_id, err = actions.find_cell_for_order(session, request_id)
    if not ok:
        return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

    order_mapping = ctx["order_mapping"]
    ok, core_order_id, b_state, kind, upper, err = order_mapping.create_order_in_core(session, request_id, src_id, dst_id)
    if not ok:
        return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

    ok, local_order_id, err = actions.finalize_order_creation(
        session, request_id, core_order_id, src_id, dst_id, client_id, recipient_id, b_state, kind, upper
    )
    if not ok:
        return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

    return FsmStepResult(new_state="COMPLETED", payload={"order_id": local_order_id})


# ==================== ASSIGN EXECUTOR ====================
def _handle_assign_executor(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальное назначение/переназначение исполнителя (курьера или водителя).
    Для order обязателен metadata.leg ("pickup" → courier1, "delivery" → courier2).
    Для trip назначается водитель на рейс и все его заказы.
    """
    actions: AssignmentActions = ctx["assignment_actions"]
    order_mapping: OrderMapping = ctx["order_mapping"]

    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    target_user_id = instance.get("target_user_id", 0)
    metadata = instance.get("metadata", {})

    if not target_user_id or target_user_id <= 0:
        return FsmStepResult(
            new_state="FAILED",
            last_error="TARGET_USER_ID_NOT_SET",
            attempts_increment=1
        )

    logger.info(
        "[FSM] assign_executor: entity=%s:%s, target=%s, metadata=%s",
        entity_type, entity_id, target_user_id, metadata
    )

    # ===== ЗАКАЗ (курьер) =====
    if entity_type == "order":
        leg = metadata.get("leg")
        if leg not in ("pickup", "delivery"):
            return FsmStepResult(
                new_state="FAILED",
                last_error="MISSING_OR_INVALID_LEG_IN_METADATA",
                attempts_increment=1
            )
        # Определяем роль по плечу (leg)
        role = "courier1" if leg == "pickup" else "courier2"

        # 1. Назначение/переназначение в Core
        ok, err = order_mapping.assign_executor_in_core(
            session,
            local_order_id=entity_id,
            performer_local_user_id=target_user_id,
            role=role
        )
        if not ok:
            logger.error("[FSM] assign_executor(order): Core назначение не удалось: %s", err)
            return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

        # 2. Локальное назначение курьера
        success = actions.assign_to_order(session, entity_id, target_user_id, role)
        if not success:
            logger.error("[FSM] assign_executor(order): локальное назначение не удалось")
            return FsmStepResult(
                new_state="FAILED",
                last_error="ASSIGN_ORDER_FAILED",
                attempts_increment=1
            )

    # ===== РЕЙС (водитель) =====
    elif entity_type == "trip":
        order_ids = db.get_orders_in_trip(session, entity_id)
        if not order_ids:
            return FsmStepResult(
                new_state="FAILED",
                last_error="NO_ORDERS_IN_TRIP",
                attempts_increment=1
            )

        # 1. Массовое назначение/переназначение в Core для всех заказов рейса
        ok, err = order_mapping.reassign_driver_for_trip(
            session,
            trip_id=entity_id,
            order_ids=order_ids,
            new_driver_local_id=target_user_id,
            role="driver"
        )
        if not ok:
            logger.error("[FSM] assign_executor(trip): Core назначение не удалось: %s", err)
            return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

        # 2. Локальное назначение водителя на рейс и обновление stage_orders
        success = actions.reassign_driver_on_trip(
            session,
            trip_id=entity_id,
            order_ids=order_ids,
            new_driver_id=target_user_id,
            role="driver"
        )
        if not success:
            logger.error("[FSM] assign_executor(trip): локальное назначение не удалось")
            return FsmStepResult(
                new_state="FAILED",
                last_error="TRIP_REASSIGN_FAILED",
                attempts_increment=1
            )

    else:
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"Неподдерживаемый entity_type: {entity_type}",
            attempts_increment=1
        )

    logger.info("[FSM] assign_executor COMPLETED: %s:%s", entity_type, entity_id)
    return FsmStepResult(new_state="COMPLETED", attempts_increment=1)

# =========== снять курьера с заказа и водителя с рейса ======
def _handle_remove_executor(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальное снятие исполнителя (курьера/водителя).
    Для order обязателен metadata.leg ("pickup" / "delivery").
    Для trip снимается водитель со всех заказов рейса.
    """
    actions: AssignmentActions = ctx["assignment_actions"]
    order_mapping: OrderMapping = ctx["order_mapping"]

    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    target_user_id = instance.get("target_user_id", 0)  
    operator_id = instance["requested_by_user_id"]    
    metadata = instance.get("metadata", {})

    if not target_user_id or target_user_id <= 0:
        return FsmStepResult(
            new_state="FAILED",
            last_error="TARGET_USER_ID_NOT_SET",
            attempts_increment=1
        )

    logger.info(
        "[FSM] remove_executor: entity=%s:%s, target=%s, initiator=%s, metadata=%s",
        entity_type, entity_id, target_user_id, operator_id, metadata
    )

    # ===== ЗАКАЗ (курьер) =====
    if entity_type == "order":
        leg = metadata.get("leg")
        if leg not in ("pickup", "delivery"):
            return FsmStepResult(
                new_state="FAILED",
                last_error="MISSING_OR_INVALID_LEG_IN_METADATA",
                attempts_increment=1
            )

        # 1. Снять подзаказ в Core
        ok, err = order_mapping.remove_suborder_performer_in_core(
            session,
            local_order_id=entity_id,
            performer_local_user_id=target_user_id,
            user_id=operator_id
        )
        if not ok:
            logger.error("[FSM] remove_executor(order): Core снятие не удалось: %s", err)
            return FsmStepResult(new_state="FAILED", last_error=err, attempts_increment=1)

        # 2. Локальное снятие курьера 
        success = actions.remove_courier_from_order(
            session, entity_id, target_user_id, leg, operator_id
        )
        if not success:
            logger.error("[FSM] remove_executor(order): локальное снятие не удалось")
            return FsmStepResult(
                new_state="FAILED",
                last_error="REMOVE_COURIER_FAILED",
                attempts_increment=1
            )

    # ===== РЕЙС (водитель) =====
    elif entity_type == "trip":
        order_ids = db.get_orders_in_trip(session, entity_id)
        if not order_ids:
            return FsmStepResult(
                new_state="FAILED",
                last_error="NO_ORDERS_IN_TRIP",
                attempts_increment=1
            )

        # 1. Снять подзаказы в Core для всех заказов рейса
        errors = []
        for oid in order_ids:
            ok, err = order_mapping.remove_suborder_performer_in_core(
                session,
                local_order_id=oid,
                performer_local_user_id=target_user_id,
                user_id=operator_id
            )
            if not ok:
                errors.append(f"Заказ {oid}: {err}")

        if errors:
            logger.error("[FSM] remove_executor(trip): ошибки Core снятия: %s", "; ".join(errors))
            return FsmStepResult(
                new_state="FAILED",
                last_error="; ".join(errors),
                attempts_increment=1
            )

        # 2. Локальное снятие водителя с рейса и очистка всех его stage_orders
        success = actions.remove_driver_from_trip_with_orders(
            session,
            trip_id=entity_id,
            order_ids=order_ids,
            executor_id=target_user_id,
            operator_id=operator_id
        )
        if not success:
            logger.error("[FSM] remove_executor(trip): локальное снятие не удалось")
            return FsmStepResult(
                new_state="FAILED",
                last_error="REMOVE_DRIVER_FAILED",
                attempts_increment=1
            )

    else:
        return FsmStepResult(
            new_state="FAILED",
            last_error=f"Неподдерживаемый entity_type: {entity_type}",
            attempts_increment=1
        )

    logger.info("[FSM] remove_executor COMPLETED: %s:%s", entity_type, entity_id)
    return FsmStepResult(new_state="COMPLETED", attempts_increment=1)
    
# ==================== OPEN/CLOSE CELL ====================
def _handle_open_cell(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    metadata = instance.get("metadata", {})
    
    logger.info(f"[FSM] open_cell: role={user_role}, entity={entity_type}:{entity_id}, user={user_id}")

    # Проверка PIN
    pin = metadata.get("pin")
    if not pin:
        return FsmStepResult(new_state="FAILED", last_error="MISSING_PIN_IN_METADATA")
    
    # ОПРЕДЕЛЕНИЕ leg И cell_id
    if entity_type == "order":
        leg = metadata.get("leg")
        if not leg or leg not in ["pickup", "delivery"]:
            return FsmStepResult(new_state="FAILED", last_error="INVALID_LEG_IN_METADATA")
        
        order = db.get_order(session, entity_id)
        if not order:
            return FsmStepResult(new_state="FAILED", last_error="ORDER_NOT_FOUND")
        
        cell_id = order["source_cell_id"] if leg == "pickup" else order["dest_cell_id"]
        
    elif entity_type == "locker":
        cell_id = entity_id
        
        order_id = db.get_order_id_by_cell_id(session, cell_id)
        if not order_id:
            return FsmStepResult(new_state="FAILED", last_error="CELL_NOT_LINKED_TO_ORDER")
        
        order = db.get_order(session, order_id)
        if not order:
            return FsmStepResult(new_state="FAILED", last_error="ORDER_NOT_FOUND")
        
        # Определяем leg: source=pickup, dest=delivery
        if cell_id == order["source_cell_id"]:
            leg = "pickup"
        elif cell_id == order["dest_cell_id"]:
            leg = "delivery"
        else:
            return FsmStepResult(new_state="FAILED", last_error="CELL_NOT_IN_ORDER")
    else:
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")
    
    # Валидация PIN
    valid, error = db.validate_access_code(
        session, order_id if entity_type == "locker" else entity_id,
        leg, user_id, pin, cell_id
    )
    
    if not valid:
        return FsmStepResult(new_state="FAILED", last_error=f"INVALID_ACCESS_CODE: {error}")

    # ОТКРЫТИЕ ЯЧЕЙКИ
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
    entity_type = "order"  → роли: client, recipient, courier, operator
    entity_type = "locker" → роль:  driver
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    entity_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    target_user_id = instance.get("target_user_id")
    target_role = instance.get("target_role")

    logger.info(f"[FSM] close_cell: role={user_role}, entity={entity_type}:{entity_id}, user={user_id}")

    order_mapping = ctx.get("order_mapping")

    if entity_type == "order":
        # ----- CLIENT -----
        if user_role == "client":
            success, error = ctx["client_actions"].close_cell_for_client(session, entity_id, user_id)

        # ----- RECIPIENT -----
        elif user_role == "recipient":
            if order_mapping:
                ok, err = order_mapping.complete_main_order_in_core(session, entity_id, user_id)
                if not ok:
                    logger.error("Core main completion failed for recipient: %s", err)
                    return FsmStepResult(new_state="FAILED", last_error=f"CORE_MAIN_COMPLETION_FAILED: {err}")
            success, error = ctx["recipient_actions"].close_cell_for_recipient(session, entity_id, user_id)

        # ----- COURIER -----
        elif user_role == "courier":
            # Определяем leg по статусу заказа
            order = db.get_order(session, entity_id)
            if not order:
                return FsmStepResult(new_state="FAILED", last_error="ORDER_NOT_FOUND")
            
            status = order["status"]
            if status in ("order_courier1_assigned", "order_courier_has_parcel"):
                leg = "pickup"
            elif status in ("order_courier2_assigned", "order_courier2_has_parcel"):
                leg = "delivery"
            else:
                return FsmStepResult(new_state="FAILED", last_error=f"UNKNOWN_COURIER_STATUS_{status}")

            # Для pickup завершаем подзаказ в Core
            if leg == "pickup" and order_mapping:
                ok, err = order_mapping.complete_suborder_in_core(session, entity_id, user_id)
                if not ok:
                    logger.error("Core suborder completion failed for courier (pickup): %s", err)
                    return FsmStepResult(new_state="FAILED", last_error=f"CORE_SUBORDER_COMPLETION_FAILED: {err}")
            else:
                logger.info("Courier delivery close_cell: skipping Core completion")

            success, error = ctx["courier_actions"].close_cell(session, entity_id, user_id)
            if not success:
                return FsmStepResult(new_state="FAILED", last_error=error)

        # ----- OPERATOR -----
        elif user_role == "operator":
            actual_user = target_user_id or user_id
            if order_mapping:
                if target_role in ("client", "recipient"):
                    ok, err = order_mapping.complete_main_order_in_core(session, entity_id, actual_user)
                elif target_role in ("courier", "driver"):
                    ok, err = order_mapping.complete_suborder_in_core(session, entity_id, actual_user)
                else:
                    ok, err = True, ""
                if not ok:
                    logger.error("Core completion by operator failed: %s", err)
                    return FsmStepResult(new_state="FAILED", last_error=f"CORE_OPERATOR_COMPLETION_FAILED: {err}")
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
    user_role = instance["requested_user_role"]
    order_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    performer_user_id = instance.get("target_user_id")
    metadata = instance.get("metadata", {})
    reason = metadata.get("reason")

    logger.info("[FSM] cancel_order: role=%s, order_id=%s, user_id=%s", user_role, order_id, user_id)

    order_mapping = ctx.get("order_mapping")
    if not order_mapping:
        logger.warning("[FSM] cancel_order: order_mapping not available")

    # 1. Core‑отмена
    if user_role == "client":
        if order_mapping:
            ok, err = order_mapping.cancel_main_order_in_core(
                session, local_order_id=order_id, user_id=user_id, reason=reason
            )
            if not ok:
                return FsmStepResult(new_state="FAILED", last_error=f"CORE: {err}")
        success, error = ctx["client_actions"].cancel_order(session, order_id, user_id)

    elif user_role == "courier":
        if order_mapping:
            ok, err = order_mapping.remove_suborder_performer_in_core(
                session, local_order_id=order_id,
                performer_local_user_id=user_id, 
                user_id=user_id
            )
            if not ok:
                return FsmStepResult(new_state="FAILED", last_error=f"CORE: {err}")
        success, error = ctx["courier_actions"].cancel_order(session, order_id, user_id)

    elif user_role == "operator":
        if not performer_user_id:
            return FsmStepResult(new_state="FAILED", last_error="MISSING_TARGET_USER_ID")
        if order_mapping:
            ok, err = order_mapping.remove_suborder_performer_in_core(
                session, local_order_id=order_id,
                performer_local_user_id=performer_user_id,
                user_id=user_id
            )
            if not ok:
                return FsmStepResult(new_state="FAILED", last_error=f"CORE: {err}")
        success, error = ctx["operator_actions"].force_cancel_order(session, order_id, user_id)

    else:
        logger.warning("[FSM] cancel_order: role %s not allowed", user_role)
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_{user_role}")

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)

    logger.info("[FSM] cancel_order: COMPLETED for order_id=%s", order_id)
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
    entity_type = "direction"
    direction_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    user_role = instance["requested_user_role"]

    logger.info("[FSM] start_trip: direction_id=%s, user_id=%s, role=%s",
                direction_id, user_id, user_role)

    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    # 1. Валидация готовности заказов
    can_start, blocked_ids, order_ids, error = db.validate_and_get_orders_for_direction_start(
        session, direction_id, user_id
    )
    if not can_start:
        return FsmStepResult(new_state="FAILED", last_error=error)

    # 2. Создание рейса и FSM-переходы (получаем trip_id)
    success, trip_id, error = ctx["driver_actions"].start_trip(session, direction_id, user_id, order_ids)
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)

    # 3. Массовое назначение водителя на все заказы рейса в Core
    order_mapping = ctx.get("order_mapping")
    if order_mapping:
        ok, err = order_mapping.reassign_driver_for_trip(
            session,
            trip_id=trip_id,
            order_ids=order_ids,
            new_driver_local_id=user_id,
            role="driver"
        )
        if not ok:
            return FsmStepResult(new_state="FAILED", last_error=f"DRIVER_SUBORDER_FAILED: {err}")

    logger.info("[FSM] start_trip COMPLETED: direction_id=%s, orders=%d", direction_id, len(order_ids))
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

def _handle_complete_trip(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    user_role = instance["requested_user_role"]
    trip_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]

    logger.info("[FSM] complete_trip: role=%s, trip_id=%s, user_id=%s", user_role, trip_id, user_id)

    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    # 1. Проверка готовности рейса к завершению
    can_complete, blocked_ids, completed_order_ids, error = db.validate_trip_for_completion(session, trip_id)
    if not can_complete:
        return FsmStepResult(new_state="FAILED", last_error=error)

    # 2. Завершение подзаказов водителя в Core
    order_mapping = ctx.get("order_mapping")
    if order_mapping:
        for order_id in completed_order_ids:
            ok, err = order_mapping.complete_suborder_in_core(session, order_id, user_id)
            if not ok:
                logger.error("[FSM] complete_suborder_in_core failed for order %s: %s", order_id, err)
                return FsmStepResult(new_state="FAILED", last_error=f"DRIVER_SUBORDER_COMPLETION_FAILED: {err}")

    # 3. Локальные FSM-переходы
    success, error = ctx["driver_actions"].complete_trip(session, trip_id, user_id)
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)

    return FsmStepResult(new_state="COMPLETED")

# ==================== Access Code ====================
def _handle_request_locker_access_code(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик запроса кода открытия ячейки.
    Поддерживает: client, courier, recipient, driver.
    Ожидает в instance["metadata"]: {"leg": "pickup" | "delivery"}
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"]
    order_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    metadata = instance.get("metadata", {})
    
    if entity_type != "order":
        logger.error(f"[FSM] request_locker_access_code: unsupported entity_type={entity_type}")
        return FsmStepResult(new_state="FAILED", last_error="UNSUPPORTED_ENTITY_TYPE")

    if not metadata or not isinstance(metadata, dict):
        logger.error(f"[FSM] request_locker_access_code: missing or invalid metadata for order {order_id}")
        return FsmStepResult(new_state="FAILED", last_error="MISSING_METADATA")

    leg = metadata.get("leg")
    if leg not in ("pickup", "delivery"):
        logger.error(f"[FSM] request_locker_access_code: invalid leg={leg} for order {order_id}")
        return FsmStepResult(new_state="FAILED", last_error="INVALID_LEG")

    logger.info(f"[FSM] request_locker_access_code: role={user_role}, order={order_id}, leg={leg}, user={user_id}")

    # Делегируем экшену
    success, error = ctx["access_code_actions"].request_access_code(
        session, order_id, user_id, leg
    )

    if not success:
        logger.error(f"[FSM] request_locker_access_code FAILED: order={order_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error or "REQUEST_FAILED")

    logger.info(f"[FSM] request_locker_access_code COMPLETED: order={order_id}")
    return FsmStepResult(new_state="COMPLETED")

def _handle_confirm_courier2_delivery(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Подтверждение доставки курьером2 с кодом от получателя.
    Только роль courier разрешена.
    Ожидает код в instance["metadata"]["pin"].
    """
    user_role = instance["requested_user_role"]
    order_id = instance["entity_id"]
    user_id = instance["requested_by_user_id"]
    metadata = instance.get("metadata", {})
    pin = metadata.get("pin")

    logger.info(f"[FSM] confirm_courier2_delivery: role={user_role}, order_id={order_id}, user_id={user_id}")

    if user_role != "courier":
        logger.warning(f"[FSM] confirm_courier2_delivery: not allowed for role {user_role}")
        return FsmStepResult(new_state="FAILED", last_error=f"NOT_ALLOWED_FOR_{user_role}")

    if not pin:
        logger.warning(f"[FSM] confirm_courier2_delivery: missing pin in metadata")
        return FsmStepResult(new_state="FAILED", last_error="MISSING_PIN_IN_METADATA")

    # 1. Проверяем PIN-код
    valid, error = db.validate_courier2_delivery_code(session, order_id, user_id, pin)
    if not valid:
        logger.warning(f"[FSM] confirm_courier2_delivery: invalid PIN: {error}")
        return FsmStepResult(new_state="FAILED", last_error=f"INVALID_PIN: {error}")

    # 2. Завершаем подзаказ курьера2 в Core
    order_mapping = ctx.get("order_mapping")
    if order_mapping:
        ok, err = order_mapping.complete_suborder_in_core(session, order_id, user_id)
        if not ok:
            logger.error("Core suborder completion failed for courier2: %s", err)
            return FsmStepResult(new_state="FAILED", last_error=f"CORE_SUBORDER_COMPLETION_FAILED: {err}")

        # 3. Завершаем главный заказ в Core от имени клиента
        ok, err = order_mapping.complete_main_order_in_core(session, order_id, user_id)
        if not ok:
            logger.error("Core main completion failed for courier delivery: %s", err)
            return FsmStepResult(new_state="FAILED", last_error=f"CORE_MAIN_COMPLETION_FAILED: {err}")

    # 4. Локальный FSM-переход
    success, error = ctx["courier_actions"].confirm_delivery_with_code(session, order_id, user_id, pin)
    if not success:
        logger.error(f"[FSM] confirm_courier2_delivery FAILED: order_id={order_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)

    logger.info(f"[FSM] confirm_courier2_delivery COMPLETED: order_id={order_id}")
    return FsmStepResult(new_state="COMPLETED")

# ==================== РЕЙСЫ ====================
def _handle_bind_order_to_trip(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Создает новый рейс, либо после того как заказ положат в ячейку и закроют ее
    """
    order_id = instance["entity_id"]
    logger.info(f"[FSM] bind_order_to_trip for order {order_id}")
    
    success, error = ctx["trip_actions"].bind_order_to_trip(
        session, order_id
    )

    if not success:
        logger.error(f"[FSM] bind_order_to_trip FAILED: order={order_id}, error={error}")
        return FsmStepResult(new_state="FAILED", last_error=error)

    logger.info(f"[FSM] bind_order_to_trip COMPLETED: order={order_id}")
    return FsmStepResult(new_state="COMPLETED")

# ==================== Универсальный обработчик ошибок ====================
def _handle_report_error(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Универсальный обработчик ошибок для ВСЕХ ролей и сущностей.
    Поддерживает: order, locker, trip
    """
    user_role = instance["requested_user_role"]
    entity_type = instance["entity_type"] 
    entity_id = instance["entity_id"]
    metadata = instance.get("metadata", {})
    
    error_type = metadata.get("error_type")
    order_id = metadata.get("order_id")
    trip_id = metadata.get("trip_id")
    
    logger.info(f"[FSM] report_error: role={user_role}, type={error_type}, entity={entity_type}:{entity_id}")

    if not error_type:
        return FsmStepResult(new_state="FAILED", last_error="MISSING_ERROR_TYPE_IN_METADATA")   
   
    if entity_type != "trip" and not order_id:
        return FsmStepResult(new_state="FAILED", last_error="MISSING_ORDER_ID_IN_METADATA")

    # Выбираем actions по роли
    if user_role == "driver":
        actions = ctx["driver_actions"]
    elif user_role == "courier":
        actions = ctx["courier_actions"]
    elif user_role == "client":
        actions = ctx["client_actions"]
    elif user_role == "recipient":
        actions = ctx["recipient_actions"]
    elif user_role == "operator":
        actions = ctx["operator_actions"]
    else:
        return FsmStepResult(new_state="FAILED", last_error=f"UNSUPPORTED_ROLE_{user_role}")    
    success, error = actions.report_error(
        session, entity_id, order_id, instance["requested_by_user_id"], error_type, trip_id
    )
    
    if not success:
        return FsmStepResult(new_state="FAILED", last_error=error)
        
    return FsmStepResult(new_state="COMPLETED")

# ==================== Направления ====================
def _handle_direction_reserve_slot(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик резервирования слота водителем.
    """
    direction_id = instance["entity_id"]
    driver_user_id = instance["requested_by_user_id"]
    metadata = instance.get("metadata", {})
    capacity = metadata.get("capacity", 0)
    
    logger.info(
        "[FSM] direction_reserve_slot: direction_id=%s, driver_user_id=%s, capacity=%s",
        direction_id, driver_user_id, capacity
    )    
    if capacity <= 0:
        return FsmStepResult(
            new_state="FAILED",
            last_error="INVALID_CAPACITY",
            attempts_increment=1
        )    
    actions: TripActions = ctx["trip_actions"]
    
    success, msg = actions.reserve_slot(
        session, direction_id, driver_user_id, capacity
    )    
    if not success:
        logger.error(
            "[FSM] direction_reserve_slot FAILED: direction_id=%s, error=%s",
            direction_id, msg
        )
        return FsmStepResult(
            new_state="FAILED",
            last_error=msg,
            attempts_increment=1
        )    
    logger.info(
        "[FSM] direction_reserve_slot COMPLETED: direction_id=%s",
        direction_id
    )    
    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1
    )

def _handle_driver_reservation_start_loading(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик начала погрузки водителем.
    """
    reservation_id = instance["entity_id"]
    driver_user_id = instance["requested_by_user_id"]
    user_role = instance.get("requested_user_role", "")
    
    logger.info(
        "[FSM] driver_reservation_start_loading: direction_id=%s, driver_user_id=%s, role=%s",
        reservation_id, driver_user_id, user_role
    )
    # 1. Проверка роли (только водитель)
    if user_role != "driver":
        logger.error(
            "[FSM] driver_reservation_start_loading: доступ запрещён для роли %s",
            user_role
        )
        return FsmStepResult(
            new_state="FAILED",
            last_error="ROLE_NOT_ALLOWED: только водитель может начать погрузку",
            attempts_increment=1
        )
    actions: TripActions = ctx["trip_actions"]
    
    # 2. Вызываем экшен
    success, msg = actions.start_loading(
        session, reservation_id, driver_user_id
    )
    if not success:
        logger.error(
            "[FSM] driver_reservation_start_loading FAILED: direction_id=%s, error=%s",
            reservation_id, msg
        )
        return FsmStepResult(
            new_state="FAILED",
            last_error=msg,
            attempts_increment=1
        )
    logger.info(
        "[FSM] direction_start_loading COMPLETED: direction_id=%s",
        reservation_id
    )
    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1
    )

def _handle_direction_complete_loading(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    direction_id = instance["entity_id"]
    driver_user_id = instance["requested_by_user_id"]
    user_role = instance.get("requested_user_role", "")

    logger.info(
        "[FSM] direction_complete_loading: direction_id=%s, driver_user_id=%s, role=%s",
        direction_id, driver_user_id, user_role
    )

    if user_role != "driver":
        return FsmStepResult(new_state="FAILED", last_error="ROLE_NOT_ALLOWED", attempts_increment=1)

    actions: TripActions = ctx["trip_actions"]
    success, msg = actions.complete_loading(session, direction_id, driver_user_id)

    if not success:
        return FsmStepResult(new_state="FAILED", last_error=msg, attempts_increment=1)

    logger.info("[FSM] direction_complete_loading COMPLETED: direction_id=%s", direction_id)
    return FsmStepResult(new_state="COMPLETED")

def _handle_driver_reservation_cancel(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик отмены резерва водителем.
    """
    reservation_id = instance["entity_id"]
    driver_user_id = instance["requested_by_user_id"]
    user_role = instance.get("requested_user_role", "")
    
    logger.info(
        "[FSM] driver_reservation_cancel: reservation_id=%s, driver_user_id=%s, role=%s",
        reservation_id, driver_user_id, user_role
    )
    
    # 1. Проверка роли (только водитель)
    if user_role != "driver":
        logger.error("[FSM] driver_reservation_cancel: доступ запрещён для роли %s", user_role)
        return FsmStepResult(
            new_state="FAILED",
            last_error="ROLE_NOT_ALLOWED: только водитель может отменить резерв",
            attempts_increment=1
        )
    
    actions: TripActions = ctx["trip_actions"]
    
    # 2. Вызываем экшен
    success, msg = actions.cancel_reservation(
        session, reservation_id, driver_user_id
    )
    
    if not success:
        logger.error(
            "[FSM] driver_reservation_cancel FAILED: reservation_id=%s, error=%s",
            reservation_id, msg
        )
        return FsmStepResult(
            new_state="FAILED",
            last_error=msg,
            attempts_increment=1
        )
    
    logger.info("[FSM] driver_reservation_cancel COMPLETED: reservation_id=%s", reservation_id)
    
    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1
    )

def _handle_driver_reservation_expire(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Обработчик истечения таймаута резерва.
    """
    reservation_id = instance["entity_id"]
    driver_user_id = instance["requested_by_user_id"]
    
    logger.info(
        "[FSM] driver_reservation_expire: reservation_id=%s, driver_user_id=%s",
        reservation_id, driver_user_id
    )
    
    actions: TripActions = ctx["trip_actions"]
    
    # Вызываем экшен
    success, msg = actions.expire_reservation(
        session, reservation_id, driver_user_id
    )
    
    if not success:
        logger.error(
            "[FSM] driver_reservation_expire FAILED: reservation_id=%s, error=%s",
            reservation_id, msg
        )
        return FsmStepResult(
            new_state="FAILED",
            last_error=msg,
            attempts_increment=1
        )
    
    logger.info(
        "[FSM] driver_reservation_expire COMPLETED: reservation_id=%s",
        reservation_id
    )
    
    return FsmStepResult(
        new_state="COMPLETED",
        last_error=None,
        attempts_increment=1
    )

# ==================== Сброс ячеек постаматов ============

def _handle_locker_cleanup(
    db: DatabaseLayer,
    session: Session,
    ctx: Dict[str, Any],
    instance: Dict[str, Any]
) -> FsmStepResult:
    """
    Системный процесс очистки ячеек в статусе locker_closed_empty.
    """
    user_id = instance["requested_by_user_id"]
    metadata = instance.get("metadata", {})
    threshold_minutes = metadata.get("threshold_minutes", 30)
    
    logger.debug(f"[FSM] locker_cleanup: threshold={threshold_minutes} мин, user_id={user_id}")

    actions: LockerActions = ctx["locker_actions"]
    success, msg = actions.cleanup_closed_empty_lockers(
        session=session,
        threshold_minutes=threshold_minutes,
        user_id=user_id
    )

    if not success:
        logger.error(f"[FSM] locker_cleanup FAILED: {msg}")
        return FsmStepResult(new_state="FAILED", last_error=msg, attempts_increment=1)

    logger.debug(f"[FSM] locker_cleanup COMPLETED: {msg}")
    return FsmStepResult(new_state="COMPLETED", attempts_increment=1)

# ==================== PROCESS REGISTRY ====================
PROCESS_DEFS: Dict[str, Dict[str, FsmStateHandler]] = {
    "order_creation": {"PENDING": _handle_order_creation_pending},
    "assign_executor": {"PENDING": _handle_assign_executor},
    "remove_executor": { "PENDING": _handle_remove_executor},
    "start_trip": {"PENDING": _handle_start_trip},
    "arrive_at_destination": {"PENDING": _handle_arrive_at_destination},
    "cancel_trip": {"PENDING": _handle_cancel_trip},
    "complete_trip": {"PENDING": _handle_complete_trip},
    "open_cell": {"PENDING": _handle_open_cell},
    "close_cell": {"PENDING": _handle_close_cell},
    "cancel_order": {"PENDING": _handle_cancel_order},
    "locker_error": {"PENDING": _handle_locker_error},
    "request_locker_access_code": {"PENDING": _handle_request_locker_access_code},
    "confirm_courier2_delivery": {"PENDING": _handle_confirm_courier2_delivery},
    "bind_order_to_trip": {"PENDING": _handle_bind_order_to_trip},
    "report_error": {"PENDING": _handle_report_error},
    "direction_reserve_slot": {"PENDING": _handle_direction_reserve_slot},
    "driver_reservation_start_loading": {"PENDING": _handle_driver_reservation_start_loading},
    "direction_complete_loading": {"PENDING": _handle_direction_complete_loading},
    "driver_reservation_cancel": {"PENDING": _handle_driver_reservation_cancel},
    "locker_cleanup": {"PENDING": _handle_locker_cleanup},
}


def build_actions_context(db: DatabaseLayer, core_adapter: CoreAdapter) -> Dict[str, Any]:
    """Собирает actions-контексты для всех процессов."""
    return {
        "order_creation_actions": OrderCreationActions(db),
        "assignment_actions": AssignmentActions(db),
        "courier_actions": CourierActions(db),
        "operator_actions": OperatorActions(db),
        "client_actions": ClientActions(db),
        "recipient_actions": RecipientActions(db),
        "driver_actions": DriverActions(db),
        "access_code_actions": AccessCodeActions(db),
        "trip_actions": TripActions(db),
        "locker_actions": LockerActions(db),
        "order_mapping": OrderMapping(db, core_adapter),
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

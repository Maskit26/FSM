# fsm_actions.py

from typing import Tuple, Optional, List
from db_layer import DatabaseLayer, DbLayerError
from sqlalchemy.orm import Session
import logging
import hashlib
import secrets
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OrderCreationActions:
    def __init__(self, db: DatabaseLayer):
        self.db = db

    def find_cell_for_order(
        self,
        session: Session,
        request_id: int,
    ) -> Tuple[bool, Optional[int], Optional[int], Optional[int], Optional[int], str]:
        logger.info("create_order_from_request (reserve cells): request_id=%s", request_id)
        try:
            req = self.db.get_order_request(session, request_id)
            if not req or req["status"] != "PENDING":
                logger.warning("create_order_from_request: request %s not found or status not PENDING", request_id)
                return False, None, None, None, None, "REQ_NOT_FOUND_OR_INVALID"

            client_user_id = req["client_user_id"]
            if not client_user_id:
                logger.warning("create_order_from_request: client_user_id missing for request %s", request_id)
                return False, None, None, None, None, "INVALID_DATA"

            cell_size = req["cell_size"]
            recipient_user_id = req["recipient_user_id"]
            if not recipient_user_id:
                logger.warning("create_order_from_request: recipient_user_id missing for request %s", request_id)
                return False, None, None, None, None, "RECIPIENT_USER_ID_REQUIRED"

            client_city = self.db.get_user_city(session, client_user_id)
            recipient_city = self.db.get_user_city(session, recipient_user_id)
            logger.debug("create_order_from_request: cities client=%s recipient=%s", client_city, recipient_city)

            if client_city == recipient_city:
                logger.warning("create_order_from_request: same city %s for request %s", client_city, request_id)
                return False, None, None, None, None, f"SELF_CITY_NOT_ALLOWED: {client_city}"

            ok, src_id, dst_id = self.db.find_and_reserve_cells_by_cities(
                session, client_city, recipient_city, cell_size
            )
            if not ok:
                logger.warning("create_order_from_request: no free cells for route %s -> %s, size=%s",
                               client_city, recipient_city, cell_size)
                return False, None, None, None, None, "NO_FREE_CELLS"

            logger.info("create_order_from_request: reserved cells src=%s dst=%s for request %s",
                        src_id, dst_id, request_id)
            return True, src_id, dst_id, client_user_id, recipient_user_id, ""

        except Exception as e:
            logger.exception("create_order_from_request failed for request %s: %s", request_id, e)
            return False, None, None, None, None, f"EXCEPTION: {e}"

    def finalize_order_creation(
        self,
        session: Session,
        request_id: int,
        core_order_id: int,
        src_cell_id: int,
        dst_cell_id: int,
        client_user_id: int,
        recipient_user_id: Optional[int],
        b_state: int,
        kind: Optional[int],
        upper: Optional[int],
    ) -> Tuple[bool, Optional[int], str]:
        logger.info("finalize_order_creation: request_id=%s, core_order_id=%s", request_id, core_order_id)
        try:
            req = self.db.get_order_request(session, request_id)
            if not req:
                return False, None, "REQ_NOT_FOUND"

            parcel_type = req["parcel_type"]
            cell_size = req["cell_size"]
            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]
            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            # Создаём или получаем локальный заказ, передаём все параметры
            local_order_id = self.db.get_or_create_order_by_core_id(
                session=session,
                core_order_id=core_order_id,
                client_user_id=client_user_id,
                recipient_user_id=recipient_user_id,
                description=description,
                parcel_type=parcel_type,
                cell_size=cell_size,
                pickup_type=pickup_type,
                delivery_type=delivery_type,
                role="main",
                kind=kind,
                upper=upper,
                b_state=b_state,
            )
            logger.info("finalize_order_creation: local_order_id=%s", local_order_id)

            # Привязываем ячейки
            self.db.bind_cells_for_order(session, local_order_id, src_cell_id, dst_cell_id)
            self.db.update_order_cells(session, local_order_id, src_cell_id, dst_cell_id)
            self.db.create_stage_order(session, None, local_order_id, "pickup")
            self.db.create_stage_order(session, None, local_order_id, "delivery")
            return True, local_order_id, ""

        except Exception as e:
            logger.exception("finalize_order_creation failed for request %s", request_id)
            return False, None, f"EXCEPTION: {e}"


class AssignmentActions:
    """
    Действия для назначения исполнителей.

    Исполнитель ВСЕГДА передаётся явно через target_user_id.
    НЕТ автоматического выбора исполнителя.
    """

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def assign_to_order(
        self,
        session: Session,
        order_id: int,
        executor_id: int,
        role: str
    ) -> bool:
        """
        Назначает исполнителя на заказ.

        Двухэтапно:
        1) stage_orders
        2) FSM вызов
        """

        logger.info(
            "[ASSIGNMENT] assign_to_order order_id=%s executor=%s role=%s",
            order_id,
            executor_id,
            role,
        )

        try:
            if role == "courier1":
                self.db.set_courier1_in_stage(session, order_id, executor_id)
                self.db.assign_courier_to_order(session, order_id, executor_id)

            elif role == "courier2":
                self.db.set_courier2_in_stage(session, order_id, executor_id)
                self.db.assign_courier2_to_order(session, order_id, executor_id)

            else:
                logger.error("[ASSIGNMENT] unknown role for order: %s", role)
                return False

            logger.info(
                "[ASSIGNMENT] assigned order_id=%s executor=%s role=%s",
                order_id,
                executor_id,
                role,
            )
            return True

        except Exception:
            logger.exception(
                "[ASSIGNMENT] assign_to_order failed order_id=%s", order_id
            )
            return False

    def reassign_driver_on_trip(
        self,
        session: Session,
        trip_id: int,
        order_ids: List[int],
        new_driver_id: int,
        role: str
    ) -> bool:
        logger.info(
            "[ASSIGNMENT] reassign_driver_on_trip trip=%s, orders=%s, new_driver=%s, role=%s",
            trip_id, order_ids, new_driver_id, role
        )
        try:
            # Обновить водителя в таблице trips
            self.db.set_driver_in_trip(session, trip_id, new_driver_id)

            # Если рейс был сломан (trip_failed) – активируем его сразу
            trip = self.db.get_trip(session, trip_id)
            if trip and trip.get("status") == "trip_failed":
                self.db.trip_resume_with_new_driver(session, trip_id, new_driver_id)
                logger.info("[ASSIGNMENT] Рейс %s возобновлён с новым водителем", trip_id)
            else:
                logger.info(
                    "[ASSIGNMENT] Рейс %s не требует активации (статус: %s)",
                    trip_id, trip.get("status") if trip else "неизвестен"
                )

            # Обновить reserved_by_driver_id во всех stage_orders
            self.db.reassign_driver_in_stage_orders(session, order_ids, new_driver_id)

            return True
        except Exception:
            logger.exception("[ASSIGNMENT] reassign_driver_on_trip failed")
            return False

# =========== снять курьера с заказа и водителя с рейса ======
    def remove_courier_from_order(
        self,
        session: Session,
        order_id: int,
        executor_id: int,
        leg: str,
        operator_id: int,
    ) -> bool:
        logger.info(
            "[ASSIGNMENT] remove_courier_from_order order_id=%s executor=%s leg=%s operator=%s",
            order_id, executor_id, leg, operator_id,
        )
        try:
            # 1. Удаление курьера из stage_orders 
            success = self.db.remove_courier_from_order(
                session, order_id, leg, operator_id
            )
            if not success:
                logger.error("[ASSIGNMENT] failed to remove courier %s from order %s", executor_id, order_id)
                return False

            # 2. Обновить статус заказа в зависимости от плеча 
            self.db.update_order_status_by_leg(session, order_id, leg)

            logger.info("[ASSIGNMENT] courier %s removed from order %s (leg=%s)", executor_id, order_id, leg)
            return True

        except Exception:
            logger.exception("[ASSIGNMENT] remove_courier_from_order failed order_id=%s", order_id)
            return False

    def remove_driver_from_trip_with_orders(
        self,
        session: Session,
        trip_id: int,
        order_ids: List[int],
        executor_id: int,
        operator_id: int
    ) -> bool:
        """
        Снимает водителя с рейса и очищает его закрепление за всеми заказами рейса.
        """
        logger.info(
            "[ASSIGNMENT] remove_driver_from_trip_with_orders trip=%s, executor=%s, orders=%s",
            trip_id, executor_id, order_ids
        )
        try:
            # 1. Снять водителя с самого рейса
            if not self.db.remove_driver_from_trip(session, trip_id, operator_id):
                raise DbLayerError("Не удалось снять водителя с рейса")

            # 2. Очистить закрепление водителя за всеми заказами рейса
            self.db.clear_driver_from_stage_orders(session, order_ids)

            logger.info(
                "[ASSIGNMENT] Водитель %s снят с рейса %s и всех связанных заказов",
                executor_id, trip_id
            )
            return True

        except Exception:
            logger.exception("[ASSIGNMENT] remove_driver_from_trip_with_orders failed")
            return False

# =========== РАБОТА С ПОСТАМАТОМ ===========================

# =========================================================
# CLIENT
# =========================================================

class ClientActions:
    """Действия клиента (отправителя)."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def open_cell_for_client(self, session, order_id, user_id):
        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            cell_id = ctx.get("cell_id")
            if not cell_id:
                return False, "CELL_NOT_FOUND"
            self.db.order_client_deliv_post1(session, order_id, user_id)
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            return True, ""
        except Exception as e:
            logger.error("[CLIENT] open_cell_for_client failed: %s", e)
            return False, str(e)

    def close_cell_for_client(self, session, order_id, user_id):
        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            cell_id = ctx.get("cell_id")
            if not cell_id:
                return False, "CELL_NOT_FOUND"
            self.db.order_confirm_parcel_in(session, order_id, user_id)
            self.db.close_locker(session, cell_id, user_id)
            return True, ""
        except Exception as e:
            logger.error("[CLIENT] close_cell_for_client failed: %s", e)
            return False, str(e)

    def cancel_order(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Клиент отменяет заказ до передачи.
        """
        logger.info("[CLIENT] cancel_order order=%s user=%s", order_id, user_id)

        try:
            order = self.db.get_order(session, order_id)
            if not order:
                logger.warning("[CLIENT] cancel_order failed: order %s not found", order_id)
                return False, "ORDER_NOT_FOUND"

            logger.debug("[CLIENT] cancelling reservation for order %s", order_id)
            self.db.order_cancel_reservation(session, order_id, user_id)

            src_id = order.get("source_cell_id")
            dst_id = order.get("dest_cell_id")

            if src_id:
                logger.debug("[CLIENT] cancelling locker reservation for source cell %s", src_id)
                self.db.cancel_locker_reservation(session, src_id, user_id)
            if dst_id:
                logger.debug("[CLIENT] cancelling locker reservation for dest cell %s", dst_id)
                self.db.cancel_locker_reservation(session, dst_id, user_id)

            logger.info("[CLIENT] order %s cancelled successfully", order_id)
            return True, ""
            
        except Exception as e:
            logger.error("[CLIENT] failed to cancel order %s: %s", order_id, str(e))
            return False, str(e)

    
# =========================================================
# RECIPIENT
# =========================================================

class RecipientActions:
    """Действия получателя."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def open_cell_for_recipient(self, session, order_id, user_id):
        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            cell_id = ctx.get("cell_id")
            if not cell_id:
                return False, "CELL_NOT_FOUND"
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            self.db.order_pickup_by_recipient(session, order_id, user_id)
            return True, ""
        except Exception as e:
            logger.error("[RECIPIENT] open_cell_for_recipient failed: %s", e)
            return False, str(e)

    def close_cell_for_recipient(self, session, order_id, user_id):
        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            cell_id = ctx.get("cell_id")
            if not cell_id:
                return False, "CELL_NOT_FOUND"
            self.db.order_mark_delivered_parcel(session, order_id, user_id)
            self.db.close_locker_pickup(session, cell_id, user_id)
            return True, ""
        except Exception as e:
            logger.error("[RECIPIENT] close_cell_for_recipient failed: %s", e)
            return False, str(e)
    
# =========================================================
# DRIVER
# =========================================================

class DriverActions:
    """Действия водителя."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def _get_active_trip_for_driver(self, session: Session, driver_id: int) -> dict:
        trips = self.db.get_active_trips_for_driver(session, driver_id)
        if not trips:
            logger.error("[DRIVER] no active trip found for driver %s", driver_id)
            raise DbLayerError("Нет активного рейса у водителя")
        return trips[0]

    def _determine_intent(self, session: Session, cell_id: int, trip: dict) -> str:
        """
        Определяет назначение ячейки в рейсе: pickup или delivery.
        """
        locker_id = self.db.get_locker_id_by_cell(session, cell_id)

        if locker_id == trip["pickup_locker_id"]:
            return "pickup"
        if locker_id == trip["delivery_locker_id"]:
            return "delivery"

        logger.error("[DRIVER] cell_id=%s не относится к рейсу trip_id=%s", cell_id, trip["id"])
        raise DbLayerError("Ячейка не относится к рейсу")

    def open_cell_for_driver(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[DRIVER] open_cell cell=%s user=%s", cell_id, user_id)

        try:
            # Получаем контекст для ячейки (он вернёт order_id, leg)
            ctx = self.db.get_context_for_entity(session, "locker", cell_id)
            order_id = ctx["order_id"]
            leg = ctx["leg"]
            if not order_id or not leg:
                return False, "CELL_NOT_LINKED_TO_ORDER"

            # Открываем ячейку
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")

            # Обновляем статус заказа в зависимости от leg
            if leg == "pickup":
                self.db.order_mark_parcel_submitted(session, order_id, user_id)
            elif leg == "delivery":
                self.db.order_arrive_at_post2(session, order_id, user_id)

            logger.info("[DRIVER] cell %s opened successfully", cell_id)
            return True, ""

        except Exception as e:
            logger.error("[DRIVER] open_cell_for_driver failed: %s", str(e))
            return False, str(e)

    def close_cell_for_driver(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[DRIVER] close_cell cell=%s user=%s", cell_id, user_id)

        try:
            ctx = self.db.get_context_for_entity(session, "locker", cell_id)
            order_id = ctx["order_id"]
            leg = ctx["leg"]
            if not order_id or not leg:
                # Если ячейка не привязана к заказу, просто закрываем
                self.db.close_locker(session, cell_id, user_id)
                return True, ""

            if leg == "pickup":
                self.db.close_locker_pickup(session, cell_id, user_id)
                self.db.order_pickup_by_driver(session, order_id, user_id)
            elif leg == "delivery":
                self.db.order_confirm_post2(session, order_id, user_id)
                self.db.close_locker(session, cell_id, user_id)
            else:
                self.db.close_locker(session, cell_id, user_id)

            logger.info("[DRIVER] cell %s closed successfully", cell_id)
            return True, ""

        except Exception as e:
            logger.error("[DRIVER] close_cell_for_driver failed: %s", str(e))
            return False, str(e)
    
    def start_trip(
        self,
        session: Session,
        direction_id: int,
        user_id: int,
        order_ids: List[int]
    ) -> Tuple[bool, Optional[int], str]:
        """
        Создаёт рейс, привязывает заказы и выполняет FSM-переходы.
        Возвращает (success, trip_id, message).
        """
        logger.info(
            "[DriverActions] start_trip: direction_id=%s, user_id=%s, orders=%d",
            direction_id, user_id, len(order_ids)
        )
        try:
            # 1. Создание рейса и привязка заказов
            trip_id = self.db.create_trip_for_direction(session, direction_id, user_id, order_ids)
            logger.info("[DriverActions] created trip_id=%s", trip_id)

            # 2. FSM-переход рейса
            self.db.start_trip(session, trip_id, user_id)
            logger.info("[DriverActions] trip %s transitioned to trip_in_progress", trip_id)

            # 3. FSM-переход для каждого заказа
            for order_id in order_ids:
                self.db.order_start_transit(session, order_id, user_id)
                logger.debug("[DriverActions] order %s transitioned to order_in_transit_to_post2", order_id)

            logger.info("[DriverActions] start_trip COMPLETED: trip_id=%s, orders=%d", trip_id, len(order_ids))
            return True, trip_id, f"Рейс {trip_id} начат: {len(order_ids)} заказов в транзите"
        except Exception as e:
            logger.exception("[DriverActions] start_trip failed")
            return False, None, f"START_TRIP_FAILED: {e}"

    def arrive_at_destination(
        self,
        session: Session,
        trip_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[DRIVER] arrive trip=%s user=%s", trip_id, user_id)

        try:
            self.db.trip_end_delivery(session, trip_id, user_id)
            logger.debug("[DRIVER] delivery ended for trip %s", trip_id)

            order_ids = self.db.get_orders_in_trip(session, trip_id)
            logger.debug("[DRIVER] found %s orders in trip %s for arrival processing", len(order_ids), trip_id)
            
            for order_id in order_ids:
                logger.info("[DRIVER] updating order %s to arrive at post2", order_id)
                self.db.order_arrive_at_post2(session, order_id, user_id)

            logger.info("[DRIVER] arrival processed for trip %s with %s orders", trip_id, len(order_ids))
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to process arrival for trip %s: %s", trip_id, str(e))
            return False, str(e)

    def cancel_trip(self, session: Session, trip_id: int, user_id: int) -> Tuple[bool, str]:
        """Отмена рейса водителем (из trip_assigned или trip_in_progress)."""
        logger.info("[DRIVER] cancel_trip trip_id=%s user_id=%s", trip_id, user_id)

        try:
            # Получаем текущий статус рейса
            trip = self.db.get_trip(session, trip_id)
            if not trip:
                return False, "TRIP_NOT_FOUND"

            current_status = trip.get("status")
            logger.info("[DRIVER] current trip status: %s", current_status)

            # Разрешаем отмену только из разрешённых статусов
            if current_status not in ("trip_assigned", "trip_in_progress"):
                return False, f"CANNOT_CANCEL_FROM_{current_status}"

            # Выполняем FSM переход
            success = self.db.trip_cancel(session, trip_id, user_id)

            if success:
                logger.info("[DRIVER] cancel_trip COMPLETED: trip_id=%s (was %s)", trip_id, current_status)
                return True, ""
            else:
                return False, "FSM_CANCEL_FAILED"

        except Exception as e:
            logger.error("[DRIVER] cancel_trip failed: %s", e)
            return False, str(e)

    def complete_trip(self, session: Session, trip_id: int, user_id: int) -> Tuple[bool, str]:
        logger.info("[DriverActions] complete_trip: trip_id=%s, user_id=%s", trip_id, user_id)
        try:
            self.db.complete_trip(session, trip_id, user_id)
            logger.info("[DriverActions] complete_trip: trip %s transitioned to trip_completed", trip_id)
            return True, f"Рейс {trip_id} завершён"
        except Exception as e:
            logger.exception("[DriverActions] complete_trip failed")
            return False, f"COMPLETE_TRIP_FAILED: {e}"

# =========================================================
# COURIER
# =========================================================

class CourierActions:
    """Действия курьера."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def open_cell(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[COURIER] open_cell order=%s user=%s", order_id, user_id)

        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            leg = ctx.get("leg")
            cell_id = ctx.get("cell_id")
            if not leg or not cell_id:
                return False, "UNKNOWN_LEG_OR_CELL"

            if leg == "pickup":
                self.db.order_courier1_pickup_parcel(session, order_id, user_id)
            else:
                self.db.order_courier2_pickup_parcel(session, order_id, user_id)

            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.info("[COURIER] cell %s opened for order %s", cell_id, order_id)
            return True, ""

        except Exception as e:
            logger.error("[COURIER] open_cell failed: %s", str(e))
            return False, str(e)

    def close_cell(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[COURIER] close_cell order=%s user=%s", order_id, user_id)

        try:
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            leg = ctx.get("leg")
            cell_id = ctx.get("cell_id")
            if not leg or not cell_id:
                return False, "UNKNOWN_LEG_OR_CELL"

            if leg == "pickup":
                self.db.order_confirm_parcel_in(session, order_id, user_id)
                self.db.close_locker(session, cell_id, user_id)
            else:
                self.db.order_courier2_delivered_parcel(session, order_id, user_id)
                self.db.close_locker_pickup(session, cell_id, user_id)

            logger.info("[COURIER] cell %s closed for order %s", cell_id, order_id)
            return True, ""

        except Exception as e:
            logger.error("[COURIER] close_cell failed: %s", str(e))
            return False, str(e)

    def cancel_order(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[COURIER] cancel order=%s user=%s", order_id, user_id)

        try:
            order = self.db.get_order(session, order_id)
            if not order:
                logger.warning("[COURIER] order %s not found", order_id)
                return False, "ORDER_NOT_FOUND"

            status = order["status"]
            logger.debug("[COURIER] order %s current status: %s", order_id, status)

            if status == "order_courier1_assigned":
                logger.info("[COURIER] cancelling courier1 assignment for order %s", order_id)
                self.db.order_courier1_cancel(session, order_id, user_id)
                self.db.clear_courier_from_stage_order(session, order_id, "pickup", user_id)

            elif status == "order_courier2_assigned":
                logger.info("[COURIER] cancelling courier2 assignment for order %s", order_id)
                self.db.order_courier2_cancel(session, order_id, user_id)
                self.db.clear_courier_from_stage_order(session, order_id, "delivery", user_id)

            else:
                logger.warning("[COURIER] cannot cancel order %s from status %s", order_id, status)
                return False, f"CANNOT_CANCEL_FROM_{status}"

            logger.info("[COURIER] order %s cancelled successfully", order_id)
            return True, ""
            
        except Exception as e:
            logger.error("[COURIER] failed to cancel order %s: %s", order_id, str(e))
            return False, str(e)
    
    def confirm_delivery_with_code(
        self,
        session: Session,
        order_id: int,
        user_id: int,
        pin: str
    ) -> Tuple[bool, str]:
        """
        Курьер2 подтверждает доставку с кодом от получателя.
        """
        logger.info("[COURIER] confirm_delivery_with_code order=%s user=%s", order_id, user_id)
        
        try:
            # FSM переход: order_courier2_parcel_delivered → order_completed
            self.db.order_recipient_confirmed(session, order_id, user_id)
            logger.info("[COURIER] order %s completed successfully with code confirmation", order_id)
            return True, ""
        except Exception as e:
            logger.error("[COURIER] confirm_delivery_with_code failed: %s", e)
            return False, str(e)

# ================= РАБОТА ОПЕРАТОРА =====================
class OperatorActions:
    """Действия оператора: технические операции с заказами и ячейками."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def _get_source_cell_id(self, session: Session, order_id: int) -> int:
        """Получить source_cell_id заказа."""
        order = self.db.get_order(session, order_id)
        if not order or not order.get("source_cell_id"):
            logger.error("[OPERATOR] source_cell_id not found for order %s", order_id)
            raise DbLayerError(f"Нет source_cell_id для заказа {order_id}")
        return order["source_cell_id"]

    def _get_dest_cell_id(self, session: Session, order_id: int) -> int:
        """Получить dest_cell_id заказа."""
        order = self.db.get_order(session, order_id)
        if not order or not order.get("dest_cell_id"):
            logger.error("[OPERATOR] dest_cell_id not found for order %s", order_id)
            raise DbLayerError(f"Нет dest_cell_id для заказа {order_id}")
        return order["dest_cell_id"]

    def open_cell_for_operator(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Оператор открывает ячейку (по умолчанию source_cell_id).
        """
        logger.info("[OPERATOR] open_cell order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[OPERATOR] opening source cell %s for order %s", cell_id, order_id)
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.info("[OPERATOR] cell %s opened successfully for order %s", cell_id, order_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to open cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def close_cell_for_operator(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Оператор закрывает ячейку (по умолчанию source_cell_id).
        """
        logger.info("[OPERATOR] close_cell order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[OPERATOR] closing source cell %s for order %s", cell_id, order_id)
            self.db.close_locker(session, cell_id, user_id)
            logger.info("[OPERATOR] cell %s closed successfully for order %s", cell_id, order_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to close cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def force_cancel_order(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Принудительно отменяет заказ оператором.
        """
        logger.warning("[OPERATOR] force_cancel_order order=%s user=%s", order_id, user_id)

        try:
            self.db.order_cancel_reservation(session, order_id, user_id)
            logger.info("[OPERATOR] order %s force cancelled successfully", order_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to force cancel order %s: %s", order_id, str(e))
            return False, str(e)
    
    def reset_locker(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Сброс состояния ячейки (locker_error → locker_free).
        """
        logger.info("[OPERATOR] reset_locker cell=%s user=%s", cell_id, user_id)

        try:
            self.db.reset_locker(session, cell_id, user_id)
            logger.info("[OPERATOR] cell %s reset successfully", cell_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to reset cell %s: %s", cell_id, str(e))
            return False, str(e)

    def set_locker_maintenance(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Поставить ячейку на обслуживание.
        """
        logger.info("[OPERATOR] set_locker_maintenance cell=%s user=%s", cell_id, user_id)

        try:
            self.db.set_locker_maintenance(session, cell_id, user_id)
            logger.info("[OPERATOR] cell %s set to maintenance successfully", cell_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to set cell %s to maintenance: %s", cell_id, str(e))
            return False, str(e)

# ==================== Access Code ====================
class AccessCodeActions:
    def __init__(self, db: DatabaseLayer):
        self.db = db

    def request_access_code(
        self,
        session: Session,
        order_id: int,
        user_id: int,
        leg: str
    ) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(session, order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"

            # Проверка, разрешён ли код при текущем статусе
            allowed_statuses = {
                "pickup": ["order_created", "order_courier1_assigned", "order_parcel_confirmed"],
                "delivery": ["order_in_transit_to_post2", "order_courier2_assigned",
                             "order_courier2_parcel_delivered", "order_parcel_confirmed_post2"]
            }
            if order["status"] not in allowed_statuses[leg]:
                return False, f"CODE_NOT_ALLOWED_IN_{order['status']}"

            # Лимит запросов
            recent = self.db.count_recent_access_code_requests(session, order_id, leg, 15)
            if recent >= 3:
                return False, "TOO_MANY_CODE_REQUESTS"

            # Получаем cell_id через контекст
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            cell_id = ctx.get("cell_id")
            if not cell_id:
                return False, "CELL_ID_MISSING"

            # Генерация и отправка PIN
            pin, token_id = self.db.generate_and_store_access_token(
                session, order_id, leg, cell_id, user_id, expires_minutes=15
            )
            self.db.send_code_to_user(session, user_id, pin)

            logger.info("Access code issued: order=%s, leg=%s, user=%s, token=%s", order_id, leg, user_id, token_id)
            return True, ""

        except Exception as e:
            logger.exception("request_access_code failed for order %s: %s", order_id, e)
            return False, str(e)

# ==================== РЕЙСЫ ====================
class TripActions:
    """Действия, связанные с управлением рейсами."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def bind_order_to_trip(
        self,
        session: Session,
        order_id: int
    ) -> Tuple[bool, str]:
        """
        Привязывает заказы к направлению.
        """
        order = self.db.get_order(session, order_id)
        if not order or order["status"] != "order_parcel_confirmed":
            return False, "ORDER_NOT_CONFIRMED"
        
        # Получаем данные маршрута
        pickup_locker_id = self.db.get_locker_id_by_cell(session, order["source_cell_id"])
        delivery_locker_id = self.db.get_locker_id_by_cell(session, order["dest_cell_id"])
        from_city = self.db.get_locker_city_by_cell(session, order["source_cell_id"])
        to_city = self.db.get_locker_city_by_cell(session, order["dest_cell_id"])
        
        # Привязка к направлению
        direction_id, success, msg = self.db.assign_order_to_direction(
            session,
            order_id=order_id,
            from_city=from_city,
            to_city=to_city,
            pickup_locker_id=pickup_locker_id,
            delivery_locker_id=delivery_locker_id,
        )
        
        if not success:
            return False, msg
        
        logger.info(f"bind_order_to_direction: order={order_id}, direction={direction_id}")
        return True, "Заказ привязан к направлению"

    def reserve_slot(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
        capacity: int,
    ) -> Tuple[bool, str]:
        """
        Водитель резервирует слот в направлении.
        """
        logger.info(
            "[TripActions] reserve_slot: direction_id=%s, driver_user_id=%s, capacity=%s",
            direction_id, driver_user_id, capacity
        )
        
        if capacity <= 0:
            logger.error("[TripActions] reserve_slot: invalid capacity=%s", capacity)
            return False, "INVALID_CAPACITY"
        
        # Резерв заказов (атомарный UPDATE + INSERT в driver_reservations)
        success, reserved_count, msg = self.db.reserve_orders_for_direction(
            session, direction_id, driver_user_id, capacity
        )
        
        if not success:
            logger.error("[TripActions] reserve_slot FAILED: direction_id=%s, error=%s", direction_id, msg)
            return False, msg
        
        logger.info(
            "[TripActions] reserve_slot COMPLETED: direction_id=%s, driver_user_id=%s, reserved=%s",
            direction_id, driver_user_id, reserved_count
        )
        
        return True, "Слот зарезервирован: %s заказов" % reserved_count

    def start_loading(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, str]:
        """
        Водитель начинает погрузку для КОНКРЕТНОГО резерва.
        """
        logger.info(
            "[TripActions] start_loading: reservation_id=%s, driver_user_id=%s",
            reservation_id, driver_user_id
        )
        
        try:
            self.db.driver_reservation_start_loading(
                session, reservation_id, driver_user_id
            )
            
            logger.info(
                "[TripActions] start_loading COMPLETED: reservation_id=%s",
                reservation_id
            )
            
            return True, "Погрузка начата"
            
        except Exception as e:
            logger.exception("[TripActions] start_loading failed")
            return False, f"START_LOADING_FAILED: {e}"

    def complete_loading(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, str]:
        """
        Водитель завершает погрузку по направлению.
        1. Проверяет что нет открытых ячеек
        2. Находит ВСЕ активные резервы водителя на направлении
        3. Определяет фактически забранные заказы
        4. Проверяет что есть хотя бы 1 забранный заказ
        5. Освобождает не забранные заказы (возврат в пул направления)
        6. Обновляет FSM reservation_loading → reservation_completed
        """
        logger.info(
            "[TripActions] complete_loading: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        
        try:
            # 1. ПРОВЕРКА ОТКРЫТЫХ ЯЧЕЕК
            has_open_cells, open_cell_ids = self.db.check_open_cells_for_driver_reservations(
                session, direction_id, driver_user_id
            )
            if has_open_cells:
                return False, f"OPEN_CELLS_DETECTED: Ячейки {open_cell_ids} не закрыты"
            
            # 2. Находим ВСЕ активные резервы водителя на направлении
            reservation_ids = self.db.get_driver_active_reservations(
                session, direction_id, driver_user_id
            )
            if not reservation_ids:
                return False, "NO_ACTIVE_RESERVATIONS"
            
            logger.info(
                "[TripActions] complete_loading: found %d reservations for driver %s",
                len(reservation_ids), driver_user_id
            )
            
            # 3. Определяем забранные заказы
            picked_order_ids = self.db.get_picked_orders_by_driver_and_direction(
                session, direction_id, driver_user_id
            )
            
            # 4. ПРОВЕРКА: >= 1 заказа
            if not picked_order_ids:
                return False, "NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов"

            # 6. Освобождаем не забранные заказы (возврат в пул)
            released_count = self.db.release_unpicked_orders_by_driver_and_direction(
                session, direction_id, driver_user_id, picked_order_ids
            )
            
            logger.info(
                "[TripActions] complete_loading: released %d unpicked orders",
                released_count
            )
            
            # 7. FSM переход для КАЖДОГО резерва: reservation_loading → reservation_completed
            for reservation_id in reservation_ids:
                self.db.driver_reservation_complete_loading(
                    session, reservation_id, driver_user_id
                )
            
            logger.info(
                "[TripActions] complete_loading COMPLETED: direction_id=%s, driver_user_id=%s, picked=%d, released=%d",
                direction_id, driver_user_id, len(picked_order_ids), released_count
            )
            
            return True, "Погрузка завершена: %d заказов готово к рейсу" % len(picked_order_ids)
            
        except Exception as e:
            logger.exception("[TripActions] complete_loading failed")
            return False, "COMPLETE_LOADING_FAILED: %s" % e

    # ===================== отмена резерва =========================
    def cancel_reservation(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, str]:
        """
        Отмена резерва водителем.
        
        1. Проверяет что все заказы в статусе order_parcel_confirmed
        2. Возвращает заказы в пул направления
        3. Делает FSM переход reservation_loading → reservation_cancelled
        """
        logger.info(
            "[TripActions] cancel_reservation: reservation_id=%s, driver_user_id=%s",
            reservation_id, driver_user_id
        )
        
        try:
            # 1. Проверка что можно отменить
            can_cancel, blocked_ids, error = self.db.validate_reservation_for_cancellation(
                session, reservation_id
            )
            
            if not can_cancel:
                logger.warning("[TripActions] cancel_reservation blocked: %s", error)
                return False, error
            
            # 2. Освобождаем заказы (возврат в пул)
            released_count = self.db.release_orders_from_reservation(
                session, reservation_id
            )
            
            logger.info("[TripActions] cancel_reservation: released %d orders", released_count)
            
            # 3. FSM переход reservation_loading → reservation_cancelled
            self.db.cancel_driver_reservation(session, reservation_id, driver_user_id)
            
            logger.info(
                "[TripActions] cancel_reservation COMPLETED: reservation_id=%s, released=%d",
                reservation_id, released_count
            )
            
            return True, "Резерв отменён: %d заказов возвращено в пул" % released_count
            
        except Exception as e:
            logger.exception("[TripActions] cancel_reservation failed")
            return False, "CANCEL_RESERVATION_FAILED: %s" % e

# ================= Автоматизация типовых ошибок =====================
class ReportErrorActions:
    """Централизованная обработка типовых проблем."""

    SCENARIO_DESCRIPTIONS = {
        "order": [
            {"error_type": "parcel_missing",         "label": "Посылка пропала",
             "roles": ["driver", "courier", "recipient", "client"]},
            {"error_type": "parcel_damaged",         "label": "Посылка повреждена",
             "roles": ["driver", "courier", "recipient", "client"]},
            {"error_type": "wrong_parcel",           "label": "В ячейке чужая посылка",
             "roles": ["driver", "courier", "recipient", "client"]},
        ],
        "locker": [
            {"error_type": "locker_failed_to_open",  "label": "Ячейка не открылась",
             "roles": ["client", "courier", "driver", "recipient", "operator"]},
            {"error_type": "locker_failed_to_close", "label": "Ячейка не закрылась",
             "roles": ["client", "courier", "driver", "recipient", "operator"]},
        ],
        "trip": [
            {"error_type": "trip_breakdown",         "label": "Поломка рейса",
             "roles": ["driver"]},
        ],
    }

    def __init__(self, db: DatabaseLayer, order_mapping):
        self.db = db
        self.order_mapping = order_mapping
        self._scenario_map = {
            # Проблемы с ячейками
            "locker_failed_to_open":   self.resolve_locker_issue,
            "locker_failed_to_close":  self.resolve_locker_issue,
            # Проблемы с посылками
            "parcel_missing":          self.resolve_parcel_missing,
            "parcel_damaged":          self.resolve_parcel_damaged,
            "wrong_parcel":            self.resolve_parcel_damaged,
            # Проблемы с рейсами
            "trip_breakdown":          self.resolve_trip_breakdown,
        }

    def get_supported_scenarios(role: str = None, entity_type: str = None) -> list[dict]:
        """Возвращает список сценариев с учётом фильтров по роли и типу сущности."""
        scenarios = []
        # Если entity_type задан, берём только его раздел, иначе все разделы
        entities = [entity_type] if entity_type else ReportErrorActions.SCENARIO_DESCRIPTIONS.keys()

        for ent in entities:
            for item in ReportErrorActions.SCENARIO_DESCRIPTIONS.get(ent, []):
                # Фильтр по роли
                if role and role not in item["roles"]:
                    continue
                # Добавляем плоский объект, готовый для фронта
                scenarios.append({
                    "error_type": item["error_type"],
                    "label": item["label"],
                    "entity_type": ent
                })
        return scenarios

    def report_error(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        user_id: int,
        error_type: str,
        user_role: str,
        description: str = ""
    ) -> Tuple[bool, str]:
        """Единая точка входа для всех жалоб."""
        logger.info(
            "[ReportErrorActions] report_error: role=%s, entity=%s:%s, error=%s",
            user_role, entity_type, entity_id, error_type
        )

        handler = self._scenario_map.get(error_type)
        if not handler:
            logger.warning("[ReportErrorActions] unsupported error_type: %s", error_type)
            return False, f"UNSUPPORTED_ERROR_TYPE: {error_type}"

        try:
            return handler(
                session, entity_type, entity_id, user_id, error_type,
                user_role, description
            )
        except DbLayerError as e:
            logger.error("[ReportErrorActions] DbLayerError: %s", e)
            return False, f"DB_ERROR: {e}"
        except Exception as e:
            logger.exception("[ReportErrorActions] Unexpected exception")
            return False, f"INTERNAL_ERROR: {e}"

    # ------------------------------------------------------------------
    # Сценарий: проблемы с ячейкой
    # ------------------------------------------------------------------
    def resolve_locker_issue(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        user_id: int,
        error_type: str,
        user_role: str,
        description: str
    ) -> Tuple[bool, str]:
        """Любые неисправности ячейки: автоматическое перебронирование или ручное вмешательство."""
        # 1. Получаем необходимые данные
        if entity_type == "locker":
            cell_id = entity_id
            order_id = self.db.get_order_id_by_cell_id(session, cell_id)
            if not order_id:
                return False, "CELL_NOT_LINKED_TO_ORDER"
            order = self.db.get_order(session, order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            leg = "pickup" if cell_id == order["source_cell_id"] else "delivery"
        elif entity_type == "order":
            order_id = entity_id
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            leg = ctx.get("leg")
            cell_id = ctx.get("cell_id")
            if not leg or not cell_id:
                return False, "INCOMPLETE_ENTITY_CONTEXT"
        else:
            return False, "ENTITY_TYPE_MUST_BE_ORDER_OR_LOCKER"

        logger.info(
            "[resolve_locker_issue] order=%s, cell=%s, leg=%s, role=%s, error=%s",
            order_id, cell_id, leg, user_role, error_type
        )

        # 2. Определяем контекст: забираем посылку или кладём
        is_retrieval = (
            (user_role == "driver" and leg == "pickup") or
            (user_role == "courier" and leg == "delivery") or
            (user_role == "recipient" and leg == "delivery")
        )

        try:
            if is_retrieval:
                self.db.set_locker_maintenance(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                self.db.create_order_issue(
                    session,
                    order_id=order_id,
                    trip_id=None,
                    user_id=user_id,
                    issue_type=error_type,
                    description=f"Ячейка {cell_id} не открылась при заборе посылки ({error_type}). Требуется ручное вмешательство. {description}"
                )
                return True, "MANUAL_INTERVENTION_REQUIRED"

            # ---------- DEPOSIT ----------
            self.db.set_locker_maintenance(session, cell_id, user_id)
            self.db.detach_cell_from_order(session, cell_id)

            new_cell_id = self.db.find_and_reserve_alternative_cell(
                session, order_id, broken_cell_id=cell_id, leg=leg
            )

            if new_cell_id:
                self.db.create_order_issue(
                    session,
                    order_id=order_id,
                    trip_id=None,
                    user_id=user_id,
                    issue_type="auto_rebooked",
                    description=f"Ячейка {cell_id} ({error_type}) заменена на {new_cell_id}. {description}"
                )
                return True, f"Ваша новая ячейка: {new_cell_id}"

            # Нет свободной ячейки
            self.db.order_request_manual_intervention(session, order_id, user_id)
            self.db.create_order_issue(
                session,
                order_id=order_id,
                trip_id=None,
                user_id=user_id,
                issue_type=error_type,
                description=f"Ячейка {cell_id} ({error_type}), свободных нет. {description}"
            )
            return True, "NO_FREE_CELL"

        except DbLayerError as e:
            logger.error("[resolve_locker_issue] DbLayerError: %s", e)
            return False, f"DB_ERROR: {e}"
        except Exception as e:
            logger.exception("[resolve_locker_issue] Unexpected error")
            return False, f"INTERNAL_ERROR: {e}"

    # ------------------------------------------------------------------
    # Сценарий: посылка пропала
    # ------------------------------------------------------------------
    def resolve_parcel_missing(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        user_id: int,
        error_type: str,
        user_role: str,
        description: str
    ) -> Tuple[bool, str]:
        if entity_type == "order":
            order_id = entity_id
            ctx = self.db.get_context_for_entity(session, "order", order_id)
            leg = ctx.get("leg")
            cell_id = ctx.get("cell_id")
            if not leg or not cell_id:
                return False, "INCOMPLETE_ENTITY_CONTEXT"
        elif entity_type == "locker":
            cell_id = entity_id
            order_id = self.db.get_order_id_by_cell_id(session, cell_id)
            if not order_id:
                return False, "CELL_NOT_LINKED_TO_ORDER"
        else:
            return False, "ENTITY_TYPE_MUST_BE_ORDER_OR_LOCKER"

        logger.info("[resolve_parcel_missing] order=%s, cell=%s, user=%s, role=%s",
                    order_id, cell_id, user_id, user_role)

        try:
            self.db.reset_locker(session, cell_id, user_id)
            self.db.order_request_manual_intervention(session, order_id, user_id)
            if user_role in ("driver", "courier"):
                self.order_mapping.complete_suborder_in_core(session, order_id, user_id)
            self.db.create_order_issue(
                session, order_id=order_id, trip_id=None, user_id=user_id,
                issue_type=error_type,
                description=f"Посылка пропала в ячейке {cell_id}. {description}"
            )
            return True, ""
        except Exception as e:
            logger.exception("[resolve_parcel_missing] failed")
            return False, str(e)

    # ------------------------------------------------------------------
    # Сценарий: посылка повреждена (или не та)
    # ------------------------------------------------------------------
    def resolve_parcel_damaged(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        user_id: int,
        error_type: str,
        user_role: str,
        description: str
    ) -> Tuple[bool, str]:
        if entity_type == "order":
            order_id = entity_id
        elif entity_type == "locker":
            order_id = self.db.get_order_id_by_cell_id(session, entity_id)
            if not order_id:
                return False, "CELL_NOT_LINKED_TO_ORDER"
        else:
            return False, "ENTITY_TYPE_MUST_BE_ORDER_OR_LOCKER"

        logger.info("[resolve_parcel_damaged] order=%s, user=%s, role=%s",
                    order_id, user_id, user_role)

        try:
            self.db.order_request_manual_intervention(session, order_id, user_id)
            if user_role in ("driver", "courier"):
                self.order_mapping.complete_suborder_in_core(session, order_id, user_id)
            self.db.create_order_issue(
                session, order_id=order_id, trip_id=None, user_id=user_id,
                issue_type=error_type,
                description=f"Посылка повреждена. {description}"
            )
            return True, ""
        except Exception as e:
            logger.exception("[resolve_parcel_damaged] failed")
            return False, str(e)

    # ------------------------------------------------------------------
    # Сценарий: поломка рейса
    # ------------------------------------------------------------------
    def resolve_trip_breakdown(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        user_id: int,
        error_type: str,
        user_role: str,
        description: str
    ) -> Tuple[bool, str]:
        if entity_type != "trip":
            return False, "ENTITY_TYPE_MUST_BE_TRIP"

        trip_id = entity_id
        trip = self.db.get_trip(session, trip_id)
        if not trip:
            return False, "TRIP_NOT_FOUND"

        driver_id = trip.get("driver_user_id")
        if not driver_id:
            return False, "NO_DRIVER_ASSIGNED"

        logger.info("[resolve_trip_breakdown] trip=%s, driver=%s, user=%s, role=%s",
                    trip_id, driver_id, user_id, user_role)

        try:
            order_ids = self.db.get_orders_in_trip(session, trip_id)
            if not order_ids:
                return False, "NO_ORDERS_IN_TRIP"

            # 1. Core – снять подзаказы водителя
            for order_id in order_ids:
                self.order_mapping.remove_suborder_performer_in_core(
                    session,
                    local_order_id=order_id,
                    performer_local_user_id=driver_id,
                    user_id=driver_id,
                    reason=f"trip_breakdown: {description}"
                )

            # 2. FSM – снять водителя с рейса и заказов
            self.db.remove_driver_from_trip(session, trip_id, user_id)
            self.db.clear_driver_from_stage_orders(session, order_ids)
            self.db.trip_request_manual_intervention(session, trip_id, user_id)

            # 3. Инцидент
            self.db.create_order_issue(
                session,
                order_id=None,
                trip_id=trip_id,
                user_id=user_id,
                issue_type=error_type,
                description=f"Рейс {trip_id} сломан, водитель снят. {description}"
            )
            return True, ""
        except Exception as e:
            logger.exception("[resolve_trip_breakdown] failed")
            return False, str(e)
            
# ================== Очистка ячеек постаматов ===========================
class LockerActions:
    """Действия для управления ячейками (системные операции)."""
    def __init__(self, db: DatabaseLayer):
        self.db = db     
    
    def cleanup_closed_empty_lockers(
        self,
        session: Session,
        threshold_minutes: int = 30,
        user_id: int = 999999
    ) -> Tuple[bool, str]:
        logger.debug(
            f"[LockerActions] cleanup_closed_empty_lockers: threshold={threshold_minutes} мин"
        )
        
        cleaned_count, error = self.db.cleanup_closed_empty_lockers(
            session=session,
            threshold_minutes=threshold_minutes,
            user_id=user_id
        )
         
        if error:
            logger.error(f"[LockerActions] cleanup_closed_empty_lockers FAILED: {error}")
            return False, error
        
        logger.debug(
            f"[LockerActions] cleanup_closed_empty_lockers COMPLETED: очищено {cleaned_count} ячеек"
        )
        return True, f"Очищено {cleaned_count} ячеек"
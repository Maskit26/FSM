# fsm_actions.py

from typing import Tuple, Optional
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

    def create_order_from_request(
        self,
        session: Session,
        request_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        logger.info("[ORDER_CREATE] start request_id=%s", request_id)

        try:
            req = self.db.get_order_request(session, request_id)
            if not req or req["status"] != "PENDING":
                return False, None, "REQ_NOT_FOUND_OR_INVALID"

            client_user_id = req["client_user_id"]
            if not client_user_id:
                return False, None, "INVALID_DATA"

            parcel_type = req["parcel_type"]
            recipient_user_id = req["recipient_user_id"]
            cell_size = req["cell_size"]
            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]

            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            # Получаем город клиента и получателя
            client_city = self.db.get_user_city(session, client_user_id)
            if not recipient_user_id:
                return False, None, "RECIPIENT_USER_ID_REQUIRED"

            recipient_city = self.db.get_user_city(session, recipient_user_id)

            # Определяем маршрут: от клиента → к получателю
            source_city = client_city
            dest_city = recipient_city

            # Запрещаем отправку в тот же город
            if source_city == dest_city:
                return False, None, f"SELF_CITY_NOT_ALLOWED: {source_city}"

            # 🔒 поиск + резерв ячеек
            ok, src_id, dst_id = self.db.find_and_reserve_cells_by_cities(
                session, source_city, dest_city, cell_size
            )
            if not ok:
                logger.info("[ORDER_CREATE] no free cells in route %s → %s", source_city, dest_city)
                return False, None, "NO_FREE_CELLS"

            # 🧾 создание заказа
            order_id = self.db.create_order_record(
                session,
                description=description,
                pickup_type=pickup_type,
                delivery_type=delivery_type,
                client_user_id=client_user_id,
                recipient_user_id=recipient_user_id,
                source_cell_id=src_id,
                dest_cell_id=dst_id,
            )

            # привязываем ячейки к заказу
            self.db.bind_cells_for_order(session, order_id, src_id, dst_id)

            # ✅ СОЗДАЁМ stage_orders с trip_id
            self.db.create_stage_order(
                session,
                trip_id=None, 
                order_id=order_id,
                leg="pickup",
                courier_user_id=None,
            )
            self.db.create_stage_order(
                session,
                trip_id=None,
                order_id=order_id,
                leg="delivery",
                courier_user_id=None,
            )

            logger.info("[ORDER_CREATE] success order_id=%s", order_id)
            return True, order_id, ""

        except DbLayerError:
            raise
        except Exception as e:
            logger.exception("create_order_from_request crash")
            raise DbLayerError(str(e))


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

    def assign_to_trip(
        self,
        session: Session,
        trip_id: int,
        executor_id: int,
        role: str
    ) -> bool:
        """
        Назначает водителя на рейс.
        """

        logger.info(
            "[ASSIGNMENT] assign_to_trip trip_id=%s executor=%s role=%s",
            trip_id,
            executor_id,
            role,
        )

        try:
            if role == "driver":
                self.db.set_driver_in_trip(session, trip_id, executor_id)
                self.db.driver_take_trip(session, trip_id, executor_id)
            else:
                logger.error("[ASSIGNMENT] unknown role for trip: %s", role)
                return False

            logger.info(
                "[ASSIGNMENT] assigned trip_id=%s driver=%s",
                trip_id,
                executor_id,
            )
            return True

        except Exception:
            logger.exception(
                "[ASSIGNMENT] assign_to_trip failed trip_id=%s", trip_id
            )
            return False


# =========== РАБОТА С ПОСТАМАТОМ ===========================

# =========================================================
# CLIENT
# =========================================================

class ClientActions:
    """Действия клиента (отправителя)."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def _get_source_cell_id(self, session: Session, order_id: int) -> int:
        """Получить source_cell_id заказа."""
        order = self.db.get_order(session, order_id)
        if not order or not order.get("source_cell_id"):
            logger.error("[CLIENT] source_cell_id not found for order %s", order_id)
            raise DbLayerError(f"Нет source_cell_id для заказа {order_id}")
        return order["source_cell_id"]

    def open_cell_for_client(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Клиент открывает ячейку отправки.

        FSM: locker_reserved → locker_opened
        """
        logger.info("[CLIENT] open_cell_for_client order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[CLIENT] opening source cell %s for order %s", cell_id, order_id)
            
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.info("[CLIENT] cell %s opened successfully for order %s", cell_id, order_id)
            
            return True, ""
        except Exception as e:
            logger.error("[CLIENT] failed to open cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def close_cell_for_client(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Клиент закрывает ячейку после помещения посылки.
        """
        logger.info("[CLIENT] close_cell_for_client order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[CLIENT] closing source cell %s for order %s", cell_id, order_id)
            
            self.db.order_confirm_parcel_in(session, order_id, user_id)
            self.db.close_locker(session, cell_id, user_id)
            
            logger.info("[CLIENT] cell %s closed successfully for order %s", cell_id, order_id)
            return True, ""
        except Exception as e:
            logger.error("[CLIENT] failed to close cell for order %s: %s", order_id, str(e))
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

    def report_error(
        self,
        session: Session,
        cell_id: int,
        order_id: int,
        user_id: int,
        error_type: str,
        trip_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Универсальный метод сообщения об ошибке клиентом.
        
        error_type: 'locker_failed_to_open' | 'locker_failed_to_close' | 'locker_not_closed' | 
                    'cancelled_by_client' | 'wrong_cell' | 'other'
        """
        logger.info("[CLIENT] report_error cell=%s order=%s type=%s", cell_id, order_id, error_type)

        try:
            if error_type == "locker_failed_to_open":
                logger.debug("[CLIENT] handling locker_failed_to_open")
                self.db.locker_report_failed_to_open(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_failed_to_close":
                logger.debug("[CLIENT] handling locker_failed_to_close")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_not_closed":
                logger.debug("[CLIENT] handling locker_not_closed")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "cancelled_by_client":
                logger.debug("[CLIENT] handling cancelled_by_client")
                self.db.order_cancel_reservation(session, order_id, user_id)
                
            elif error_type == "wrong_cell":
                logger.debug("[CLIENT] handling wrong_cell")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "other":
                logger.debug("[CLIENT] handling other")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            else:
                logger.warning("[CLIENT] unknown error_type=%s", error_type)
                return False, f"UNKNOWN_ERROR_TYPE:{error_type}"

            self.db.create_order_issue(
                session, order_id, trip_id, user_id, error_type, f"Client reported: {error_type}"
            )

            logger.info("[CLIENT] report_error completed successfully")
            return True, ""
            
        except Exception as e:
            logger.error("[CLIENT] report_error failed: %s", e)
            return False, str(e)


# =========================================================
# RECIPIENT
# =========================================================

class RecipientActions:
    """Действия получателя."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def _get_dest_cell_id(self, session: Session, order_id: int) -> int:
        order = self.db.get_order(session, order_id)
        if not order or not order.get("dest_cell_id"):
            logger.error("[RECIPIENT] dest_cell_id not found for order %s", order_id)
            raise DbLayerError(f"Нет dest_cell_id для заказа {order_id}")
        return order["dest_cell_id"]

    def open_cell_for_recipient(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Получатель открывает ячейку получения.
        """
        logger.info("[RECIPIENT] open_cell order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_dest_cell_id(session, order_id)
            logger.debug("[RECIPIENT] opening destination cell %s for order %s", cell_id, order_id)
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.info("[RECIPIENT] cell %s opened successfully for order %s", cell_id, order_id)
            return True, ""
        except Exception as e:
            logger.error("[RECIPIENT] failed to open cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def close_cell_for_recipient(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Получатель закрывает пустую ячейку.
        """
        logger.info("[RECIPIENT] close_cell order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_dest_cell_id(session, order_id)
            logger.debug("[RECIPIENT] closing destination cell %s for order %s", cell_id, order_id)
            self.db.close_locker_pickup(session, cell_id, user_id)
            logger.info("[RECIPIENT] cell %s closed successfully for order %s", cell_id, order_id)
            return True, ""
        except Exception as e:
            logger.error("[RECIPIENT] failed to close cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def report_error(
        self,
        session: Session,
        cell_id: int,
        order_id: int,
        user_id: int,
        error_type: str,
        trip_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Универсальный метод сообщения об ошибке получателем.
        
        error_type: 'locker_failed_to_open' | 'locker_failed_to_close' | 'locker_not_closed' | 
                    'parcel_missing' | 'parcel_damaged' | 'other'
        """
        logger.info("[RECIPIENT] report_error cell=%s order=%s type=%s", cell_id, order_id, error_type)

        try:
            if error_type == "locker_failed_to_open":
                logger.debug("[RECIPIENT] handling locker_failed_to_open")
                self.db.locker_report_failed_to_open(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_failed_to_close":
                logger.debug("[RECIPIENT] handling locker_failed_to_close")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_not_closed":
                logger.debug("[RECIPIENT] handling locker_not_closed")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "parcel_missing":
                logger.debug("[RECIPIENT] handling parcel_missing")
                self.db.order_report_parcel_missing(session, order_id, user_id)
                self.db.confirm_locker_parcel_not_found(session, cell_id, user_id)
                self.db.reset_locker(session, cell_id, user_id)
                
            elif error_type == "parcel_damaged":
                logger.debug("[RECIPIENT] handling parcel_damaged")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "other":
                logger.debug("[RECIPIENT] handling other")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            else:
                logger.warning("[RECIPIENT] unknown error_type=%s", error_type)
                return False, f"UNKNOWN_ERROR_TYPE:{error_type}"

            self.db.create_order_issue(
                session, order_id, trip_id, user_id, error_type, f"Recipient reported: {error_type}"
            )

            logger.info("[RECIPIENT] report_error completed successfully")
            return True, ""
            
        except Exception as e:
            logger.error("[RECIPIENT] report_error failed: %s", e)
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
        """
        Водитель открывает ячейку.
                
        """
        logger.info("[DRIVER] open_cell cell=%s user=%s", cell_id, user_id)

        try:
            # 1. Получаем order_id по cell_id
            order_id = self.db.get_order_id_by_cell_id(session, cell_id)
            if not order_id:
                raise DbLayerError(f"Ячейка {cell_id} не привязана ни к одному заказу")

            # 2. Получаем trip_id из stage_orders
            trip_id = self.db.get_trip_id_by_order_id(session, order_id)
            if not trip_id:
                raise DbLayerError(f"Заказ {order_id} не привязан к рейсу")

            # 3. Проверяем, что водитель назначен на этот рейс
            trip = self.db.get_trip(session, trip_id)
            if not trip or trip["driver_user_id"] != user_id:
                raise DbLayerError(f"Водитель {user_id} не назначен на рейс {trip_id}")

            # 4. Определяем intent: pickup или delivery
            order = self.db.get_order(session, order_id)
            if cell_id == order["source_cell_id"]:
                intent = "pickup"
            elif cell_id == order["dest_cell_id"]:
                intent = "delivery"
            else:
                raise DbLayerError(f"Ячейка {cell_id} не совпадает ни с source, ни с dest для заказа {order_id}")

            # 5. Открываем ячейку
            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.debug("[DRIVER] cell %s opened (Locker FSM)", cell_id)

            # 6. Order FSM
            if intent == "pickup":
                logger.info("[DRIVER] processing pickup for order %s", order_id)                
                self.db.order_mark_parcel_submitted(session, order_id, user_id)
            elif intent == "delivery":
                logger.info("[DRIVER] processing delivery for order %s", order_id)                
                self.db.order_arrive_at_post2(session, order_id, user_id)

            logger.info("[DRIVER] cell %s opened successfully", cell_id)
            return True, ""

        except Exception as e:
            logger.error("[DRIVER] failed to open cell %s: %s", cell_id, str(e))
            return False, str(e)

    def close_cell_for_driver(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Водитель закрывает ячейку. Логика основана на связке Cell -> Order -> Trip.
        """
        logger.info("[DRIVER] close_cell cell=%s user=%s", cell_id, user_id)

        try:
            # 1. Находим заказ по ячейке
            order_id = self.db.get_order_id_by_cell_id(session, cell_id)
            if not order_id:
                logger.warning("[DRIVER] cell %s not linked to any order, just closing", cell_id)
                self.db.close_locker(session, cell_id, user_id)
                return True, ""

            # 2. Находим рейс через заказ
            trip_id = self.db.get_trip_id_by_order_id(session, order_id)
            if not trip_id:
                raise DbLayerError(f"Заказ {order_id} не привязан к рейсу")

            # 3. Проверяем водителя и получаем данные рейса
            trip = self.db.get_trip(session, trip_id)
            if not trip or trip["driver_user_id"] != user_id:
                raise DbLayerError(f"Водитель {user_id} не назначен на рейс {trip_id} для ячейки {cell_id}")

            # 4. Получаем данные заказа для определения intent (pickup/delivery)
            order = self.db.get_order(session, order_id)
            if cell_id == order["source_cell_id"]:
                intent = "pickup"
            elif cell_id == order["dest_cell_id"]:
                intent = "delivery"
            else:
                intent = "unknown"

            logger.debug("[DRIVER] closing cell %s with intent %s for trip %s", cell_id, intent, trip_id)

            # 5. Обрабатываем бизнес-логику в зависимости от намерения
            if intent == "pickup":
                logger.info("[DRIVER] Finishing PICKUP: cell %s will be EMPTY", cell_id)                
                self.db.close_locker_pickup(session, cell_id, user_id)                
                self.db.order_pickup_by_driver(session, order_id, user_id)                

            elif intent == "delivery":
                logger.info("[DRIVER] Finishing DELIVERY: cell %s will be OCCUPIED", cell_id)                
                self.db.order_confirm_post2(session, order_id, user_id)
                self.db.close_locker(session, cell_id, user_id)
                
            else:                
                raise DbLayerError(f"Не удалось определить тип операции (pickup/delivery) для ячейки {cell_id}")
                
            return True, ""

        except Exception as e:
            logger.error("[DRIVER] failed to close cell %s for driver %s: %s", cell_id, user_id, str(e))
            return False, str(e)

    def report_error(
        self,
        session: Session,
        cell_id: int,
        order_id: int,
        user_id: int,
        error_type: str,
        trip_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Универсальный метод сообщения об ошибке водителем.
        
        error_type: 
        - Для locker: 'locker_failed_to_open' | 'locker_failed_to_close' | 'locker_not_closed'
        - Для order: 'parcel_missing' | 'parcel_damaged' | 'other'
        - Для trip: 'trip_breakdown' | 'trip_delayed' | 'trip_route_issue' | 'trip_manual_intervention'
        """
        logger.info("[DRIVER] report_error cell=%s order=%s trip=%s type=%s", cell_id, order_id, trip_id, error_type)

        try:
            # === ОШИБКИ РЕЙСА ===
            if error_type in ["trip_breakdown", "trip_delayed", "trip_route_issue"]:
                logger.debug("[DRIVER] handling trip error: %s", error_type)                
                self.db.trip_report_failure(session, trip_id, user_id)
                self.db.create_order_issue(
                    session, None, trip_id, user_id, error_type, f"Driver reported: {error_type}"
                )
                return True, ""
                
            elif error_type == "trip_manual_intervention":
                logger.debug("[DRIVER] handling trip_manual_intervention")                
                self.db.trip_request_manual_intervention(session, trip_id, user_id)
                self.db.create_order_issue(
                    session, None, trip_id, user_id, error_type, f"Driver reported: {error_type}"
                )
                return True, ""
            
            # === ОШИБКИ ЯЧЕЙКИ ===
            elif error_type == "locker_failed_to_open":
                logger.debug("[DRIVER] handling locker_failed_to_open")
                self.db.locker_report_failed_to_open(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_failed_to_close":
                logger.debug("[DRIVER] handling locker_failed_to_close")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_not_closed":
                logger.debug("[DRIVER] handling locker_not_closed")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
            
            # === ОШИБКИ ЗАКАЗА ===
            elif error_type == "parcel_missing":
                logger.debug("[DRIVER] handling parcel_missing")
                self.db.order_report_parcel_missing(session, order_id, user_id)
                self.db.confirm_locker_parcel_not_found(session, cell_id, user_id)
                self.db.reset_locker(session, cell_id, user_id)
                
            elif error_type == "parcel_damaged":
                logger.debug("[DRIVER] handling parcel_damaged")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                self.db.reset_locker(session, cell_id, user_id)
                
            elif error_type == "other":
                logger.debug("[DRIVER] handling other")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            else:
                logger.warning("[DRIVER] unknown error_type=%s", error_type)
                return False, f"UNKNOWN_ERROR_TYPE:{error_type}"

            # Записываем инцидент в базу
            self.db.create_order_issue(
                session, order_id, trip_id, user_id, error_type, f"Driver reported: {error_type}"
            )

            logger.info("[DRIVER] report_error completed successfully")
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] report_error failed: %s", e)
            return False, str(e)

    def start_trip(self, session: Session, trip_id: int, user_id: int) -> Tuple[bool, str]:
        logger.info("[DRIVER] start_trip trip=%s user=%s", trip_id, user_id)

        try:            
            can_start, blocked, transit_ids, error = (
                self.db.validate_and_get_orders_for_trip_start(session, trip_id)
            ) 
            
            if not can_start:
                logger.warning("[DRIVER] start_trip blocked: %s", error)
                return False, error

            self.db.start_trip(session, trip_id, user_id)

            for order_id in transit_ids:
                self.db.order_start_transit(session, order_id, user_id)

            logger.info("[DRIVER] trip %s started: %d orders to transit", trip_id, len(transit_ids))
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to start trip %s: %s", trip_id, str(e))
            return False, str(e)

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

    def cancel_trip(
        self,
        session: Session,
        trip_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[DRIVER] cancel_trip trip=%s user=%s", trip_id, user_id)

        try:
            trip = self.db.get_trip(session, trip_id)
            if not trip or trip.get("driver_user_id") != user_id:
                logger.warning("[DRIVER] trip %s not assigned to driver %s", trip_id, user_id)
                return False, "TRIP_NOT_ASSIGNED_TO_DRIVER"

            if trip["status"] != "trip_assigned":
                logger.warning("[DRIVER] cannot cancel trip %s from status %s", trip_id, trip["status"])
                return False, f"CANNOT_CANCEL_FROM_{trip['status']}"

            self.db.trip_report_failure(session, trip_id, user_id)
            logger.info("[DRIVER] trip %s cancelled successfully", trip_id)
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to cancel trip %s: %s", trip_id, str(e))
            return False, str(e)

    def complete_trip(self, session: Session, trip_id: int, user_id: int) -> Tuple[bool, str]:
        logger.info("[DRIVER] complete_trip trip=%s user=%s", trip_id, user_id)
        
        try:
            can_complete, blocked, completed_ids, error = (
                self.db.validate_trip_for_completion(session, trip_id)
            )
            if not can_complete:
                logger.warning("[DRIVER] complete_trip blocked: %s", error)
                return False, error
            
            self.db.complete_trip(session, trip_id, user_id)
            
            logger.info("[DRIVER] trip %s completed: %d orders", trip_id, len(completed_ids))
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to complete trip %s: %s", trip_id, str(e))
            return False, str(e)

# =========================================================
# COURIER
# =========================================================

class CourierActions:
    """Действия курьера."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def _get_leg_and_cell_id(self, order: dict):
        status = order["status"]

        if status in ["order_courier1_assigned", "order_courier_has_parcel"]:
            return "pickup", order["source_cell_id"]

        if status in ["order_courier2_assigned", "order_courier2_has_parcel"]:
            return "delivery", order["dest_cell_id"]

        raise DbLayerError(f"Неизвестный статус курьера: {status}")

    def open_cell(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[COURIER] open_cell order=%s user=%s", order_id, user_id)

        try:
            order = self.db.get_order(session, order_id)
            if not order:
                logger.warning("[COURIER] order %s not found", order_id)
                return False, "ORDER_NOT_FOUND"

            leg, cell_id = self._get_leg_and_cell_id(order)
            logger.debug("[COURIER] determined leg %s for cell %s in order %s", leg, cell_id, order_id)

            if leg == "pickup":
                logger.info("[COURIER] processing pickup parcel for order %s", order_id)
                self.db.order_courier1_pickup_parcel(session, order_id, user_id)
            else:
                logger.info("[COURIER] processing delivery parcel for order %s", order_id)
                self.db.order_courier2_pickup_parcel(session, order_id, user_id)

            self.db.open_locker_for_recipient(session, cell_id, user_id, "")
            logger.info("[COURIER] cell %s opened successfully for order %s", cell_id, order_id)
            return True, ""
            
        except Exception as e:
            logger.error("[COURIER] failed to open cell for order %s: %s", order_id, str(e))
            return False, str(e)

    def close_cell(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[COURIER] close_cell order=%s user=%s", order_id, user_id)

        try:
            order = self.db.get_order(session, order_id)
            if not order:
                logger.warning("[COURIER] order %s not found", order_id)
                return False, "ORDER_NOT_FOUND"

            leg, cell_id = self._get_leg_and_cell_id(order)
            logger.debug("[COURIER] determined leg %s for cell %s in order %s", leg, cell_id, order_id)

            if leg == "pickup":
                logger.info("[COURIER] confirming parcel in and closing pickup cell %s for order %s", cell_id, order_id)
                self.db.order_confirm_parcel_in(session, order_id, user_id)
                self.db.close_locker(session, cell_id, user_id)
            else:
                logger.info("[COURIER] confirming delivery and closing delivery cell %s for order %s", cell_id, order_id)
                self.db.order_courier2_delivered_parcel(session, order_id, user_id)
                self.db.close_locker_pickup(session, cell_id, user_id)

            logger.info("[COURIER] cell %s closed successfully for order %s", cell_id, order_id)
            return True, ""
            
        except Exception as e:
            logger.error("[COURIER] failed to close cell for order %s: %s", order_id, str(e))
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

    def report_error(
        self,
        session: Session,
        cell_id: int,
        order_id: int,
        user_id: int,
        error_type: str,
        trip_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Универсальный метод сообщения об ошибке курьером.
        
        error_type: 'locker_failed_to_open' | 'locker_failed_to_close' | 'locker_not_closed' | 
                    'parcel_missing' | 'parcel_damaged' | 'wrong_parcel' | 'other'
        """
        logger.info("[COURIER] report_error cell=%s order=%s type=%s", cell_id, order_id, error_type)

        try:
            if error_type == "locker_failed_to_open":
                logger.debug("[COURIER] handling locker_failed_to_open")
                self.db.locker_report_failed_to_open(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_failed_to_close":
                logger.debug("[COURIER] handling locker_failed_to_close")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_not_closed":
                logger.debug("[COURIER] handling locker_not_closed")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "parcel_missing":
                logger.debug("[COURIER] handling parcel_missing")
                self.db.order_report_parcel_missing(session, order_id, user_id)
                self.db.confirm_locker_parcel_not_found(session, cell_id, user_id)
                self.db.reset_locker(session, cell_id, user_id)
                
            elif error_type == "parcel_damaged":
                logger.debug("[COURIER] handling parcel_damaged")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "wrong_parcel":
                logger.debug("[COURIER] handling wrong_parcel")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "other":
                logger.debug("[COURIER] handling other")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            else:
                logger.warning("[COURIER] unknown error_type=%s", error_type)
                return False, f"UNKNOWN_ERROR_TYPE:{error_type}"

            self.db.create_order_issue(
                session, order_id, trip_id, user_id, error_type, f"Courier reported: {error_type}"
            )

            logger.info("[COURIER] report_error completed successfully")
            return True, ""
            
        except Exception as e:
            logger.error("[COURIER] report_error failed: %s", e)
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
            # 1. Проверка кода
            valid, error = self.db.validate_courier2_delivery_code(session, order_id, user_id, pin)
            if not valid:
                logger.warning("[COURIER] confirm_delivery_with_code: код не прошёл проверку: %s", error)
                return False, f"INVALID_CODE: {error}"
            
            # 2. FSM переход: order_courier2_parcel_delivered → order_completed
            logger.info("[COURIER] executing FSM transition: order_recipient_confirmed for order %s", order_id)
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

    def report_error(
        self,
        session: Session,
        cell_id: int,
        order_id: int,
        user_id: int,
        error_type: str,
        trip_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Универсальный метод сообщения об ошибке оператором (ручное вмешательство).
        error_type: 
        - Для locker: 'locker_failed_to_open' | 'locker_failed_to_close' | 'locker_not_closed'
        - Для order: 'parcel_missing' | 'parcel_damaged' | 'manual_override' | 'other'
        - Для trip: 'trip_breakdown' | 'trip_delayed' | 'trip_route_issue' | 'trip_manual_intervention'
        
        """
        logger.info("[OPERATOR] report_error cell=%s order=%s trip=%s type=%s", cell_id, order_id, trip_id, error_type)

        try:
            # === ОШИБКИ РЕЙСА (используем существующие методы db_layer) ===
            if error_type in ["trip_breakdown", "trip_delayed", "trip_route_issue"]:
                logger.debug("[OPERATOR] handling trip error: %s", error_type)
                self.db.trip_report_failure(session, trip_id, user_id)
                self.db.create_order_issue(
                    session, 0, trip_id, user_id, error_type, f"Operator reported: {error_type}"
                )
                return True, ""
                
            elif error_type == "trip_manual_intervention":
                logger.debug("[OPERATOR] handling trip_manual_intervention")
                self.db.trip_request_manual_intervention(session, trip_id, user_id)
                self.db.create_order_issue(
                    session, 0, trip_id, user_id, error_type, f"Operator reported: {error_type}"
                )
                return True, ""
            
            # === ОШИБКИ ЯЧЕЙКИ ===
            elif error_type == "locker_failed_to_open":
                logger.debug("[OPERATOR] handling locker_failed_to_open")
                self.db.locker_report_failed_to_open(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_failed_to_close":
                logger.debug("[OPERATOR] handling locker_failed_to_close")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "locker_not_closed":
                logger.debug("[OPERATOR] handling locker_not_closed")
                self.db.locker_not_closed(session, cell_id, user_id)
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            # === ОШИБКИ ЗАКАЗА ===
            elif error_type == "parcel_missing":
                logger.debug("[OPERATOR] handling parcel_missing")
                self.db.order_report_parcel_missing(session, order_id, user_id)
                self.db.confirm_locker_parcel_not_found(session, cell_id, user_id)
                self.db.reset_locker(session, cell_id, user_id)
                
            elif error_type == "parcel_damaged":
                logger.debug("[OPERATOR] handling parcel_damaged")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "manual_override":
                logger.debug("[OPERATOR] handling manual_override")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            elif error_type == "other":
                logger.debug("[OPERATOR] handling other")
                self.db.order_request_manual_intervention(session, order_id, user_id)
                
            else:
                logger.warning("[OPERATOR] unknown error_type=%s", error_type)
                return False, f"UNKNOWN_ERROR_TYPE:{error_type}"

            # Записываем инцидент в базу
            self.db.create_order_issue(
                session, order_id, trip_id, user_id, error_type, f"Operator reported: {error_type}"
            )

            logger.info("[OPERATOR] report_error completed successfully")
            return True, ""
            
        except Exception as e:
            logger.error("[OPERATOR] report_error failed: %s", e)
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
            # 1. Загрузить заказ
            order = self.db.get_order(session, order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"

            # 2. Проверить статус
            allowed_statuses = {
                "pickup": ["order_created", "order_courier1_assigned"],
                "delivery": ["order_parcel_confirmed_post2", "order_courier2_assigned", "order_courier2_parcel_delivered"]
            }
            if order["status"] not in allowed_statuses[leg]:
                return False, f"CODE_NOT_ALLOWED_IN_{order['status']}"

            # 3. Определить, кто авторизован
            authorized_user_id = None
            
            # 🔥 ПОЛУЧИТЬ РОЛЬ ИЗ БАЗЫ
            user_role = self.db.get_user_role(session, user_id)
            
            if leg == "pickup":
                if order["pickup_type"] == "self":
                    authorized_user_id = order["client_user_id"]
                else:
                    stage = self.db.get_stage_order(session, order_id, "pickup")
                    authorized_user_id = stage.courier_user_id if stage else None
            else:  # delivery
                if order["delivery_type"] == "self":
                    # Самовывоз: только получатель
                    authorized_user_id = order.get("recipient_user_id")
                else:
                    # 🔥 КУРЬЕР2: И курьер, И получатель могут запросить код
                    if user_role == "courier":
                        stage = self.db.get_stage_order(session, order_id, "delivery")
                        authorized_user_id = stage.courier_user_id if stage else None
                    elif user_role == "recipient":
                        authorized_user_id = order.get("recipient_user_id")
                    else:
                        return False, "USER_NOT_AUTHORIZED"

            if authorized_user_id != user_id:
                return False, "USER_NOT_AUTHORIZED"

            # 4. Проверить лимит (≤3 за 15 мин)
            recent = self.db.count_recent_access_code_requests(session, order_id, leg, 15)
            if recent >= 3:
                return False, "TOO_MANY_CODE_REQUESTS"

            # 5. Определить cell_id
            cell_id = order["source_cell_id"] if leg == "pickup" else order["dest_cell_id"]
            if not cell_id:
                return False, "CELL_ID_MISSING"

            # 6. Генерация PIN и запись в базу
            pin, token_id = self.db.generate_and_store_access_token(
                session, order_id, leg, cell_id, user_id, expires_minutes=15
            )

            # 7. Отправить PIN
            self.db.send_code_to_user(session, user_id, pin)
            
            logger.info(f"Access code issued: order={order_id}, leg={leg}, user={user_id}, token={token_id}")
            return True, ""

        except Exception as e:
            logger.exception(f"request_access_code failed for order {order_id}: {e}")
            return False, str(e)

# ==================== РЕЙСЫ ====================
class TripActions:
    """Действия, связанные с управлением рейсами."""

    def __init__(self, db: DatabaseLayer):
        self.db = db

    def bind_order_to_trip(self, session: Session, order_id: int) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(session, order_id)
            if not order or order["status"] != "order_parcel_confirmed":
                return False, "ORDER_NOT_CONFIRMED"

            # Получаем locker_id
            pickup_locker_id = self.db.get_locker_id_by_cell(session, order["source_cell_id"])
            delivery_locker_id = self.db.get_locker_id_by_cell(session, order["dest_cell_id"])

            # Получаем города
            from_city = self.db.get_locker_city_by_cell(session, order["source_cell_id"])
            to_city = self.db.get_locker_city_by_cell(session, order["dest_cell_id"])

            # Передаём ВСЁ в assign_order_to_trip_smart
            trip_id, success, msg = self.db.assign_order_to_trip_smart(
                session,
                order_id=order_id,
                pickup_locker_id=pickup_locker_id,
                delivery_locker_id=delivery_locker_id,
                from_city=from_city,
                to_city=to_city,
            )
            return success, msg

        except Exception as e:
            logger.exception("bind_order_to_trip failed for order %s: %s", order_id, e)
            return False, str(e)
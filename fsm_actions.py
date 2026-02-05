# fsm_actions.py

from typing import Tuple, Optional
from db_layer import DatabaseLayer, DbLayerError
from sqlalchemy.orm import Session
import logging

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

            if not req:
                return False, None, "ORDER_REQUEST_NOT_FOUND"

            if req["status"] != "PENDING":
                return False, None, "INVALID_REQUEST_STATE"

            client_user_id = req["client_user_id"]
            if not client_user_id:
                return False, None, "INVALID_REQUEST_DATA"

            parcel_type = req["parcel_type"]
            cell_size = req["cell_size"]
            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]

            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            # 🔒 поиск + резерв
            ok, src_id, dst_id = self.db.find_and_reserve_cells_by_size(
                session,
                source_locker_id=1,
                dest_locker_id=2,
                cell_size=cell_size,
            )

            if not ok:
                logger.info("[ORDER_CREATE] no free cells")
                return False, None, "NO_FREE_CELLS"

            # 🧾 create order
            order_id = self.db.create_order_record(
                session,
                description=description,
                pickup_type=pickup_type,
                delivery_type=delivery_type,
                client_user_id=client_user_id,
                source_cell_id=src_id,
                dest_cell_id=dst_id,
            )

            # 🚚 trip bind (без commit)
            try:
                self.db.assign_order_to_trip_smart(
                    session,
                    order_id,
                    "LOCAL",
                    "LOCAL",
                )
            except Exception as e:
                logger.warning(
                    "[ORDER_CREATE] trip assign failed order_id=%s err=%s",
                    order_id,
                    e,
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

    def report_locker_error(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Клиент сообщает об ошибке ячейки.
        """
        logger.warning("[CLIENT] report_locker_error order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[CLIENT] reporting locker error for cell %s", cell_id)
            self.db.locker_not_closed(session, cell_id, user_id)
            logger.info("[CLIENT] locker error reported successfully for order %s", order_id)
            return True, ""
        except Exception as e:
            logger.error("[CLIENT] failed to report locker error for order %s: %s", order_id, str(e))
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

    def report_locker_error(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.warning("[RECIPIENT] locker_error order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_dest_cell_id(session, order_id)
            logger.debug("[RECIPIENT] reporting locker error for cell %s", cell_id)
            self.db.locker_not_closed(session, cell_id, user_id)
            logger.info("[RECIPIENT] locker error reported successfully for order %s", order_id)
            return True, ""
        except Exception as e:
            logger.error("[RECIPIENT] failed to report locker error for order %s: %s", order_id, str(e))
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
            trip = self._get_active_trip_for_driver(session, user_id)
            logger.debug("[DRIVER] active trip %s found for driver %s", trip["id"], user_id)
            
            intent = self._determine_intent(session, cell_id, trip)
            logger.debug("[DRIVER] cell %s intent determined as %s for trip %s", cell_id, intent, trip["id"])

            self.db.open_locker_for_recipient(session, cell_id, user_id, "")

            order_id = self.db.get_order_id_by_cell_id(session, cell_id)

            if order_id:
                logger.debug("[DRIVER] order %s found for cell %s", order_id, cell_id)
                if intent == "pickup":
                    logger.info("[DRIVER] processing pickup for order %s in trip %s", order_id, trip["id"])
                    self.db.order_parcel_submitted(session, order_id, user_id)
                    self.db.trip_assign_voditel(session, trip["id"], user_id)
                else:
                    logger.info("[DRIVER] processing delivery for order %s in trip %s", order_id, trip["id"])
                    self.db.order_confirm_parcel_in(session, order_id, user_id)

            logger.info("[DRIVER] cell %s opened successfully for driver %s", cell_id, user_id)
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to open cell %s for driver %s: %s", cell_id, user_id, str(e))
            return False, str(e)

    def close_cell_for_driver(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Водитель закрывает ячейку.
        """
        logger.info("[DRIVER] close_cell cell=%s user=%s", cell_id, user_id)

        try:
            trip = self._get_active_trip_for_driver(session, user_id)
            logger.debug("[DRIVER] active trip %s found for driver %s", trip["id"], user_id)
            
            intent = self._determine_intent(session, cell_id, trip)
            logger.debug("[DRIVER] closing cell %s with intent %s for trip %s", cell_id, intent, trip["id"])

            order_id = self.db.get_order_id_by_cell_id(session, cell_id)

            if intent == "pickup":
                self.db.close_locker_pickup(session, cell_id, user_id)
                if order_id:
                    logger.info("[DRIVER] processing pickup completion for order %s", order_id)
                    self.db.order_pickup_by_voditel(session, order_id, user_id)
                    self.db.trip_confirm_pickup(session, trip["id"], user_id)
            else:
                self.db.close_locker(session, cell_id, user_id)

            logger.info("[DRIVER] cell %s closed successfully for driver %s", cell_id, user_id)
            return True, ""
            
        except Exception as e:
            logger.error("[DRIVER] failed to close cell %s for driver %s: %s", cell_id, user_id, str(e))
            return False, str(e)

    def report_locker_error_cell(
        self,
        session: Session,
        cell_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.warning("[DRIVER] locker_error cell=%s user=%s", cell_id, user_id)
        
        try:
            self.db.locker_not_closed(session, cell_id, user_id)
            logger.info("[DRIVER] locker error reported successfully for cell %s", cell_id)
            return True, ""
        except Exception as e:
            logger.error("[DRIVER] failed to report locker error for cell %s: %s", cell_id, str(e))
            return False, str(e)

    def start_trip(
        self,
        session: Session,
        trip_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.info("[DRIVER] start_trip trip=%s user=%s", trip_id, user_id)

        try:
            self.db.trip_start_trip(session, trip_id, user_id)
            logger.debug("[DRIVER] trip %s started successfully", trip_id)

            order_ids = self.db.get_orders_in_trip(session, trip_id)
            logger.debug("[DRIVER] found %s orders in trip %s", len(order_ids), trip_id)
            
            for order_id in order_ids:
                logger.info("[DRIVER] updating order %s to start transit", order_id)
                self.db.order_start_transit(session, order_id, user_id)

            logger.info("[DRIVER] trip %s started with %s orders", trip_id, len(order_ids))
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

    def report_locker_error(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        logger.warning("[COURIER] locker_error order=%s user=%s", order_id, user_id)

        try:
            order = self.db.get_order(session, order_id)
            if not order:
                logger.warning("[COURIER] order %s not found for locker error report", order_id)
                return False, "ORDER_NOT_FOUND"

            _, cell_id = self._get_leg_and_cell_id(order)
            logger.debug("[COURIER] reporting locker error for cell %s in order %s", cell_id, order_id)
            self.db.locker_not_closed(session, cell_id, user_id)
            logger.info("[COURIER] locker error reported successfully for order %s", order_id)
            return True, ""
            
        except Exception as e:
            logger.error("[COURIER] failed to report locker error for order %s: %s", order_id, str(e))
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

    def report_locker_error(
        self,
        session: Session,
        order_id: int,
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Сообщение оператора об ошибке ячейки.
        """
        logger.warning("[OPERATOR] report_locker_error order=%s user=%s", order_id, user_id)

        try:
            cell_id = self._get_source_cell_id(session, order_id)
            logger.debug("[OPERATOR] reporting locker error for cell %s in order %s", cell_id, order_id)
            self.db.locker_not_closed(session, cell_id, user_id)
            logger.info("[OPERATOR] locker error reported successfully for order %s", order_id)
            return True, ""
        except Exception as e:
            logger.error("[OPERATOR] failed to report locker error for order %s: %s", order_id, str(e))
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
# fsm_actions.py

from typing import Tuple, Optional
from sqlalchemy import text
from db_layer import DatabaseLayer, DbLayerError, FsmCallError
import logging

logger = logging.getLogger(__name__)


class OrderCreationActions:
    """
    Actions для процесса 'order_creation':
    1) поиск двух свободных ячеек нужного размера;
    2) создание заказа из заявки и резерв ячеек.

    Единственный класс, который имеет право:
    - менять order_requests.status
    - писать order_requests.order_id
    """

    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    # =====================================================
    # ACTION 1 — ТОЛЬКО поиск ячеек (БЕЗ side-effects)
    # =====================================================
    def find_cells_for_request(
        self,
        request_id: int,
    ) -> Tuple[bool, Optional[int], Optional[int], str]:
        try:
            req = self.db.get_order_request(request_id)
            if not req:
                return False, None, None, "ORDER_REQUEST_NOT_FOUND"

            if req["status"] != "PENDING":
                return False, None, None, "INVALID_REQUEST_STATE"

            cell_size = req["cell_size"]
            source_locker_id = 1
            dest_locker_id = 2

            src_cells = self.db.get_locker_cells_by_status(source_locker_id, "locker_free")
            dst_cells = self.db.get_locker_cells_by_status(dest_locker_id, "locker_free")

            src_cell = next((c for c in src_cells if c["cell_type"] == cell_size), None)
            dst_cell = next((c for c in dst_cells if c["cell_type"] == cell_size), None)

            if not src_cell or not dst_cell:
                self.db.mark_request_failed(
                    request_id=request_id,
                    error_code="NO_FREE_CELLS",
                    error_message=f"No free cells of type '{cell_size}' found for request {request_id}."
                )
                return False, None, None, "NO_FREE_CELLS"

            return True, int(src_cell["id"]), int(dst_cell["id"]), ""

        except DbLayerError:
            raise
        except Exception as e:
            raise DbLayerError(f"find_cells_for_request({request_id}) failed: {e}")

    # =====================================================
    # ACTION 2 — создание заказа (ВСЯ бизнес-логика)
    # =====================================================
    def create_order_from_request(
        self,
        request_id: int,
        source_cell_id: int,
        dest_cell_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        try:
            req = self.db.get_order_request(request_id)
            if not req:
                return False, None, "ORDER_REQUEST_NOT_FOUND"

            if req["status"] != "PENDING":
                return False, None, "INVALID_REQUEST_STATE"

            client_user_id = req["client_user_id"]
            if client_user_id is None:
                self.db.mark_request_failed(
                    request_id=request_id,
                    error_code="LOGIC_ERROR_INVALID_REQUEST_DATA",
                    error_message="Request has no associated user."
                )
                return False, None, "LOGIC_ERROR_INVALID_REQUEST_DATA"

            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]
            parcel_type = req["parcel_type"]
            cell_size = req["cell_size"]

            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            success, order_id, error_msg = self.db.create_order_and_reserve_cells(
                source_cell_id=source_cell_id,
                dest_cell_id=dest_cell_id,
                client_user_id=client_user_id,
                description=description,
                pickup_type=pickup_type,
                delivery_type=delivery_type,
            )

            if not success:
                self.db.mark_request_failed(
                    request_id=request_id,
                    error_code="ORDER_CREATION_FAILED",
                    error_message=f"Order creation failed: {error_msg}"
                )
                return False, None, "ORDER_CREATION_FAILED"

            trip_id, trip_success, trip_msg = self.db.assign_order_to_trip_smart(
                order_id=order_id,
                order_from_city="LOCAL",
                order_to_city="LOCAL",
            )

            if not trip_success:
                logger.warning(f"[ORDER_CREATION] assignment failed for order {order_id}: {trip_msg}")

            completed_success = self.db.mark_request_completed(
                request_id=request_id,
                order_id=order_id
            )
            if not completed_success:
                self.db.mark_request_failed(
                    request_id=request_id,
                    error_code="REQUEST_COMPLETION_FAILED",
                    error_message=f"Could not link request {request_id} to order {order_id} after creation."
                )
                return False, order_id, "REQUEST_COMPLETION_FAILED"

            return True, order_id, ""

        except DbLayerError:
            raise
        except Exception as e:
            raise DbLayerError(f"create_order_from_request({request_id}) failed: {e}")


class AssignmentActions:
    """
    Действия для назначения исполнителей.
    
    Исполнитель ВСЕГДА передаётся явно через target_user_id.
    НЕТ автоматического выбора исполнителя.
    """

    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def assign_to_order(self, order_id: int, executor_id: int, role: str) -> bool:
        """
        Назначает исполнителя на заказ.
        
        ВАЖНО: Двухэтапный процесс:
        1. Сначала запись в stage_orders
        2. Потом FSM action (триггер проверит наличие записи в stage_orders)
        
        Args:
            order_id: ID заказа
            executor_id: ID исполнителя (курьера) - передан явно через target_user_id
            role: "courier1" (pickup) или "courier2" (delivery)
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            if role == "courier1":
                # 1. Записать в stage_orders (pickup leg)
                self.db.set_courier1_in_stage(order_id, executor_id)
                # 2. FSM action → orders.status (триггер проверит stage_orders)
                self.db.assign_courier_to_order(order_id, executor_id)
                
            elif role == "courier2":
                # 1. Записать в stage_orders (delivery leg)
                self.db.set_courier2_in_stage(order_id, executor_id)
                # 2. FSM action → orders.status
                self.db.assign_courier2_to_order(order_id, executor_id)
                
            else:
                print(f"[ASSIGNMENT] Неизвестная роль для order: {role}")
                return False
            
            print(f"[ASSIGNMENT] ✅ Назначен {role} user_id={executor_id} на order_id={order_id}")
            return True
            
        except Exception as e:
            print(f"[ASSIGNMENT] ❌ Ошибка назначения order: {e}")
            return False

    def assign_to_trip(self, trip_id: int, executor_id: int, role: str) -> bool:
        """
        Назначает водителя на рейс.
        
        ВАЖНО: Двухэтапный процесс:
        1. Сначала запись в trips.driver_user_id
        2. Потом FSM action (если есть соответствующий переход)
        
        Args:
            trip_id: ID рейса
            executor_id: ID водителя - передан явно через target_user_id
            role: "driver"
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            if role == "driver":
                # 1. Записать в trips.driver_user_id
                self.db.set_driver_in_trip(trip_id, executor_id)
                # 2. FSM action 
                self.db.driver_take_trip(trip_id, executor_id)
                
            else:
                print(f"[ASSIGNMENT] Неизвестная роль для trip: {role}")
                return False
            
            print(f"[ASSIGNMENT] ✅ Назначен {role} user_id={executor_id} на trip_id={trip_id}")
            return True
            
        except Exception as e:
            print(f"[ASSIGNMENT] ❌ Ошибка назначения trip: {e}")
            return False

# =========== РАБОТА С ПОСТАМАТОМ ===========================

class ClientActions:
    """Действия клиента (отправителя)."""
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def _get_source_cell_id(self, order_id: int) -> int:
        order = self.db.get_order(order_id)
        if not order or not order.get("source_cell_id"):
            raise DbLayerError(f"Нет source_cell_id для заказа {order_id}")
        return order["source_cell_id"]

    def open_cell_for_client(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Клиент открывает ячейку отправки (locker_reserved → locker_opened)."""
        try:
            cell_id = self._get_source_cell_id(order_id)
            self.db.open_locker_for_recipient(cell_id, user_id, "")
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def close_cell_for_client(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Клиент закрывает ячейку после помещения посылки."""
        try:
            cell_id = self._get_source_cell_id(order_id)
            # Подтверждаем посылку в заказе
            self.db.order_confirm_parcel_in(order_id, user_id)
            # Закрываем ячейку → locker_occupied
            self.db.close_locker(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def cancel_order(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Клиент отменяет заказ до передачи."""
        try:
            # 1. Получаем заказ
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"

            # 2. Отменяем заказ (FSM: order_created → order_cancelled)
            self.db.order_cancel_reservation(order_id, user_id)

            # 3. Сбрасываем резерв ячеек
            src_id = order.get("source_cell_id")
            dst_id = order.get("dest_cell_id")
            if src_id:
                self.db.cancel_locker_reservation(src_id, user_id)
            if dst_id:
                self.db.cancel_locker_reservation(dst_id, user_id)

            return True, ""
        except DbLayerError as e:            
            raise 
        except FsmCallError as e: 
            raise

    def report_locker_error(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Клиент сообщает, что ячейка не закрылась."""
        try:
            cell_id = self._get_source_cell_id(order_id)
            self.db.locker_not_closed(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)


class RecipientActions:
    """Действия получателя."""
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def _get_dest_cell_id(self, order_id: int) -> int:
        order = self.db.get_order(order_id)
        if not order or not order.get("dest_cell_id"):
            raise DbLayerError(f"Нет dest_cell_id для заказа {order_id}")
        return order["dest_cell_id"]

    def open_cell_for_recipient(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Получатель открывает ячейку получения."""
        try:
            cell_id = self._get_dest_cell_id(order_id)
            self.db.open_locker_for_recipient(cell_id, user_id, "")
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def close_cell_for_recipient(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Получатель закрывает пустую ячейку."""
        try:
            cell_id = self._get_dest_cell_id(order_id)
            self.db.close_locker_pickup(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def report_locker_error(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        try:
            cell_id = self._get_dest_cell_id(order_id)
            self.db.locker_not_closed(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)


class DriverActions:
    """Действия водителя с ячейками."""
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def _get_active_trip_for_driver(self, driver_id: int) -> dict:
        trips = self.db.get_active_trips_for_driver(driver_id)
        if not trips:
            raise DbLayerError("Нет активного рейса у водителя")
        return trips[0]

    def _determine_intent(self, cell_id: int, trip: dict) -> str:
        locker_id = self.session.execute(
            text("SELECT locker_id FROM locker_cells WHERE id = :cell_id"),
            {"cell_id": cell_id}
        ).scalar()
        if locker_id == trip["pickup_locker_id"]:
            return "pickup"   # Забирает из locker_occupied
        elif locker_id == trip["delivery_locker_id"]:
            return "delivery" # Кладёт в locker_reserved
        else:
            raise DbLayerError(f"Ячейка {cell_id} не относится к рейсу")

    def open_cell_for_driver(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель открывает ячейку (locker_occupied или locker_reserved → locker_opened)."""
        try:
            trip = self._get_active_trip_for_driver(user_id)
            intent = self._determine_intent(cell_id, trip)

            if intent == "pickup":
                # === FSM: locker ===
                self.db.open_locker_for_recipient(cell_id, user_id, "")
                # === FSM: order ===
                order_id = self.db.get_order_id_by_cell_id(cell_id)
                if order_id:
                    self.db.order_parcel_submitted(order_id, user_id)
                # === FSM: trip ===
                self.db.trip_assign_voditel(trip["id"], user_id)

            elif intent == "delivery":
                # === FSM: locker ===
                self.db.open_locker_for_recipient(cell_id, user_id, "")
                # === FSM: order ===
                order_id = self.db.get_order_id_by_cell_id(cell_id)
                if order_id:
                    self.db.order_confirm_parcel_in(order_id, user_id)            

            else:
                return False, f"UNKNOWN_INTENT_{intent}"

            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def close_cell_for_driver(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель закрывает ячейку — логика зависит от intent."""
        try:
            trip = self._get_active_trip_for_driver(user_id)
            intent = self._determine_intent(cell_id, trip)

            if intent == "pickup":
                # === FSM: locker ===
                self.db.close_locker_pickup(cell_id, user_id)
                # === FSM: order ===
                order_id = self.db.get_order_id_by_cell_id(cell_id)
                if order_id:
                    self.db.order_pickup_by_voditel(order_id, user_id)
                # === FSM: trip ===
                self.db.trip_confirm_pickup(trip["id"], user_id)

            elif intent == "delivery":
                # === FSM: locker ===
                # Закрываем → locker_occupied
                self.db.close_locker(cell_id, user_id)

            else:
                return False, f"UNKNOWN_INTENT_{intent}"

            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def report_locker_error_cell(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель сообщает об ошибке ячейки."""
        try:
            self.db.locker_not_closed(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def start_trip(self, trip_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель начинает рейс (после забора)."""
        try:
            # === FSM: trip ===
            self.db.trip_start_trip(trip_id, user_id)
            # === FSM: order ===
            # Обновить статусы всех заказов в рейсе
            order_ids = self.db.get_orders_in_trip(trip_id)
            for order_id in order_ids:
                self.db.order_start_transit(order_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def arrive_at_destination(self, trip_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель прибыл в точку доставки."""
        try:
            # === FSM: trip ===
            self.db.trip_end_delivery(trip_id, user_id)
            # === FSM: order ===
            # Обновить статусы всех заказов в рейсе
            order_ids = self.db.get_orders_in_trip(trip_id)
            for order_id in order_ids:
                self.db.order_arrive_at_post2(order_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def cancel_trip(self, trip_id: int, user_id: int) -> Tuple[bool, str]:
        """Водитель отказывается от рейса до начала забора."""
        try:
            # Проверка: водитель действительно назначен на рейс
            trip = self.db.get_trip(trip_id)
            if not trip or trip.get("driver_user_id") != user_id:
                return False, "TRIP_NOT_ASSIGNED_TO_DRIVER"

            # Проверка: статус рейса — должен быть trip_assigned
            status = trip["status"]
            if status != "trip_assigned":
                return False, f"CANNOT_CANCEL_FROM_STATUS_{status}"

            # FSM: trip_assigned → trip_created
            self.db.trip_report_failure(trip_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

class CourierActions:
    """Универсальные действия курьера (courier1 и courier2 определяются по статусу заказа)."""
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def _get_leg_and_cell_id(self, order: dict) -> Tuple[str, int]:
        """Определяет leg и cell_id по статусу заказа."""
        status = order["status"]
        pickup_statuses = ["order_courier1_assigned", "order_courier_has_parcel"]
        delivery_statuses = ["order_courier2_assigned", "order_courier2_has_parcel"]

        if status in pickup_statuses:
            return "pickup", order["source_cell_id"]
        elif status in delivery_statuses:
            return "delivery", order["dest_cell_id"]
        else:
            raise DbLayerError(f"Неизвестный статус для курьера: {status}")

    def open_cell(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            leg, cell_id = self._get_leg_and_cell_id(order)

            # FSM переход по заказу (создаёт контекст для открытия)
            if leg == "pickup":
                self.db.order_courier1_pickup_parcel(order_id, user_id)
            else:  # delivery
                self.db.order_courier2_pickup_parcel(order_id, user_id)

            # Открытие ячейки
            self.db.open_locker_for_recipient(cell_id, user_id, "")
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def close_cell(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            leg, cell_id = self._get_leg_and_cell_id(order)

            if leg == "pickup":
                # Подтверждаем посылку в системе забора
                self.db.order_confirm_parcel_in(order_id, user_id)
                # Закрываем ячейку → locker_occupied
                self.db.close_locker(cell_id, user_id)
            else:  # delivery
                # Подтверждаем доставку
                self.db.order_courier2_delivered_parcel(order_id, user_id)
                # Закрываем → locker_closed_empty
                self.db.close_locker_pickup(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    # fsm_actions.py → CourierActions
    def cancel_order(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            status = order["status"]
            if status == "order_courier1_assigned":
                self.db.order_courier1_cancel(order_id, user_id)
                # === ОЧИСТКА КУРЬЕРА ИЗ STAGE_ORDERS ===
                self.db.clear_courier_from_stage_order(order_id, "pickup", user_id)
            elif status == "order_courier2_assigned":
                self.db.order_courier2_cancel(order_id, user_id)
                # === ОЧИСТКА КУРЬЕРА2 ИЗ STAGE_ORDERS ===
                self.db.clear_courier_from_stage_order(order_id, "delivery", user_id)
            else:
                return False, f"CANNOT_CANCEL_FROM_{status}"
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def report_locker_error(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            _, cell_id = self._get_leg_and_cell_id(order)
            self.db.locker_not_closed(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

# ================= РАБОТА ОПЕРАТОРА =====================
class OperatorActions:
    """Действия оператора: технические операции с заказами и ячейками."""
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def _get_source_cell_id(self, order_id: int) -> int:
        order = self.db.get_order(order_id)
        if not order or not order.get("source_cell_id"):
            raise DbLayerError(f"Нет source_cell_id для заказа {order_id}")
        return order["source_cell_id"]

    def _get_dest_cell_id(self, order_id: int) -> int:
        order = self.db.get_order(order_id)
        if not order or not order.get("dest_cell_id"):
            raise DbLayerError(f"Нет dest_cell_id для заказа {order_id}")
        return order["dest_cell_id"]

    def open_cell_for_operator(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Оператор открывает ячейку (любую — по логике, но пока только source)."""
        try:
            # Оператор может открыть любую ячейку, но для совместимости — source
            cell_id = self._get_source_cell_id(order_id)
            self.db.open_locker_for_recipient(cell_id, user_id, "")
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def close_cell_for_operator(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Оператор закрывает ячейку (source)."""
        try:
            cell_id = self._get_source_cell_id(order_id)
            # Можно закрыть как пустую, так и занятую — используем общий close
            # В FSM: из locker_opened → можно в locker_occupied или locker_closed_empty
            # Но без контекста — безопаснее использовать общий метод
            self.db.close_locker(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def force_cancel_order(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Оператор принудительно отменяет заказ."""
        try:
            self.db.order_cancel_reservation(order_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def report_locker_error(self, order_id: int, user_id: int) -> Tuple[bool, str]:
        """Оператор сообщает об ошибке ячейки."""
        try:
            cell_id = self._get_source_cell_id(order_id)
            self.db.locker_not_closed(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)    

    def reset_locker(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """Сброс состояния ячейки (из locker_error → locker_free)."""
        try:
            self.db.reset_locker(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)

    def set_locker_maintenance(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """Поставить ячейку на обслуживание."""
        try:
            self.db.set_locker_maintenance(cell_id, user_id)
            return True, ""
        except (FsmCallError, Exception) as e:
            self.session.rollback()
            return False, str(e)
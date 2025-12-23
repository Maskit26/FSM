# fsm_actions.py

from typing import Tuple, Optional
from sqlalchemy import text
from db_layer import DatabaseLayer, DbLayerError, FsmCallError


class OrderCreationActions:
    """
    Actions для процесса 'order_creation':
    1) поиск двух свободных ячеек нужного размера;
    2) создание заказа из заявки и резерв ячеек.
    
    Работает поверх DatabaseLayer и таблиц:
    - order_requests
    - locker_cells
    - orders
    """

    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session

    def find_cells_for_request(
        self,
        request_id: int,
    ) -> Tuple[bool, Optional[int], Optional[int], str]:
        """
        Action 1: поиск двух свободных ячеек нужного размера для заявки.
        
        Логика:
        - читает заявку из order_requests;
        - по полю cell_size ищет:
          * одну свободную ячейку нужного размера в POST1 (locker_id = 1),
          * одну свободную ячейку нужного размера в POST2 (locker_id = 2);
        - при отсутствии ячеек помечает заявку как FAILED с кодом 'NO_FREE_CELLS'.
        
        Возвращает:
        - success: bool
        - source_cell_id: Optional[int]
        - dest_cell_id: Optional[int]
        - error_code: str ('', 'ORDER_REQUEST_NOT_FOUND', 'INVALID_REQUEST_STATE', 'NO_FREE_CELLS')
        """
        session = self.session
        
        try:
            # 1. Читаем заявку
            row = session.execute(
                text(
                    """
                    SELECT id, cell_size, status
                    FROM order_requests
                    WHERE id = :id
                    """
                ),
                {"id": request_id},
            ).fetchone()
            
            if not row:
                return False, None, None, "ORDER_REQUEST_NOT_FOUND"
            
            _id, cell_size, status = row
            
            if status != "PENDING":
                return False, None, None, "INVALID_REQUEST_STATE"
            
            # 2. Жёстко выбираем два постамата: POST1 и POST2
            source_locker_id = 1  # POST1
            dest_locker_id = 2    # POST2
            
            # 3. Ищем свободные ячейки по размеру
            src_cells = self.db.get_locker_cells_by_status(source_locker_id, "locker_free")
            dst_cells = self.db.get_locker_cells_by_status(dest_locker_id, "locker_free")
            
            src_cell = next((c for c in src_cells if c["cell_type"] == cell_size), None)
            dst_cell = next((c for c in dst_cells if c["cell_type"] == cell_size), None)
            
            if not src_cell or not dst_cell:
                # Нет двух свободных ячеек нужного размера
                session.execute(
                    text(
                        """
                        UPDATE order_requests
                        SET status = 'FAILED',
                            error_code = 'NO_FREE_CELLS',
                            error_message = 'Не найдены свободные ячейки нужного размера'
                        WHERE id = :id
                        """
                    ),
                    {"id": request_id},
                )
                session.commit()
                return False, None, None, "NO_FREE_CELLS"
            
            return True, int(src_cell["id"]), int(dst_cell["id"]), ""
            
        except Exception as e:
            session.rollback()
            raise DbLayerError(f"find_cells_for_request({request_id}) failed: {e}") from e

    def create_order_from_request(
        self,
        request_id: int,
        source_cell_id: int,
        dest_cell_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        """
        Action 2: создать заказ из заявки и зарезервировать найденные ячейки.
        
        Логика:
        - читает заявку из order_requests;
        - маппит sender_delivery → pickup_type, recipient_delivery → delivery_type;
        - создаёт запись в orders со статусом 'order_created';
        - ✨ FSM переходы locker_cells → locker_reserved
        - помечает заявку COMPLETED и привязывает order_id.
        
        Возвращает:
        - success: bool
        - order_id: Optional[int]
        - error_code: str
        """
        session = self.session
        
        try:
            # 1. Читаем заявку
            row = session.execute(
                text(
                    """
                    SELECT id, client_user_id, parcel_type, cell_size,
                           sender_delivery, recipient_delivery, status
                    FROM order_requests
                    WHERE id = :id
                    """
                ),
                {"id": request_id},
            ).fetchone()
            
            if not row:
                return False, None, "ORDER_REQUEST_NOT_FOUND"
            
            (
                _id,
                client_user_id,
                parcel_type,
                cell_size,
                sender_delivery,
                recipient_delivery,
                status,
            ) = row
            
            if status != "PENDING":
                return False, None, "INVALID_REQUEST_STATE"
            
            # 2. Маппим типы доставки
            pickup_type = "courier" if sender_delivery == "courier" else "self"
            delivery_type = "courier" if recipient_delivery == "courier" else "self"
            description = f"{parcel_type} ({cell_size})"
            
            # 3. Создаём заказ
            session.execute(
                text(
                    """
                    INSERT INTO orders
                        (description, from_city, to_city,
                         source_cell_id, dest_cell_id,
                         pickup_type, delivery_type, status)
                    VALUES
                        (:desc, :from_city, :to_city,
                         :source_cell_id, :dest_cell_id,
                         :pickup_type, :delivery_type, 'order_created')
                    """
                ),
                {
                    "desc": description,
                    "from_city": "LOCAL",
                    "to_city": "LOCAL",
                    "source_cell_id": source_cell_id,
                    "dest_cell_id": dest_cell_id,
                    "pickup_type": pickup_type,
                    "delivery_type": delivery_type,
                },
            )
            
            result = session.execute(text("SELECT LAST_INSERT_ID()"))
            order_id = int(result.scalar_one())
            
            # 4. Резервируем ячейки через db_layer (в той же транзакции)
            self.db.reserve_cells_for_order_in_session(order_id, source_cell_id, dest_cell_id)

            
            # 5. Привязываем ячейки к заказу (current_order_id)
            session.execute(
                text(
                    """
                    UPDATE locker_cells
                    SET current_order_id = :order_id
                    WHERE id IN (:src_id, :dst_id)
                    """
                ),
                {"order_id": order_id, "src_id": source_cell_id, "dst_id": dest_cell_id},
            )

            # 6. Создаём или получаем trip через ORM слой            
            trip_id, success, msg = self.db.assign_order_to_trip_smart(
                order_id=order_id,
                order_from_city="LOCAL",
                order_to_city="LOCAL"
            )

            if not success:
                session.rollback()
                print(f"[ORDER_CREATION] ❌ Не удалось назначить заказ на trip: {msg}")
                return False, None, "TRIP_ASSIGNMENT_FAILED"

            print(f"[ORDER_CREATION] Заказ {order_id} назначен на trip {trip_id}")            
            
            # 7. Помечаем заявку COMPLETED
            session.execute(
                text(
                    """
                    UPDATE order_requests
                    SET status = 'COMPLETED',
                        order_id = :order_id,
                        error_code = NULL,
                        error_message = NULL
                    WHERE id = :id
                    """
                ),
                {"id": request_id, "order_id": order_id},
            )
            
            session.commit()
            
            print(f"[ORDER_CREATION] Заказ {order_id} создан, ячейки {source_cell_id},{dest_cell_id} зарезервированы")
            return True, order_id, ""
            
        except Exception as e:
            session.rollback()
            raise DbLayerError(f"create_order_from_request({request_id}) failed: {e}") from e


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
                # 2. FSM action (если есть trip_assign_driver)
                self.db.trip_assign_driver(trip_id, operator_id=0)
                
            else:
                print(f"[ASSIGNMENT] Неизвестная роль для trip: {role}")
                return False
            
            print(f"[ASSIGNMENT] ✅ Назначен {role} user_id={executor_id} на trip_id={trip_id}")
            return True
            
        except Exception as e:
            print(f"[ASSIGNMENT] ❌ Ошибка назначения trip: {e}")
            return False

# =========== РАБОТА С ПОСТАМАТОМ ===========================

class CourierCellActions:
    """
    Действия курьеров с ячейками постаматов.

    """
    
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session
    
    def _determine_leg(self, order_status: str) -> str:
        """
        Определяет leg (pickup/delivery) по статусу заказа.
        
        Returns:
            "pickup" для курьера1 (забор от клиента)
            "delivery" для курьера2 (доставка получателю)
        """
        pickup_statuses = [
            "order_courier1_assigned",
            "order_courier_has_parcel"
        ]
        
        delivery_statuses = [
            "order_courier2_assigned",
            "order_courier2_has_parcel"
        ]
        
        if order_status in pickup_statuses:
            return "pickup"
        elif order_status in delivery_statuses:
            return "delivery"
        else:
            return "unknown"
    
    def open_cell(self, order_id: int, courier_id: int) -> Tuple[bool, str]:
        """
        Открывает ячейку для курьера (используя готовые методы db_layer).
        
        Курьер1 (pickup leg):
        - db.order_courier1_pickup_parcel() → order_courier_has_parcel
        - db.open_locker_for_recipient() → locker_opened
        
        Курьер2 (delivery leg):
        - db.order_courier2_pickup_parcel() → order_courier2_has_parcel
        - db.open_locker_for_recipient() → locker_opened
        
        Args:
            order_id: ID заказа
            courier_id: ID курьера (роль = "courier")
        
        Returns:
            (success, error_code)
        """
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            
            # Определяем leg по статусу заказа
            leg = self._determine_leg(order["status"])
            
            if leg == "pickup":
                # Курьер1 (забор от клиента на POST1)
                cell_id = order["source_cell_id"]
                expected_status = "order_courier1_assigned"
                
                # FSM переход 1: Order (курьер1 взял посылку)
                self.db.order_courier1_pickup_parcel(order_id, courier_id)
                
            elif leg == "delivery":
                # Курьер2 (доставка получателю с POST2)
                cell_id = order["dest_cell_id"]
                expected_status = "order_courier2_assigned"
                
                # FSM переход 1: Order (курьер2 открыл ячейку)
                self.db.order_courier2_pickup_parcel(order_id, courier_id)
                
            else:
                return False, f"CANNOT_DETERMINE_LEG_FOR_STATUS_{order['status']}"
            
            if not cell_id:
                return False, f"NO_CELL_FOR_LEG_{leg}"
            
            # FSM переход 2: Locker (открыть ячейку)
            # Используем готовый метод с unlock_code (или пустой строкой)
            self.db.open_locker_for_recipient(cell_id, courier_id, unlock_code="")
            
            print(f"[COURIER_CELL] ✅ Курьер ({leg}) открыл ячейку {cell_id} для заказа {order_id}")
            return True, ""
            
        except FsmCallError as e:
            print(f"[COURIER_CELL] ❌ FSM ошибка открытия: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[COURIER_CELL] ❌ Ошибка открытия: {e}")
            self.session.rollback()
            return False, str(e)
    
    def close_cell(self, order_id: int, courier_id: int) -> Tuple[bool, str]:
        """
        Закрывает ячейку и делает переход по заказу.
        
        Курьер1 (pickup leg):
        - db.order_confirm_parcel_in() → order_parcel_confirmed
        - db.close_locker() → locker_occupied
        
        Курьер2 (delivery leg):
        - db.order_courier2_delivered_parcel() → order_courier2_parcel_delivered
        - db.close_locker_pickup() → locker_closed_empty
        
        Args:
            order_id: ID заказа
            courier_id: ID курьера
        
        Returns:
            (success, error_code)
        """
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            
            # Определяем leg
            leg = self._determine_leg(order["status"])
            
            if leg == "pickup":
                # Курьер1 закрывает POST1
                cell_id = order["source_cell_id"]
                expected_status = "order_courier_has_parcel"
                
                # FSM переход 1: Order (подтвердить посылку в ячейке)
                self.db.order_confirm_parcel_in(order_id, courier_id)
                
                # FSM переход 2: Locker (закрыть ячейку → locker_occupied)
                self.db.close_locker(cell_id, courier_id)
                
            elif leg == "delivery":
                # Курьер2 закрывает POST2
                cell_id = order["dest_cell_id"]
                expected_status = "order_courier2_has_parcel"
                
                # FSM переход 1: Order (курьер2 доставил посылку)
                self.db.order_courier2_delivered_parcel(order_id, courier_id)
                
                # FSM переход 2: Locker (закрыть ячейку → locker_closed_empty)
                self.db.close_locker_pickup(cell_id, courier_id)
                
            else:
                return False, f"CANNOT_DETERMINE_LEG_FOR_STATUS_{order['status']}"
            
            if not cell_id:
                return False, f"NO_CELL_FOR_LEG_{leg}"
            
            print(f"[COURIER_CELL] ✅ Курьер ({leg}) закрыл ячейку {cell_id} для заказа {order_id}")
            return True, ""
            
        except FsmCallError as e:
            print(f"[COURIER_CELL] ❌ FSM ошибка закрытия: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[COURIER_CELL] ❌ Ошибка закрытия: {e}")
            self.session.rollback()
            return False, str(e)

class CourierErrorActions:
    """
    Технические действия курьеров: отмена заказа, ошибки с ячейками.
    """
    
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session
    
    def cancel_order(self, order_id: int, courier_id: int) -> Tuple[bool, str]:
        """
        Отмена заказа курьером (используя готовые методы).
        
        Курьер1: db.order_courier1_cancel() → order_created
        Курьер2: db.order_courier2_cancel() → order_arrived_at_post2
        """
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            
            status = order["status"]
            
            if status == "order_courier1_assigned":
                # Отмена курьером1
                self.db.order_courier1_cancel(order_id, courier_id)
                print(f"[COURIER_ERROR] ✅ Курьер1 отменил заказ {order_id}")
                
            elif status == "order_courier2_assigned":
                # Отмена курьером2
                self.db.order_courier2_cancel(order_id, courier_id)
                print(f"[COURIER_ERROR] ✅ Курьер2 отменил заказ {order_id}")
                
            else:
                return False, f"CANNOT_CANCEL_FROM_STATUS_{status}"
            
            return True, ""
            
        except FsmCallError as e:
            print(f"[COURIER_ERROR] ❌ FSM ошибка отмены: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[COURIER_ERROR] ❌ Ошибка отмены: {e}")
            self.session.rollback()
            return False, str(e)
    
    def locker_error(self, order_id: int, courier_id: int) -> Tuple[bool, str]:
        """
        Ячейка не открылась или не закрылась.
        
        Locker: db.locker_not_closed() → locker_error
        """
        try:
            order = self.db.get_order(order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"
            
            # Определяем ячейку по статусу
            status = order["status"]
            
            if status in ["order_courier1_assigned", "order_courier_has_parcel"]:
                cell_id = order["source_cell_id"]
            elif status in ["order_courier2_assigned", "order_courier2_has_parcel"]:
                cell_id = order["dest_cell_id"]
            else:
                return False, f"CANNOT_REPORT_ERROR_FROM_STATUS_{status}"
            
            if not cell_id:
                return False, "NO_CELL_ID"
            
            # FSM переход: locker_opened → locker_error
            self.db.locker_not_closed(cell_id, courier_id)
            
            print(f"[COURIER_ERROR] ⚠️ Ошибка с ячейкой {cell_id} для заказа {order_id}")
            return True, ""
            
        except FsmCallError as e:
            print(f"[COURIER_ERROR] ❌ FSM ошибка: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[COURIER_ERROR] ❌ Ошибка: {e}")
            self.session.rollback()
            return False, str(e)
    
    def cancel_cell_reservation(self, cell_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Отмена резерва ячейки.
        
        Locker: db.cancel_locker_reservation() → locker_free
        """
        try:
            self.db.cancel_locker_reservation(cell_id, user_id)
            print(f"[COURIER_ERROR] ✅ Отменён резерв ячейки {cell_id}")
            return True, ""
            
        except FsmCallError as e:
            print(f"[COURIER_ERROR] ❌ FSM ошибка отмены резерва: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[COURIER_ERROR] ❌ Ошибка отмены резерва: {e}")
            self.session.rollback()
            return False, str(e)

# ================= РАБОТА ОПЕРАТОРА =====================
class OperatorActions:
    """
    Действия оператора: обслуживание ячеек, управление системой.
    """
    
    def __init__(self, db: DatabaseLayer):
        self.db = db
        self.session = db.session
    
    def reset_locker(self, cell_id: int, operator_id: int) -> Tuple[bool, str]:
        """
        Сброс ячейки в свободное состояние.
        Locker: * → locker_free
        FSM: locker_reset
        
        Используется когда:
        - Ячейка зависла в неправильном статусе
        - Нужно принудительно освободить ячейку
        """
        try:
            self.db.reset_locker(cell_id, operator_id)
            print(f"[OPERATOR] ✅ Ячейка {cell_id} сброшена в locker_free")
            return True, ""
            
        except FsmCallError as e:
            print(f"[OPERATOR] ❌ FSM ошибка сброса: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[OPERATOR] ❌ Ошибка сброса ячейки: {e}")
            self.session.rollback()
            return False, str(e)
    
    def set_locker_maintenance(self, cell_id: int, operator_id: int) -> Tuple[bool, str]:
        """
        Перевод ячейки в обслуживание.
        Locker: * → locker_maintenance
        FSM: locker_set_locker_to_maintenance
        
        Используется когда:
        - Ячейка неисправна (замок, датчик)
        - Требуется физический ремонт
        - Нужно временно вывести ячейку из работы
        """
        try:
            self.db.set_locker_maintenance(cell_id, operator_id)
            print(f"[OPERATOR] ✅ Ячейка {cell_id} переведена в locker_maintenance")
            return True, ""
            
        except FsmCallError as e:
            print(f"[OPERATOR] ❌ FSM ошибка перевода в обслуживание: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[OPERATOR] ❌ Ошибка перевода в обслуживание: {e}")
            self.session.rollback()
            return False, str(e)
    
    def force_cancel_order(self, order_id: int, operator_id: int) -> Tuple[bool, str]:
        """
        Принудительная отмена заказа оператором (если есть такой FSM action).
        """
        try:
            # Если в базе есть order_operator_cancel или подобное
            # self.db.order_operator_cancel(order_id, operator_id)
            
            # Временно через универсальный метод:
            self.db.call_fsm_action("order", order_id, "order_cancel_reservation", operator_id)
            print(f"[OPERATOR] ✅ Заказ {order_id} отменён оператором")
            return True, ""
            
        except FsmCallError as e:
            print(f"[OPERATOR] ❌ FSM ошибка отмены заказа: {e}")
            self.session.rollback()
            return False, str(e)
        except Exception as e:
            print(f"[OPERATOR] ❌ Ошибка отмены заказа: {e}")
            self.session.rollback()
            return False, str(e)
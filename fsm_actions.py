# fsm_actions.py

from typing import Tuple, Optional
from sqlalchemy import text
from db_layer import DatabaseLayer, DbLayerError


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

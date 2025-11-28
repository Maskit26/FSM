"""
ORM слой для работы с базой данных логистической системы.

FSM имена: trip_vzyat_reis, trip_start_trip (с подчёркиваниями!)
Все поля: from_city, to_city, driver_user_id (с подчёркиваниями!)

Требования:
pip install sqlalchemy mysql-connector-python

Использование:
from db_layer import DatabaseLayer, DbLayerError, FsmCallError

db = DatabaseLayer(port=3307, password="root")
order_id = db.create_order(...)
trip_id, success, msg = db.assign_order_to_trip_smart(order_id, "Москва", "СПб")
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import mysql.connector
from mysql.connector import Error
import traceback


class DbLayerError(Exception):
    """Базовое исключение для ошибок db_layer."""
    pass


class FsmCallError(DbLayerError):
    """Ошибка вызова FSM."""
    pass


class DatabaseLayer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3307,
        database: str = "testdb",
        user: str = "root",
        password: str = "root",
        echo: bool = False,
    ):
        """Инициализация подключения."""
        connection_string = (
            f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        )

        # ОДИН раз создаём engine с правильными параметрами
        self.engine = create_engine(
            connection_string,
            echo=echo,
            future=True,
            pool_pre_ping=True,
            pool_recycle=1800,
        )

        Session = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.session = Session()

        self._raw_config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }

    # ==================== FSM БАЗОВЫЙ ВЫЗОВ ====================

    def call_fsm_action(
        self,
        entity_type: str,
        entity_id: int,
        action_name: str,
        user_id: int,
        extra_id: Optional[str] = None,
    ) -> bool:
        """Вызов FSM процедуры fsm_perform_action."""
        try:
            conn = mysql.connector.connect(**self._raw_config)
            cursor = conn.cursor()
            cursor.callproc(
                "fsm_perform_action",
                [entity_type, entity_id, action_name, user_id, extra_id or None],
            )
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            conn.commit()
            cursor.close()
            conn.close()

            if results and len(results) > 0:
                first_result = results[0]
                if isinstance(first_result, tuple) and len(first_result) > 0:
                    result_text = str(first_result[0])
                    if result_text.startswith("FSM action "):
                        return True
                    raise FsmCallError(result_text)
            raise FsmCallError(
                f"FSM {action_name}: нет результата от fsm_perform_action"
            )
        except Error as e:
            raise FsmCallError(f"FSM {action_name}: {e}") from e

    # ==================== FSM ОБЁРТКИ (TRIP / ORDER / LOCKER) ====================

    # ---------- TRIP / РЕЙСЫ ----------

    def driver_take_trip(self, trip_id: int, driver_id: int) -> bool:
        """Водитель берет рейс (FSM: trip_vzyat_reis)."""
        trip_data = self.get_trip(trip_id)
        if not trip_data or trip_data.get("active", 0) == 0:
            raise FsmCallError(
                f"Рейс {trip_id} неактивен (active={trip_data.get('active', 0) if trip_data else None})"
            )
        return self.call_fsm_action("trip", trip_id, "trip_vzyat_reis", driver_id)

    def start_trip(self, trip_id: int, driver_id: int) -> bool:
        """Старт рейса (FSM: trip_start_trip)."""
        trip_data = self.get_trip(trip_id)
        if not trip_data or trip_data.get("active", 0) == 0:
            raise FsmCallError(f"Рейс {trip_id} неактивен")
        return self.call_fsm_action("trip", trip_id, "trip_start_trip", driver_id)

    def trip_assign_driver(self, trip_id: int, operator_id: int) -> bool:
        """Назначение водителя на рейс (FSM: trip_assign_voditel)."""
        return self.call_fsm_action("trip", trip_id, "trip_assign_voditel", operator_id)

    def trip_start_pickup(self, trip_id: int, driver_id: int) -> bool:
        """Начало этапа забора посылок (FSM: trip_start_pickup)."""
        return self.call_fsm_action("trip", trip_id, "trip_start_pickup", driver_id)

    def trip_confirm_pickup(self, trip_id: int, driver_id: int) -> bool:
        """Подтверждение, что посылки забраны (FSM: trip_confirm_pickup)."""
        return self.call_fsm_action("trip", trip_id, "trip_confirm_pickup", driver_id)

    def trip_confirm_delivery(self, trip_id: int, driver_id: int) -> bool:
        """Подтверждение доставки по рейсу (FSM: trip_confirm_delivery)."""
        return self.call_fsm_action("trip", trip_id, "trip_confirm_delivery", driver_id)

    def trip_complete_trip(self, trip_id: int, driver_id: int) -> bool:
        """Завершение рейса (FSM: trip_complete_trip)."""
        return self.call_fsm_action("trip", trip_id, "trip_complete_trip", driver_id)

    def trip_end_delivery(self, trip_id: int, driver_id: int) -> bool:
        """Завершение этапа доставки (FSM: trip_end_delivery)."""
        return self.call_fsm_action("trip", trip_id, "trip_end_delivery", driver_id)

    def trip_report_driver_not_found(self, trip_id: int, user_id: int) -> bool:
        """Сообщение, что водитель не найден (FSM: trip_report_driver_not_found)."""
        return self.call_fsm_action("trip", trip_id, "trip_report_driver_not_found", user_id)

    def trip_report_failure(self, trip_id: int, user_id: int) -> bool:
        """Сообщение о сбое рейса (FSM: trip_report_failure)."""
        return self.call_fsm_action("trip", trip_id, "trip_report_failure", user_id)

    def trip_request_manual_intervention(self, trip_id: int, user_id: int) -> bool:
        """Запрос ручного вмешательства по рейсу (FSM: trip_request_manual_intervention)."""
        return self.call_fsm_action("trip", trip_id, "trip_request_manual_intervention", user_id)

    # ---------- ORDER / ЗАКАЗЫ ----------

    def assign_courier_to_order(self, order_id: int, courier_id: int) -> bool:
        """Назначение первого курьера (FSM: order_assign_courier1_to_order)."""
        return self.call_fsm_action(
            "order", order_id, "order_assign_courier1_to_order", courier_id
        )

    def set_courier1_in_stage(self, order_id: int, courier_id: int):
        """
        Устанавливает курьера для плеча pickup (courier1) в stage_orders.
        Пишет только в courier_user_id для строки с leg='pickup'.
        """
        session = self.session
        session.execute(
            text(
                """
                UPDATE stage_orders
                SET courier_user_id = :cid
                WHERE orderid = :oid
                AND leg = 'pickup'
                """
            ),
            {"cid": courier_id, "oid": order_id},
        )
        session.commit()

    def set_courier2_in_stage(self, order_id: int, courier_id: int):
        """
        Устанавливает курьера для плеча delivery (courier2) в stage_orders.
        Создаёт/обновляет строку с leg='delivery', пишет только в courier_user_id.
        """
        session = self.session

        # Берём tripid из pickup-строки
        row = session.execute(
            text(
                """
                SELECT trip_id
                FROM stage_orders
                WHERE order_id = :oid AND leg = 'pickup'
                LIMIT 1
                """
            ),
            {"oid": order_id},
        ).fetchone()

        if not row:
            raise DbLayerError(f"Для заказа {order_id} не найдена строка pickup в stageorders")

        trip_id = row[0]

        session.execute(
            text(
                """
                INSERT INTO stage_orders (trip_id, order_id, leg, courier_user_id)
                VALUES (:trip_id, :order_id, 'delivery', :cid) AS new
                ON DUPLICATE KEY UPDATE
                    courier_user_id = new.courier_user_id
                """
            ),
            {"trip_id": trip_id, "order_id": order_id, "cid": courier_id},
        )
        session.commit()

    def order_pickup_by_driver(self, order_id: int, driver_id: int) -> bool:
        """Водитель забирает заказ из постамата (FSM: order_pickup_by_voditel)."""
        return self.call_fsm_action(
            "order", order_id, "order_pickup_by_voditel", driver_id
        )

    def order_client_will_deliver(self, order_id: int, user_id: int) -> bool:
        """Клиент выбирает самодоставку A→B (FSM: order_client_will_deliver)."""
        return self.call_fsm_action(
            "order", order_id, "order_client_will_deliver", user_id
        )

    def order_timeout_reservation(self, order_id: int, user_id: int) -> bool:
        """Таймаут резерва заказа (FSM: order_timeout_reservation)."""
        return self.call_fsm_action(
            "order", order_id, "order_timeout_reservation", user_id
        )

    def order_timeout_confirmation(self, order_id: int, user_id: int) -> bool:
        """Таймаут подтверждения курьером (FSM: order_timeout_confirmation)."""
        return self.call_fsm_action(
            "order", order_id, "order_timeout_confirmation", user_id
        )

    def order_reserve_for_client_A_to_B(self, order_id: int, user_id: int) -> bool:
        """Резерв слота A→B клиентом (FSM: order_reserve_for_client_A_to_B)."""
        return self.call_fsm_action(
            "order", order_id, "order_reserve_for_client_A_to_B", user_id
        )

    def order_reserve_for_courier_A_to_B(self, order_id: int, courier_id: int) -> bool:
        """Резерв слота A→B курьером (FSM: order_reserve_for_courier_A_to_B)."""
        return self.call_fsm_action(
            "order", order_id, "order_reserve_for_courier_A_to_B", courier_id
        )

    def order_confirm_parcel_in(self, order_id: int, user_id: int) -> bool:
        """Подтверждение, что посылка находится в нужном месте (FSM: order_confirm_parcel_in)."""
        return self.call_fsm_action(
            "order", order_id, "order_confirm_parcel_in", user_id
        )

    def order_mark_parcel_submitted(self, order_id: int, user_id: int) -> bool:
        """Фиксация, что посылка сдана (FSM: order_parcel_submitted)."""
        return self.call_fsm_action(
            "order", order_id, "order_parcel_submitted", user_id
        )

    def order_courier1_pickup_parcel(self, order_id: int, courier_id: int) -> bool:
        """Курьер1 забирает посылку (FSM: order_courier_pickup_parcel)."""
        return self.call_fsm_action(
            "order", order_id, "order_courier_pickup_parcel", courier_id
        )

    def order_start_transit(self, order_id: int, user_id: int) -> bool:
        """Начало транзита заказа к второму постамату (FSM: order_start_transit)."""
        return self.call_fsm_action("order", order_id, "order_start_transit", user_id)

    def order_arrive_at_post2(self, order_id: int, user_id: int) -> bool:
        """Заказ прибыл во второй постамат (FSM: order_arrive_at_post2)."""
        return self.call_fsm_action("order", order_id, "order_arrive_at_post2", user_id)

    def assign_courier2_to_order(self, order_id: int, courier2_id: int) -> bool:
        """Назначение второго курьера (FSM: order_assign_courier2_to_order)."""
        return self.call_fsm_action(
            "order", order_id, "order_assign_courier2_to_order", courier2_id
        )

    def order_courier2_pickup_parcel(self, order_id: int, courier2_id: int) -> bool:
        """Курьер2 забирает посылку (FSM: order_courier2_pickup_parcel)."""
        return self.call_fsm_action(
            "order", order_id, "order_courier2_pickup_parcel", courier2_id
        )

    def order_courier2_delivered_parcel(self, order_id: int, courier2_id: int) -> bool:
        """Курьер2 доставил посылку (FSM: order_courier2_delivered_parcel)."""
        return self.call_fsm_action(
            "order", order_id, "order_courier2_delivered_parcel", courier2_id
        )

    def order_pickup_by_recipient(self, order_id: int, recipient_id: int) -> bool:
        """Получатель забирает заказ (FSM: order_pickup_poluchatel)."""
        return self.call_fsm_action(
            "order", order_id, "order_pickup_poluchatel", recipient_id
        )

    def order_mark_delivered_parcel(self, order_id: int, user_id: int) -> bool:
        """Заказ отмечен как доставленный (FSM: order_delivered_parcel)."""
        return self.call_fsm_action(
            "order", order_id, "order_delivered_parcel", user_id
        )

    def order_recipient_confirmed(self, order_id: int, recipient_id: int) -> bool:
        """Получатель подтвердил получение (FSM: order_recipient_confirmed)."""
        return self.call_fsm_action(
            "order", order_id, "order_recipient_confirmed", recipient_id
        )

    def order_report_parcel_missing(self, order_id: int, user_id: int) -> bool:
        """Отчёт: посылка пропала (FSM: order_report_parcel_missing)."""
        return self.call_fsm_action(
            "order", order_id, "order_report_parcel_missing", user_id
        )

    def order_report_delivery_failed(self, order_id: int, user_id: int) -> bool:
        """Отчёт: доставка не удалась (FSM: order_report_delivery_failed)."""
        return self.call_fsm_action(
            "order", order_id, "order_report_delivery_failed", user_id
        )

    def order_request_manual_intervention(self, order_id: int, user_id: int) -> bool:
        """Запрос ручного вмешательства по заказу (FSM: order_request_manual_intervention)."""
        return self.call_fsm_action(
            "order", order_id, "order_request_manual_intervention", user_id
        )

    def order_courier1_cancel(self, order_id: int, courier1_id: int) -> bool:
        """Курьер1 отменяет доставку (FSM: order_courier1_cancel)."""
        return self.call_fsm_action(
            "order", order_id, "order_courier1_cancel", courier1_id
        )

    def order_courier2_cancel(self, order_id: int, courier2_id: int) -> bool:
        """Курьер2 отменяет доставку (FSM: order_courier2_cancel)."""
        return self.call_fsm_action(
            "order", order_id, "order_courier2_cancel", courier2_id
        )

    def order_timeout_no_pickup(self, order_id: int, user_id: int) -> bool:
        """Таймаут, когда никто не забрал заказ (FSM: order_timeout_no_pickup)."""
        return self.call_fsm_action(
            "order", order_id, "order_timeout_no_pickup", user_id
        )

    def order_cancel_reservation(self, order_id: int, user_id: int) -> bool:
        """Отмена резерва заказа (FSM: order_cancel_reservation)."""
        return self.call_fsm_action(
            "order", order_id, "order_cancel_reservation", user_id
        )

    # ---------- LOCKER / ЯЧЕЙКИ ----------

    def open_locker_for_recipient(
        self, cell_id: int, user_id: int, unlock_code: str
    ) -> bool:
        """Открытие ячейки (FSM: locker_open_locker)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_open_locker", user_id, unlock_code
        )

    def close_locker(self, cell_id: int, user_id: int) -> bool:
        """Закрытие ячейки (FSM: locker_close_locker)."""
        return self.call_fsm_action("locker", cell_id, "locker_close_locker", user_id)

    def close_locker_pickup(self, cell_id: int, user_id: int) -> bool:
        """Закрытие ячейки после забора посылки (FSM: locker_close_pickup)."""
        return self.call_fsm_action("locker", cell_id, "locker_close_pickup", user_id)

    def reserve_locker_cell(self, cell_id: int, user_id: int) -> bool:
        """Резерв ячейки под заказ (FSM: locker_reserve_cell)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_reserve_cell", user_id
        )

    def reset_locker(self, cell_id: int, user_id: int) -> bool:
        """Сброс ячейки в свободное состояние (FSM: locker_reset)."""
        return self.call_fsm_action("locker", cell_id, "locker_reset", user_id)

    def set_locker_maintenance(self, cell_id: int, user_id: int) -> bool:
        """Перевод ячейки в обслуживание (FSM: locker_set_locker_to_maintenance)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_set_locker_to_maintenance", user_id
        )

    def cancel_locker_reservation(self, cell_id: int, user_id: int) -> bool:
        """Отмена резерва ячейки (FSM: locker_cancel_reservation)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_cancel_reservation", user_id
        )

    def confirm_locker_parcel_not_found(self, cell_id: int, user_id: int) -> bool:
        """Подтверждение, что посылка не найдена в открытой ячейке (FSM: locker_confirm_parcel_not_found)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_confirm_parcel_not_found", user_id
        )

    def confirm_locker_parcel_out_driver(self, cell_id: int, user_id: int) -> bool:
        """Водитель забрал посылку из ячейки (FSM: locker_confirm_parcel_out)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_confirm_parcel_out", user_id
        )

    def confirm_locker_parcel_out_recipient(self, cell_id: int, user_id: int) -> bool:
        """Получатель забрал посылку из ячейки (FSM: locker_confirm_parcel_out_recipient)."""
        return self.call_fsm_action(
            "locker", cell_id, "locker_confirm_parcel_out_recipient", user_id
        )

    def locker_not_closed(self, cell_id: int, user_id: int) -> bool:
        """Фиксация незакрытой ячейки (FSM: locker_dont_closed)."""
        return self.call_fsm_action("locker", cell_id, "locker_dont_closed", user_id)

    # ==================== КНОПКИ ====================

    def get_buttons(
        self, user_role: str, entity_type: str, entity_id: int
    ) -> List[Dict]:
        """Доступные кнопки для роли и статуса."""
        session = self.session
        status_query = {
            "order": text("SELECT status FROM orders WHERE id = :id"),
            "trip": text("SELECT status, active FROM trips WHERE id = :id"),
            "locker": text("SELECT status FROM locker_cells WHERE id = :id"),
        }
        if entity_type not in status_query:
            raise DbLayerError(f"Неизвестный entity_type: {entity_type}")

        result = session.execute(
            status_query[entity_type], {"id": entity_id}
        ).fetchone()
        if not result:
            raise DbLayerError(f"Сущность {entity_type}/{entity_id} не найдена")

        if entity_type == "trip":
            current_status, active_flag = result
            if active_flag == 0 and current_status in ["trip_created", "trip_assigned"]:
                effective_state = current_status + "_inactive"
            else:
                effective_state = current_status
        else:
            effective_state = result[0]

        rows = session.execute(
            text(
                "SELECT button_name, is_enabled "
                "FROM button_states "
                "WHERE user_role = :role AND entity_state = :state"
            ),
            {"role": user_role, "state": effective_state},
        ).fetchall()

        # Fallback для неактивных рейсов
        if not rows and entity_type == "trip" and "_inactive" in effective_state:
            rows = session.execute(
                text(
                    "SELECT button_name, is_enabled "
                    "FROM button_states "
                    "WHERE user_role = :role AND entity_state = :state"
                ),
                {"role": user_role, "state": current_status},
            ).fetchall()

        return [
            {
                "button_name": row[0],
                "is_enabled": (
                    row[1] == "active" if isinstance(row[1], str) else bool(row[1])
                ),
            }
            for row in rows
        ]

    def get_active_buttons(
        self, user_role: str, entity_type: str, entity_id: int
    ) -> List[str]:
        """Имена только активных кнопок."""
        all_buttons = self.get_buttons(user_role, entity_type, entity_id)
        return [b["button_name"] for b in all_buttons if b["is_enabled"]]

    def get_active_nonbasic_buttons(
        self,
        user_role: str,
        entity_type: str,
        entity_id: int,
        basic_buttons: List[str],
    ) -> List[Dict]:
        """Активные кнопки, исключая базовые."""
        all_buttons = self.get_buttons(user_role, entity_type, entity_id)
        return [
            b
            for b in all_buttons
            if b.get("is_enabled") and b.get("button_name") not in basic_buttons
        ]

    # ==================== СПРАВОЧНИКИ / ПОЛЬЗОВАТЕЛИ / ПОСТАМАТЫ ====================

    def create_user(self, user_id: int, name: str, role: str) -> bool:
        """Создать пользователя (идемпотентно через INSERT IGNORE)."""
        try:
            self.session.execute(
                text(
                    "INSERT IGNORE INTO users (id, name, role_name) "
                    "VALUES (:id, :name, :role)"
                ),
                {"id": user_id, "name": name, "role": role},
            )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Пользователь {user_id}: {e}") from e

    def get_user_role(self, user_id: int) -> Optional[str]:
        """Вернуть роль пользователя по ID."""
        row = self.session.execute(
            text("SELECT role_name FROM users WHERE id = :id"),
            {"id": user_id},
        ).fetchone()
        return row[0] if row else None

    def create_locker_model(
        self,
        model_id: int,
        model_name: str,
        cell_count_s: int = 10,
        cell_count_m: int = 5,
        cell_count_l: int = 2,
        cell_count_p: int = 1,
    ) -> bool:
        """Создать модель постамата."""
        try:
            self.session.execute(
                text(
                    "INSERT IGNORE INTO locker_models "
                    "(id, model_name, cell_count_s, cell_count_m, cell_count_l, cell_count_p) "
                    "VALUES (:id, :name, :count_s, :count_m, :count_l, :count_p)"
                ),
                {
                    "id": model_id,
                    "name": model_name,
                    "count_s": cell_count_s,
                    "count_m": cell_count_m,
                    "count_l": cell_count_l,
                    "count_p": cell_count_p,
                },
            )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Модель {model_id}: {e}") from e

    def create_locker(
        self, locker_id: int, locker_code: str, location_address: str, model_id: int = 1
    ) -> bool:
        """Создать постамат."""
        try:
            self.session.execute(
                text(
                    "INSERT IGNORE INTO lockers "
                    "(id, model_id, locker_code, location_address) "
                    "VALUES (:id, :model_id, :code, :address)"
                ),
                {
                    "id": locker_id,
                    "model_id": model_id,
                    "code": locker_code,
                    "address": location_address,
                },
            )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Постамат {locker_id}: {e}") from e

    def create_locker_cell(
        self, locker_id: int, cell_code: str, cell_type: str = "S"
    ) -> Optional[int]:
        """Создать ячейку постамата (или вернуть существующую)."""
        try:
            existing = self.session.execute(
                text(
                    "SELECT id FROM locker_cells "
                    "WHERE locker_id = :l_id AND cell_code = :c_code"
                ),
                {"l_id": locker_id, "c_code": cell_code},
            ).fetchone()
            if existing:
                return existing[0]

            self.session.execute(
                text(
                    "INSERT INTO locker_cells "
                    "(locker_id, cell_code, cell_type, status) "
                    "VALUES (:locker_id, :cell_code, :cell_type, 'locker_free')"
                ),
                {
                    "locker_id": locker_id,
                    "cell_code": cell_code,
                    "cell_type": cell_type,
                },
            )
            row = self.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
            self.session.commit()
            return int(row[0]) if row and row[0] else None
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Ячейка {cell_code}: {e}") from e

    def find_free_cell(self, locker_id: int) -> Optional[int]:
        """Найти любую свободную ячейку в постамате."""
        row = self.session.execute(
            text(
                "SELECT id FROM locker_cells "
                "WHERE locker_id = :locker_id AND status = 'locker_free' "
                "LIMIT 1"
            ),
            {"locker_id": locker_id},
        ).fetchone()
        return row[0] if row else None   

    def get_lockers(self) -> List[Dict]:
        """
        Получить список всех постаматов.

        Возвращает:
            [
                {
                    "id": 1,
                    "locker_code": "POST1",
                    "location_address": "Москва, Точка #1",
                    "status": "locker_active",
                    "latitude": 55.123456,
                    "longitude": 37.123456,
                },
                ...
            ]
        """
        rows = self.session.execute(
            text(
                """
                SELECT
                    id,
                    locker_code,
                    location_address,
                    status,
                    latitude,
                    longitude
                FROM lockers
                ORDER BY id ASC
                """
            )
        ).fetchall()

        return [
            {
                "id": row[0],
                "locker_code": row[1],
                "location_address": row[2],
                "status": row[3],
                "latitude": row[4],
                "longitude": row[5],
            }
            for row in rows
        ]

    def get_locker_cells_by_status(
        self, locker_id: int, status: str
    ) -> List[Dict]:
        """Вернуть ячейки постамата по статусу."""
        rows = self.session.execute(
            text(
                "SELECT id, cell_code, cell_type, status, current_order_id "
                "FROM locker_cells "
                "WHERE locker_id = :locker_id AND status = :status"
            ),
            {"locker_id": locker_id, "status": status},
        ).fetchall()
        return [
            {
                "id": r[0],
                "cell_code": r[1],
                "cell_type": r[2],
                "status": r[3],
                "current_order_id": r[4],
            }
            for r in rows
        ]

    def get_locker_city_by_cell(self, cell_id: int) -> str:
        """
        Получить город по ID ячейки (парсит из location_address).
        
        Args:
            cell_id: ID ячейки постамата
            
        Returns:
            Город (например: "Москва")
            
        Example:
            city = db.get_locker_city_by_cell(1)  # "Москва"
        """
        result = self.session.execute(text("""
            SELECT l.location_address 
            FROM locker_cells lc
            JOIN lockers l ON l.id = lc.locker_id
            WHERE lc.id = :cell_id
        """), {"cell_id": cell_id}).scalar()
        
        if not result:
            raise DbLayerError(f"Ячейка {cell_id} не найдена или у постамата нет адреса")
        
        # Парсим: "Москва, Ленина 10" → "Москва"
        return result.split(",")[0].strip()

    def clear_locker_cells(self, locker_id: int) -> bool:
        """Удалить все ячейки постамата (осторожно)."""
        try:
            self.session.execute(
                text("DELETE FROM locker_cells WHERE locker_id = :locker_id"),
                {"locker_id": locker_id},
            )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Ячейки постамата {locker_id}: {e}") from e

    def reserve_cells_for_order(
        self,
        order_id: int,
        source_cell_id: int,
        dest_cell_id: int,
        source_code: Optional[str] = None,
        dest_code: Optional[str] = None,
    ) -> bool:
        """Зарезервировать ячейки под заказ (обновить статус и current_order_id, опционально unlock_code)."""
        try:
            self.session.execute(
                text(
                    "UPDATE locker_cells "
                    "SET status = 'locker_reserved', current_order_id = :order_id "
                    "WHERE id IN (:source_id, :dest_id)"
                ),
                {
                    "order_id": order_id,
                    "source_id": source_cell_id,
                    "dest_id": dest_cell_id,
                },
            )
            if source_code:
                self.session.execute(
                    text(
                        "UPDATE locker_cells "
                        "SET unlock_code = :code "
                        "WHERE id = :cell_id"
                    ),
                    {"code": source_code, "cell_id": source_cell_id},
                )
            if dest_code:
                self.session.execute(
                    text(
                        "UPDATE locker_cells "
                        "SET unlock_code = :code "
                        "WHERE id = :cell_id"
                    ),
                    {"code": dest_code, "cell_id": dest_cell_id},
                )
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Резерв ячеек для заказа {order_id}: {e}") from e

    # ==================== ЗАКАЗЫ ====================

    def create_order(
        self,
        description: str,
        source_cell_id: Optional[int],
        dest_cell_id: Optional[int],
        from_city: str,
        to_city: str,
        pickup_type: str = "courier",     # ← НОВОЕ
        delivery_type: str = "courier",   # ← ОБНОВЛЕНО
    ) -> int:
        """
        Создать заказ.
        
        Args:
            description: Описание заказа
            source_cell_id: ID ячейки отправления
            dest_cell_id: ID ячейки назначения
            from_city: Город отправления
            to_city: Город назначения
            pickup_type: Как забрать у отправителя ('self' | 'courier')
            delivery_type: Как доставить получателю ('self' | 'courier')
        
        Returns:
            ID созданного заказа
        """
        try:
            self.session.execute(
                text(
                    "INSERT INTO orders "
                    "(description, from_city, to_city, source_cell_id, dest_cell_id, "
                    "pickup_type, delivery_type, status) "
                    "VALUES (:desc, :from_city, :to_city, :source_cell_id, :dest_cell_id, "
                    ":pickup_type, :delivery_type, 'order_created')"
                ),
                {
                    "desc": description,
                    "from_city": from_city,
                    "to_city": to_city,
                    "source_cell_id": source_cell_id,
                    "dest_cell_id": dest_cell_id,
                    "pickup_type": pickup_type,
                    "delivery_type": delivery_type,
                },
            )
            row = self.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
            self.session.commit()
            return int(row[0]) if row and row[0] else 0
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Заказ '{description}': {e}") from e

    def get_order(self, order_id: int) -> Optional[Dict]:
        """Вернуть заказ по ID."""
        row = self.session.execute(
            text(
                "SELECT id, status, description, pickup_type, delivery_type, from_city, to_city, "
                "source_cell_id, dest_cell_id "
                "FROM orders WHERE id = :id"
            ),
            {"id": order_id},
        ).fetchone()
        if row:
            return {
                "id": row[0],
                "status": row[1],
                "description": row[2],
                "pickup_type": row[3],      # ← НОВОЕ
                "delivery_type": row[4],
                "from_city": row[5],
                "to_city": row[6],
                "source_cell_id": row[7],
                "dest_cell_id": row[8],
            }
        return None

    def get_orders_for_route(
        self, from_city: str, to_city: str, statuses: Optional[List[str]] = None
    ) -> List[Dict]:
        """Вернуть заказы по маршруту (опционально фильтруя по статусам)."""
        params: Dict[str, object] = {"from_city": from_city, "to_city": to_city}
        query = (
            "SELECT id, status, description, pickup_type, delivery_type, from_city, to_city, "
            "source_cell_id, dest_cell_id "
            "FROM orders WHERE from_city = :from_city AND to_city = :to_city"
        )
        if statuses:
            placeholders = ", ".join([f":status{i}" for i in range(len(statuses))])
            query += f" AND status IN ({placeholders})"
            params.update({f"status{i}": s for i, s in enumerate(statuses)})

        rows = self.session.execute(text(query), params).fetchall()
        return [
            {
                "id": row[0],
                "status": row[1],
                "description": row[2],
                "pickup_type": row[3],
                "delivery_type": row[4],
                "from_city": row[5],
                "to_city": row[6],
                "source_cell_id": row[7],
                "dest_cell_id": row[8],
            }
            for row in rows
        ]

    def get_all_orders(
        self,
        statuses: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Получить список всех заказов (без привязки к маршруту).
        Optionally: фильтр по статусам.
        """
        query = """
            SELECT
                id,
                status,
                description,
                pickup_type,
                delivery_type,
                from_city,
                to_city,
                source_cell_id,
                dest_cell_id
            FROM orders
            WHERE 1 = 1
        """
        params: Dict[str, object] = {}

        if statuses:
            placeholders = ", ".join(f":status{i}" for i in range(len(statuses)))
            query += f" AND status IN ({placeholders})"
            params.update({f"status{i}": s for i, s in enumerate(statuses)})

        rows = self.session.execute(text(query), params).fetchall()

        return [
            {
                "id": row[0],
                "status": row[1],
                "description": row[2],
                "pickup_type": row[3],
                "delivery_type": row[4],
                "from_city": row[5],
                "to_city": row[6],
                "source_cell_id": row[7],
                "dest_cell_id": row[8],
            }
            for row in rows
        ]

    def get_orders_for_courier(self, courier_id: int) -> List[int]:
        """IDs заказов, в которых участвует курьер (courier1 или courier2)."""
        rows = self.session.execute(
            text(
                "SELECT DISTINCT so.order_id "
                "FROM stage_orders so "
                "WHERE so.courier_user_id = :courier_id"
            ),
            {"courier_id": courier_id},
        ).fetchall()
        return [row[0] for row in rows]

    # ==================== НОВЫЕ МЕТОДЫ: РАЗВИЛКИ FSM ====================

    def start_order_flow(self, order_id: int, user_id: int = 0):
        """
        Запустить FSM flow заказа на основе pickup_type (первая развилка).
        
        Проверяет pickup_type и делает первый FSM переход:
        - pickup_type='self' → order_reserve_for_client_A_to_B
        - pickup_type='courier' → order_reserve_for_courier_A_to_B
        
        Args:
            order_id: ID заказа
            user_id: ID курьера (если pickup_type='courier'), иначе 0
        """
        order = self.get_order(order_id)
        if not order:
            raise DbLayerError(f"Заказ {order_id} не найден")
        
        pickup_type = order.get("pickup_type", "courier")
        
        if pickup_type == "self":
            # Клиент сам несёт
            action = "order_reserve_for_client_A_to_B"
            print(f"[DEBUG] Заказ {order_id}: клиент сам несёт (pickup_type='self')")
        
        elif pickup_type == "courier":
            # Курьер забирает
            action = "order_reserve_for_courier_A_to_B"
            print(f"[DEBUG] Заказ {order_id}: назначен курьер1 для забора (pickup_type='courier')")
        
        else:
            raise DbLayerError(f"Неизвестный pickup_type: {pickup_type}")
        
        # Выполняем FSM переход
        self.call_fsm_action("order", order_id, action, user_id)

    def handle_parcel_confirmed(self, order_id: int):
        """
        Обработка после попадания посылки в постамат2 (вторая развилка).

        Ожидается, что заказ уже в состоянии order_parcel_confirmed_post2.
        НЕ делает FSM-переходов, только логирует ветку по delivery_type.
        """
        order = self.get_order(order_id)
        if not order:
            raise DbLayerError(f"Заказ {order_id} не найден")

        status = order.get("status")
        if status != "order_parcel_confirmed_post2":
            raise DbLayerError(
                f"handle_parcel_confirmed: некорректный статус '{status}', "
                "ожидается 'order_parcel_confirmed_post2'"
            )

        delivery_type = order.get("delivery_type", "self")

        if delivery_type == "self":
            print(f"[DEBUG] Заказ {order_id}: в постамате2, ожидает самовывоз получателем")
            print("[DEBUG] Доступное действие: order_pickup_poluchatel")
        elif delivery_type == "courier":
            print(f"[DEBUG] Заказ {order_id}: в постамате2, доступен на бирже для курьера2")
            print("[DEBUG] Доступное действие: order_assign_courier2_to_order")
        else:
            raise DbLayerError(f"Неизвестный delivery_type: {delivery_type}")


    # ==================== НОВЫЕ МЕТОДЫ: БИРЖИ ====================

    def get_available_orders_for_courier1(self, city: str = None) -> List[Dict]:
        """
        Биржа для курьера1 (забор от клиента).
        
        Показывает заказы:
        - Статус: order_courier_reserved_post1_and_post2
        - pickup_type: courier
        """
        query = """
            SELECT o.id, o.status, o.description, o.from_city, o.to_city,
                l.location_address as source_address,
                lc.cell_code as source_cell_code,
                lc.cell_type as cell_size
            FROM orders o
            JOIN locker_cells lc ON lc.id = o.source_cell_id
            JOIN lockers l ON l.id = lc.locker_id
            WHERE o.status = 'order_courier_reserved_post1_and_post2'  # ← ПРАВИЛЬНЫЙ СТАТУС
            AND o.pickup_type = 'courier'
        """
        
        params = {}
        if city:
            query += " AND o.from_city = :city"
            params["city"] = city
        
        query += " ORDER BY o.created_at ASC"
        
        result = self.session.execute(text(query), params).fetchall()
        
        return [
            {
                "id": row[0],
                "status": row[1],
                "description": row[2],
                "from_city": row[3],
                "to_city": row[4],
                "source_address": row[5],
                "source_cell_code": row[6],
                "cell_size": row[7],
            }
            for row in result
        ]


    def get_available_orders_for_courier2(self, city: str = None) -> List[Dict]:
        """
        Получить заказы для курьера2 (доставка получателю).
        
        Это заказы в статусе order_parcel_confirmed_post2 с delivery_type='courier'.
        
        Args:
            city: Фильтр по городу назначения (опционально)
        
        Returns:
            List[dict]: Список заказов для курьера2
        """
        query = """
            SELECT o.id, o.status, o.description, o.from_city, o.to_city,
                   l.location_address as dest_address,
                   lc.cell_code as dest_cell_code,
                   lc.cell_type as cell_size
            FROM orders o
            JOIN locker_cells lc ON lc.id = o.dest_cell_id
            JOIN lockers l ON l.id = lc.locker_id
            WHERE o.status = 'order_parcel_confirmed_post2'
              AND o.delivery_type = 'courier'
        """
        
        params = {}
        if city:
            query += " AND o.to_city = :city"
            params["city"] = city
        
        query += " ORDER BY o.created_at ASC"
        
        result = self.session.execute(text(query), params).fetchall()
        
        return [
            {
                "id": row[0],
                "status": row[1],
                "description": row[2],
                "from_city": row[3],
                "to_city": row[4],
                "dest_address": row[5],
                "dest_cell_code": row[6],
                "cell_size": row[7],
            }
            for row in result
        ]

    # ==================== РЕЙСЫ ====================

    def create_trip(
        self,
        from_city: str,
        to_city: str,
        driver_user_id: Optional[int] = None,
        description: Optional[str] = None,
        active: int = 0,
    ) -> int:
        """Создать рейс."""
        try:
            self.session.execute(
                text(
                    "INSERT INTO trips "
                    "(driver_user_id, from_city, to_city, status, description, active) "
                    "VALUES (:driver_user_id, :from_city, :to_city, 'trip_created', :description, :active)"
                ),
                {
                    "driver_user_id": driver_user_id,
                    "from_city": from_city,
                    "to_city": to_city,
                    "description": description,
                    "active": active,
                },
            )
            row = self.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
            self.session.commit()
            return int(row[0]) if row and row[0] else 0
        except Exception as e:
            self.session.rollback()
            raise DbLayerError(f"Рейс '{from_city}→{to_city}': {e}") from e

    def get_trip(self, trip_id: int) -> Optional[Dict]:
        """Вернуть рейс по ID."""
        row = self.session.execute(
            text(
                "SELECT id, status, active, from_city, to_city, driver_user_id "
                "FROM trips WHERE id = :id"
            ),
            {"id": trip_id},
        ).fetchone()
        if row:
            return {
                "id": row[0],
                "status": row[1],
                "active": row[2],
                "from_city": row[3],
                "to_city": row[4],
                "driver_user_id": row[5],
            }
        return None

    def get_open_trips_for_route(
        self, from_city: str, to_city: str
    ) -> List[Dict]:
        """Незавершённые рейсы по маршруту."""
        rows = self.session.execute(
            text(
                "SELECT id, status, active, from_city, to_city, driver_user_id "
                "FROM trips "
                "WHERE from_city = :from_city AND to_city = :to_city "
                "  AND status != 'trip_completed'"
            ),
            {"from_city": from_city, "to_city": to_city},
        ).fetchall()
        return [
            {
                "id": row[0],
                "status": row[1],
                "active": row[2],
                "from_city": row[3],
                "to_city": row[4],
                "driver_user_id": row[5],
            }
            for row in rows
        ]

    def get_active_trips_for_driver(self, driver_id: int) -> List[Dict]:
        """Активные незавершённые рейсы водителя."""
        rows = self.session.execute(
            text(
                "SELECT id, status, active, from_city, to_city, driver_user_id "
                "FROM trips "
                "WHERE driver_user_id = :driver_id AND active = 1 "
                "  AND status != 'trip_completed'"
            ),
            {"driver_id": driver_id},
        ).fetchall()
        return [
            {
                "id": row[0],
                "status": row[1],
                "active": row[2],
                "from_city": row[3],
                "to_city": row[4],
                "driver_user_id": row[5],
            }
            for row in rows
        ]

    def get_trip_orders(self, trip_id: int) -> List[int]:
        """Вернуть список order_id, привязанных к рейсу."""
        rows = self.session.execute(
            text("SELECT order_id FROM stage_orders WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        ).fetchall()
        return [row[0] for row in rows]

    def assign_order_to_trip(
        self, order_id: int, trip_id: int
    ) -> Tuple[bool, str]:
        """Привязать заказ к рейсу с валидацией."""
        session = self.session
        try:
            # 1. Заказ не должен быть в активном рейсе
            count = session.execute(
                text(
                    "SELECT COUNT(*) "
                    "FROM stage_orders so "
                    "JOIN trips t ON t.id = so.trip_id "
                    "WHERE so.order_id = :order_id "
                    "  AND t.status NOT IN ('trip_completed', 'trip_failed')"
                ),
                {"order_id": order_id},
            ).scalar()
            if count and count > 0:
                return False, "Заказ уже привязан к активному рейсу"

            # 2. Проверка статуса рейса
            trip_status = session.execute(
                text("SELECT status FROM trips WHERE id = :trip_id"),
                {"trip_id": trip_id},
            ).scalar()
            if not trip_status:
                return False, f"Рейс {trip_id} не найден"
            if trip_status not in ("trip_created", "trip_assigned"):
                return (
                    False,
                    f"Нельзя привязать к рейсу в статусе '{trip_status}'",
                )

            # 3. Лимит 5 заказов на рейс
            trip_count = session.execute(
                text("SELECT COUNT(*) FROM stage_orders WHERE trip_id = :trip_id"),
                {"trip_id": trip_id},
            ).scalar()
            if trip_count is not None and trip_count >= 5:
                return False, "На рейсе уже 5 заказов"

            # 4. Вставка
            session.execute(
                text(
                    "INSERT INTO stage_orders (trip_id, order_id, leg) "
                    "VALUES (:trip_id, :order_id, 'pickup')"
                ),
                {"trip_id": trip_id, "order_id": order_id},
            )

            session.commit()
            return True, "Заказ привязан к рейсу"
        except Exception as e:
            session.rollback()
            raise DbLayerError(f"Ошибка привязки заказа {order_id} к рейсу {trip_id}: {e}") from e

    def assign_order_to_trip_smart(
        self, order_id: int, order_from_city: str, order_to_city: str
    ) -> Tuple[int, bool, str]:
        """
        Умная привязка заказа к рейсу:
        - ищет существующий рейс по маршруту с <5 заказов
        - если не находит, создаёт новый
        """
        session = self.session
        try:
            # 1. Проверка маршрута заказа
            order_route = session.execute(
                text(
                    "SELECT from_city, to_city "
                    "FROM orders WHERE id = :order_id"
                ),
                {"order_id": order_id},
            ).fetchone()
            if not order_route or (
                order_route[0] != order_from_city
                or order_route[1] != order_to_city
            ):
                raise DbLayerError(f"Маршрут заказа {order_id} не совпадает")

            # 2. Ищем существующий рейс (<5 заказов)
            potential_trip = session.execute(
                text(
                    """
                    SELECT t.id
                    FROM trips t
                    LEFT JOIN (
                        SELECT trip_id, COUNT(*) AS cnt
                        FROM stage_orders
                        GROUP BY trip_id
                    ) so ON so.trip_id = t.id
                    WHERE t.from_city = :from_city
                      AND t.to_city = :to_city
                      AND t.status IN ('trip_created', 'trip_assigned')
                      AND (so.cnt IS NULL OR so.cnt < 5)
                    LIMIT 1
                    """
                ),
                {"from_city": order_from_city, "to_city": order_to_city},
            ).fetchone()

            if potential_trip:
                trip_id = potential_trip[0]
                print(f"[DEBUG smart] Используем существующий рейс: {trip_id}")
            else:
                # 3. Создаём новый рейс без водителя
                trip_id = self.create_trip(
                    order_from_city, order_to_city, driver_user_id=None, active=0
                )
                print(f"[DEBUG smart] Создан новый рейс: {trip_id}")

            # 4. Привязываем заказ
            success, msg = self.assign_order_to_trip(order_id, trip_id)
            if (not success) and ("5 заказов" in msg):
                print("[DEBUG smart] Рейс полон, создаём новый рейс")
                trip_id = self.create_trip(
                    order_from_city, order_to_city, driver_user_id=None, active=0
                )
                success, msg = self.assign_order_to_trip(order_id, trip_id)

            return trip_id, success, msg
        except Exception as e:
            session.rollback()
            raise DbLayerError(
                f"Ошибка умной привязки заказа {order_id}: {e}"
            ) from e

    
    def update_trip_active_flags(self, max_orders: int = 5, wait_hours: float = 24.0) -> int:
        """
        Активация рейсов с учётом ТОЛЬКО активных заказов.
        
        Исключает заказы в статусах: cancelled, completed, failed.
        """
        if max_orders <= 0 and wait_hours <= 0:
            return 0

        session = self.session
        threshold = datetime.now() - timedelta(hours=wait_hours)

        # Считаем только активные заказы
        rows = session.execute(
            text(
                """
                SELECT t.id, t.created_at, COUNT(o.id) AS order_count
                FROM trips t
                LEFT JOIN stage_orders so ON so.trip_id = t.id
                LEFT JOIN orders o ON o.id = so.order_id 
                    AND o.status NOT IN ('order_cancelled', 'order_completed', 'order_failed')
                WHERE t.status = 'trip_created' AND t.active = 0
                GROUP BY t.id, t.created_at
                """
            )
        ).fetchall()

        updated = 0
        for trip_id, created_at, order_count in rows:
            make_active = False

            if max_orders > 0 and order_count >= max_orders:
                make_active = True
                print(f"[DEBUG active] Рейс {trip_id}: {order_count} активных заказов → активируем")
            elif wait_hours > 0 and created_at and created_at < threshold:
                make_active = True
                print(f"[DEBUG active] Рейс {trip_id}: ожидание более {wait_hours} ч.")

            if make_active:
                session.execute(
                    text("UPDATE trips SET active = 1 WHERE id = :trip_id"),
                    {"trip_id": trip_id},
                )
                updated += 1

        if updated > 0:
            session.commit()
            print(f"[DEBUG active] Активировано {updated} рейсов")

        return updated

    # ==================== АВТОМАТИЧЕСКАЯ ОБРАБОТКА ТАЙМАУТОВ ====================

    def check_and_process_reservation_timeouts(self, timeout_seconds: int = 30) -> int:
        """
        Находит просроченные резервы и автоматически вызывает order_timeout_reservation.
        
        Returns:
            Количество обработанных заказов
        """
        # Находим просроченные заказы
        expired_orders = self.session.execute(text("""
            SELECT id FROM orders
            WHERE status IN ('order_courier_reserved_post1_and_post2', 'order_client_reserved_post1_and_post2')
              AND TIMESTAMPDIFF(SECOND, created_at, NOW()) > :timeout
        """), {"timeout": timeout_seconds}).fetchall()

        processed = 0
        for (oid,) in expired_orders:
            try:
                # Автоматически вызываем таймаут
                self.call_fsm_action("order", oid, "order_timeout_reservation", 0)  # system user_id=0
                processed += 1
            except Exception as e:
                print(f"Ошибка обработки таймаута заказа {oid}: {e}")

        return processed

    # ==================== СЕРВИСНЫЕ ПРОЦЕДУРЫ ====================

    def clear_test_data(self) -> bool:
        """Вызвать хранимую процедуру clear_test_data()."""
        try:
            conn = mysql.connector.connect(**self._raw_config)
            cursor = conn.cursor()
            cursor.callproc("clear_test_data")
            for result in cursor.stored_results():
                _ = result.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            raise DbLayerError(f"clear_test_data: {e}") from e

    def get_log_counters(self) -> Tuple[int, int, int]:
        """Вернуть счётчики логов: (fsm_errors_log, fsm_action_logs, hardware_command_log)."""
        try:
            error_count = self.session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM fsm_errors_log")
            ).scalar()
            fsm_count = self.session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM fsm_action_logs")
            ).scalar()
            hw_count = self.session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM hardware_command_log")
            ).scalar()
            return int(error_count or 0), int(fsm_count or 0), int(hw_count or 0)
        except Exception as e:
            print(f"⚠ Счётчики логов: {e}")
            return 0, 0, 0

    def close(self) -> None:
        """Закрыть сессию SQLAlchemy."""
        if self.session:
            self.session.close()

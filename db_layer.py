#"""
#ORM слой для работы с базой данных логистической системы.
#
#FSM имена: trip_vzyat_reis, trip_start_trip (с подчёркиваниями!)
#Все поля: from_city, to_city, driver_user_id (с подчёркиваниями!)
#
#Требования:
#pip install sqlalchemy mysql-connector-python

#Использование:
#from db_layer import DatabaseLayer, DbLayerError, FsmCallError

#db = DatabaseLayer(port=3306, password="6eF1zb")
#order_id = db.create_order(...)
#trip_id, success, msg = db.assign_order_to_trip_smart(order_id, "Москва", "СПб")
#"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError

import mysql.connector
from mysql.connector import Error

import logging
import time
import traceback
import json
import requests
import secrets
import hashlib

logger = logging.getLogger(__name__)

class DbLayerError(Exception):
    """Базовое исключение для ошибок db_layer."""
    pass


class FsmCallError(DbLayerError):
    """Ошибка вызова FSM."""
    pass


class DatabaseLayer:
    """Чистый stateless слой доступа к данным. Не хранит engine, не создаёт сессию."""
    pass
        

    # ==================== FSM БАЗОВЫЙ ВЫЗОВ ====================

    def call_fsm_action(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        action_name: str,
        user_id: int,
        extra_id: Optional[str] = None,
    ) -> bool:
        """Стабильный вызов процедуры через raw_cursor с очисткой протокола."""
        
        # Защита от NULL (SQLAlchemy None -> MySQL NULL может вешать драйвер)
        safe_extra_id = extra_id if extra_id is not None else ""

        try:
            # Используем DBAPI курсор для прямого взаимодействия
            connection = session.connection().connection
            cursor = connection.cursor()

            try:
                # Вызываем процедуру
                cursor.callproc("fsm_perform_action", [
                    entity_type, 
                    entity_id, 
                    action_name, 
                    user_id, 
                    safe_extra_id
                ])

                # Вычитываем первый набор данных (результат SELECT из процедуры)
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())

                # Важно: поглощаем все оставшиеся наборы данных, чтобы не было 'Commands out of sync'
                while cursor.nextset():
                    pass

                if results:
                    result_text = str(results[0][0])
                    if "FSM action completed" in result_text:
                        logger.debug("[FSM] Success: %s", result_text)
                        return True
                    else:
                        # Если процедура вернула текст ошибки через SELECT
                        raise DbLayerError(f"FSM Procedure returned: {result_text}")
                
                raise DbLayerError("FSM Procedure: No result returned")

            finally:
                cursor.close()

        except Exception as e:            
            logger.error("[FSM] Call failed: %s", e)
            raise DbLayerError(f"FSM {action_name} failed: {e}") from e

    # ==================== FSM ОБЁРТКИ (TRIP / ORDER / LOCKER) ====================

    # ---------- TRIP / РЕЙСЫ ----------

    def driver_take_trip(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Водитель берет рейс (FSM: trip_vzyat_reis)."""
        trip_data = self.get_trip(session, trip_id)

        if not trip_data or trip_data.get("active", 0) == 0:
            raise FsmCallError(
                f"Рейс {trip_id} неактивен "
                f"(active={trip_data.get('active', 0) if trip_data else None})"
            )

        return self.call_fsm_action(session, "trip", trip_id, "trip_vzyat_reis", driver_id)


    def start_trip(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Старт рейса (FSM: trip_start_trip)."""
        trip_data = self.get_trip(session, trip_id)

        if not trip_data or trip_data.get("active", 0) == 0:
            raise FsmCallError(f"Рейс {trip_id} неактивен")

        return self.call_fsm_action(session, "trip", trip_id, "trip_start_trip", driver_id)


    def trip_assign_driver(self, session: Session, trip_id: int, operator_id: int) -> bool:
        """Назначение водителя на рейс (FSM: trip_assign_voditel)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_assign_voditel", operator_id)


    def trip_start_pickup(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Начало этапа забора посылок (FSM: trip_start_pickup)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_start_pickup", driver_id)


    def trip_confirm_pickup(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Подтверждение, что посылки забраны (FSM: trip_confirm_pickup)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_confirm_pickup", driver_id)


    def trip_confirm_delivery(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Подтверждение доставки по рейсу (FSM: trip_confirm_delivery)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_confirm_delivery", driver_id)


    def complete_trip(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """
        Завершение рейса водителем (FSM: trip_complete_trip).        
        
        """
        logger.debug("complete_trip вызван: trip_id=%s, driver_id=%s", trip_id, driver_id)
        
        trip_data = self.get_trip(session, trip_id)
        
        if not trip_data or trip_data.get("active", 0) == 0:
            raise FsmCallError(f"Рейс {trip_id} неактивен")
        
        if trip_data.get("driver_user_id") != driver_id:
            raise DbLayerError(f"Водитель {driver_id} не назначен на рейс {trip_id}")
        
        return self.call_fsm_action(session, "trip", trip_id, "trip_complete_trip", driver_id)    

    def trip_end_delivery(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Завершение этапа доставки (FSM: trip_end_delivery)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_end_delivery", driver_id)


    def trip_report_driver_not_found(self, session: Session, trip_id: int, user_id: int) -> bool:
        """Сообщение, что водитель не найден (FSM: trip_report_driver_not_found)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_report_driver_not_found", user_id)


    def trip_report_failure(self, session: Session, trip_id: int, user_id: int) -> bool:
        """Сообщение о сбое рейса (FSM: trip_report_failure)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_report_failure", user_id)


    def trip_request_manual_intervention(
        self,
        session: Session,
        trip_id: int,
        user_id: int,
    ) -> bool:
        """Запрос ручного вмешательства по рейсу (FSM: trip_request_manual_intervention)."""
        return self.call_fsm_action(
            session,
            "trip",
            trip_id,
            "trip_request_manual_intervention",
            user_id,
        )


    # ---------- ORDER / ЗАКАЗЫ ----------

    def get_orders_in_trip(self, session: Session, trip_id: int) -> List[int]:
        """Возвращает список order_id, привязанных к trip_id через stage_orders."""
        result = session.execute(
            text("SELECT order_id FROM stage_orders WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        ).fetchall()

        return [row[0] for row in result]    

    def assign_courier_to_order(
        self,
        session: Session,
        order_id: int,
        courier_id: int,
    ) -> bool:
        """Назначение первого курьера (FSM: order_assign_courier1_to_order)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_assign_courier1_to_order",
            courier_id,
        )

    def set_courier1_in_stage(
        self,
        session: Session,
        order_id: int,
        courier_id: int,
    ) -> None:
        """
        Устанавливает курьера для плеча pickup (courier1) в stage_orders.
        Пишет только в courier_user_id для строки с leg='pickup'.
        """
        session.execute(
            text(
                """
                UPDATE stage_orders
                SET courier_user_id = :cid
                WHERE order_id = :oid
                AND leg = 'pickup'
                """
            ),
            {"cid": courier_id, "oid": order_id},
        )


    def set_courier2_in_stage(
        self,
        session: Session,
        order_id: int,
        courier_id: int,
    ) -> None:
        """
        Устанавливает курьера для плеча delivery (courier2) в stage_orders.
        Создаёт/обновляет строку с leg='delivery', пишет только в courier_user_id.
        """

        # Берём trip_id из pickup-строки
        row = session.execute(
            text(
                """
                SELECT trip_id
                FROM stage_orders
                WHERE order_id = :oid
                AND leg = 'pickup'
                LIMIT 1
                """
            ),
            {"oid": order_id},
        ).fetchone()

        if not row:
            raise DbLayerError(
                f"Для заказа {order_id} не найдена строка pickup в stage_orders"
            )

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
            {
                "trip_id": trip_id,
                "order_id": order_id,
                "cid": courier_id,
            },
        )

    def create_stage_order(
        self,
        session: Session,
        trip_id: int,
        order_id: int,
        leg: str,
        courier_user_id: Optional[int] = None,
    ) -> None:
        """
        Создаёт запись в stage_orders.
        """

        session.execute(
            text(
                """
                INSERT INTO stage_orders (
                    trip_id,
                    order_id,
                    leg,
                    courier_user_id
                )
                VALUES (
                    :trip_id,
                    :order_id,
                    :leg,
                    :courier_user_id
                )
                """
            ),
            {
                "trip_id": trip_id,
                "order_id": order_id,
                "leg": leg,
                "courier_user_id": courier_user_id,
            },
        )

        logger.info(
            "[DB] stage_order created trip=%s order=%s leg=%s courier=%s",
            trip_id,
            order_id,
            leg,
            courier_user_id,
        )

    def create_order_issue(
        self,
        session: Session,
        order_id: Optional[int],  # ← Сделать Optional
        trip_id: Optional[int],
        user_id: int,
        issue_type: str,
        description: str = ""
    ) -> int:
        """Создать запись об инциденте в таблице report_issues."""
        logger.debug("create_order_issue вызван: order_id=%s, type=%s", order_id, issue_type)
        
        try:
            session.execute(
                text("""
                    INSERT INTO report_issues (order_id, trip_id, user_id, issue_type, description)
                    VALUES (:order_id, :trip_id, :user_id, :issue_type, :description)
                """),
                {
                    "order_id": order_id,  
                    "trip_id": trip_id,
                    "user_id": user_id,
                    "issue_type": issue_type,
                    "description": description,
                }
            )
            issue_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            logger.info("Создан инцидент %s для заказа %s", issue_id, order_id)
            return issue_id
            
        except Exception as e:
            logger.error("create_order_issue завершился с ошибкой: %s", e)
            raise DbLayerError(f"create_order_issue failed: {e}") from e

    def order_pickup_by_driver(self, session: Session, order_id: int, driver_id: int) -> bool:
        """Водитель забирает заказ из постамата (FSM: order_pickup_by_voditel)."""
        return self.call_fsm_action(session, "order", order_id, "order_pickup_by_voditel", driver_id)

    def order_client_will_deliver(self, session: Session, order_id: int, user_id: int) -> bool:
        """Клиент выбирает самодоставку A→B (FSM: order_client_will_deliver)."""
        return self.call_fsm_action(session, "order", order_id, "order_client_will_deliver", user_id)

    def order_timeout_reservation(self, session: Session, order_id: int, user_id: int) -> bool:
        """Таймаут резерва заказа (FSM: order_timeout_reservation)."""
        return self.call_fsm_action(session, "order", order_id, "order_timeout_reservation", user_id)

    def order_timeout_confirmation(self, session: Session, order_id: int, user_id: int) -> bool:
        """Таймаут подтверждения курьером (FSM: order_timeout_confirmation)."""
        return self.call_fsm_action(session, "order", order_id, "order_timeout_confirmation", user_id)

    def order_reserve_for_client_A_to_B(self, session: Session, order_id: int, user_id: int) -> bool:
        """Резерв слота A→B клиентом (FSM: order_reserve_for_client_A_to_B)."""
        return self.call_fsm_action(session, "order", order_id, "order_reserve_for_client_A_to_B", user_id)

    def order_reserve_for_courier_A_to_B(self, session: Session, order_id: int, courier_id: int) -> bool:
        """Резерв слота A→B курьером (FSM: order_reserve_for_courier_A_to_B)."""
        return self.call_fsm_action(session, "order", order_id, "order_reserve_for_courier_A_to_B", courier_id)

    def order_confirm_parcel_in(self, session: Session, order_id: int, user_id: int) -> bool:
        """Подтверждение, что посылка находится в нужном месте."""
        logger.debug("order_confirm_parcel_in вызван: order_id=%s, user_id=%s", order_id, user_id)
        
        # Выполняем FSM-переход
        self.call_fsm_action(session, "order", order_id, "order_confirm_parcel_in", user_id)

        # Ставим задачу на привязку к рейсу
        self.enqueue_fsm_instance(
            session,
            entity_type="order",
            entity_id=order_id,
            process_name="bind_order_to_trip",
            fsm_state="PENDING",
            requested_by_user_id=999999,  # системный
            requested_user_role="system"
        )

        return True

    def order_confirm_post2(self, session: Session, order_id: int, user_id: int) -> bool:
        """Водитель подтверждает посылку в постамате2."""
        logger.debug("order_confirm_post2 вызван: order_id=%s, user_id=%s", order_id, user_id)
        return self.call_fsm_action(session, "order", order_id, "order_confirm_post2", user_id)

    def order_mark_parcel_submitted(self, session: Session, order_id: int, user_id: int) -> bool:
        """Фиксация, что посылка сдана (FSM: order_parcel_submitted)."""
        return self.call_fsm_action(session, "order", order_id, "order_parcel_submitted", user_id)

    def order_courier1_pickup_parcel(self, session: Session, order_id: int, courier_id: int) -> bool:
        """Курьер1 забирает посылку (FSM: order_courier_pickup_parcel)."""
        return self.call_fsm_action(session, "order", order_id, "order_courier_pickup_parcel", courier_id)

    def order_start_transit(self, session: Session, order_id: int, user_id: int) -> bool:
        """Начало транзита заказа к второму постамату (FSM: order_start_transit)."""
        return self.call_fsm_action(session, "order", order_id, "order_start_transit", user_id)

    def order_arrive_at_post2(self, session: Session, order_id: int, user_id: int) -> bool:
        """Заказ прибыл во второй постамат (FSM: order_arrive_at_post2)."""
        return self.call_fsm_action(session, "order", order_id, "order_arrive_at_post2", user_id)

    def assign_courier2_to_order(self, session: Session, order_id: int, courier2_id: int) -> bool:
        """Назначение второго курьера (FSM: order_assign_courier2_to_order)."""
        return self.call_fsm_action(session, "order", order_id, "order_assign_courier2_to_order", courier2_id)

    def order_courier2_pickup_parcel(self, session: Session, order_id: int, courier2_id: int) -> bool:
        """Курьер2 забирает посылку (FSM: order_courier2_pickup_parcel)."""
        return self.call_fsm_action(session, "order", order_id, "order_courier2_pickup_parcel", courier2_id)

    def order_courier2_delivered_parcel(self, session: Session, order_id: int, courier2_id: int) -> bool:
        """Курьер2 доставил посылку (FSM: order_courier2_delivered_parcel)."""
        return self.call_fsm_action(session, "order", order_id, "order_courier2_delivered_parcel", courier2_id)

    def order_pickup_by_recipient(self, session: Session, order_id: int, recipient_id: int) -> bool:
        """Получатель забирает заказ (FSM: order_pickup_poluchatel)."""
        return self.call_fsm_action(session, "order", order_id, "order_pickup_poluchatel", recipient_id)

    def order_mark_delivered_parcel(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Заказ отмечен как доставленный (FSM: order_delivered_parcel)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_delivered_parcel",
            user_id,
        )


    def order_recipient_confirmed(
        self,
        session: Session,
        order_id: int,
        recipient_id: int,
    ) -> bool:
        """Получатель подтвердил получение (FSM: order_recipient_confirmed)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_recipient_confirmed",
            recipient_id,
        )


    def order_report_parcel_missing(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Отчёт: посылка пропала (FSM: order_report_parcel_missing)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_report_parcel_missing",
            user_id,
        )


    def order_report_delivery_failed(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Отчёт: доставка не удалась (FSM: order_report_delivery_failed)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_report_delivery_failed",
            user_id,
        )


    def order_request_manual_intervention(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Запрос ручного вмешательства по заказу (FSM: order_request_manual_intervention)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_request_manual_intervention",
            user_id,
        )


    def order_courier1_cancel(
        self,
        session: Session,
        order_id: int,
        courier1_id: int,
    ) -> bool:
        """Курьер1 отменяет доставку (FSM: order_courier1_cancel)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_courier1_cancel",
            courier1_id,
        )


    def order_courier2_cancel(
        self,
        session: Session,
        order_id: int,
        courier2_id: int,
    ) -> bool:
        """Курьер2 отменяет доставку (FSM: order_courier2_cancel)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_courier2_cancel",
            courier2_id,
        )


    def order_timeout_no_pickup(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Таймаут, когда никто не забрал заказ (FSM: order_timeout_no_pickup)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_timeout_no_pickup",
            user_id,
        )


    def order_cancel_reservation(
        self,
        session: Session,
        order_id: int,
        user_id: int,
    ) -> bool:
        """Отмена резерва заказа (FSM: order_cancel_reservation)."""
        return self.call_fsm_action(
            session,
            "order",
            order_id,
            "order_cancel_reservation",
            user_id,
        )

    # == выдача информации о заказах/рейсах для клиента/курьера/водителя ====
    def get_user_orders(self, session: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить все заказы пользователя.

        Источник истины:
        - orders (client_user_id)
        """
        logger.debug("get_user_orders вызван для user_id=%s", user_id)

        if user_id <= 0:
            raise DbLayerError("Invalid user_id")

        try:
            rows = session.execute(
                text("""
                    SELECT
                        o.id,
                        o.status,
                        o.description,
                        o.parcel_type,
                        o.pickup_type,
                        o.delivery_type,
                        o.source_cell_id,
                        o.dest_cell_id,
                        o.created_at,
                        o.updated_at
                    FROM orders o
                    WHERE o.client_user_id = :user_id
                    ORDER BY o.created_at DESC
                """),
                {"user_id": user_id},
            ).fetchall()

            orders: List[Dict[str, Any]] = []
            for row in rows:
                orders.append({
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "parcel_type": row[3],
                    "pickup_type": row[4],
                    "delivery_type": row[5],
                    "source_cell_id": row[6],
                    "dest_cell_id": row[7],
                    "created_at": row[8].isoformat() if row[8] else None,
                    "updated_at": row[9].isoformat() if row[9] else None,
                })

            logger.debug("get_user_orders: найдено %d заказов для user_id=%s", len(orders), user_id)
            return orders

        except Exception as e:
            logger.error("get_user_orders завершился с ошибкой для user_id=%s: %s", user_id, e)
            raise DbLayerError(f"get_user_orders failed: {e}") from e

    def get_courier_orders(
        self, 
        session: Session, 
        courier_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить все заказы курьера с полной информацией.
        
        Источник истины:
        - stage_orders (courier_user_id)
        - orders (данные заказа)
                 
        """
        logger.debug("get_courier_orders вызван для courier_id=%s", courier_id)
        
        if courier_id <= 0:
            raise DbLayerError("Invalid courier_id")
        
        try:
            rows = session.execute(
                text("""
                    SELECT
                        o.id,
                        o.status,
                        o.description,
                        o.parcel_type,
                        o.pickup_type,
                        o.delivery_type,
                        o.source_cell_id,
                        o.dest_cell_id,
                        o.client_user_id,
                        o.recipient_user_id,
                        o.created_at,
                        o.updated_at,
                        so.leg
                    FROM orders o
                    JOIN stage_orders so ON so.order_id = o.id
                    WHERE so.courier_user_id = :courier_id
                    ORDER BY o.created_at DESC
                """),
                {"courier_id": courier_id},
            ).fetchall()
            
            orders: List[Dict[str, Any]] = []
            for row in rows:
                orders.append({
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "parcel_type": row[3],
                    "pickup_type": row[4],
                    "delivery_type": row[5],
                    "source_cell_id": row[6],
                    "dest_cell_id": row[7],
                    "client_user_id": row[8],
                    "recipient_user_id": row[9],
                    "created_at": row[10].isoformat() if row[10] else None,
                    "updated_at": row[11].isoformat() if row[11] else None,
                    "leg": row[12],                    
                })
            
            logger.debug("get_courier_orders: найдено %d заказов для courier_id=%s", len(orders), courier_id)
            return orders
            
        except Exception as e:
            logger.error("get_courier_orders завершился с ошибкой для courier_id=%s: %s", courier_id, e)
            raise DbLayerError(f"get_courier_orders failed: {e}") from e

    def get_driver_trips_with_orders(
        self, 
        session: Session, 
        driver_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить активные рейсы водителя со всеми заказами внутри.
        
        Источник истины:
        - trips (driver_user_id, active, status)
        - stage_orders (trip_id → order_id)
        - orders (данные заказа)
        
        Args:
            session: активная сессия SQLAlchemy
            driver_id: ID водителя
        
        Returns:
            Список словарей с данными рейсов и заказов внутри.
            Водители видят trip_id — они работают с рейсами.
            БЕЗ leg — чтобы избежать дублирования заказов.
        
        Raises:
            DbLayerError: при ошибке выполнения запроса
        """
        logger.debug("get_driver_trips_with_orders вызван для driver_id=%s", driver_id)
        
        if driver_id <= 0:
            raise DbLayerError("Invalid driver_id")
        
        try:
            # Получаем активные рейсы водителя
            trips_rows = session.execute(
                text("""
                    SELECT
                        t.id,
                        t.status,
                        t.active,
                        t.from_city,
                        t.to_city,
                        t.pickup_locker_id,
                        t.delivery_locker_id,
                        t.created_at
                    FROM trips t
                    WHERE t.driver_user_id = :driver_id
                    AND t.active = 1
                    AND t.status != 'trip_completed'
                    ORDER BY t.created_at DESC
                """),
                {"driver_id": driver_id},
            ).fetchall()
            
            trips: List[Dict[str, Any]] = []
            
            for trip_row in trips_rows:
                trip_id = trip_row[0]
                
                # Получаем заказы этого рейса (БЕЗ leg, чтобы не дублировать)
                orders_rows = session.execute(
                    text("""
                        SELECT
                            o.id,
                            o.status,
                            o.description,
                            o.parcel_type,
                            o.pickup_type,
                            o.delivery_type,
                            o.source_cell_id,
                            o.dest_cell_id,
                            o.client_user_id,
                            o.recipient_user_id,
                            o.created_at,
                            o.updated_at
                        FROM orders o
                        WHERE o.id IN (
                            SELECT order_id FROM stage_orders WHERE trip_id = :trip_id
                        )
                        ORDER BY o.created_at ASC
                    """),
                    {"trip_id": trip_id},
                ).fetchall()
                
                orders: List[Dict[str, Any]] = []
                for order_row in orders_rows:
                    orders.append({
                        "id": order_row[0],
                        "status": order_row[1],
                        "description": order_row[2],
                        "parcel_type": order_row[3],
                        "pickup_type": order_row[4],
                        "delivery_type": order_row[5],
                        "source_cell_id": order_row[6],
                        "dest_cell_id": order_row[7],
                        "client_user_id": order_row[8],
                        "recipient_user_id": order_row[9],
                        "created_at": order_row[10].isoformat() if order_row[10] else None,
                        "updated_at": order_row[11].isoformat() if order_row[11] else None,
                    })
                
                trips.append({
                    "id": trip_row[0],
                    "status": trip_row[1],
                    "active": trip_row[2],
                    "from_city": trip_row[3],
                    "to_city": trip_row[4],
                    "pickup_locker_id": trip_row[5],
                    "delivery_locker_id": trip_row[6],
                    "created_at": trip_row[7].isoformat() if trip_row[7] else None,
                    "orders": orders,
                })
            
            logger.debug("get_driver_trips_with_orders: найдено %d рейсов для driver_id=%s", len(trips), driver_id)
            return trips
            
        except Exception as e:
            logger.error("get_driver_trips_with_orders завершился с ошибкой для driver_id=%s: %s", driver_id, e)
            raise DbLayerError(f"get_driver_trips_with_orders failed: {e}") from e

    def get_order_request(self, session: Session, request_id: int, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        logger.debug("get_order_request вызван для request_id=%s", request_id)
        retries = 0
        while retries < max_retries:
            try:
                row = session.execute(
                    text("""
                        SELECT id, client_user_id, recipient_user_id, parcel_type, cell_size,
                               sender_delivery, recipient_delivery, status
                        FROM order_requests
                        WHERE id = :id
                    """),
                    {"id": request_id}
                ).fetchone()

                if not row:
                    logger.debug("get_order_request: заявка request_id=%s не найдена", request_id)
                    return None

                result = {
                    "id": row[0],
                    "client_user_id": row[1],
                    "recipient_user_id": row[2], 
                    "parcel_type": row[3],
                    "cell_size": row[4],
                    "sender_delivery": row[5],
                    "recipient_delivery": row[6],
                    "status": row[7]
                }
                logger.debug("get_order_request: успешно получена заявка request_id=%s", request_id)
                return result

            except OperationalError as e:
                retries += 1
                if retries >= max_retries:
                    logger.error("get_order_request: OperationalError после %d попыток для request_id=%s: %s", max_retries, request_id, e)
                    raise DbLayerError(f"Failed to get order request {request_id} after {max_retries} retries: {e}") from e
                else:
                    logger.warning("get_order_request: OperationalError на попытке %d для request_id=%s, повтор...", retries, request_id)
                    time.sleep(0.5 * retries)

            except SQLAlchemyError as e:
                logger.error("get_order_request: SQLAlchemy ошибка для request_id=%s: %s", request_id, e)
                raise DbLayerError(f"SQLAlchemy error in get_order_request for request_id {request_id}: {e}") from e

            except Exception as e:
                logger.error("get_order_request: неизвестная ошибка для request_id=%s: %s", request_id, e)
                raise DbLayerError(f"General error in get_order_request for request_id {request_id}: {e}") from e

    def get_user_city(self, session: Session, user_id: int) -> str:
        """
        Получить город пользователя по ID.
        """
        logger.debug("get_user_city вызван для user_id=%s", user_id)
        row = session.execute(
            text("SELECT city FROM users WHERE id = :id"),
            {"id": user_id}  
        ).fetchone()
        if not row or not row[0]:
            raise DbLayerError(f"User {user_id} has no city")
        return row[0]

    def find_and_reserve_cells_by_cities(
        self,
        session: Session,
        source_city: str,
        dest_city: str,
        cell_size: str,
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        logger.debug(
            "find_and_reserve_cells_by_cities вызван: source_city=%s, dest_city=%s, cell_size=%s",
            source_city, dest_city, cell_size
        )

        try:
            # Ищем source_cell в source_city
            src = session.execute(text("""
                SELECT lc.id
                FROM locker_cells lc
                JOIN lockers l ON lc.locker_id = l.id
                WHERE 
                    l.city = :source_city
                    AND lc.cell_type = :cell_size
                    AND lc.status = 'locker_free'
                ORDER BY l.id, lc.id
                LIMIT 1
                FOR UPDATE
            """), {
                "source_city": source_city,
                "cell_size": cell_size,
            }).fetchone()

            if not src:
                logger.debug("Нет свободной ячейки в городе отправителя: %s", source_city)
                return False, None, None

            # Ищем dest_cell в dest_city
            dst = session.execute(text("""
                SELECT lc.id
                FROM locker_cells lc
                JOIN lockers l ON lc.locker_id = l.id
                WHERE 
                    l.city = :dest_city
                    AND lc.cell_type = :cell_size
                    AND lc.status = 'locker_free'
                ORDER BY l.id, lc.id
                LIMIT 1
                FOR UPDATE
            """), {
                "dest_city": dest_city,
                "cell_size": cell_size,
            }).fetchone()

            if not dst:
                logger.debug("Нет свободной ячейки в городе получателя: %s", dest_city)
                return False, None, None

            src_id = src[0]
            dst_id = dst[0]

            # Резервируем обе ячейки
            session.execute(text("""
                UPDATE locker_cells
                SET status = 'locker_reserved'
                WHERE id IN (:src_id, :dst_id)
            """), {
                "src_id": src_id,
                "dst_id": dst_id,
            })

            logger.debug("Успешно зарезервированы ячейки: %s (из %s) → %s (в %s)",
                        src_id, source_city, dst_id, dest_city)
            return True, src_id, dst_id

        except Exception as e:
            logger.error(
                "find_and_reserve_cells_by_cities завершился с ошибкой: %s → %s, size=%s, error=%s",
                source_city, dest_city, cell_size, e
            )
            raise DbLayerError(f"find_and_reserve_cells_by_cities failed: {e}") from e

    def create_order_record(
        self,
        session: Session,
        description: str,
        pickup_type: str,
        delivery_type: str,
        client_user_id: int,
        recipient_user_id: Optional[int],
        source_cell_id: int,
        dest_cell_id: int,
    ) -> int:
        logger.debug(
            "create_order_record вызван: client_user_id=%s, source_cell_id=%s, dest_cell_id=%s",
            client_user_id, source_cell_id, dest_cell_id
        )

        try:
            session.execute(text("""
                INSERT INTO orders (
                    description,
                    source_cell_id,
                    dest_cell_id,
                    pickup_type,
                    delivery_type,
                    status,
                    client_user_id,
                    recipient_user_id
                )
                VALUES (
                    :description,
                    :src,
                    :dst,
                    :pickup,
                    :delivery,
                    'order_created',
                    :client,
                    :recipient
                )
            """), {
                "description": description,
                "src": source_cell_id,
                "dst": dest_cell_id,
                "pickup": pickup_type,
                "delivery": delivery_type,
                "client": client_user_id,
                "recipient": recipient_user_id,
            })

            order_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            logger.debug("create_order_record: создан заказ с id=%s", order_id)
            return order_id

        except Exception as e:
            logger.error(
                "create_order_record завершился с ошибкой: client=%s, src=%s, dst=%s, error=%s",
                client_user_id, source_cell_id, dest_cell_id, e
            )
            raise DbLayerError(f"create_order_record failed: {e}") from e

    def mark_request_completed(self, session: Session, request_id: int, order_id: int) -> bool:
        logger.debug("mark_request_completed вызван: request_id=%s, order_id=%s", request_id, order_id)

        try:
            stmt = text("""
                UPDATE order_requests
                SET status = 'COMPLETED',
                    order_id = :order_id,
                    error_code = NULL,
                    error_message = NULL
                WHERE id = :request_id
            """)
            result = session.execute(stmt, {
                "request_id": request_id,
                "order_id": order_id
            })

            if result.rowcount == 0:
                logger.warning("mark_request_completed: заявка request_id=%s не найдена", request_id)
                return False

            logger.info("Заявка %s помечена COMPLETED, привязан заказ %s", request_id, order_id)
            return True

        except SQLAlchemyError as e:
            logger.error("mark_request_completed: SQLAlchemy ошибка для request_id=%s: %s", request_id, e)
            raise DbLayerError(f"Failed to mark request {request_id} as completed: {e}") from e
        except Exception as e:
            logger.error("mark_request_completed: неизвестная ошибка для request_id=%s: %s", request_id, e)
            raise DbLayerError(f"General error in mark_request_completed for request {request_id}: {e}") from e

    def mark_request_failed(
        self,
        session: Session,
        request_id: int,
        error_code: str,
        error_message: str,
        max_retries: int = 3,
    ) -> bool:
        """
        Помечает заявку FAILED с кодом и сообщением.
        Не управляет транзакцией — commit/rollback должен быть сделан вызывающей стороной.
        """
        logger.debug(
            "mark_request_failed вызван: request_id=%s, error_code=%s",
            request_id, error_code
        )

        retries = 0
        while retries < max_retries:
            try:
                stmt = text("""
                    UPDATE order_requests
                    SET status = 'FAILED',
                        error_code = :error_code,
                        error_message = :error_message
                    WHERE id = :request_id
                """)
                result = session.execute(stmt, {
                    "request_id": request_id,
                    "error_code": error_code,
                    "error_message": error_message
                })

                if result.rowcount == 0:
                    logger.warning("mark_request_failed: заявка request_id=%s не найдена", request_id)
                    return False

                logger.info(
                    "Заявка %s помечена FAILED: %s - %s",
                    request_id, error_code, error_message
                )
                return True

            except OperationalError as e:
                retries += 1
                if retries >= max_retries:
                    logger.error(
                        "mark_request_failed: OperationalError после %d попыток для request_id=%s: %s",
                        max_retries, request_id, e
                    )
                    raise DbLayerError(
                        f"Failed to mark request {request_id} as FAILED after {max_retries} retries: {e}"
                    ) from e
                else:
                    logger.warning(
                        "mark_request_failed: OperationalError на попытке %d для request_id=%s, повтор...",
                        retries, request_id
                    )
                    time.sleep(0.5 * retries)

            except SQLAlchemyError as e:
                logger.error(
                    "mark_request_failed: SQLAlchemy ошибка для request_id=%s: %s",
                    request_id, e
                )
                raise DbLayerError(
                    f"SQLAlchemy error in mark_request_failed for request_id {request_id}: {e}"
                ) from e

            except Exception as e:
                logger.error(
                    "mark_request_failed: неизвестная ошибка для request_id=%s: %s",
                    request_id, e
                )
                raise DbLayerError(
                    f"General error in mark_request_failed for request_id {request_id}: {e}"
                ) from e

    def get_order_request_status(self, session: Session, request_id: int) -> Optional[Dict[str, Any]]:
        logger.debug("get_order_request_status вызван для request_id=%s", request_id)

        try:
            row = session.execute(
                text("""
                    SELECT status, order_id, error_code, error_message
                    FROM order_requests
                    WHERE id = :request_id
                """),
                {"request_id": request_id}
            ).fetchone()

            if not row:
                logger.debug("get_order_request_status: заявка request_id=%s не найдена", request_id)
                return None

            result = {
                "status": row[0],
                "order_id": row[1],
                "error_code": row[2],
                "error_message": row[3]
            }
            logger.debug("get_order_request_status: получен статус=%s для request_id=%s", result["status"], request_id)
            return result

        except SQLAlchemyError as e:
            logger.error("get_order_request_status: SQLAlchemy ошибка для request_id=%s: %s", request_id, e)
            raise DbLayerError(f"Failed to get status for order request {request_id}: {e}") from e
        except Exception as e:
            logger.error("get_order_request_status: неизвестная ошибка для request_id=%s: %s", request_id, e)
            raise DbLayerError(f"General error getting status for order request {request_id}: {e}") from e

    # ---------- LOCKER / ЯЧЕЙКИ ----------

    def open_locker_for_recipient(
        self,
        session: Session,
        cell_id: int,
        user_id: int,
        unlock_code: str
    ) -> bool:
        """Открытие ячейки (FSM: locker_open_locker)."""
        logger.debug(
            "open_locker_for_recipient вызван: cell_id=%s, user_id=%s",
            cell_id, user_id
        )
        return self.call_fsm_action(
            session, "locker", cell_id, "locker_open_locker", user_id, unlock_code
        )

    def close_locker(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Закрытие ячейки (FSM: locker_close_locker)."""
        logger.debug("close_locker вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_close_locker", user_id)

    def close_locker_pickup(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Закрытие ячейки после забора посылки (FSM: locker_close_pickup)."""
        logger.debug("close_locker_pickup вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_close_pickup", user_id)

    def reserve_locker_cell(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Резерв ячейки под заказ (FSM: locker_reserve_cell)."""
        logger.debug("reserve_locker_cell вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_reserve_cell", user_id)

    def reset_locker(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Сброс ячейки в свободное состояние (FSM: locker_reset)."""
        logger.debug("reset_locker вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_reset", user_id)

    def locker_report_failed_to_open(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Ячейка не открылась (FSM: locker_failed_to_open)."""
        logger.debug("locker_report_failed_to_open вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_failed_to_open", user_id)

    def set_locker_maintenance(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Перевод ячейки в обслуживание (FSM: locker_set_locker_to_maintenance)."""
        logger.debug("set_locker_maintenance вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_set_locker_to_maintenance", user_id)

    def cancel_locker_reservation(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Отмена резерва ячейки (FSM: locker_cancel_reservation)."""
        logger.debug("cancel_locker_reservation вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_cancel_reservation", user_id)

    def confirm_locker_parcel_not_found(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Подтверждение, что посылка не найдена в открытой ячейке (FSM: locker_confirm_parcel_not_found)."""
        logger.debug("confirm_locker_parcel_not_found вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_confirm_parcel_not_found", user_id)

    def confirm_locker_parcel_out_driver(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Водитель забрал посылку из ячейки (FSM: locker_confirm_parcel_out)."""
        logger.debug("confirm_locker_parcel_out_driver вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_confirm_parcel_out", user_id)

    def confirm_locker_parcel_out_recipient(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Получатель забрал посылку из ячейки (FSM: locker_confirm_parcel_out_recipient)."""
        logger.debug("confirm_locker_parcel_out_recipient вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_confirm_parcel_out_recipient", user_id)

    def locker_not_closed(self, session: Session, cell_id: int, user_id: int) -> bool:
        """Фиксация незакрытой ячейки (FSM: locker_dont_closed)."""
        logger.debug("locker_not_closed вызван: cell_id=%s, user_id=%s", cell_id, user_id)
        return self.call_fsm_action(session, "locker", cell_id, "locker_dont_closed", user_id)

    def get_order_id_by_cell_id(
        self,
        session: Session,
        cell_id: int
    ) -> Optional[int]:
        """
        Возвращает ID заказа, привязанного к ячейке.
        Ищет в:
        1. locker_cells.current_order_id (для source ячеек)
        2. orders.source_cell_id или orders.dest_cell_id (для destination ячеек)
        """
        logger.debug("get_order_id_by_cell_id вызван: cell_id=%s", cell_id)
        try:
            # 1. Сначала пробуем current_order_id
            result = session.execute(
                text("SELECT current_order_id FROM locker_cells WHERE id = :cell_id"),
                {"cell_id": cell_id}
            ).scalar()
            
            if result:
                logger.debug("get_order_id_by_cell_id: найдено через current_order_id: %s", result)
                return result
            
            # 2. Если NULL, ищем в orders (для destination ячеек)
            result = session.execute(
                text("""
                    SELECT id FROM orders 
                    WHERE source_cell_id = :cell_id OR dest_cell_id = :cell_id
                    LIMIT 1
                """),
                {"cell_id": cell_id}
            ).scalar()
            
            logger.debug("get_order_id_by_cell_id: найдено через orders: %s", result)
            return result
            
        except Exception as e:
            logger.error("get_order_id_by_cell_id завершился с ошибкой для cell_id=%s: %s", cell_id, e)
            raise DbLayerError(f"Failed to get order_id for cell_id {cell_id}: {e}") from e

    def get_locker_id_by_cell(self, session: Session, cell_id: int) -> int:
        """
        Возвращает locker_id для ячейки.
        """
        logger.debug("get_locker_id_by_cell вызван: cell_id=%s", cell_id)
        try:
            row = session.execute(
                text("SELECT locker_id FROM locker_cells WHERE id = :id"),
                {"id": cell_id},
            ).scalar()
            if row is None:
                logger.error("get_locker_id_by_cell: ячейка %s не найдена", cell_id)
                raise DbLayerError(f"Ячейка {cell_id} не найдена")
            logger.debug("get_locker_id_by_cell: cell_id=%s → locker_id=%s", cell_id, row)
            return row
        except Exception as e:
            logger.error("get_locker_id_by_cell завершился с ошибкой для cell_id=%s: %s", cell_id, e)
            raise DbLayerError(f"Failed to get locker_id for cell_id {cell_id}: {e}") from e
    

    # ==================== КНОПКИ ====================

    def get_buttons(
        self,
        session: Session,
        user_role: str,
        entity_type: str,
        entity_id: int
    ) -> List[Dict[str, Any]]:
        """Доступные кнопки для роли и статуса."""
        logger.debug(
            "get_buttons вызван: user_role=%s, entity_type=%s, entity_id=%s",
            user_role, entity_type, entity_id
        )

        status_query = {
            "order": text("SELECT status FROM orders WHERE id = :id"),
            "trip": text("SELECT status, active FROM trips WHERE id = :id"),
            "locker": text("SELECT status FROM locker_cells WHERE id = :id"),
        }

        if entity_type not in status_query:
            logger.error("get_buttons: неизвестный entity_type=%s", entity_type)
            raise DbLayerError(f"Неизвестный entity_type: {entity_type}")

        try:
            result = session.execute(
                status_query[entity_type], {"id": entity_id}
            ).fetchone()

            if not result:
                logger.error("get_buttons: сущность %s/%s не найдена", entity_type, entity_id)
                raise DbLayerError(f"Сущность {entity_type}/{entity_id} не найдена")

            if entity_type == "trip":
                current_status, active_flag = result
                if active_flag == 0 and current_status in ["trip_created", "trip_assigned"]:
                    effective_state = current_status + "_inactive"
                else:
                    effective_state = current_status
            else:
                effective_state = result[0]

            logger.debug("get_buttons: effective_state=%s для %s/%s", effective_state, entity_type, entity_id)

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
                logger.debug("get_buttons: fallback к состоянию %s для trip %s", current_status, entity_id)
                rows = session.execute(
                    text(
                        "SELECT button_name, is_enabled "
                        "FROM button_states "
                        "WHERE user_role = :role AND entity_state = :state"
                    ),
                    {"role": user_role, "state": current_status},
                ).fetchall()

            buttons = [
                {
                    "button_name": row[0],
                    "is_enabled": (
                        row[1] == "active" if isinstance(row[1], str) else bool(row[1])
                    ),
                }
                for row in rows
            ]

            logger.debug("get_buttons: найдено %d кнопок для %s/%s", len(buttons), entity_type, entity_id)
            return buttons

        except Exception as e:
            logger.error(
                "get_buttons завершился с ошибкой: role=%s, type=%s, id=%s, error=%s",
                user_role, entity_type, entity_id, e
            )
            raise DbLayerError(f"Failed to get buttons for {entity_type}/{entity_id}: {e}") from e

    def get_active_buttons(
        self,
        session: Session,
        user_role: str,
        entity_type: str,
        entity_id: int
    ) -> List[str]:
        """Имена только активных кнопок."""
        logger.debug(
            "get_active_buttons вызван: user_role=%s, entity_type=%s, entity_id=%s",
            user_role, entity_type, entity_id
        )

        try:
            all_buttons = self.get_buttons(session, user_role, entity_type, entity_id)
            active_names = [b["button_name"] for b in all_buttons if b["is_enabled"]]
            logger.debug("get_active_buttons: активные кнопки=%s", active_names)
            return active_names
        except Exception as e:
            logger.error(
                "get_active_buttons завершился с ошибкой: role=%s, type=%s, id=%s, error=%s",
                user_role, entity_type, entity_id, e
            )
            raise DbLayerError(f"Failed to get active buttons for {entity_type}/{entity_id}: {e}") from e

    def get_active_nonbasic_buttons(
        self,
        session: Session,
        user_role: str,
        entity_type: str,
        entity_id: int,
        basic_buttons: List[str],
    ) -> List[Dict[str, Any]]:
        """Активные кнопки, исключая базовые."""
        logger.debug(
            "get_active_nonbasic_buttons вызван: user_role=%s, entity_type=%s, entity_id=%s, basic_buttons=%s",
            user_role, entity_type, entity_id, basic_buttons
        )

        try:
            all_buttons = self.get_buttons(session, user_role, entity_type, entity_id)
            nonbasic = [
                b
                for b in all_buttons
                if b.get("is_enabled") and b.get("button_name") not in basic_buttons
            ]
            logger.debug("get_active_nonbasic_buttons: найдено %d не-базовых кнопок", len(nonbasic))
            return nonbasic
        except Exception as e:
            logger.error(
                "get_active_nonbasic_buttons завершился с ошибкой: role=%s, type=%s, id=%s, error=%s",
                user_role, entity_type, entity_id, e
            )
            raise DbLayerError(f"Failed to get non-basic active buttons for {entity_type}/{entity_id}: {e}") from e

    # ==================== СПРАВОЧНИКИ / ПОЛЬЗОВАТЕЛИ / ПОСТАМАТЫ ====================

    def create_user(
        self,
        session: Session,
        user_id: int,
        name: str,
        role: str
    ) -> bool:
        """Создать пользователя (идемпотентно через INSERT IGNORE)."""
        logger.debug("create_user вызван: user_id=%s, name=%s, role=%s", user_id, name, role)
        try:
            result = session.execute(
                text(
                    "INSERT IGNORE INTO users (id, name, role_name) "
                    "VALUES (:id, :name, :role)"
                ),
                {"id": user_id, "name": name, "role": role},
            )
            inserted = result.rowcount > 0
            logger.debug("create_user: пользователь %s — %s", user_id, "создан" if inserted else "уже существует")
            return True  # Идемпотентность: всегда успех
        except Exception as e:
            logger.error("create_user завершился с ошибкой для user_id=%s: %s", user_id, e)
            raise DbLayerError(f"Пользователь {user_id}: {e}") from e

    def get_user_role(self, session: Session, user_id: int) -> Optional[str]:
        """Вернуть роль пользователя по ID."""
        logger.debug("get_user_role вызван: user_id=%s", user_id)
        try:
            row = session.execute(
                text("SELECT role_name FROM users WHERE id = :id"),
                {"id": user_id},
            ).fetchone()
            role = row[0] if row else None
            logger.debug("get_user_role: user_id=%s → role=%s", user_id, role)
            return role
        except Exception as e:
            logger.error("get_user_role завершился с ошибкой для user_id=%s: %s", user_id, e)
            raise DbLayerError(f"Failed to get role for user {user_id}: {e}") from e

    def get_all_users(self, session: Session) -> List[Dict[str, Any]]:
        """
        Получить всех пользователей из таблицы users.
        
        Returns:
            Список словарей с данными пользователей
        """
        logger.debug("get_all_users вызван")
        
        try:
            rows = session.execute(
                text("""
                    SELECT
                        id,
                        name,
                        role_name,
                        city,
                        phone
                    FROM users
                    ORDER BY id ASC
                """)
            ).fetchall()
            
            users: List[Dict[str, Any]] = []
            for row in rows:
                users.append({
                    "id": row[0],
                    "name": row[1],
                    "role_name": row[2],
                    "city": row[3],
                    "phone": row[4],
                })
            
            logger.debug("get_all_users: найдено %d пользователей", len(users))
            return users
            
        except Exception as e:
            logger.error("get_all_users завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_all_users failed: {e}") from e

    def create_locker_model(
        self,
        session: Session,
        model_id: int,
        model_name: str,
        cell_count_s: int = 10,
        cell_count_m: int = 5,
        cell_count_l: int = 2,
        cell_count_p: int = 1,
    ) -> bool:
        """Создать модель постамата."""
        logger.debug(
            "create_locker_model вызван: model_id=%s, model_name=%s",
            model_id, model_name
        )
        try:
            result = session.execute(
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
            inserted = result.rowcount > 0
            logger.debug(
                "create_locker_model: модель %s — %s",
                model_id, "создана" if inserted else "уже существует"
            )
            return True
        except Exception as e:
            logger.error("create_locker_model завершился с ошибкой для model_id=%s: %s", model_id, e)
            raise DbLayerError(f"Модель {model_id}: {e}") from e

    def create_locker(
        self,
        session: Session,
        locker_id: int,
        locker_code: str,
        location_address: str,
        model_id: int = 1
    ) -> bool:
        """Создать постамат."""
        logger.debug(
            "create_locker вызван: locker_id=%s, code=%s, address=%s, model_id=%s",
            locker_id, locker_code, location_address, model_id
        )
        try:
            result = session.execute(
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
            inserted = result.rowcount > 0
            logger.debug(
                "create_locker: постамат %s — %s",
                locker_id, "создан" if inserted else "уже существует"
            )
            return True
        except Exception as e:
            logger.error("create_locker завершился с ошибкой для locker_id=%s: %s", locker_id, e)
            raise DbLayerError(f"Постамат {locker_id}: {e}") from e

    def create_locker_cell(
        self,
        session: Session,
        locker_id: int,
        cell_code: str,
        cell_type: str = "S"
    ) -> Optional[int]:
        """Создать ячейку постамата (или вернуть существующую)."""
        logger.debug(
            "create_locker_cell вызван: locker_id=%s, cell_code=%s, cell_type=%s",
            locker_id, cell_code, cell_type
        )
        try:
            existing = session.execute(
                text(
                    "SELECT id FROM locker_cells "
                    "WHERE locker_id = :l_id AND cell_code = :c_code"
                ),
                {"l_id": locker_id, "c_code": cell_code},
            ).fetchone()

            if existing:
                cell_id = existing[0]
                logger.debug("create_locker_cell: ячейка %s уже существует, id=%s", cell_code, cell_id)
                return cell_id

            session.execute(
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
            row = session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
            cell_id = int(row[0]) if row and row[0] else None
            logger.debug("create_locker_cell: создана новая ячейка %s → id=%s", cell_code, cell_id)
            return cell_id
        except Exception as e:
            logger.error(
                "create_locker_cell завершился с ошибкой: locker_id=%s, cell_code=%s, error=%s",
                locker_id, cell_code, e
            )
            raise DbLayerError(f"Ячейка {cell_code}: {e}") from e

    def find_free_cell(self, session: Session, locker_id: int) -> Optional[int]:
        """Найти любую свободную ячейку в постамате."""
        logger.debug("find_free_cell вызван: locker_id=%s", locker_id)
        try:
            row = session.execute(
                text(
                    "SELECT id FROM locker_cells "
                    "WHERE locker_id = :locker_id AND status = 'locker_free' "
                    "LIMIT 1"
                ),
                {"locker_id": locker_id},
            ).fetchone()
            cell_id = row[0] if row else None
            logger.debug("find_free_cell: locker_id=%s → cell_id=%s", locker_id, cell_id)
            return cell_id
        except Exception as e:
            logger.error("find_free_cell завершился с ошибкой для locker_id=%s: %s", locker_id, e)
            raise DbLayerError(f"Failed to find free cell for locker {locker_id}: {e}") from e

    def get_lockers(self, session: Session) -> List[Dict[str, Any]]:
        """
        Получить список всех постаматов.
        """
        logger.debug("get_lockers вызван")
        try:
            rows = session.execute(
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

            lockers = [
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
            logger.debug("get_lockers: найдено %d постаматов", len(lockers))
            return lockers
        except Exception as e:
            logger.error("get_lockers завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to fetch lockers: {e}") from e

    def get_locker_cells_by_status(
        self, session: Session, locker_id: int, status: str
    ) -> List[Dict[str, Any]]:
        """Вернуть ячейки постамата по статусу."""
        logger.debug("get_locker_cells_by_status вызван: locker_id=%s, status=%s", locker_id, status)
        try:
            rows = session.execute(
                text(
                    "SELECT id, cell_code, cell_type, status, current_order_id "
                    "FROM locker_cells "
                    "WHERE locker_id = :locker_id AND status = :status"
                ),
                {"locker_id": locker_id, "status": status},
            ).fetchall()

            cells = [
                {
                    "id": r[0],
                    "cell_code": r[1],
                    "cell_type": r[2],
                    "status": r[3],
                    "current_order_id": r[4],
                }
                for r in rows
            ]
            logger.debug("get_locker_cells_by_status: найдено %d ячеек", len(cells))
            return cells
        except Exception as e:
            logger.error(
                "get_locker_cells_by_status завершился с ошибкой: locker_id=%s, status=%s, error=%s",
                locker_id, status, e
            )
            raise DbLayerError(f"Failed to get cells by status for locker {locker_id}: {e}") from e

    def get_locker_city_by_cell(self, session: Session, cell_id: int) -> str:
        """
        Возвращает город по ID ячейки через locker.city.
        """
        logger.debug("get_locker_city_by_cell вызван: cell_id=%s", cell_id)
        try:
            result = session.execute(
                text("""
                    SELECT l.city
                    FROM locker_cells c
                    JOIN lockers l ON l.id = c.locker_id
                    WHERE c.id = :cell_id
                """),
                {"cell_id": cell_id}
            ).scalar()

            if not result:
                raise DbLayerError(f"Ячейка {cell_id} не найдена или не привязана к постамату")

            city = result.strip()
            if not city:
                raise DbLayerError(f"Постамат для ячейки {cell_id} не имеет города")

            logger.debug("get_locker_city_by_cell: cell_id=%s → city='%s'", cell_id, city)
            return city

        except Exception as e:
            logger.error("get_locker_city_by_cell завершился с ошибкой для cell_id=%s: %s", cell_id, e)
            raise DbLayerError(f"Failed to get city for cell {cell_id}: {e}") from e

    def clear_locker_cells(self, session: Session, locker_id: int) -> bool:
        """Удалить все ячейки постамата (осторожно)."""
        logger.warning("clear_locker_cells вызван: locker_id=%s — УДАЛЕНИЕ ЯЧЕЕК!", locker_id)
        try:
            result = session.execute(
                text("DELETE FROM locker_cells WHERE locker_id = :locker_id"),
                {"locker_id": locker_id},
            )
            deleted_count = result.rowcount
            logger.info("clear_locker_cells: удалено %d ячеек для locker_id=%s", deleted_count, locker_id)
            return True
        except Exception as e:
            logger.error("clear_locker_cells завершился с ошибкой для locker_id=%s: %s", locker_id, e)
            raise DbLayerError(f"Ячейки постамата {locker_id}: {e}") from e

    def reserve_cells_for_order_in_session(
        self,
        session: Session,
        order_id: int,
        source_cell_id: int,
        dest_cell_id: int,
    ) -> None:
        """
        Резервирует две ячейки для заказа в ТЕКУЩЕЙ транзакции (без FSM).
        Используется внутри create_order_from_request чтобы избежать блокировок.
        """
        logger.debug(
            "reserve_cells_for_order_in_session вызван: order_id=%s, src=%s, dst=%s",
            order_id, source_cell_id, dest_cell_id
        )
        try:
            session.execute(
                text(
                    """
                    UPDATE locker_cells
                    SET status = 'locker_reserved', current_order_id = :order_id
                    WHERE id IN (:src_id, :dst_id)
                    """
                ),
                {"order_id": order_id, "src_id": source_cell_id, "dst_id": dest_cell_id},
            )
            logger.info(
                "Зарезервированы ячейки %s, %s для заказа %s",
                source_cell_id, dest_cell_id, order_id
            )
        except Exception as e:
            logger.error(
                "reserve_cells_for_order_in_session завершился с ошибкой: "
                "order_id=%s, src=%s, dst=%s, error=%s",
                order_id, source_cell_id, dest_cell_id, e
            )
            raise DbLayerError(f"Failed to reserve cells for order {order_id}: {e}") from e

    def bind_cells_for_order(
        self,
        session: Session,
        order_id: int,
        source_cell_id: int,
        dest_cell_id: int,
    ) -> bool:
        """
        Привязывает заказ к двум ячейкам через current_order_id.
        Не меняет статус ячеек — они уже зарезервированы.
        """
        logger.debug(
            "bind_cells_for_order вызван: order_id=%s, source_cell_id=%s, dest_cell_id=%s",
            order_id, source_cell_id, dest_cell_id
        )
        try:
            session.execute(
                text("""
                    UPDATE locker_cells
                    SET current_order_id = :order_id
                    WHERE id IN (:source_id, :dest_id)
                """),
                {
                    "order_id": order_id,
                    "source_id": source_cell_id,
                    "dest_id": dest_cell_id,
                }
            )
            logger.info(
                "Ячейки %s и %s привязаны к заказу %s",
                source_cell_id, dest_cell_id, order_id
            )
            return True
        except Exception as e:
            logger.error(
                "bind_cells_for_order завершился с ошибкой: order_id=%s, error=%s",
                order_id, e
            )
            raise DbLayerError(f"Привязка ячеек к заказу {order_id}: {e}") from e

    def enqueue_fsm_instance(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        process_name: str,
        fsm_state: str,
        requested_by_user_id: int,
        requested_user_role: str,
        target_user_id: Optional[int] = None,
        target_role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Создать или обновить инстанс FSM-процесса."""
        logger.debug(
            "enqueue_fsm_instance вызван: entity_type=%s, entity_id=%s, process_name=%s, state=%s",
            entity_type, entity_id, process_name, fsm_state
        )
        try:
            metadata_json = json.dumps(metadata) if metadata is not None else None
            session.execute(text("""
                INSERT INTO server_fsm_instances (
                    entity_type, entity_id, process_name, fsm_state, attempts_count,
                    requested_by_user_id, requested_user_role,
                    target_user_id, target_role,
                    last_error, next_timer_at, metadata_json
                ) VALUES (
                    :entity_type, :entity_id, :process_name, :fsm_state, 0,
                    :requested_by_user_id, :requested_user_role,
                    :target_user_id, :target_role,
                    NULL, NULL,
                    :metadata_json
                )
                ON DUPLICATE KEY UPDATE
                    fsm_state = VALUES(fsm_state),
                    attempts_count = 0,
                    last_error = NULL,
                    next_timer_at = NULL,
                    requested_by_user_id = VALUES(requested_by_user_id),
                    requested_user_role = VALUES(requested_user_role),
                    target_user_id = VALUES(target_user_id),
                    target_role = VALUES(target_role),
                    metadata_json = VALUES(metadata_json),
                    updated_at = NOW()
            """), {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "process_name": process_name,
                "fsm_state": fsm_state,
                "requested_by_user_id": requested_by_user_id,
                "requested_user_role": requested_user_role,
                "target_user_id": target_user_id,
                "target_role": target_role,
                "metadata_json": metadata_json,
            })

            row = session.execute(text("""
                SELECT id
                FROM server_fsm_instances
                WHERE entity_type = :entity_type
                  AND entity_id = :entity_id
                  AND process_name = :process_name
                LIMIT 1
            """), {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "process_name": process_name,
            }).fetchone()

            if not row:
                logger.error(
                    "enqueue_fsm_instance: не удалось прочитать ID после вставки: "
                    "entity_type=%s, entity_id=%s, process_name=%s",
                    entity_type, entity_id, process_name
                )
                raise DbLayerError("enqueue_fsm_instance: cannot read back instance id")

            instance_id = int(row[0])
            logger.debug(
                "enqueue_fsm_instance: создан/обновлён инстанс id=%s для %s/%s (%s)",
                instance_id, entity_type, entity_id, process_name
            )
            return instance_id

        except Exception as e:
            logger.error(
                "enqueue_fsm_instance завершился с ошибкой: "
                "entity_type=%s, entity_id=%s, process_name=%s, error=%s",
                entity_type, entity_id, process_name, e
            )
            raise DbLayerError(f"enqueue_fsm_instance failed: {e}") from e

    def get_last_instance_status_for_request(
        self,
        session: Session,
        request_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получает статус и last_error самого свежего инстанса для заявки.
        Возвращает {'fsm_state': ..., 'last_error': ...} или None
        """
        logger.debug("get_last_instance_status_for_request вызван: request_id=%s", request_id)
        try:
            row = session.execute(
                text("""
                    SELECT fsm_state, last_error
                    FROM server_fsm_instances
                    WHERE entity_type = 'order_request'
                      AND entity_id = :request_id
                      AND process_name = 'order_creation'
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {"request_id": request_id}
            ).fetchone()

            if row:
                result = {
                    "fsm_state": row[0],
                    "last_error": row[1]
                }
                logger.debug(
                    "get_last_instance_status_for_request: request_id=%s → state=%s, error=%s",
                    request_id, result["fsm_state"], result["last_error"]
                )
                return result

            logger.debug("get_last_instance_status_for_request: инстанс для request_id=%s не найден", request_id)
            return None

        except Exception as e:
            logger.error(
                "get_last_instance_status_for_request завершился с ошибкой для request_id=%s: %s",
                request_id, e
            )
            raise DbLayerError(f"Failed to get FSM instance status for request {request_id}: {e}") from e

    def fetch_ready_fsm_instances(
        self,
        session: Session,
        limit: int,
    ) -> List[Any]:
        """
        Получить FSM-инстансы, готовые к обработке.

        Условия:
        - fsm_state NOT IN ('COMPLETED', 'FAILED')
        - next_timer_at IS NULL OR <= NOW()
        """
        logger.debug("fetch_ready_fsm_instances вызван: limit=%s", limit)
        try:
            rows = session.execute(
                text("""
                    SELECT
                        id,
                        entity_type,
                        entity_id,
                        process_name,
                        fsm_state,
                        next_timer_at,
                        attempts_count,
                        last_error,
                        requested_by_user_id,
                        requested_user_role,
                        target_user_id,
                        target_role,
                        metadata_json
                    FROM server_fsm_instances
                    WHERE fsm_state NOT IN ('COMPLETED', 'FAILED')
                      AND (next_timer_at IS NULL OR next_timer_at <= NOW())
                    ORDER BY id
                    LIMIT :limit
                """),
                {"limit": limit},
            ).fetchall()

            logger.debug("fetch_ready_fsm_instances: найдено %d инстансов", len(rows))
            return rows

        except Exception as e:
            logger.error("fetch_ready_fsm_instances завершился с ошибкой: limit=%s, error=%s", limit, e)
            raise DbLayerError(f"Failed to fetch ready FSM instances: {e}") from e

    def update_fsm_instance(
        self,
        session: Session,
        instance_id: int,
        new_state: str,
        last_error: Optional[str] = None,
        next_timer_at: Optional[datetime] = None,
        attempts_increment: int = 1,
    ) -> None:
        """
        Обновляет состояние FSM-инстанса.
        
        """
        logger.debug(
            "update_fsm_instance вызван: instance_id=%s, new_state=%s, attempts_inc=%s",
            instance_id, new_state, attempts_increment
        )
        try:
            session.execute(
                text("""
                    UPDATE server_fsm_instances
                    SET
                        fsm_state = :new_state,
                        last_error = :last_error,
                        next_timer_at = :next_timer_at,
                        attempts_count = attempts_count + :attempts_increment,
                        updated_at = NOW()
                    WHERE id = :id
                """),
                {
                    "id": instance_id,
                    "new_state": new_state,
                    "last_error": last_error,
                    "next_timer_at": next_timer_at,
                    "attempts_increment": attempts_increment,
                },
            )
            logger.debug(
                "update_fsm_instance: инстанс %s обновлён → state=%s",
                instance_id, new_state
            )
        except Exception as e:
            logger.error(
                "update_fsm_instance завершился с ошибкой: instance_id=%s, error=%s",
                instance_id, e
            )
            raise DbLayerError(f"Failed to update FSM instance {instance_id}: {e}") from e

    def get_stuck_fsm_instances(
        self,
        session: Session,
        threshold_minutes: int,
    ) -> List[int]:
        """
        Возвращает ID FSM-инстансов, которые:
        - не COMPLETED / FAILED
        - updated_at слишком давно
        """
        logger.debug("get_stuck_fsm_instances вызван: threshold_minutes=%s", threshold_minutes)
        try:
            rows = session.execute(
                text("""
                    SELECT id
                    FROM server_fsm_instances
                    WHERE fsm_state NOT IN ('COMPLETED', 'FAILED')
                      AND updated_at < NOW() - INTERVAL :minutes MINUTE
                """),
                {"minutes": threshold_minutes},
            ).fetchall()
            
            stuck_ids = [row[0] for row in rows]
            logger.debug("get_stuck_fsm_instances: найдено %d зависших инстансов", len(stuck_ids))
            return stuck_ids

        except Exception as e:
            logger.error(
                "get_stuck_fsm_instances завершился с ошибкой: threshold=%s, error=%s",
                threshold_minutes, e
            )
            raise DbLayerError(f"Failed to fetch stuck FSM instances: {e}") from e

    def mark_fsm_failed(
        self,
        session: Session,
        instance_id: int,
        error: str,
    ) -> None:
        """Помечает FSM-инстанс как FAILED."""
        logger.info("mark_fsm_failed: инстанс %s помечен как FAILED — %s", instance_id, error)
        self.update_fsm_instance(
            session=session,
            instance_id=instance_id,
            new_state="FAILED",
            last_error=error,
            attempts_increment=0,
        )

    def get_error_types(self, session: Session) -> List[str]:
        """
        Получить список типов ошибок из ENUM report_issues.issue_type.
        """
        logger.debug("get_error_types вызван")
        
        try:
            # Читаем ENUM определение из INFORMATION_SCHEMA
            result = session.execute(
                text("""
                    SELECT COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'report_issues'
                    AND COLUMN_NAME = 'issue_type'
                """)
            ).scalar_one()
            
            # Парсим ENUM: enum('type1','type2',...) → ['type1', 'type2', ...]
            import re
            types = re.findall(r"'([^']+)'", result)
            
            logger.debug("get_error_types: найдено %d типов", len(types))
            return types
            
        except Exception as e:
            logger.error("get_error_types завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_error_types failed: {e}") from e

    # ==================== ЗАКАЗЫ ====================

    def create_order(
        self,
        session: Session,
        description: str,
        source_cell_id: Optional[int],
        dest_cell_id: Optional[int],
        from_city: str,
        to_city: str,
        pickup_type: str = "courier",
        delivery_type: str = "courier",
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
        logger.debug(
            "create_order вызван: from=%s, to=%s, pickup=%s, delivery=%s",
            from_city, to_city, pickup_type, delivery_type
        )
        try:
            session.execute(
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

            result = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            order_id = int(result)
            logger.info("Создан заказ %s: %s → %s", order_id, from_city, to_city)
            return order_id

        except Exception as e:
            logger.error("create_order завершился с ошибкой: %s", e)
            raise DbLayerError(f"Заказ '{description}': {e}") from e

    def create_order_request_and_fsm(
        self,
        session: Session,
        client_user_id: int,
        recipient_user_id: int,
        parcel_type: str,
        cell_size: str,
        sender_delivery: str,
        recipient_delivery: str,
    ) -> int:
        """
        Создаёт заявку в order_requests + инстанс серверного FSM процесса 'order_creation'.
        Возвращает request_id.
        """
        logger.debug(
            "create_order_request_and_fsm вызван: client=%s, parcel=%s, size=%s",
            client_user_id, parcel_type, cell_size
        )
        try:
            # 1. INSERT в order_requests
            session.execute(
                text(
                    """
                    INSERT INTO order_requests
                        (client_user_id, recipient_user_id, parcel_type, cell_size, sender_delivery, recipient_delivery)
                    VALUES
                        (:client_user_id, :recipient_user_id, :parcel_type, :cell_size, :sender_delivery, :recipient_delivery)
                    """
                ),
                {
                    "client_user_id": client_user_id,
                    "recipient_user_id": recipient_user_id,
                    "parcel_type": parcel_type,
                    "cell_size": cell_size,
                    "sender_delivery": sender_delivery,
                    "recipient_delivery": recipient_delivery,
                },
            )

            request_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            request_id = int(request_id)

            # 2. INSERT в server_fsm_instances для процесса 'order_creation'
            session.execute(
                text(
                    """
                    INSERT INTO server_fsm_instances
                        (entity_type, entity_id, process_name, fsm_state, attempts_count)
                    VALUES
                        (:entity_type, :entity_id, :process_name, :fsm_state, :attempts_count)
                    """
                ),
                {
                    "entity_type": "order_request",
                    "entity_id": request_id,
                    "process_name": "order_creation",
                    "fsm_state": "PENDING",
                    "attempts_count": 0,
                },
            )

            logger.info(
                "Создана заявка %s и FSM-инстанс для клиента %s",
                request_id, client_user_id
            )
            return request_id

        except Exception as e:
            logger.error(
                "create_order_request_and_fsm завершился с ошибкой для клиента %s: %s",
                client_user_id, e
            )
            raise DbLayerError(f"create_order_request_and_fsm failed: {e}") from e

    def get_order(self, session: Session, order_id: int) -> Optional[Dict[str, Any]]:
        logger.debug("get_order вызван: order_id=%s", order_id)
        try:
            row = session.execute(
                text(
                    "SELECT id, status, description, pickup_type, delivery_type, "
                    "source_cell_id, dest_cell_id, client_user_id, recipient_user_id "
                    "FROM orders WHERE id = :id"
                ),
                {"id": order_id},
            ).fetchone()

            if row:
                order = {
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "pickup_type": row[3],
                    "delivery_type": row[4],
                    "source_cell_id": row[5],
                    "dest_cell_id": row[6],
                    "client_user_id": row[7],
                    "recipient_user_id": row[8],
                }
                logger.debug("get_order: найден заказ %s", order_id)
                return order

            logger.debug("get_order: заказ %s не найден", order_id)
            return None

        except Exception as e:
            logger.error("get_order завершился с ошибкой для order_id=%s: %s", order_id, e)
            raise DbLayerError(f"Failed to fetch order {order_id}: {e}") from e

    def get_orders_for_route(
        self,
        session: Session,
        from_city: str,
        to_city: str,
        statuses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Вернуть заказы по маршруту (опционально фильтруя по статусам)."""
        logger.debug(
            "get_orders_for_route вызван: from=%s, to=%s, statuses=%s",
            from_city, to_city, statuses
        )
        try:
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

            rows = session.execute(text(query), params).fetchall()

            orders = [
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

            logger.debug("get_orders_for_route: найдено %d заказов", len(orders))
            return orders

        except Exception as e:
            logger.error(
                "get_orders_for_route завершился с ошибкой: from=%s, to=%s, error=%s",
                from_city, to_city, e
            )
            raise DbLayerError(f"Failed to fetch orders for route {from_city}→{to_city}: {e}") from e

    def get_all_orders(
        self,
        session: Session,
        statuses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить список всех заказов (без привязки к маршруту).
        Optionally: фильтр по статусам.
        """
        logger.debug("get_all_orders вызван: statuses=%s", statuses)
        try:
            query = """
                SELECT
                    id,
                    status,
                    description,
                    pickup_type,
                    delivery_type,
                    parcel_type,
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

            rows = session.execute(text(query), params).fetchall()

            orders = [
                {
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "pickup_type": row[3],
                    "delivery_type": row[4],
                    "parcel_type": row[5],
                    "source_cell_id": row[6],
                    "dest_cell_id": row[7],
                }
                for row in rows
            ]

            logger.debug("get_all_orders: найдено %d заказов", len(orders))
            return orders

        except Exception as e:
            logger.error("get_all_orders завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to fetch all orders: {e}") from e

    def get_orders_for_courier(self, session: Session, courier_id: int) -> List[int]:
        """IDs заказов, в которых участвует курьер (courier1 или courier2)."""
        logger.debug("get_orders_for_courier вызван: courier_id=%s", courier_id)
        try:
            rows = session.execute(
                text(
                    "SELECT DISTINCT so.order_id "
                    "FROM stage_orders so "
                    "WHERE so.courier_user_id = :courier_id"
                ),
                {"courier_id": courier_id},
            ).fetchall()

            order_ids = [row[0] for row in rows]
            logger.debug("get_orders_for_courier: найдено %d заказов для курьера %s", len(order_ids), courier_id)
            return order_ids

        except Exception as e:
            logger.error("get_orders_for_courier завершился с ошибкой для courier_id=%s: %s", courier_id, e)
            raise DbLayerError(f"Failed to fetch orders for courier {courier_id}: {e}") from e

    def clear_courier_from_stage_order(
        self,
        session: Session,
        order_id: int,
        leg: str,
        user_id: int
    ) -> bool:
        """
        Очищает courier_user_id в stage_orders для указанного leg.
        Вызывается при отказе курьера от заказа.
        """
        logger.debug(
            "clear_courier_from_stage_order вызван: order_id=%s, leg=%s, user_id=%s",
            order_id, leg, user_id
        )
        try:
            result = session.execute(
                text("""
                    UPDATE stage_orders
                    SET courier_user_id = NULL
                    WHERE order_id = :order_id AND leg = :leg
                """),
                {"order_id": order_id, "leg": leg}
            )
            updated = result.rowcount > 0
            if updated:
                logger.info("Курьер удалён из этапа %s заказа %s", leg, order_id)
            else:
                logger.debug("clear_courier_from_stage_order: запись не найдена (order_id=%s, leg=%s)", order_id, leg)
            return True  # Идемпотентность: всегда успех
        except Exception as e:
            logger.error(
                "clear_courier_from_stage_order завершился с ошибкой: order_id=%s, leg=%s, error=%s",
                order_id, leg, e
            )
            raise DbLayerError(f"clear_courier_from_stage_order failed: {e}") from e

    # ==================== Access Code ====================
    def get_stage_order(self, session: Session, order_id: int, leg: str):
        row = session.execute(
            text("SELECT courier_user_id FROM stage_orders WHERE order_id = :oid AND leg = :leg"),
            {"oid": order_id, "leg": leg}
        ).fetchone()
        return row if row else None

    def count_recent_access_code_requests(
        self,
        session: Session,
        order_id: int,
        leg: str,
        minutes: int
    ) -> int:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        result = session.execute(
            text("""
                SELECT COUNT(*) 
                FROM cell_access_tokens 
                WHERE order_id = :order_id 
                AND leg = :leg 
                AND created_at > :cutoff
            """),
            {"order_id": order_id, "leg": leg, "cutoff": cutoff}
        ).scalar()
        return int(result) if result else 0

    def generate_and_store_access_token(
        self,
        session: Session,
        order_id: int,
        leg: str,
        cell_id: int,
        actor_user_id: int,
        expires_minutes: int = 15
    ) -> Tuple[str, int]:
        """
        Генерирует PIN-код, создаёт хэш и сохраняет токен.
        Для тестирования: PIN хранится в открытом виде в pin_encrypted.
        """
        logger.debug(
            "generate_and_store_access_token вызван: order_id=%s, leg=%s, cell_id=%s, actor=%s",
            order_id, leg, cell_id, actor_user_id
        )
        
        try:
            # 1. Отозвать предыдущие ACTIVE токены
            revoked_result = session.execute(
                text("""
                    UPDATE cell_access_tokens
                    SET status = 'REVOKED'
                    WHERE order_id = :order_id
                    AND leg = :leg
                    AND actor_user_id = :actor_user_id
                    AND status = 'ACTIVE'
                """),
                {
                    "order_id": order_id,
                    "leg": leg,
                    "actor_user_id": actor_user_id,
                }
            )
            revoked_count = revoked_result.rowcount
            if revoked_count > 0:
                logger.info(
                    "generate_and_store_access_token: отозвано %d предыдущих токенов",
                    revoked_count
                )
            
            # 2. Генерация 6-значного PIN
            pin = f"{secrets.randbelow(900000) + 100000:06d}"
            
            # 3. Создание хэша: SHA256(pin + order_id + cell_id)
            pin_hash = hashlib.sha256(f"{pin}{order_id}{cell_id}".encode()).hexdigest()
            
            # 4. Время истечения
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            # 5. Сохранение в базу (PIN в открытом виде для тестирования)
            session.execute(
                text("""
                    INSERT INTO cell_access_tokens (
                        order_id, leg, cell_id, actor_user_id, pin_hash, pin_encrypted, expires_at
                    ) VALUES (
                        :order_id, :leg, :cell_id, :actor_user_id, :pin_hash, :pin_encrypted, :expires_at
                    )
                """),
                {
                    "order_id": order_id,
                    "leg": leg,
                    "cell_id": cell_id,
                    "actor_user_id": actor_user_id,
                    "pin_hash": pin_hash,
                    "pin_encrypted": pin,  # ← Удалить после этапа теста
                    "expires_at": expires_at,
                }
            )
            
            token_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            
            logger.info(
                "generate_and_store_access_token: создан токен %s для заказа %s (leg=%s, actor=%s)",
                token_id, order_id, leg, actor_user_id
            )
            
            return pin, token_id
            
        except Exception as e:
            logger.error("generate_and_store_access_token завершился с ошибкой: %s", e)
            raise DbLayerError(f"generate_and_store_access_token failed: {e}") from e

    def get_access_token_pin(
        self,
        session: Session,
        order_id: int,
        leg: str,
        user_id: int
    ) -> Optional[str]:
        """
        Получить PIN-код для доступа к ячейке.
        Для тестирования: удалить после этапа теста
        """
        logger.debug("get_access_token_pin вызван: order_id=%s, leg=%s, user_id=%s", order_id, leg, user_id)
        
        try:
            row = session.execute(
                text("""
                    SELECT pin_encrypted, expires_at, status
                    FROM cell_access_tokens
                    WHERE order_id = :order_id
                    AND leg = :leg
                    AND actor_user_id = :user_id
                    AND status = 'ACTIVE'
                    AND expires_at > NOW()
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {
                    "order_id": order_id,
                    "leg": leg,
                    "user_id": user_id,
                }
            ).fetchone()
            
            if not row:
                logger.debug("get_access_token_pin: активный токен не найден")
                return None
            
            pin, expires_at, status = row
            
            logger.info("get_access_token_pin: PIN получен для заказа %s", order_id)
            return pin
            
        except Exception as e:
            logger.error("get_access_token_pin завершился с ошибкой: %s", e)
            return None

    def send_code_to_user(self, session: Session, user_id: int, pin: str) -> bool:
        """
        ЗАГЛУШКА: имитация отправки SMS.
        В продакшене заменить на интеграцию с SMS.RU / Twilio.
        """
        try:
            # Получаем телефон для лога
            row = session.execute(
                text("SELECT phone FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            phone = row[0] if row and row[0] else "UNKNOWN"

            # Логируем как MOCK
            logger.info(f"[MOCK SMS] Отправлен PIN {pin} пользователю {user_id} (телефон: {phone})")
            return True  # Всегда успешно

        except Exception as e:
            logger.exception(f"send_code_to_user mock failed for user_id={user_id}: {e}")
            return False

    def validate_courier2_delivery_code(
        self,
        session: Session,
        order_id: int,
        courier_id: int,
        pin: str
    ) -> Tuple[bool, str]:
        """
        Проверка PIN-кода подтверждения доставки для курьера2.
        
        Код должен быть выдан ПОЛУЧАТЕЛЕМ (actor_user_id = recipient_user_id)
        
        Проверки:
        1. Токен существует для этого заказа и leg='delivery'
        2. Токен выдан получателю (actor_user_id = recipient_user_id из заказа)
        3. PIN совпадает (по хэшу SHA256(pin + order_id + cell_id))
        4. Токен активен (status='ACTIVE')
        5. Токен не истёк (expires_at > NOW())
        
        """
        logger.debug("validate_courier2_delivery_code вызван: order_id=%s, courier_id=%s", order_id, courier_id)
        
        try:
            # 1. Получаем заказ для получения recipient_user_id и dest_cell_id
            order = self.get_order(session, order_id)
            if not order:
                return False, "Заказ не найден"
            
            recipient_user_id = order.get("recipient_user_id")
            dest_cell_id = order.get("dest_cell_id")
            
            if not recipient_user_id:
                return False, "У заказа нет получателя"
            
            if not dest_cell_id:
                return False, "У заказа нет dest_cell_id"
            
            # 2. Находим токен для этого заказа (leg='delivery', выдан получателю)
            token_row = session.execute(
                text("""
                    SELECT id, pin_hash, status, expires_at, actor_user_id, cell_id
                    FROM cell_access_tokens
                    WHERE order_id = :order_id
                    AND leg = 'delivery'
                    AND actor_user_id = :recipient_id
                    ORDER BY created_at DESC
                    LIMIT 1
                """),
                {
                    "order_id": order_id,
                    "recipient_id": recipient_user_id,
                }
            ).fetchone()
            
            if not token_row:
                return False, "Код подтверждения не найден для этого заказа"
            
            token_id, stored_pin_hash, token_status, expires_at, actor_user_id, cell_id = token_row
            
            # 3. Проверка статуса токена
            if token_status != 'ACTIVE':
                return False, f"Код неактивен (статус: {token_status})"
            
            # 4. Проверка срока действия
            if expires_at < datetime.utcnow():
                return False, "Код истёк"
            
            # 5. Проверка PIN (сравниваем хэш)
            # Формат: SHA256(pin + order_id + cell_id) — как в AccessCodeActions.request_access_code()
            expected_hash = hashlib.sha256(f"{pin}{order_id}{dest_cell_id}".encode()).hexdigest()
            
            if expected_hash != stored_pin_hash:
                return False, "Неверный код"
            
            # 6. Помечаем токен как использованный
            session.execute(
                text("""
                    UPDATE cell_access_tokens
                    SET status = 'USED', used_at = NOW()
                    WHERE id = :token_id
                """),
                {"token_id": token_id}
            )
            
            logger.info("validate_courier2_delivery_code: код принят для заказа %s (курьер %s)", order_id, courier_id)
            return True, ""
            
        except Exception as e:
            logger.error("validate_courier2_delivery_code завершился с ошибкой: %s", e)
            raise DbLayerError(f"validate_courier2_delivery_code failed: {e}") from e


    # ==================== НОВЫЕ МЕТОДЫ: РАЗВИЛКИ FSM ====================

    def start_order_flow(
        self,
        session: Session,
        order_id: int,
        user_id: int = 0,
    ) -> None:
        """
        Запустить FSM flow заказа на основе pickup_type (первая развилка).
        
        Проверяет pickup_type и делает первый FSM переход:
        - pickup_type='self' → order_reserve_for_client_A_to_B
        - pickup_type='courier' → order_reserve_for_courier_A_to_B
        
        Args:
            session: активная сессия SQLAlchemy
            order_id: ID заказа
            user_id: ID курьера (если pickup_type='courier'), иначе 0
        """
        logger.debug("start_order_flow вызван: order_id=%s, user_id=%s", order_id, user_id)

        order = self.get_order(session, order_id)
        if not order:
            logger.error("start_order_flow: заказ %s не найден", order_id)
            raise DbLayerError(f"Заказ {order_id} не найден")

        pickup_type = order.get("pickup_type", "courier")

        if pickup_type == "self":
            action = "order_reserve_for_client_A_to_B"
            logger.debug("Заказ %s: клиент сам несёт (pickup_type='self')", order_id)

        elif pickup_type == "courier":
            action = "order_reserve_for_courier_A_to_B"
            logger.debug("Заказ %s: назначен курьер1 для забора (pickup_type='courier')", order_id)

        else:
            logger.error("start_order_flow: неизвестный pickup_type='%s' для заказа %s", pickup_type, order_id)
            raise DbLayerError(f"Неизвестный pickup_type: {pickup_type}")

        # Выполняем FSM переход
        self.call_fsm_action(session, "order", order_id, action, user_id)
        logger.info("FSM-действие '%s' выполнено для заказа %s", action, order_id)

    def handle_parcel_confirmed(
        self,
        session: Session,
        order_id: int,
    ) -> None:
        """
        Обработка после попадания посылки в постамат2 (вторая развилка).

        Ожидается, что заказ уже в состоянии order_parcel_confirmed_post2.
        НЕ делает FSM-переходов, только логирует ветку по delivery_type.
        """
        logger.debug("handle_parcel_confirmed вызван: order_id=%s", order_id)

        order = self.get_order(session, order_id)
        if not order:
            logger.error("handle_parcel_confirmed: заказ %s не найден", order_id)
            raise DbLayerError(f"Заказ {order_id} не найден")

        status = order.get("status")
        if status != "order_parcel_confirmed_post2":
            logger.error(
                "handle_parcel_confirmed: некорректный статус '%s' для заказа %s, ожидается 'order_parcel_confirmed_post2'",
                status, order_id
            )
            raise DbLayerError(
                f"handle_parcel_confirmed: некорректный статус '{status}', "
                "ожидается 'order_parcel_confirmed_post2'"
            )

        delivery_type = order.get("delivery_type", "self")

        if delivery_type == "self":
            logger.debug("Заказ %s: в постамате2, ожидает самовывоз получателем", order_id)
            logger.debug("Доступное действие: order_pickup_poluchatel")

        elif delivery_type == "courier":
            logger.debug("Заказ %s: в постамате2, доступен на бирже для курьера2", order_id)
            logger.debug("Доступное действие: order_assign_courier2_to_order")

        else:
            logger.error("handle_parcel_confirmed: неизвестный delivery_type='%s' для заказа %s", delivery_type, order_id)
            raise DbLayerError(f"Неизвестный delivery_type: {delivery_type}")

    # ==================== НОВЫЕ МЕТОДЫ: БИРЖИ ====================

    def get_available_orders_for_pickup(
        self,
        session: Session,
        courier_city: str
    ) -> List[Dict[str, Any]]:
        """
        Биржа для курьеров: забрать посылку у клиента → отнести в постамат А.
        Показывает только заказы, где pickup_type='courier', этап ещё не взят,
        и постамат отправителя находится в городе курьера.
        """
        logger.debug("get_available_orders_for_pickup вызван для города: %s", courier_city)
        try:
            query = """
                SELECT 
                    o.id,
                    o.status,
                    o.description,
                    l.location_address AS source_address,
                    l.city AS source_city,
                    lc.cell_code AS source_cell_code,
                    lc.cell_type AS cell_size
                FROM orders o
                JOIN stage_orders so 
                    ON so.order_id = o.id AND so.leg = 'pickup'
                JOIN locker_cells lc 
                    ON lc.id = o.source_cell_id
                JOIN lockers l 
                    ON l.id = lc.locker_id
                WHERE 
                    o.status = 'order_created'
                    AND o.pickup_type = 'courier'
                    AND so.courier_user_id IS NULL
                    AND l.city = :courier_city  
                ORDER BY o.created_at ASC
            """
            result = session.execute(text(query), {"courier_city": courier_city}).fetchall()  
            orders = [
                {
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "source_address": row[3],
                    "source_city": row[4],
                    "source_cell_code": row[5],
                    "cell_size": row[6],
                }
                for row in result
            ]
            logger.debug("get_available_orders_for_pickup: найдено %d заказов", len(orders))
            return orders
        except Exception as e:
            logger.error("get_available_orders_for_pickup завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to fetch pickup orders: {e}") from e

    def get_available_orders_for_delivery(
        self,
        session: Session,
        courier_city: str
    ) -> List[Dict[str, Any]]:
        """
        Биржа для курьеров: забрать посылку из постамата Б → отдать получателю.
        Показывает только заказы, где delivery_type='courier', этап ещё не взят,
        и постамат получателя находится в городе курьера.
        """
        logger.debug("get_available_orders_for_delivery вызван для города: %s", courier_city)
        try:
            query = """
                SELECT 
                    o.id,
                    o.status,
                    o.description,
                    l.location_address AS dest_address,
                    l.city AS dest_city,
                    lc.cell_code AS dest_cell_code,
                    lc.cell_type AS cell_size
                FROM orders o
                JOIN stage_orders so 
                    ON so.order_id = o.id AND so.leg = 'delivery'
                JOIN locker_cells lc 
                    ON lc.id = o.dest_cell_id
                JOIN lockers l 
                    ON l.id = lc.locker_id
                WHERE 
                    o.status = 'order_parcel_confirmed_post2'
                    AND o.delivery_type = 'courier'
                    AND so.courier_user_id IS NULL
                    AND l.city = :courier_city
                ORDER BY o.created_at ASC
            """
            result = session.execute(text(query), {"courier_city": courier_city}).fetchall()
            orders = [
                {
                    "id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "dest_address": row[3],
                    "dest_city": row[4],
                    "dest_cell_code": row[5],
                    "cell_size": row[6],
                }
                for row in result
            ]
            logger.debug("get_available_orders_for_delivery: найдено %d заказов", len(orders))
            return orders
        except Exception as e:
            logger.error("get_available_orders_for_delivery завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to fetch delivery orders: {e}") from e

    def get_user_by_id(self, session: Session, user_id: int) -> Optional[Dict[str, Any]]:
        row = session.execute(
            text("SELECT id, name, role_name, city FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "role_name": row[2],
                "city": row[3]
            }
        return None

    def get_all_available_orders_for_courier(
        self,
        session: Session,
        courier_city: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Возвращает все доступные заказы для курьера в его городе:
        - pickup: забор у клиента (source_cell в городе курьера)
        - delivery: доставка получателю (dest_cell в городе курьера)
        """
        pickup = self.get_available_orders_for_pickup(session, courier_city)
        delivery = self.get_available_orders_for_delivery(session, courier_city)

        # Добавляем тип прямо здесь — чтобы не дублировать логику в API
        for order in pickup:
            order["type"] = "pickup"
        for order in delivery:
            order["type"] = "delivery"

        return {
            "pickup": pickup,
            "delivery": delivery,
            "all": pickup + delivery  # ← удобно для фронта: один список
        }

    def get_available_trips_for_driver_exchange(
        self,
        session: Session,
        city: str
    ) -> List[Dict[str, Any]]:
        """
        Возвращает рейсы, доступные для взятия водителем из указанного города.
        
        Условия:
        - trips.from_city = :city
        - trips.status = 'trip_created'
        - trips.active = 1
        - trips.driver_user_id IS NULL (ещё не назначен водитель)
        
        Args:
            session: активная сессия SQLAlchemy
            city: город отправления
        
        Returns:
            Список словарей с данными рейсов
        
        Raises:
            DbLayerError: при ошибке выполнения запроса
        """
        logger.debug("get_available_trips_for_driver_exchange вызван для города: %s", city)

        query = text("""
            SELECT
                t.id,
                t.from_city,
                t.to_city,
                t.pickup_locker_id,
                t.delivery_locker_id,
                t.created_at
            FROM trips t
            WHERE
                t.from_city = :city
                AND t.status = 'trip_created'
                AND t.active = 1
                AND t.driver_user_id IS NULL
            ORDER BY t.created_at ASC;
        """)

        try:
            result = session.execute(query, {"city": city}).fetchall()

            trips = [
                {
                    "id": row[0],
                    "from_city": row[1],
                    "to_city": row[2],
                    "pickup_locker_id": row[3],
                    "delivery_locker_id": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                }
                for row in result
            ]

            logger.debug("Найдено %d рейсов для города %s", len(trips), city)
            return trips

        except Exception as e:
            logger.error("get_available_trips_for_driver_exchange завершился с ошибкой: %s", e)
            raise DbLayerError(f"Ошибка получения рейсов для биржи: {e}") from e

    # ==================== РЕЙСЫ ====================

    def set_driver_in_trip(
        self,
        session: Session,
        trip_id: int,
        driver_id: int,
    ) -> None:
        """Назначить водителя на рейс (в trips.driver_user_id)."""
        logger.debug("set_driver_in_trip вызван: trip_id=%s, driver_id=%s", trip_id, driver_id)
        try:
            result = session.execute(
                text("UPDATE trips SET driver_user_id = :driver_id WHERE id = :trip_id"),
                {"driver_id": driver_id, "trip_id": trip_id}
            )
            updated = result.rowcount > 0
            if updated:
                logger.info("Водитель %s назначен на рейс %s", driver_id, trip_id)
            else:
                logger.warning("set_driver_in_trip: рейс %s не найден", trip_id)
        except Exception as e:
            logger.error("set_driver_in_trip завершился с ошибкой: trip_id=%s, error=%s", trip_id, e)
            raise DbLayerError(f"Failed to assign driver {driver_id} to trip {trip_id}: {e}") from e

    def create_trip(
        self,
        session: Session,
        from_city: str,
        to_city: str,
        pickup_locker_id: int,
        delivery_locker_id: int,
        driver_user_id: Optional[int] = None,
        description: Optional[str] = None,
        active: int = 0,
    ) -> int:
        """Создать рейс."""
        logger.debug(
            "create_trip вызван: from=%s, to=%s, pickup_locker=%s, delivery_locker=%s",
            from_city, to_city, pickup_locker_id, delivery_locker_id
        )
        try:
            session.execute(
                text(
                    "INSERT INTO trips (from_city, to_city, pickup_locker_id, delivery_locker_id, "
                    "driver_user_id, active, status) "
                    "VALUES (:from_city, :to_city, :pickup_locker_id, :delivery_locker_id, "
                    ":driver_user_id, :active, 'trip_created')"
                ),
                {
                    "from_city": from_city,
                    "to_city": to_city,
                    "pickup_locker_id": pickup_locker_id,
                    "delivery_locker_id": delivery_locker_id,
                    "driver_user_id": driver_user_id,
                    "active": active,
                },
            )
            trip_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            trip_id = int(trip_id)
            logger.info("Создан рейс %s: %s → %s", trip_id, from_city, to_city)
            return trip_id
        except Exception as e:
            logger.error("create_trip завершился с ошибкой: %s → %s, error=%s", from_city, to_city, e)
            raise DbLayerError(f"Рейс '{from_city}→{to_city}': {e}") from e

    def get_trip(
        self,
        session: Session,
        trip_id: int
    ) -> Optional[Dict[str, Any]]:
        """Вернуть рейс по ID."""
        logger.debug("get_trip вызван: trip_id=%s", trip_id)
        try:
            row = session.execute(
                text(
                    "SELECT id, status, active, from_city, to_city, driver_user_id "
                    "FROM trips WHERE id = :id"
                ),
                {"id": trip_id},
            ).fetchone()
            if row:
                trip = {
                    "id": row[0],
                    "status": row[1],
                    "active": row[2],
                    "from_city": row[3],
                    "to_city": row[4],
                    "driver_user_id": row[5],
                }
                logger.debug("get_trip: найден рейс %s", trip_id)
                return trip
            logger.debug("get_trip: рейс %s не найден", trip_id)
            return None
        except Exception as e:
            logger.error("get_trip завершился с ошибкой для trip_id=%s: %s", trip_id, e)
            raise DbLayerError(f"Failed to fetch trip {trip_id}: {e}") from e

    def get_open_trips_for_route(
        self,
        session: Session,
        from_city: str,
        to_city: str
    ) -> List[Dict[str, Any]]:
        """Незавершённые рейсы по маршруту."""
        logger.debug("get_open_trips_for_route вызван: from=%s, to=%s", from_city, to_city)
        try:
            rows = session.execute(
                text(
                    "SELECT id, status, active, from_city, to_city, driver_user_id "
                    "FROM trips "
                    "WHERE from_city = :from_city AND to_city = :to_city "
                    "  AND status != 'trip_completed'"
                ),
                {"from_city": from_city, "to_city": to_city},
            ).fetchall()
            trips = [
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
            logger.debug("get_open_trips_for_route: найдено %d рейсов", len(trips))
            return trips
        except Exception as e:
            logger.error(
                "get_open_trips_for_route завершился с ошибкой: %s → %s, error=%s",
                from_city, to_city, e
            )
            raise DbLayerError(f"Failed to fetch open trips for route {from_city}→{to_city}: {e}") from e

    def get_active_trips_for_driver(
        self,
        session: Session,
        driver_id: int
    ) -> List[Dict[str, Any]]:
        logger.debug("get_active_trips_for_driver вызван: driver_id=%s", driver_id)
        try:
            rows = session.execute(
                text("""
                    SELECT 
                        id, 
                        status, 
                        active, 
                        from_city, 
                        to_city, 
                        driver_user_id,
                        pickup_locker_id, 
                        delivery_locker_id 
                    FROM trips  
                    WHERE driver_user_id = :driver_id 
                    AND active = 1  
                    AND status != 'trip_completed'
                """),
                {"driver_id": driver_id},
            ).fetchall()

            trips = [
                {
                    "id": row[0],
                    "status": row[1],
                    "active": row[2],
                    "from_city": row[3],
                    "to_city": row[4],
                    "driver_user_id": row[5],
                    "pickup_locker_id": row[6],      # Теперь есть
                    "delivery_locker_id": row[7],    # Теперь есть
                }
                for row in rows
            ]
            logger.debug("get_active_trips_for_driver: найдено %d активных рейсов", len(trips))
            return trips
        except Exception as e:
            logger.error(
                "get_active_trips_for_driver завершился с ошибкой для driver_id=%s: %s",
                driver_id, e
            )
            raise DbLayerError(f"Failed to fetch active trips for driver {driver_id}: {e}") from e

    def get_trip_orders(
        self,
        session: Session,
        trip_id: int
    ) -> List[Dict[str, Any]]:
        """
        Вернуть список заказов рейса с деталями.        
        
        """
        logger.debug("get_trip_orders вызван: trip_id=%s", trip_id)
        try:
            rows = session.execute(
                text("""
                    SELECT 
                        o.id,
                        o.status,
                        o.description,
                        o.pickup_type,
                        o.delivery_type,
                        o.source_cell_id,
                        o.dest_cell_id,
                        o.client_user_id,
                        o.recipient_user_id
                    FROM stage_orders so
                    JOIN orders o ON o.id = so.order_id
                    WHERE so.trip_id = :trip_id
                    AND so.leg = 'pickup'
                """),
                {"trip_id": trip_id},
            ).fetchall()
            
            orders = [
                {
                    "order_id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "pickup_type": row[3],
                    "delivery_type": row[4],
                    "source_cell_id": row[5],
                    "dest_cell_id": row[6],
                    "client_user_id": row[7],
                    "recipient_user_id": row[8],
                }
                for row in rows
            ]
            
            logger.debug("get_trip_orders: найдено %d заказов для рейса %s", len(orders), trip_id)
            return orders
            
        except Exception as e:
            logger.error("get_trip_orders завершился с ошибкой для trip_id=%s: %s", trip_id, e)
            raise DbLayerError(f"Failed to fetch orders for trip {trip_id}: {e}") from e

    def get_trip_id_by_order_id(self, session: Session, order_id: int) -> Optional[int]:
        """Возвращает trip_id из stage_orders по order_id."""
        logger.debug("get_trip_id_by_order_id вызван: order_id=%s", order_id)
        try:
            result = session.execute(
                text("SELECT trip_id FROM stage_orders WHERE order_id = :order_id LIMIT 1"),
                {"order_id": order_id}
            ).scalar()
            return result  # может быть int или None
        except Exception as e:
            logger.error("get_trip_id_by_order_id завершился с ошибкой для order_id=%s: %s", order_id, e)
            raise DbLayerError(f"Failed to get trip_id for order {order_id}: {e}") from e

    def assign_order_to_trip(
        self,
        session: Session,
        order_id: int,
        trip_id: int
    ) -> Tuple[bool, str]:
        """
        Привязывает заказ к рейсу.
        Обновляет trip_id в уже существующих записях stage_orders (pickup/delivery).
        """
        logger.debug("assign_order_to_trip вызван: order_id=%s, trip_id=%s", order_id, trip_id)
        try:
            # Проверка: заказ не должен быть в активном рейсе
            count = session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM stage_orders so
                    JOIN trips t ON t.id = so.trip_id
                    WHERE so.order_id = :order_id
                    AND t.status NOT IN ('trip_completed', 'trip_failed')
                """),
                {"order_id": order_id},
            ).scalar()
            if count and count > 0:
                msg = "Заказ уже привязан к активному рейсу"
                logger.warning("assign_order_to_trip: %s (order_id=%s)", msg, order_id)
                return False, msg

            # Проверка статуса рейса
            trip_status = session.execute(
                text("SELECT status FROM trips WHERE id = :trip_id"),
                {"trip_id": trip_id},
            ).scalar()
            if not trip_status:
                msg = f"Рейс {trip_id} не найден"
                logger.warning("assign_order_to_trip: %s", msg)
                return False, msg
            if trip_status not in ("trip_created", "trip_assigned"):
                msg = f"Нельзя привязать к рейсу в статусе '{trip_status}'"
                logger.warning("assign_order_to_trip: %s", msg)
                return False, msg

            # Лимит 5 заказов на рейс
            trip_count = session.execute(
                text("SELECT COUNT(DISTINCT order_id) FROM stage_orders WHERE trip_id = :trip_id"),
                {"trip_id": trip_id},
            ).scalar()
            logger.debug("assign_order_to_trip: текущее количество заказов в рейсе %s = %s", trip_id, trip_count)
            if trip_count is not None and trip_count >= 5:
                msg = "На рейсе уже 5 заказов"
                logger.warning("assign_order_to_trip: %s (trip_id=%s)", msg, trip_id)
                return False, msg

            # ОБНОВЛЕНИЕ trip_id в существующих записях
            result = session.execute(
                text("""
                    UPDATE stage_orders
                    SET trip_id = :trip_id
                    WHERE order_id = :order_id
                    AND leg IN ('pickup', 'delivery')
                """),
                {"trip_id": trip_id, "order_id": order_id},
            )

            if result.rowcount != 2:
                logger.warning("assign_order_to_trip: обновлено %d строк вместо 2 для order_id=%s", result.rowcount, order_id)

            logger.info("Заказ %s успешно привязан к рейсу %s", order_id, trip_id)
            return True, "Заказ привязан к рейсу"

        except Exception as e:
            logger.error(
                "assign_order_to_trip завершился с ошибкой: order_id=%s, trip_id=%s, error=%s",
                order_id, trip_id, e
            )
            raise DbLayerError(f"Ошибка привязки заказа {order_id} к рейсу {trip_id}: {e}") from e

    def assign_order_to_trip_smart(
        self,
        session: Session,
        order_id: int,
        pickup_locker_id: int,
        delivery_locker_id: int,
        from_city: str,
        to_city: str,
    ) -> Tuple[int, bool, str]:
        """
        Привязывает заказ к рейсу.
        Ищет рейсы с <5 заказами, если нет — создаёт новый.
        Если после привязки стало ровно 5 заказов — сразу активирует рейс.
        """
        logger.debug("assign_order_to_trip_smart: order=%s, from=%s, to=%s", order_id, from_city, to_city)
        try:
            # 1. Ищем существующий рейс ПО ЛОКЕРАМ
            existing_trip = session.execute(text("""
                SELECT t.id
                FROM trips t
                LEFT JOIN (
                    SELECT trip_id, COUNT(DISTINCT order_id) AS cnt
                    FROM stage_orders
                    GROUP BY trip_id
                ) so ON so.trip_id = t.id
                WHERE t.pickup_locker_id = :pickup_locker_id
                AND t.delivery_locker_id = :delivery_locker_id
                AND t.status IN ('trip_created', 'trip_assigned')
                AND t.active = 0
                AND (so.cnt IS NULL OR so.cnt < 5)
                ORDER BY t.id ASC
                LIMIT 1
            """), {
                "pickup_locker_id": pickup_locker_id,
                "delivery_locker_id": delivery_locker_id,
            }).fetchone()

            if existing_trip:
                trip_id = existing_trip[0]
                logger.debug("Используем существующий рейс %s для заказа %s", trip_id, order_id)
            else:
                # 2. Создаём новый рейс
                trip_id = self.create_trip(
                    session,
                    from_city=from_city,
                    to_city=to_city,
                    pickup_locker_id=pickup_locker_id,
                    delivery_locker_id=delivery_locker_id,
                    driver_user_id=None,
                    active=0,
                )
                logger.debug("Создан новый рейс %s для заказа %s", trip_id, order_id)

            # 3. Привязываем заказ
            success, msg = self.assign_order_to_trip(session, order_id, trip_id)
            if not success:
                return 0, False, msg

            # 4. 🔥 Проверяем: стало ли 5 заказов?
            current_count = session.execute(text("""
                SELECT COUNT(DISTINCT order_id)
                FROM stage_orders
                WHERE trip_id = :trip_id
            """), {"trip_id": trip_id}).scalar()

            if current_count == 5:
                logger.info("Рейс %s набрал 5 заказов — активируем немедленно", trip_id)
                session.execute(text("UPDATE trips SET active = 1 WHERE id = :trip_id"), {"trip_id": trip_id})

            return trip_id, True, "Заказ привязан"
        except Exception as e:
            logger.error("assign_order_to_trip_smart failed for order %s: %s", order_id, e)
            raise DbLayerError(f"assign_order_to_trip_smart failed: {e}") from e

    def update_trip_active_flags(
        self,
        session: Session,
        max_orders=5,        
        wait_hours: float = 24.0
    ) -> int:
        """
        Активация рейсов ТОЛЬКО по таймауту (24 часа).
        Рейсы с 5+ заказами уже активированы в assign_order_to_trip_smart.
        """
        logger.debug("update_trip_active_flags (таймаут-режим): wait_hours=%s", wait_hours)
        if wait_hours <= 0:
            return 0

        try:
            threshold = datetime.now() - timedelta(hours=wait_hours)
            rows = session.execute(text("""
                SELECT t.id, t.created_at
                FROM trips t
                WHERE t.status = 'trip_created'
                AND t.active = 0
                AND t.created_at < :threshold
            """), {"threshold": threshold}).fetchall()

            updated = 0
            for trip_id, _ in rows:
                logger.info("Рейс %s активирован по таймауту (%s ч)", trip_id, wait_hours)
                session.execute(text("UPDATE trips SET active = 1 WHERE id = :trip_id"), {"trip_id": trip_id})
                updated += 1

            if updated > 0:
                logger.info("Активировано %s рейсов по таймауту", updated)
            return updated
        except Exception as e:
            logger.error("update_trip_active_flags завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to update trip active flags: {e}") from e

    def get_orders_with_status_in_trip(
        self,
        session: Session,
        trip_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить все заказы рейса с их FSM-статусами.
        
        Args:            
            trip_id: ID рейса
        
        Returns:
            Список словарей: [{"order_id": int, "status": str}, ...]
        """
        logger.debug("get_orders_with_status_in_trip вызван: trip_id=%s", trip_id)
        
        try:
            rows = session.execute(
                text("""
                    SELECT 
                        so.order_id,
                        o.status
                    FROM stage_orders so
                    JOIN orders o ON o.id = so.order_id
                    WHERE so.trip_id = :trip_id
                    AND so.leg = 'pickup'
                """),
                {"trip_id": trip_id}
            ).fetchall()
            
            orders = [
                {
                    "order_id": row[0],
                    "status": row[1],
                }
                for row in rows
            ]
            
            logger.debug("get_orders_with_status_in_trip: найдено %d заказов", len(orders))
            return orders
            
        except Exception as e:
            logger.error("get_orders_with_status_in_trip завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_orders_with_status_in_trip failed: {e}") from e

    def validate_and_get_orders_for_trip_start(
        self,
        session: Session,
        trip_id: int
    ) -> Tuple[bool, List[int], List[int], str]:
        """
        Проверка готовности рейса к старту (забор посылок из Пост1).    
        
        """
        logger.debug("validate_and_get_orders_for_trip_start вызван: trip_id=%s", trip_id)
        
        try:        
            # 1. Проверка статуса рейса        
            trip = self.get_trip(session, trip_id)
            if not trip:
                return False, [], [], f"Рейс {trip_id} не найден"
            
            if trip["status"] != "trip_assigned":
                return False, [], [], (
                    f"Рейс в статусе '{trip['status']}', ожидается 'trip_assigned'"
                )       
            
            # 2. Получаем все заказы рейса с их статусами        
            orders = self.get_orders_with_status_in_trip(session, trip_id)
            if not orders:
                return False, [], [], "В рейсе нет заказов"        
            
            # 3. Статусы заказов        
            expected_order_status = "order_picked_up_from_post1"       
            
            excluded_order_statuses = [
                "order_manual_intervention_required",
                "order_parcel_missing",
                "order_cancelled",
            ]        
            
            # 4. Статусы ячеек        
            expected_cell_status = "locker_occupied"       
        
            excluded_cell_statuses = [
                "locker_error",
                "locker_maintenance",
            ]        
            
            # 5. Проверка заказов       
            blocked_ids: List[int] = []
            transit_ids: List[int] = []
            
            for o in orders:
                order_id = o["order_id"]
                order_status = o["status"]
                
                # Пропускаем проблемные заказы
                if order_status in excluded_order_statuses:
                    logger.debug(
                        "validate_and_get_orders_for_trip_start: заказ %s в статусе '%s' — исключён",
                        order_id, order_status
                    )
                    continue
                
                # Проверяем успешные заказы
                if order_status == expected_order_status:
                    transit_ids.append(order_id)
                else:
                    blocked_ids.append(order_id)
            
            if blocked_ids:
                return False, blocked_ids, [], (
                    f"Нельзя начать путь: заказы {blocked_ids} не готовы "
                    f"(ожидался статус '{expected_order_status}')"
                )        
            
            # 6. Проверка pickup ячеек (Пост1)        
            pickup_cells = session.execute(
                text("""
                    SELECT 
                        lc.id,
                        lc.status,
                        o.id as order_id
                    FROM locker_cells lc
                    JOIN orders o ON o.id = lc.current_order_id
                    JOIN stage_orders so ON so.order_id = o.id
                    WHERE so.trip_id = :trip_id
                    AND lc.id = o.source_cell_id
                    AND o.status NOT IN :excluded_order_statuses
                """),
                {
                    "trip_id": trip_id,
                    "excluded_order_statuses": tuple(excluded_order_statuses)
                }
            ).fetchall()
            
            for cell_row in pickup_cells:
                cell_id, cell_status, order_id = cell_row
                
                # Пропускаем проблемные ячейки
                if cell_status in excluded_cell_statuses:
                    logger.debug(
                        "validate_and_get_orders_for_trip_start: ячейка %s в статусе '%s' — исключена",
                        cell_id, cell_status
                    )
                    continue
                
                # Проверяем успешные ячейки
                if cell_status != expected_cell_status:
                    return False, [], [], (
                        f"Pickup ячейка {cell_id} (заказ {order_id}) в статусе '{cell_status}', "
                        f"ожидается '{expected_cell_status}'"
                    )
            
            logger.info(
                "validate_and_get_orders_for_trip_start: trip_id=%s — OK, transit=%d заказов",
                trip_id, len(transit_ids)
            )
            return True, [], transit_ids, ""
            
        except Exception as e:
            logger.error("validate_and_get_orders_for_trip_start завершился с ошибкой: %s", e)
            raise DbLayerError(f"validate_and_get_orders_for_trip_start failed: {e}") from e

    def validate_trip_for_completion(
        self,
        session: Session,
        trip_id: int
    ) -> Tuple[bool, List[int], List[int], str]:
        """
        Проверка готовности рейса к завершению (посылки размещены в Пост2).
        
        """
        logger.debug("validate_trip_for_completion вызван: trip_id=%s", trip_id)
        
        try:            
            # 1. Проверка статуса рейса            
            trip = self.get_trip(session, trip_id)
            if not trip:
                return False, [], [], f"Рейс {trip_id} не найден"
            
            if trip["status"] != "trip_in_progress":
                return False, [], [], (
                    f"Рейс в статусе '{trip['status']}', ожидается 'trip_in_progress'"
                )            
            
            # 2. Получаем все заказы рейса с их статусами            
            orders = self.get_orders_with_status_in_trip(session, trip_id)
            if not orders:
                return False, [], [], "В рейсе нет заказов"            
            
            # 3. Статусы заказов            
            expected_order_status = "order_parcel_confirmed_post2"           
            
            excluded_order_statuses = [
                "order_manual_intervention_required",
                "order_parcel_missing",
                "order_cancelled",
            ]            
            # 4. Статусы ячеек            
            expected_cell_status = "locker_occupied"            
            
            excluded_cell_statuses = [
                "locker_error",
                "locker_maintenance",
            ]            
            
            # 5. Проверка заказов            
            blocked_ids: List[int] = []
            completed_ids: List[int] = []
            
            for o in orders:
                order_id = o["order_id"]
                order_status = o["status"]
                
                # Пропускаем проблемные заказы
                if order_status in excluded_order_statuses:
                    logger.debug(
                        "validate_trip_for_completion: заказ %s в статусе '%s' — исключён",
                        order_id, order_status
                    )
                    continue
                
                # Проверяем успешные заказы
                if order_status == expected_order_status:
                    completed_ids.append(order_id)
                else:
                    blocked_ids.append(order_id)
            
            if blocked_ids:
                return False, blocked_ids, [], (
                    f"Нельзя завершить рейс: заказы {blocked_ids} не размещены в Пост2 "
                    f"(ожидался статус '{expected_order_status}')"
                )            
            
            # 6. Проверка delivery ячеек (Пост2)            
            delivery_cells = session.execute(
                text("""
                    SELECT 
                        lc.id,
                        lc.status,
                        o.id as order_id
                    FROM locker_cells lc
                    JOIN orders o ON o.id = lc.current_order_id
                    JOIN stage_orders so ON so.order_id = o.id
                    WHERE so.trip_id = :trip_id
                    AND lc.id = o.dest_cell_id
                    AND o.status NOT IN :excluded_order_statuses
                """),
                {
                    "trip_id": trip_id,
                    "excluded_order_statuses": tuple(excluded_order_statuses)
                }
            ).fetchall()
            
            for cell_row in delivery_cells:
                cell_id, cell_status, order_id = cell_row
                
                # Пропускаем проблемные ячейки
                if cell_status in excluded_cell_statuses:
                    logger.debug(
                        "validate_trip_for_completion: ячейка %s в статусе '%s' — исключена",
                        cell_id, cell_status
                    )
                    continue
                
                # Проверяем успешные ячейки
                if cell_status != expected_cell_status:
                    return False, [], [], (
                        f"Delivery ячейка {cell_id} (заказ {order_id}) в статусе '{cell_status}', "
                        f"ожидается '{expected_cell_status}'"
                    )
            
            logger.info(
                "validate_trip_for_completion: trip_id=%s — OK, completed=%d заказов",
                trip_id, len(completed_ids)
            )
            return True, [], completed_ids, ""
            
        except Exception as e:
            logger.error("validate_trip_for_completion завершился с ошибкой: %s", e)
            raise DbLayerError(f"validate_trip_for_completion failed: {e}") from e

    # ==================== АВТОМАТИЧЕСКАЯ ОБРАБОТКА ТАЙМАУТОВ ====================

    def check_and_process_reservation_timeouts(
        self,
        session: Session,
        timeout_seconds: int = 30
    ) -> int:
        """
        Находит просроченные резервы и автоматически вызывает order_timeout_reservation.
        
        Returns:
            Количество обработанных заказов
        """
        logger.debug("check_and_process_reservation_timeouts вызван: timeout=%s сек", timeout_seconds)
        try:
            # Находим просроченные заказы
            expired_orders = session.execute(text("""
                SELECT id FROM orders
                WHERE status IN ('order_courier_reserved_post1_and_post2', 'order_client_reserved_post1_and_post2')
                  AND TIMESTAMPDIFF(SECOND, created_at, NOW()) > :timeout
            """), {"timeout": timeout_seconds}).fetchall()

            processed = 0
            for (oid,) in expired_orders:
                try:
                    # Автоматически вызываем таймаут
                    self.call_fsm_action(session, "order", oid, "order_timeout_reservation", 0)  # system user_id=0
                    logger.info("Обработан таймаут резерва для заказа %s", oid)
                    processed += 1
                except Exception as e:
                    logger.error("Ошибка обработки таймаута заказа %s: %s", oid, e)
                    # Не прерываем цикл — продолжаем обработку других заказов

            logger.debug("check_and_process_reservation_timeouts: обработано %d заказов", processed)
            return processed

        except Exception as e:
            logger.error("check_and_process_reservation_timeouts завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to process reservation timeouts: {e}") from e

    # ==================== СЕРВИСНЫЕ ПРОЦЕДУРЫ ====================

    def clear_test_data(self) -> bool:
        """
        Вызвать хранимую процедуру clear_test_data().
        ВНИМАНИЕ: этот метод НЕ использует session и работает напрямую с БД.
        Предназначен ТОЛЬКО для тестов/разработки.
        """
        logger.warning("Вызывается clear_test_data() — ОЧИСТКА ТЕСТОВЫХ ДАННЫХ!")
        try:
            # Предполагается, что self._raw_config доступен (как в оригинале)
            conn = mysql.connector.connect(**self._raw_config)
            cursor = conn.cursor()
            cursor.callproc("clear_test_data")
            for result in cursor.stored_results():
                _ = result.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Тестовые данные успешно очищены")
            return True
        except Error as e:
            logger.error("clear_test_data завершился с ошибкой: %s", e)
            raise DbLayerError(f"clear_test_data: {e}") from e

    def get_log_counters(self, session: Session) -> Tuple[int, int, int]:
        """Вернуть счётчики логов: (fsm_errors_log, fsm_action_logs, report_issues)."""
        logger.debug("get_log_counters вызван")
        try:
            error_count = session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM fsm_errors_log")
            ).scalar()
            fsm_count = session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM fsm_action_logs")
            ).scalar()
            # ✅ Заменили hardware_command_log на report_issues
            issues_count = session.execute(
                text("SELECT COALESCE(MAX(id), 0) FROM report_issues")
            ).scalar()

            counters = (
                int(error_count or 0),
                int(fsm_count or 0),
                int(issues_count or 0)
            )
            logger.debug("get_log_counters: %s", counters)
            return counters
        except Exception as e:
            logger.error("get_log_counters завершился с ошибкой: %s", e)
            return 0, 0, 0
    

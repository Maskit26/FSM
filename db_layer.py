#"""
#ORM слой для работы с базой данных логистической системы.
#
#Требования:
#pip install sqlalchemy mysql-connector-python

#Использование:
#from db_layer import DatabaseLayer, DbLayerError, FsmCallError

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
import re

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
        safe_extra_id = extra_id if extra_id is not None else ""

        try:
            connection = session.connection().connection
            cursor = connection.cursor()

            try:
                cursor.callproc("fsm_perform_action", [
                    entity_type, 
                    entity_id, 
                    action_name, 
                    user_id, 
                    safe_extra_id
                ])

                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())

                while cursor.nextset():
                    pass

                if results:
                    result_text = str(results[0][0])
                    if "FSM action completed" in result_text:
                        logger.debug("[FSM] Success: %s", result_text)
                        return True
                    else:
                        raise DbLayerError(f"FSM Procedure returned: {result_text}")
                
                raise DbLayerError("FSM Procedure: No result returned")

            finally:
                cursor.close()

        except Exception as e:
            logger.error("[FSM] Call failed: %s", e)                       
            raise DbLayerError(f"FSM {action_name} failed: {e}") from e

    def log_error_to_db(
        self,
        session: Session,
        error_message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action_name: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        """Записать общую ошибку бэкенда в fsm_errors_log."""
        logger.debug( "log_error_to_db вызван: error=%s ", error_message[:100] if error_message else None)
        
        try:
            session.execute(text( """
                INSERT INTO fsm_errors_log (
                    error_time, error_message, entity_type, entity_id, action_name, user_id
                ) VALUES (
                    NOW(), :error_message, :entity_type, :entity_id, :action_name, :user_id
                )
            """ ), {
                "error_message": error_message,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action_name": action_name,
                "user_id": user_id,
            })
            
            logger.debug( "log_error_to_db: ошибка записана в fsm_errors_log ")
            
        except Exception as e:
            logger.error( "log_error_to_db завершился с ошибкой: %s ", e)

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
    
    def trip_reassign_driver(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Переназначение водителя на рейс после поломки (FSM: trip_reassign_driver)."""
        
        return self.call_fsm_action(session, "trip", trip_id, "trip_reassign_driver", driver_id)

    def trip_resume_with_new_driver(self, session: Session, trip_id: int, new_driver_id: int) -> bool:
        """
        Назначает нового водителя на сломанный рейс и сразу переводит его в trip_in_progress.
        """
        return self.call_fsm_action(session, "trip", trip_id, "trip_resume_with_new_driver", new_driver_id)

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

    def trip_cancel(self, session: Session, trip_id: int, driver_id: int) -> bool:
        """Отмена рейса водителем (FSM: trip_cancel)."""
        return self.call_fsm_action(session, "trip", trip_id, "trip_cancel", driver_id)

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

    def driver_reservation_start_loading(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> bool:
        """
        Начать погрузку (FSM: reservation_active → reservation_loading).
        """
        logger.debug(
            "driver_reservation_start_loading вызван: reservation_id=%s, driver_user_id=%s",
            reservation_id, driver_user_id
        )
        return self.call_fsm_action(
            session,
            "driver_reservations",
            reservation_id,
            "driver_reservation_start_loading",
            driver_user_id,
        )

    def driver_reservation_complete_loading(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> bool:
        """
        Завершить погрузку (FSM: reservation_loading → reservation_completed).
        """
        logger.debug(
            "driver_reservation_complete_loading вызван: reservation_id=%s, driver_user_id=%s",
            reservation_id, driver_user_id
        )
        return self.call_fsm_action(
            session,
            "driver_reservations",
            reservation_id,
            "driver_reservation_complete_loading",
            driver_user_id,
        )

    def driver_reservation_expire(
        self,
        session: Session,
        reservation_id: int,
        user_id: int,
    ) -> bool:
        """
        Таймаут резерва (FSM: reservation_active/loading → reservation_expired).
        """
        logger.debug(
            "driver_reservation_expire вызван: reservation_id=%s, user_id=%s",
            reservation_id, user_id
        )
        return self.call_fsm_action(
            session,
            "driver_reservations",
            reservation_id,
            "driver_reservation_expire",
            user_id,
        )

    def cancel_driver_reservation(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> bool:
        """
        Отмена резерва (FSM: reservation_loading → reservation_cancelled).
        """
        logger.debug("cancel_driver_reservation вызван: reservation_id=%s, driver_user_id=%s", reservation_id, driver_user_id)
        
        return self.call_fsm_action(
            session,
            "driver_reservations",
            reservation_id,
            "driver_reservation_cancel",
            driver_user_id,
        )

    # ---------- ORDER / ЗАКАЗЫ ----------

    def get_orders_in_trip(self, session: Session, trip_id: int) -> List[int]:
        result = session.execute(
            text("SELECT DISTINCT order_id FROM stage_orders WHERE trip_id = :trip_id"),
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
        order_id: Optional[int],
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

    def order_client_deliv_post1(self, session: Session, order_id: int, user_id: int) -> bool:
        """Клиент положил посылку в постамат1 (FSM: order_client_deliv_post1)."""
        return self.call_fsm_action(session, "order", order_id, "order_client_deliv_post1", user_id)
    
    def order_confirm_parcel_in(self, session: Session, order_id: int, user_id: int) -> bool:
        """Подтверждение, что посылка находится в нужном месте."""
        logger.debug("order_confirm_parcel_in вызван: order_id=%s, user_id=%s", order_id, user_id)
        
        # Выполняем FSM-переход
        self.call_fsm_action(session, "order", order_id, "order_confirm_parcel_in", user_id)

        # Ставим задачу на привязку к Направлению
        self.enqueue_fsm_instance(
            session,
            entity_type="order",
            entity_id=order_id,
            process_name="bind_order_to_trip",
            fsm_state="PENDING",
            requested_by_user_id=999999,
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

    def order_mark_delivered_parcel(self, session: Session, order_id: int, user_id: int) -> bool:
        """Заказ отмечен как доставленный (FSM: order_delivered_parcel)."""
        return self.call_fsm_action(session, "order", order_id, "order_delivered_parcel", user_id)

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

    def reassign_driver_in_stage_orders(
        self,
        session: Session,
        order_ids: List[int],
        new_driver_id: int
    ) -> None:
        """Обновляет reserved_by_driver_id во всех stage_orders для списка заказов."""
        if not order_ids:
            return
        try:
            # Генерируем плейсхолдеры :order_0, :order_1, ...
            placeholders = ", ".join([f":order_{i}" for i in range(len(order_ids))])
            params = {f"order_{i}": oid for i, oid in enumerate(order_ids)}
            params["new_driver"] = new_driver_id

            session.execute(
                text(f"""
                    UPDATE stage_orders
                    SET reserved_by_driver_id = :new_driver
                    WHERE order_id IN ({placeholders})
                    AND leg IN ('pickup', 'delivery')
                """),
                params
            )
            logger.info("[DB] Водитель обновлён в stage_orders для заказов: %s", order_ids)
        except Exception as e:
            logger.exception("Ошибка при переназначении водителя в stage_orders: %s", e)
            raise DbLayerError(f"Не удалось обновить stage_orders: {e}") from e

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

    def get_recipient_orders(self, session: Session, recipient_id: int) -> List[Dict[str, Any]]:
        """
        Получить все заказы получателя.
        
        Источник истины:
        - orders (recipient_user_id)
        """
        logger.debug("get_recipient_orders вызван для recipient_id=%s", recipient_id)
        
        if recipient_id <= 0:
            raise DbLayerError("Invalid recipient_id")
        
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
                        o.updated_at
                    FROM orders o
                    WHERE o.recipient_user_id = :recipient_id
                    ORDER BY o.created_at DESC
                """),
                {"recipient_id": recipient_id},
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
                })
            
            logger.debug("get_recipient_orders: найдено %d заказов для recipient_id=%s", len(orders), recipient_id)
            return orders
            
        except Exception as e:
            logger.error("get_recipient_orders завершился с ошибкой для recipient_id=%s: %s", recipient_id, e)
            raise DbLayerError(f"get_recipient_orders failed: {e}") from e

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

    def get_driver_reservations(
        self,
        session: Session,
        driver_user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Получить активные резервы (слоты) водителя.        
        """
        logger.debug("get_driver_reservations вызван для driver_user_id=%s", driver_user_id)
        
        try:
            reservations_rows = session.execute(
                text("""
                    SELECT
                        dr.id,
                        dr.direction_id,
                        dr.reserved_count,
                        dr.requested_count,
                        dr.reserved_at,
                        dr.expires_at,
                        dr.status,
                        d.from_city,
                        d.to_city,
                        d.pickup_locker_id,
                        d.delivery_locker_id
                    FROM driver_reservations dr
                    JOIN directions d ON d.id = dr.direction_id
                    WHERE dr.driver_user_id = :driver_user_id
                    AND dr.status IN ('reservation_active', 'reservation_loading')
                    ORDER BY dr.reserved_at DESC
                """),
                {"driver_user_id": driver_user_id},
            ).fetchall()
            
            reservations = []
            for res_row in reservations_rows:
                reservations.append({
                    "reservation_id": res_row[0],
                    "direction_id": res_row[1],
                    "reserved_count": res_row[2],
                    "requested_count": res_row[3],
                    "reserved_at": res_row[4].isoformat() if res_row[4] else None,
                    "expires_at": res_row[5].isoformat() if res_row[5] else None,
                    "status": res_row[6],
                    "from_city": res_row[7],
                    "to_city": res_row[8],
                    "pickup_locker_id": res_row[9],
                    "delivery_locker_id": res_row[10],                    
                })
            
            return reservations
            
        except Exception as e:
            logger.error("get_driver_reservations завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_driver_reservations failed: {e}") from e    

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
    
    def get_user_fsm_errors(
        self,
        session: Session,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получить последние FSM-ошибки для пользователя.
        
        Возвращает ошибки из server_fsm_instances где:
        - requested_by_user_id = user_id
        - fsm_state = 'FAILED'
        - last_error IS NOT NULL
        
        """
        logger.debug("get_user_fsm_errors вызван: user_id=%s", user_id)
        
        try:
            rows = session.execute(
                text("""
                    SELECT 
                        id,
                        entity_type,
                        entity_id,
                        process_name,
                        fsm_state,
                        last_error,
                        created_at,
                        updated_at,
                        metadata_json
                    FROM server_fsm_instances
                    WHERE requested_by_user_id = :user_id
                    AND fsm_state = 'FAILED'
                    AND last_error IS NOT NULL
                    ORDER BY updated_at DESC
                    LIMIT :limit
                """),
                {
                    "user_id": user_id,
                    "limit": limit,
                }
            ).fetchall()
            
            errors = [
                {
                    "instance_id": row[0],
                    "entity_type": row[1],
                    "entity_id": row[2],
                    "process_name": row[3],
                    "fsm_state": row[4],
                    "last_error": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                    "updated_at": row[7].isoformat() if row[7] else None,
                    "metadata": json.loads(row[8]) if row[8] else None,
                }
                for row in rows
            ]
            
            logger.debug("get_user_fsm_errors: найдено %d ошибок для user_id=%s", len(errors), user_id)
            return errors
            
        except Exception as e:
            logger.error("get_user_fsm_errors завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_user_fsm_errors failed: {e}") from e

    def get_fsm_instance_state(
        self,
        session: Session,
        instance_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Возвращает (fsm_state, last_error) для FSM-инстанса.
        Если инстанс не найден, возвращает (None, None).
        """
        logger.debug("get_fsm_instance_state: instance_id=%s", instance_id)
        try:
            row = session.execute(
                text("SELECT fsm_state, last_error FROM server_fsm_instances WHERE id = :id"),
                {"id": instance_id}
            ).fetchone()
            if not row:
                return None, None
            return row[0], row[1]
        except Exception as e:
            logger.error("get_fsm_instance_state failed: %s", e)
            raise DbLayerError(f"Failed to get FSM instance state: {e}") from e

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
    ) -> Tuple[int, int]: 
        logger.debug("create_order_request_and_fsm: client=%s", client_user_id)
        try:
            session.execute(
                text("""
                    INSERT INTO order_requests
                        (client_user_id, recipient_user_id, parcel_type, cell_size, sender_delivery, recipient_delivery)
                    VALUES
                        (:client_user_id, :recipient_user_id, :parcel_type, :cell_size, :sender_delivery, :recipient_delivery)
                """),
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

            session.execute(
                text("""
                    INSERT INTO server_fsm_instances
                        (entity_type, entity_id, process_name, fsm_state, attempts_count)
                    VALUES
                        (:entity_type, :entity_id, :process_name, :fsm_state, :attempts_count)
                """),
                {
                    "entity_type": "order_request",
                    "entity_id": request_id,
                    "process_name": "order_creation",
                    "fsm_state": "PENDING",
                    "attempts_count": 0,
                },
            )
            instance_id = session.execute(
                text("""
                    SELECT id FROM server_fsm_instances
                    WHERE entity_type = 'order_request' AND entity_id = :request_id
                    AND process_name = 'order_creation'
                """),
                {"request_id": request_id}
            ).scalar_one()

            logger.info("Создана заявка %s и FSM-инстанс %s", request_id, instance_id)
            return request_id, instance_id

        except Exception as e:
            logger.error("create_order_request_and_fsm failed: %s", e)
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

    # ==================== TRACKING ЗАКАЗА ====================

    def get_order_tracking_path(
        self,
        session: Session,
        order_id: int,
    ) -> Dict[str, Any]:
        """
        Возвращает полный путь статусов заказа с флагами is_current и is_completed.
        Путь строится динамически на основе pickup_type и delivery_type.
        """
        logger.debug("get_order_tracking_path вызван: order_id=%s", order_id)
        
        try:
            # 1. Получаем текущий статус и типы доставки заказа
            order = self.get_order(session, order_id)
            if not order:
                raise DbLayerError(f"Заказ {order_id} не найден")
            
            current_status = order.get("status")
            pickup_type = order.get("pickup_type", "courier")
            delivery_type = order.get("delivery_type", "courier")
            
            # 2. Определяем полный путь статусов в зависимости от сценария
            status_path = self._build_status_path(pickup_type, delivery_type)
            
            # 3. Строим путь с флагами
            path = []
            current_index = -1
            
            # Находим индекс текущего статуса
            for i, status in enumerate(status_path):
                if status == current_status:
                    current_index = i
                    break
            
            # Если статус не найден в пути (например, order_cancelled), добавляем его
            if current_index == -1:
                special_statuses = [
                    "order_cancelled",
                    "order_manual_intervention_required",
                    "order_parcel_missing",
                    "order_delivery_failed",
                    "order_courier_failed",
                    "order_reservation_expired",
                ]
                if current_status in special_statuses:
                    path.append({
                        "status": current_status,
                        "is_current": True,
                        "is_completed": True,
                    })
                    return {
                        "order_id": order_id,
                        "current_status": current_status,
                        "pickup_type": pickup_type,
                        "delivery_type": delivery_type,
                        "path": path,
                    }
                else:
                    logger.warning("get_order_tracking_path: неизвестный статус %s", current_status)
                    current_index = len(status_path) - 1
            
            # 4. Заполняем путь с флагами
            for i, status in enumerate(status_path):
                path.append({
                    "status": status,
                    "is_current": (i == current_index),
                    "is_completed": (i <= current_index),
                })
            
            logger.debug(
                "get_order_tracking_path: order_id=%s, current=%s, path_length=%d",
                order_id, current_status, len(path)
            )
            
            return {
                "order_id": order_id,
                "current_status": current_status,
                "pickup_type": pickup_type,
                "delivery_type": delivery_type,
                "path": path,
            }
            
        except Exception as e:
            logger.error("get_order_tracking_path завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to get tracking path for order {order_id}: {e}") from e

    def _build_status_path(self, pickup_type: str, delivery_type: str) -> List[str]:
        """
        Строит путь статусов в зависимости от сценария доставки.
        """
        
        # Сценарий 1: courier/courier (полный путь)
        if pickup_type == "courier" and delivery_type == "courier":
            return [
                "order_created",
                "order_courier1_assigned",
                "order_courier_has_parcel",
                "order_parcel_confirmed",
                "order_parcel_submitted",
                "order_picked_up_from_post1",
                "order_in_transit_to_post2",
                "order_arrived_at_post2",
                "order_parcel_confirmed_post2",
                "order_courier2_assigned",
                "order_courier2_has_parcel",
                "order_courier2_parcel_delivered",
                "order_completed",
            ]
        
        # Сценарий 2: self/courier (клиент сам несёт в постамат)
        elif pickup_type == "self" and delivery_type == "courier":
            return [
                "order_created",
                "order_client_post1",
                "order_parcel_confirmed",
                "order_parcel_submitted",
                "order_picked_up_from_post1",
                "order_in_transit_to_post2",
                "order_arrived_at_post2",
                "order_parcel_confirmed_post2",
                "order_courier2_assigned",
                "order_courier2_has_parcel",
                "order_courier2_parcel_delivered",
                "order_completed",
            ]
        
        # Сценарий 3: courier/self (курьер1 забирает, получатель сам забирает)
        elif pickup_type == "courier" and delivery_type == "self":
            return [
                "order_created",
                "order_courier1_assigned",
                "order_courier_has_parcel",
                "order_parcel_confirmed",
                "order_parcel_submitted",
                "order_picked_up_from_post1",
                "order_in_transit_to_post2",
                "order_arrived_at_post2",
                "order_parcel_confirmed_post2",
                "order_delivered_to_client",
                "order_completed",
            ]
        
        # Сценарий 4: self/self (клиент и получатель сами)
        elif pickup_type == "self" and delivery_type == "self":
            return [
                "order_created",
                "order_client_post1",
                "order_parcel_confirmed",
                "order_parcel_submitted",
                "order_picked_up_from_post1",
                "order_in_transit_to_post2",
                "order_arrived_at_post2",
                "order_parcel_confirmed_post2",
                "order_delivered_to_client",
                "order_completed",
            ]
        
        # Fallback: полный путь
        else:
            logger.warning("_build_status_path: неизвестный сценарий pickup=%s, delivery=%s", 
                        pickup_type, delivery_type)
            return [
                "order_created",
                "order_courier1_assigned",
                "order_courier_has_parcel",
                "order_parcel_confirmed",
                "order_parcel_submitted",
                "order_picked_up_from_post1",
                "order_in_transit_to_post2",
                "order_arrived_at_post2",
                "order_parcel_confirmed_post2",
                "order_courier2_assigned",
                "order_courier2_has_parcel",
                "order_courier2_parcel_delivered",
                "order_completed",
            ]

    # ==================== Access Code ====================
    def get_stage_order(self, session: Session, order_id: int, leg: str) -> Optional[Dict[str, Any]]:
        """
        Получить запись stage_orders для заказа и плеча.
        Возвращает dict или None.
        """
        logger.debug("get_stage_order вызван: order_id=%s, leg=%s", order_id, leg)
        
        try:
            row = session.execute(
                text("""
                    SELECT trip_id, direction_id, order_id, leg, courier_user_id,
                        reservation_id, reserved_by_driver_id
                    FROM stage_orders
                    WHERE order_id = :order_id AND leg = :leg
                """), {
                    "order_id": order_id,
                    "leg": leg,
                }
            ).fetchone()
            
            if not row:
                logger.debug("get_stage_order: не найдено для order_id=%s, leg=%s", order_id, leg)
                return None
            result = {
                "trip_id": row[0],
                "direction_id": row[1],
                "order_id": row[2],
                "leg": row[3],
                "courier_user_id": row[4],
                "reservation_id": row[5],
                "reserved_by_driver_id": row[6],
            }
            
            logger.debug("get_stage_order: найдено для order_id=%s, leg=%s", order_id, leg)
            return result
            
        except Exception as e:
            logger.error("get_stage_order завершился с ошибкой: %s", e)
            return None

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

    def validate_access_code(
        self,
        session: Session,
        order_id: int,
        leg: str,
        user_id: int,
        pin: str,
        cell_id: int
    ) -> Tuple[bool, str]:
        """
        Проверка PIN-кода перед открытием ячейки.
        
        Проверки:
        1. Токен существует для этого заказа и leg
        2. Токен выдан этому пользователю (actor_user_id = user_id)
        3. PIN совпадает (по хэшу SHA256(pin + order_id + cell_id))
        4. Токен активен (status='ACTIVE')
        5. Токен не истёк (expires_at > NOW())
        
        Returns:
            Tuple[bool, str]: (успех, сообщение_об_ошибке)
        """
        logger.debug(
            "validate_access_code вызван: order_id=%s, leg=%s, user_id=%s, cell_id=%s",
            order_id, leg, user_id, cell_id
        )
        
        try:
            # 1. Находим токен для этого заказа
            row = session.execute(
                text("""
                    SELECT id, pin_hash, status, expires_at, actor_user_id, cell_id
                    FROM cell_access_tokens
                    WHERE order_id = :order_id
                    AND leg = :leg
                    AND actor_user_id = :user_id
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
                logger.warning(
                    "validate_access_code: токен не найден (order_id=%s, leg=%s, user_id=%s)",
                    order_id, leg, user_id
                )
                return False, "ACCESS_CODE_NOT_FOUND"
            
            token_id, stored_pin_hash, token_status, expires_at, actor_user_id, token_cell_id = row
            
            # 2. Проверка статуса токена
            if token_status != 'ACTIVE':
                logger.warning(
                    "validate_access_code: токен неактивен (status=%s, token_id=%s)",
                    token_status, token_id
                )
                return False, f"ACCESS_CODE_NOT_ACTIVE ({token_status})"
            
            # 3. Проверка срока действия
            if expires_at < datetime.utcnow():
                logger.warning(
                    "validate_access_code: токен истёк (expires_at=%s, token_id=%s)",
                    expires_at, token_id
                )
                return False, "ACCESS_CODE_EXPIRED"
            
            # 4. Проверка ячейки (cell_id должен совпадать)
            if token_cell_id != cell_id:
                logger.warning(
                    "validate_access_code: ячейка не совпадает (token_cell=%s, request_cell=%s)",
                    token_cell_id, cell_id
                )
                return False, "ACCESS_CODE_WRONG_CELL"
            
            # 5. Проверка PIN через хэш ← ТОЛЬКО pin_hash
            expected_hash = hashlib.sha256(f"{pin}{order_id}{cell_id}".encode()).hexdigest()
            
            if expected_hash != stored_pin_hash:
                # Увеличиваем счётчик неудачных попыток
                session.execute(
                    text("""
                        UPDATE cell_access_tokens
                        SET failed_attempts = failed_attempts + 1
                        WHERE id = :token_id
                    """),
                    {"token_id": token_id}
                )
                
                logger.warning(
                    "validate_access_code: PIN неверный (token_id=%s, attempts++)",
                    token_id
                )
                return False, "ACCESS_CODE_INVALID"
            
            logger.info(
                "validate_access_code: PIN верный (token_id=%s, order_id=%s)",
                token_id, order_id
            )
            return True, ""
            
        except Exception as e:
            logger.error("validate_access_code завершился с ошибкой: %s", e)
            return False, f"VALIDATION_ERROR: {e}"


    # ==================== Сервисные методы ====================
    def get_leg_for_order(self, order: Dict[str, Any]) -> Optional[str]:
        """
        Возвращает плечо ('pickup' или 'delivery') на основе статуса заказа.
        Опирается на полный список статусов из всех 4 сценариев.
        Возвращает None, если статус не удалось однозначно определить.
        """
        status = order.get("status", "")
        
        # Статусы, в которых работа идёт с ячейкой отправления (Постамат1)
        pickup_statuses = {
            "order_created",
            "order_client_post1",
            "order_courier1_assigned",
            "order_courier_has_parcel",
            "order_parcel_confirmed",
            "order_parcel_submitted",
            "order_picked_up_from_post1",
        }
        
        # Статусы, в которых работа идёт с ячейкой назначения (Постамат2)
        delivery_statuses = {
            "order_in_transit_to_post2",
            "order_arrived_at_post2",
            "order_parcel_confirmed_post2",
            "order_courier2_assigned",
            "order_courier2_has_parcel",
            "order_courier2_parcel_delivered",
            "order_delivered_to_client",
            "order_completed",
        }
        
        if status in pickup_statuses:
            return "pickup"
        if status in delivery_statuses:
            return "delivery"
        
        # Неизвестный статус – fallback на основе типа доставки
        pickup_type = order.get("pickup_type", "courier")
        delivery_type = order.get("delivery_type", "courier")
        
        # Если pickup_type=self и ещё не дошли до транзита – вероятно pickup
        if pickup_type == "self" and status.startswith("order_client"):
            return "pickup"
        # Для остальных непонятных статусов возвращаем None
        logger.warning("get_leg_for_order: неизвестный статус '%s', не удалось определить плечо", status)
        return None
    
    def get_all_cities(self, session: Session) -> List[str]:
        """
        Получить список уникальных городов из таблицы users (не пустые).
        """
        logger.debug("get_all_cities вызван")
        try:
            rows = session.execute(
                text("SELECT DISTINCT city FROM users WHERE city IS NOT NULL AND city != '' ORDER BY city")
            ).fetchall()
            cities = [row[0] for row in rows]
            logger.debug("get_all_cities: найдено %d городов", len(cities))
            return cities
        except Exception as e:
            logger.error("get_all_cities завершился с ошибкой: %s", e)
            raise DbLayerError(f"Failed to fetch cities: {e}") from e

    # ==================== БИРЖИ ====================

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
        
        for order in pickup:
            order["type"] = "pickup"
        for order in delivery:
            order["type"] = "delivery"

        return {
            "pickup": pickup,
            "delivery": delivery,
            "all": pickup + delivery  
        }

    def get_available_directions_for_driver_exchange(
        self,
        session: Session,
        city: str
    ) -> List[Dict[str, Any]]:
        """
        Возвращает направления, доступные для взятия водителем из указанного города.
        """
        logger.debug("get_available_directions_for_driver_exchange вызван для города: %s", city)

        query = text("""
            SELECT
                d.id,
                d.from_city,
                d.to_city,
                d.pickup_locker_id,
                d.delivery_locker_id,
                d.orders_available,
                d.orders_reserved
            FROM directions d
            WHERE
                d.from_city = :city
                AND d.orders_available > 0
            ORDER BY d.id ASC
        """)

        try:
            result = session.execute(query, {"city": city}).fetchall()

            directions = [
                {
                    "id": row[0],
                    "from_city": row[1],
                    "to_city": row[2],
                    "pickup_locker_id": row[3],
                    "delivery_locker_id": row[4],
                    "orders_available": row[5],
                    "orders_reserved": row[6],
                }
                for row in result
            ]

            logger.debug("Найдено %d направлений для города %s", len(directions), city)
            return directions

        except Exception as e:
            logger.error("get_available_directions_for_driver_exchange завершился с ошибкой: %s", e)
            raise DbLayerError(f"Ошибка получения направлений для биржи: {e}") from e

    # ==================== Направления ====================
    def reserve_orders_for_direction(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int, 
        capacity: int,
    ) -> Tuple[bool, int, str]:
        """
        Резервирует capacity заказов за водителем в направлении.
        """
        logger.debug(
            "reserve_orders_for_direction вызван: direction_id=%s, driver_user_id=%s, capacity=%s",
            direction_id, driver_user_id, capacity
        )
        
        try:
            # 1. Проверка лимита слотов (максимум 3 активных резерва на направление)
            active_slots = session.execute(text("""
                SELECT COUNT(*) 
                FROM driver_reservations 
                WHERE driver_user_id = :driver_user_id 
                AND direction_id = :direction_id 
                AND status IN ('reservation_active', 'reservation_loading')
            """), {
                "driver_user_id": driver_user_id,
                "direction_id": direction_id,
            }).scalar()
            
            if active_slots >= 3:
                return False, 0, "LIMIT_EXCEEDED: Максимум 3 слота на направление"
            
            # 2. Проверка доступных заказов
            available = session.execute(text("""
                SELECT COUNT(DISTINCT so.order_id)
                FROM stage_orders so
                WHERE so.direction_id = :direction_id
                AND so.leg = 'pickup'
                AND so.reserved_by_driver_id IS NULL
                AND so.trip_id IS NULL
            """), {"direction_id": direction_id}).scalar()
            
            if available == 0:
                return False, 0, "NO_AVAILABLE_ORDERS"
            
            # 3. Сначала INSERT → получаем reservation_id
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            
            session.execute(text("""
                INSERT INTO driver_reservations (
                    driver_user_id, direction_id, reserved_count,
                    requested_count, expires_at, status
                ) VALUES (
                    :driver_user_id, :direction_id, 0,
                    :requested_count, :expires_at, 'reservation_active'
                )
            """), {
                "driver_user_id": driver_user_id,
                "direction_id": direction_id,
                "requested_count": capacity,
                "expires_at": expires_at,
            })
            
            reservation_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
            
            # 4. Атомарный UPDATE заказов
            result = session.execute(text("""
                UPDATE stage_orders so
                SET so.reserved_by_driver_id = :driver_user_id,
                    so.reservation_id = :reservation_id
                WHERE so.direction_id = :direction_id
                AND so.leg IN ('pickup', 'delivery')
                AND so.reserved_by_driver_id IS NULL
                AND so.trip_id IS NULL
                ORDER BY so.order_id ASC
                LIMIT :capacity
            """), {
                "driver_user_id": driver_user_id,
                "reservation_id": reservation_id,
                "direction_id": direction_id,
                "capacity": capacity,
            })
            
            reserved_count = result.rowcount
            
            if reserved_count == 0:
                logger.warning(
                    "reserve_orders_for_direction: не удалось зарезервировать заказы direction_id=%s",
                    direction_id
                )
                return False, 0, "RESERVATION_FAILED"
            
            # 5. ЧАСТИЧНЫЙ РЕЗЕРВ (логирование)
            if reserved_count < capacity:
                logger.warning(
                    "reserve_orders_for_direction: частичный резерв запрошено=%s, зарезервировано=%s",
                    capacity, reserved_count
                )
            
            # 6. Обновить driver_reservations.reserved_count
            session.execute(text("""
                UPDATE driver_reservations
                SET reserved_count = :count
                WHERE id = :reservation_id
            """), {
                "count": reserved_count,
                "reservation_id": reservation_id,
            })
            
            # 7. Обновить счётчики в directions (БЕЗ orders_total!)
            self.recalculate_direction_counters(session, direction_id)
            
            logger.info(
                "reserve_orders_for_direction: direction_id=%s, driver_user_id=%s, reserved=%s, reservation_id=%s",
                direction_id, driver_user_id, reserved_count, reservation_id
            )
            
            return True, reserved_count, "Заказы зарезервированы"
            
        except Exception as e:
            logger.exception("reserve_orders_for_direction завершился с ошибкой")
            raise DbLayerError("reserve_orders_for_direction failed: %s" % e) from e

    def get_orders_by_driver_and_direction(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Получить все заказы водителя на направлении (из ВСЕХ его резервов).
        """
        logger.debug(
            "get_orders_by_driver_and_direction вызван: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        
        try:
            rows = session.execute(text("""
                SELECT
                    so.order_id,
                    o.status,
                    o.description,
                    o.parcel_type,
                    o.source_cell_id,
                    o.dest_cell_id,
                    l_src.city as from_city,
                    l_dst.city as to_city
                FROM stage_orders so
                JOIN orders o ON o.id = so.order_id
                JOIN locker_cells lc_src ON lc_src.id = o.source_cell_id
                JOIN lockers l_src ON l_src.id = lc_src.locker_id
                JOIN locker_cells lc_dst ON lc_dst.id = o.dest_cell_id
                JOIN lockers l_dst ON l_dst.id = lc_dst.locker_id
                WHERE so.direction_id = :direction_id
                AND so.reserved_by_driver_id = :driver_user_id
                AND so.leg = 'pickup'
                ORDER BY o.created_at ASC
            """), {
                "direction_id": direction_id,
                "driver_user_id": driver_user_id,
            }).fetchall()
            
            orders = [
                {
                    "order_id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "parcel_type": row[3],
                    "source_cell_id": row[4],
                    "dest_cell_id": row[5],
                    "from_city": row[6],
                    "to_city": row[7],
                }
                for row in rows
            ]
            
            logger.info(
                "get_orders_by_driver_and_direction: direction_id=%s, driver_user_id=%s, orders=%d",
                direction_id, driver_user_id, len(orders)
            )
            
            return orders
            
        except Exception as e:
            logger.error("get_orders_by_driver_and_direction завершился с ошибкой: %s", e)
            raise DbLayerError("get_orders_by_driver_and_direction failed: %s" % e) from e    

    def check_open_cells_for_driver_reservations(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, List[int]]:
        """
        Проверить есть ли открытые ячейки у водителя в активных резервах направления.
        """
        logger.debug(
            "check_open_cells_for_driver_reservations вызван: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        
        try:
            # 1. Находим все активные резервы водителя на направлении
            reservation_ids = self.get_driver_active_reservations(
                session, direction_id, driver_user_id
            )
            
            if not reservation_ids:
                logger.info(
                    "check_open_cells_for_driver_reservations: нет активных резервов у водителя %s на направлении %s",
                    driver_user_id, direction_id
                )
                return False, []
            
            reservation_placeholders = ', '.join([f':res_{i}' for i in range(len(reservation_ids))])
            reservation_params = {f'res_{i}': rid for i, rid in enumerate(reservation_ids)}
            
            # 2. Проверяем ячейки через fsm_action_logs
            query = text(f"""
                SELECT DISTINCT lc.id
                FROM fsm_action_logs fal_open
                JOIN locker_cells lc ON lc.id = fal_open.entity_id
                WHERE fal_open.entity_type = 'locker'
                AND fal_open.action_name = 'locker_open_locker'
                AND fal_open.user_id = :driver_user_id
                AND lc.id NOT IN (
                    SELECT fal_close.entity_id
                    FROM fsm_action_logs fal_close
                    WHERE fal_close.entity_type = 'locker'
                    AND fal_close.action_name IN ('locker_close_pickup', 'locker_close_locker')
                    AND fal_close.user_id = :driver_user_id
                    AND fal_close.created_at > fal_open.created_at
                )
                AND lc.current_order_id IN (
                    SELECT so.order_id
                    FROM stage_orders so
                    WHERE so.reservation_id IN ({reservation_placeholders})
                    AND so.leg = 'pickup'
                )
            """)
            
            # 3. Объединяем параметры
            params = {
                "driver_user_id": driver_user_id,
                **reservation_params,
            }
            
            open_cells = session.execute(query, params).fetchall()
            
            open_cell_ids = [row[0] for row in open_cells]
            has_open = len(open_cell_ids) > 0
            
            if has_open:
                logger.warning(
                    "check_open_cells_for_driver_reservations: обнаружены открытые ячейки: %s",
                    open_cell_ids
                )
            else:
                logger.info(
                    "check_open_cells_for_driver_reservations: direction_id=%s, driver_user_id=%s, open_cells=0",
                    direction_id, driver_user_id
                )
            
            return has_open, open_cell_ids
            
        except Exception as e:
            logger.error("check_open_cells_for_driver_reservations завершился с ошибкой: %s", e)
            raise DbLayerError("check_open_cells_for_driver_reservations failed: %s" % e) from e

    def get_driver_active_reservations(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> List[int]:
        """
        Получить все активные резервы (слоты) водителя на направлении.
        """
        logger.debug(
            "get_driver_active_reservations вызван: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        
        try:
            rows = session.execute(text("""
                SELECT id
                FROM driver_reservations
                WHERE driver_user_id = :driver_user_id
                AND direction_id = :direction_id
                AND status IN ('reservation_active', 'reservation_loading')
                ORDER BY reserved_at ASC
            """), {
                "driver_user_id": driver_user_id,
                "direction_id": direction_id,
            }).fetchall()
            
            reservation_ids = [row[0] for row in rows]
            
            logger.info(
                "get_driver_active_reservations: direction_id=%s, driver_user_id=%s, reservations=%d",
                direction_id, driver_user_id, len(reservation_ids)
            )
            
            return reservation_ids
            
        except Exception as e:
            logger.error("get_driver_active_reservations завершился с ошибкой: %s", e)
            raise DbLayerError("get_driver_active_reservations failed: %s" % e) from e

    def get_picked_orders_by_driver_and_direction(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> List[int]:
        """
        Получить order_id которые водитель фактически забрал (открыл + закрыл ячейки)
        """
        logger.debug(
            "[DatabaseLayer] get_picked_orders_by_driver_and_direction: direction_id=%s, driver_user_id=%s ",
            direction_id, driver_user_id
        )
        try:
            # Статусы заказов с ошибкой
            excluded_statuses = [
                'order_cancelled',
                'order_manual_intervention_required',
                'order_parcel_missing',
                'order_delivery_failed',
                'order_courier_failed',
                'order_reservation_expired',
            ]
            excluded_status_placeholders = ', '.join([f':status_{i}' for i in range(len(excluded_statuses))])
            excluded_status_params = {f'status_{i}': status for i, status in enumerate(excluded_statuses)}

            query = text(f"""
                SELECT DISTINCT lc.current_order_id
                FROM fsm_action_logs fal
                JOIN locker_cells lc ON lc.id = fal.entity_id
                WHERE fal.entity_type = 'locker'
                AND fal.action_name = 'locker_close_pickup'
                AND fal.user_id = :driver_user_id
                AND lc.current_order_id IS NOT NULL
                AND lc.current_order_id IN (
                    SELECT so.order_id
                    FROM stage_orders so
                    JOIN orders o ON o.id = so.order_id 
                    WHERE so.direction_id = :direction_id
                    AND so.leg = 'pickup'
                    AND so.reserved_by_driver_id = :driver_user_id
                    AND so.trip_id IS NULL
                    AND o.status NOT IN ({excluded_status_placeholders})
                )
            """)
            params = {
                "driver_user_id": driver_user_id,
                "direction_id": direction_id,
                **excluded_status_params,
            }

            result = session.execute(query, params).fetchall()
            picked_order_ids = [int(row[0]) for row in result if row[0] is not None]

            logger.info(
                "[DatabaseLayer] get_picked_orders_by_driver_and_direction: direction_id=%s, driver_user_id=%s, picked=%d",
                direction_id, driver_user_id, len(picked_order_ids)
            )
            return picked_order_ids

        except Exception as e:
            logger.error("get_picked_orders_by_driver_and_direction завершился с ошибкой: %s", e)
            raise DbLayerError("get_picked_orders_by_driver_and_direction failed: %s" % e) from e

    def release_unpicked_orders_by_driver_and_direction(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
        picked_order_ids: List[int],
    ) -> int:
        """
        Освободить не забранные заказы из ВСЕХ резервов водителя (вернуть в пул направления).
        """
        logger.debug(
            "release_unpicked_orders_by_driver_and_direction вызван: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        
        try:
            # 1. Находим все зарезервированные заказы водителя на направлении
            reserved = session.execute(text("""
                SELECT DISTINCT so.order_id
                FROM stage_orders so
                WHERE so.direction_id = :direction_id
                AND so.reserved_by_driver_id = :driver_user_id
                AND so.leg = 'pickup'
            """), {
                "direction_id": direction_id,
                "driver_user_id": driver_user_id,
            }).fetchall()
            
            reserved_order_ids = [row[0] for row in reserved]
            
            # 2. Находим разницу (не забранные)
            unpicked = [oid for oid in reserved_order_ids if oid not in picked_order_ids]
            
            if not unpicked:
                logger.info("release_unpicked_orders_by_driver_and_direction: все заказы забраны")
                return 0
            
            # 3. Динамически создаём плейсхолдеры для IN (чтобы избежать SQL injection)
            unpicked_placeholders = ', '.join([f':unpicked_{i}' for i in range(len(unpicked))])
            unpicked_params = {f'unpicked_{i}': oid for i, oid in enumerate(unpicked)}
            
            # 4. Освобождаем не забранные (сброс reservation_id и reserved_by_driver_id)
            query = text(f"""
                UPDATE stage_orders
                SET reserved_by_driver_id = NULL,
                    reservation_id = NULL
                WHERE direction_id = :direction_id
                AND reserved_by_driver_id = :driver_user_id
                AND order_id IN ({unpicked_placeholders})
            """)
            
            params = {
                "direction_id": direction_id,
                "driver_user_id": driver_user_id,
                **unpicked_params, 
            }
            
            session.execute(query, params)
            
            # 5. Обновляем счётчики в directions
            self.recalculate_direction_counters(session, direction_id)
            
            logger.info(
                "release_unpicked_orders_by_driver_and_direction: direction_id=%s, released=%d заказов",
                direction_id, len(unpicked)
            )
            
            return len(unpicked)
            
        except Exception as e:
            logger.error("release_unpicked_orders_by_driver_and_direction завершился с ошибкой: %s", e)
            raise DbLayerError("release_unpicked_orders_by_driver_and_direction failed: %s" % e) from e 
    
    def validate_and_get_orders_for_direction_start(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, List[int], List[int], str]:
        logger.debug(
            "validate_and_get_orders_for_direction_start: direction_id=%s, driver_user_id=%s",
            direction_id, driver_user_id
        )
        try:
            picked_order_ids = self.get_picked_orders_by_driver_and_direction(
                session, direction_id, driver_user_id
            )
            if not picked_order_ids:
                return False, [], [], "NO_PICKED_ORDERS"

            expected_status = "order_picked_up_from_post1"
            blocked = []
            ready = []
            for oid in picked_order_ids:
                status = session.execute(
                    text("SELECT status FROM orders WHERE id = :oid"), {"oid": oid}
                ).scalar()
                if status == expected_status:
                    ready.append(oid)
                else:
                    blocked.append(oid)

            if blocked:
                return False, blocked, [], f"ORDERS_NOT_READY: {blocked}"

            return True, [], ready, ""
        except Exception as e:
            logger.error("validate_and_get_orders_for_direction_start failed: %s", e)
            raise DbLayerError(f"validate_and_get_orders_for_direction_start failed: {e}") from e

    def create_trip_for_direction(
        self,
        session: Session,
        direction_id: int,
        driver_user_id: int,
        order_ids: List[int],
    ) -> int:
        logger.debug(
            "create_trip_for_direction: direction_id=%s, driver_user_id=%s, orders=%d",
            direction_id, driver_user_id, len(order_ids)
        )
        try:
            direction = session.execute(text("""
                SELECT from_city, to_city, pickup_locker_id, delivery_locker_id
                FROM directions WHERE id = :direction_id
            """), {"direction_id": direction_id}).fetchone()
            if not direction:
                raise DbLayerError(f"Направление {direction_id} не найдено")
            from_city, to_city, pickup_locker_id, delivery_locker_id = direction

            session.execute(text("""
                INSERT INTO trips (
                    driver_user_id, from_city, to_city,
                    pickup_locker_id, delivery_locker_id,
                    status, active, created_at
                ) VALUES (
                    :driver_user_id, :from_city, :to_city,
                    :pickup_locker_id, :delivery_locker_id,
                    'trip_assigned', 1, NOW()
                )
            """), {
                "driver_user_id": driver_user_id,
                "from_city": from_city,
                "to_city": to_city,
                "pickup_locker_id": pickup_locker_id,
                "delivery_locker_id": delivery_locker_id,
            })

            trip_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            if trip_id is None:
                raise DbLayerError("Не удалось получить trip_id после INSERT")
            trip_id = int(trip_id)

            if order_ids:
                placeholders = ', '.join([f':order_{i}' for i in range(len(order_ids))])
                params = {f'order_{i}': oid for i, oid in enumerate(order_ids)}
                params["trip_id"] = trip_id
                session.execute(text(f"""
                    UPDATE stage_orders
                    SET trip_id = :trip_id
                    WHERE order_id IN ({placeholders})
                    AND leg IN ('pickup', 'delivery')
                """), params)

            self.recalculate_direction_counters(session, direction_id)
            return trip_id
        except DbLayerError:
            raise
        except Exception as e:
            logger.error("create_trip_for_direction failed: %s", e)
            raise DbLayerError(f"create_trip_for_direction failed: {e}") from e

    # ================ отмена резерва ===============
    def get_orders_by_reservation(
        self,
        session: Session,
        reservation_id: int,
        driver_user_id: int,
    ) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Получить заказы для начала погрузки.
        """
        logger.debug(
            "get_orders_by_reservation вызван: reservation_id=%s, driver_user_id=%s",
            reservation_id, driver_user_id
        )
        
        try:
            # 1. Проверка резерва (существует + статус + водитель)
            reservation = session.execute(text("""
                SELECT dr.driver_user_id, dr.direction_id, dr.status
                FROM driver_reservations dr
                WHERE dr.id = :reservation_id
            """), {
                "reservation_id": reservation_id,
            }).fetchone()
            
            if not reservation:
                return False, [], f"Резерв {reservation_id} не найден"
            
            res_driver_id, direction_id, reservation_status = reservation
            
            # 2. Проверка что резерв принадлежит водителю
            if res_driver_id != driver_user_id:
                return False, [], f"Резерв {reservation_id} не принадлежит водителю {driver_user_id}"
            
            # 3. Проверка статуса
            if reservation_status not in ('reservation_active', 'reservation_loading'):
                return False, [], (
                    f"Статус резерва не соответсвует '{reservation_status}' "                    
                )
            
            # 4. Получаем заказы резерва
            rows = session.execute(text("""
                SELECT
                    so.order_id,
                    o.status,
                    o.description,
                    o.parcel_type,
                    o.source_cell_id,
                    o.dest_cell_id,
                    o.client_user_id,
                    o.recipient_user_id
                FROM stage_orders so
                JOIN orders o ON o.id = so.order_id
                WHERE so.reservation_id = :reservation_id
                AND so.leg = 'pickup'
                AND so.reserved_by_driver_id = :driver_user_id
            """), {
                "reservation_id": reservation_id,
                "driver_user_id": driver_user_id,
            }).fetchall()
            
            if not rows:
                return False, [], "В резерве нет заказов"
            
            orders = [
                {
                    "order_id": row[0],
                    "status": row[1],
                    "description": row[2],
                    "parcel_type": row[3],
                    "source_cell_id": row[4],
                    "dest_cell_id": row[5],
                    "client_user_id": row[6],
                    "recipient_user_id": row[7],
                }
                for row in rows
            ]
            
            logger.info(
                "get_orders_by_reservation: reservation_id=%s, orders=%d",
                reservation_id, len(orders)
            )
            
            return True, orders, ""
            
        except Exception as e:
            logger.error("get_orders_by_reservation завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_orders_by_reservation failed: {e}") from e

    def validate_reservation_for_cancellation(
        self,
        session: Session,
        reservation_id: int,
    ) -> Tuple[bool, List[int], str]:
        logger.debug("validate_reservation_for_cancellation вызван: reservation_id=%s", reservation_id)
        
        try:
            # 1. Получаем резерв
            reservation = session.execute(text("""
                SELECT driver_user_id, direction_id, status
                FROM driver_reservations
                WHERE id = :reservation_id
            """), {
                "reservation_id": reservation_id,
            }).fetchone()
            
            if not reservation:
                return False, [], f"Резерв {reservation_id} не найден"
            
            driver_user_id, direction_id, reservation_status = reservation
            
            # 2. ПРОВЕРКА СТАТУСА
            if reservation_status not in ('reservation_active', 'reservation_loading'):
                return False, [], (
                    f"Нельзя отменить резерв: статус '{reservation_status}'  "
                    f"(требуется 'reservation_active' или 'reservation_loading')"
                )
            
            # 3. Получаем заказы резерва
            success, orders, error = self.get_orders_by_reservation(
                session, 
                reservation_id,
                driver_user_id,
            )
            
            if not success:
                return False, [], error
            
            if not orders:
                return False, [], "В резерве нет заказов"
            
            # 4. Проверяем статусы заказов
            allowed_status = "order_parcel_confirmed"
            blocked_ids: List[int] = []
            
            for o in orders:
                if o["status"] != allowed_status:
                    blocked_ids.append(o["order_id"])
            
            if blocked_ids:
                return False, blocked_ids, (
                    f"Нельзя отменить резерв: заказы {blocked_ids} не в статусе '{allowed_status}'"
                )
            
            logger.info("validate_reservation_for_cancellation: reservation_id=%s — OK", reservation_id)
            return True, [], ""
            
        except Exception as e:
            logger.error("validate_reservation_for_cancellation завершился с ошибкой: %s", e)
            raise DbLayerError("validate_reservation_for_cancellation failed: %s" % e) from e

    def release_orders_from_reservation(
        self,
        session: Session,
        reservation_id: int,
    ) -> int:
        """
        Освободить заказы из резерва (вернуть в пул направления).
        """
        logger.debug("release_orders_from_reservation вызван: reservation_id=%s", reservation_id)
        
        try:
            # 1. Получаем направление из резерва
            reservation = session.execute(text("""
                SELECT direction_id
                FROM driver_reservations
                WHERE id = :reservation_id
            """), {
                "reservation_id": reservation_id,
            }).fetchone()
            
            if not reservation:
                raise DbLayerError(f"Резерв {reservation_id} не найден")
            
            direction_id = reservation[0]
            
            # 2. Считаем количество заказов
            result = session.execute(text("""
                SELECT COUNT(*)
                FROM stage_orders
                WHERE reservation_id = :reservation_id
                AND leg = 'pickup'
            """), {
                "reservation_id": reservation_id,
            }).scalar()
            
            released_count = int(result) if result else 0
            
            if released_count == 0:
                logger.info("release_orders_from_reservation: нет заказов для освобождения")
                return 0
            
            # 3. Освобождаем заказы (сброс reservation_id и reserved_by_driver_id)
            session.execute(text("""
                UPDATE stage_orders
                SET reserved_by_driver_id = NULL,
                    reservation_id = NULL
                WHERE reservation_id = :reservation_id
                AND leg = 'pickup'
            """), {
                "reservation_id": reservation_id,
            })
            
            # 4. Обновляем счётчики в directions
            self.recalculate_direction_counters(session, direction_id)
            
            logger.info("release_orders_from_reservation: reservation_id=%s, released=%d", reservation_id, released_count)
            return released_count
            
        except Exception as e:
            logger.error("release_orders_from_reservation завершился с ошибкой: %s", e)
            raise DbLayerError("release_orders_from_reservation failed: %s" % e) from e

    def recalculate_direction_counters(self, session: Session, direction_id: int) -> None:
        """
        Пересчитать orders_available и orders_reserved из stage_orders.
        Вызывать после любых изменений в stage_orders.
        """
        logger.debug(f"recalculate_direction_counters: direction_id={direction_id}")
        
        # orders_available: заказы без reservation_id и trip_id
        available = session.execute(text("""
            SELECT COUNT(DISTINCT order_id)
            FROM stage_orders
            WHERE direction_id = :direction_id
            AND leg = 'pickup'
            AND reservation_id IS NULL
            AND trip_id IS NULL
        """), {"direction_id": direction_id}).scalar()
        
        # orders_reserved: заказы с reservation_id (но без trip_id)
        reserved = session.execute(text("""
            SELECT COUNT(DISTINCT order_id)
            FROM stage_orders
            WHERE direction_id = :direction_id
            AND leg = 'pickup'
            AND reservation_id IS NOT NULL
            AND trip_id IS NULL
        """), {"direction_id": direction_id}).scalar()
        
        # Обновить счётчики
        old_values = session.execute(text("""
            SELECT orders_available, orders_reserved
            FROM directions
            WHERE id = :direction_id
        """), {"direction_id": direction_id}).fetchone()
        
        session.execute(text("""
            UPDATE directions
            SET orders_available = :available,
                orders_reserved = :reserved
            WHERE id = :direction_id
        """), {
            "available": available or 0,
            "reserved": reserved or 0,
            "direction_id": direction_id,
        })
        
        logger.info(
            f"recalculate_direction_counters: direction_id={direction_id}, "
            f"was_available={old_values[0] if old_values else 'N/A'}, "
            f"was_reserved={old_values[1] if old_values else 'N/A'}, "
            f"new_available={available or 0}, new_reserved={reserved or 0}"
        )

    # ================ Оператор =====================
    # ================ Вывод ленты рейсов ===========
    def get_all_trips_for_operator(
        self,
        session: Session,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить все рейсы для оператора.
        Опционально: фильтр по статусу (например, 'trip_failed').
        """
        logger.debug(
            "[DB] get_all_trips_for_operator: status_filter=%s",
            status_filter
        )
        
        try:
            query = text("""
                SELECT 
                    t.id,
                    t.driver_user_id,
                    t.from_city,
                    t.to_city,
                    t.pickup_locker_id,
                    t.delivery_locker_id,
                    t.status,
                    t.active,
                    t.created_at,
                    l_pickup.location_address as pickup_address,
                    l_delivery.location_address as delivery_address,
                    ri.id as issue_id,
                    ri.issue_type,
                    ri.description as issue_description,
                    ri.created_at as issue_created_at
                FROM trips t
                LEFT JOIN lockers l_pickup ON l_pickup.id = t.pickup_locker_id
                LEFT JOIN lockers l_delivery ON l_delivery.id = t.delivery_locker_id
                LEFT JOIN report_issues ri ON ri.trip_id = t.id
                    AND ri.issue_type IN ('trip_breakdown', 'trip_manual_intervention', 'trip_delayed', 'trip_route_issue')
                WHERE 1=1
            """)
            
            params = {}
            
            if status_filter:
                query = text("""
                    SELECT 
                        t.id,
                        t.driver_user_id,
                        t.from_city,
                        t.to_city,
                        t.pickup_locker_id,
                        t.delivery_locker_id,
                        t.status,
                        t.active,
                        t.created_at,
                        l_pickup.location_address as pickup_address,
                        l_delivery.location_address as delivery_address,
                        ri.id as issue_id,
                        ri.issue_type,
                        ri.description as issue_description,
                        ri.created_at as issue_created_at
                    FROM trips t
                    LEFT JOIN lockers l_pickup ON l_pickup.id = t.pickup_locker_id
                    LEFT JOIN lockers l_delivery ON l_delivery.id = t.delivery_locker_id
                    LEFT JOIN report_issues ri ON ri.trip_id = t.id
                        AND ri.issue_type IN ('trip_breakdown', 'trip_manual_intervention', 'trip_delayed', 'trip_route_issue')
                    WHERE t.status = :status
                    ORDER BY t.created_at DESC
                """)
                params = {"status": status_filter}
            
            rows = session.execute(query, params).fetchall()
            
            trips = []
            for row in rows:
                trips.append({
                    "trip_id": row[0],
                    "driver_user_id": row[1],
                    "from_city": row[2],
                    "to_city": row[3],
                    "pickup_locker_id": row[4],
                    "delivery_locker_id": row[5],
                    "status": row[6],
                    "active": bool(row[7]),
                    "created_at": row[8].isoformat() if row[8] else None,
                    "pickup_address": row[9],
                    "delivery_address": row[10],
                    "issue_id": row[11],
                    "issue_type": row[12],
                    "issue_description": row[13],
                    "issue_created_at": row[14].isoformat() if row[14] else None,
                })
            
            logger.info(
                "[DB] get_all_trips_for_operator: found %d trips",
                len(trips)
            )
            
            return trips
            
        except Exception as e:
            logger.error("[DB] get_all_trips_for_operator failed: %s", e)
            raise DbLayerError(f"get_all_trips_for_operator failed: {e}") from e

    def get_all_lockers_with_orders_for_operator(
        self,
        session: Session,
    ) -> List[Dict[str, Any]]:
        """
        Получить все постаматы с заказами для оператора.
        Показывает ВСЕ постаматы и ВСЕ заказы в ячейках этих постаматов.
        Без рейсов, направлений, резервов.
        """
        logger.debug("[DB] get_all_lockers_with_orders_for_operator")
        
        try:
            # 1. Получаем ВСЕ постаматы
            lockers_rows = session.execute(text("""
                SELECT 
                    l.id,
                    l.locker_code,
                    l.location_address,
                    l.city,
                    l.status
                FROM lockers l
                ORDER BY l.id ASC
            """)).fetchall()
            
            lockers = []
            for locker_row in lockers_rows:
                locker_id = locker_row[0]
                
                # 2. Для каждого постамата получаем ВСЕ заказы в его ячейках
                #    (и source_cell_id, и dest_cell_id)
                orders_rows = session.execute(text("""
                    SELECT 
                        o.id as order_id,
                        o.status,
                        o.pickup_type,
                        o.delivery_type,
                        o.source_cell_id,
                        o.dest_cell_id,
                        o.client_user_id,
                        o.recipient_user_id,
                        o.created_at,
                        o.updated_at,
                        so_pickup.courier_user_id as pickup_courier_id,
                        so_pickup.trip_id as pickup_trip_id,
                        so_delivery.courier_user_id as delivery_courier_id,
                        so_delivery.trip_id as delivery_trip_id,
                        lc_src.cell_code as source_cell_code,
                        lc_dst.cell_code as dest_cell_code
                    FROM orders o
                    JOIN locker_cells lc_src ON lc_src.id = o.source_cell_id
                    JOIN locker_cells lc_dst ON lc_dst.id = o.dest_cell_id
                    LEFT JOIN stage_orders so_pickup 
                        ON so_pickup.order_id = o.id AND so_pickup.leg = 'pickup'
                    LEFT JOIN stage_orders so_delivery 
                        ON so_delivery.order_id = o.id AND so_delivery.leg = 'delivery'
                    WHERE lc_src.locker_id = :locker_id
                    OR lc_dst.locker_id = :locker_id
                    ORDER BY o.created_at DESC
                """), {"locker_id": locker_id}).fetchall()
                
                orders = [{
                    "order_id": row[0],
                    "status": row[1],
                    "pickup_type": row[2],
                    "delivery_type": row[3],
                    "source_cell_id": row[4],
                    "dest_cell_id": row[5],
                    "client_user_id": row[6],
                    "recipient_user_id": row[7],
                    "created_at": row[8].isoformat() if row[8] else None,
                    "updated_at": row[9].isoformat() if row[9] else None,
                    "pickup_courier_id": row[10],
                    "pickup_trip_id": row[11],
                    "delivery_courier_id": row[12],
                    "delivery_trip_id": row[13],
                    "source_cell_code": row[14],
                    "dest_cell_code": row[15],
                } for row in orders_rows]
                
                # 3. Считаем статистику
                orders_waiting_courier = len([
                    o for o in orders 
                    if o["pickup_courier_id"] is None 
                    and o["pickup_type"] == "courier"
                    and o["status"] not in ("order_completed", "order_cancelled")
                ])

                orders_assigned = len([
                    o for o in orders 
                    if o["pickup_courier_id"] is not None
                    and o["status"] not in ("order_completed", "order_cancelled")
                ])

                # заказы на доставку для курьера2
                orders_waiting_delivery = len([
                    o for o in orders 
                    if o["delivery_courier_id"] is None 
                    and o["delivery_type"] == "courier"
                    and o["status"] == "order_parcel_confirmed_post2"
                ])
                
                lockers.append({
                    "locker_id": locker_id,
                    "locker_code": locker_row[1],
                    "location_address": locker_row[2],
                    "city": locker_row[3],
                    "status": locker_row[4],
                    "orders": orders,
                    "orders_waiting_courier": orders_waiting_courier,
                    "orders_assigned": orders_assigned,
                })
            
            logger.info(
                "[DB] get_all_lockers_with_orders_for_operator: found %d lockers",
                len(lockers)
            )
            return lockers
            
        except Exception as e:
            logger.error("[DB] get_all_lockers_with_orders_for_operator failed: %s", e)
            raise DbLayerError(f"get_all_lockers_with_orders_for_operator failed: {e}") from e

    # ================ Снять курьера с заказа и водителя с рейса =====
    def remove_courier_from_order(
        self,
        session: Session,
        order_id: int,
        leg: str, 
        operator_id: int,
    ) -> bool:
        """
        Снять курьера с заказа (без FSM перехода).
        Просто обнуляет stage_orders.courier_user_id + логирует в report_issues.
        """
        logger.debug(
            "[DB] remove_courier_from_order: order_id=%s, leg=%s, operator_id=%s",
            order_id, leg, operator_id
        )
        
        try:
            # 1. Получаем текущего курьера
            old_courier = session.execute(
                text("""
                    SELECT courier_user_id
                    FROM stage_orders
                    WHERE order_id = :order_id AND leg = :leg
                """),
                {"order_id": order_id, "leg": leg}
            ).scalar_one_or_none()
            
            if not old_courier:
                logger.warning(
                    "remove_courier_from_order: курьер не назначен order_id=%s, leg=%s",
                    order_id, leg
                )
                return False
            
            # 2. Снимаем курьера (UPDATE)
            result = session.execute(
                text("""
                    UPDATE stage_orders
                    SET courier_user_id = NULL
                    WHERE order_id = :order_id AND leg = :leg
                """),
                {"order_id": order_id, "leg": leg}
            )
            
            if result.rowcount == 0:
                logger.warning(
                    "remove_courier_from_order: не удалось снять курьера order_id=%s, leg=%s",
                    order_id, leg
                )
                return False
            
            # 3. Логируем в report_issues
            self.create_order_issue(
                session,
                order_id=order_id,
                trip_id=None,
                user_id=operator_id,
                issue_type="manual_override",
                description=f"Курьер {old_courier} снят с заказа {leg} оператором"
            )
            
            logger.info(
                "Курьер %s снят с заказа %s (leg=%s) оператором %s",
                old_courier, order_id, leg, operator_id
            )
            return True
            
        except Exception as e:
            logger.error("remove_courier_from_order завершился с ошибкой: %s", e)
            raise DbLayerError(f"remove_courier_from_order failed: {e}") from e

    def update_order_status_by_leg(self, session: Session, order_id: int, leg: str) -> None:
        """
        Устанавливает статус заказа в зависимости от плеча:
        pickup  → order_created
        delivery → order_parcel_confirmed_post2
        """
        if leg == "pickup":
            new_status = "order_created"
        elif leg == "delivery":
            new_status = "order_parcel_confirmed_post2"
        else:
            raise ValueError(f"Неизвестное плечо: {leg}")

        try:
            session.execute(
                text("UPDATE orders SET status = :status WHERE id = :oid"),
                {"status": new_status, "oid": order_id}
            )
            logger.info("[DB] Статус заказа %s обновлён на %s (leg=%s)", order_id, new_status, leg)
        except Exception as e:
            logger.exception("Ошибка при обновлении статуса заказа %s: %s", order_id, e)
            raise DbLayerError(f"Не удалось обновить статус заказа {order_id}: {e}") from e

    def remove_driver_from_trip(
        self,
        session: Session,
        trip_id: int,
        operator_id: int,
    ) -> bool:
        """
        Снять водителя с рейса (без FSM перехода).
        Просто обнуляет trips.driver_user_id + логирует в report_issues.
        """
        logger.debug(
            "[DB] remove_driver_from_trip: trip_id=%s, operator_id=%s",
            trip_id, operator_id
        )
        
        try:
            # 1. Получаем текущего водителя
            old_driver = session.execute(
                text("SELECT driver_user_id FROM trips WHERE id = :trip_id"),
                {"trip_id": trip_id}
            ).scalar_one_or_none()
            
            if not old_driver:
                logger.warning("remove_driver_from_trip: рейс %s не найден", trip_id)
                return False
            
            # 2. Снимаем водителя (UPDATE)
            result = session.execute(
                text("UPDATE trips SET driver_user_id = NULL WHERE id = :trip_id"),
                {"trip_id": trip_id}
            )
            
            if result.rowcount == 0:
                logger.warning("remove_driver_from_trip: не удалось снять водителя с рейса %s", trip_id)
                return False
            
            # 3. Логируем в report_issues
            self.create_order_issue(
                session,
                order_id=None,
                trip_id=trip_id,
                user_id=operator_id,
                issue_type="manual_override",
                description=f"Водитель {old_driver} снят с рейса оператором"
            )
            
            logger.info("Водитель %s снят с рейса %s оператором %s", old_driver, trip_id, operator_id)
            return True
            
        except Exception as e:
            logger.error("remove_driver_from_trip завершился с ошибкой: %s", e)
            raise DbLayerError(f"remove_driver_from_trip failed: {e}") from e

    def clear_driver_from_stage_orders(
        self,
        session: Session,
        order_ids: List[int]
    ) -> None:
        """Сбрасывает reserved_by_driver_id для всех переданных заказов в stage_orders."""
        if not order_ids:
            return
        try:
            # Генерируем плейсхолдеры :order_0, :order_1, ...
            placeholders = ", ".join([f":order_{i}" for i in range(len(order_ids))])
            params = {f"order_{i}": oid for i, oid in enumerate(order_ids)}

            session.execute(
                text(f"""
                    UPDATE stage_orders
                    SET reserved_by_driver_id = NULL
                    WHERE order_id IN ({placeholders})
                    AND leg IN ('pickup', 'delivery')
                """),
                params
            )
            logger.info("[DB] Водитель снят со stage_orders для заказов: %s", order_ids)
        except Exception as e:
            logger.exception("Ошибка при очистке водителя из stage_orders: %s", e)
            raise DbLayerError(f"Не удалось очистить stage_orders: {e}") from e

    # ================ сброс резерва ================

    def get_expired_reservations(
        self,
        session: Session,
        threshold_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Получить резервы у которых истёк таймаут до начала погрузки.
        """
        logger.debug("get_expired_reservations вызван: threshold_minutes=%s", threshold_minutes)
        try:
            rows = session.execute(text("""
                SELECT
                    dr.id,
                    dr.driver_user_id,
                    dr.direction_id,
                    dr.status,
                    dr.reserved_count,
                    dr.expires_at
                FROM driver_reservations dr
                WHERE dr.status = 'reservation_active'
                AND dr.expires_at < NOW()
                ORDER BY dr.expires_at ASC
            """)).fetchall()
            
            reservations = [{
                "reservation_id": row[0],
                "driver_user_id": row[1],
                "direction_id": row[2],
                "status": row[3],
                "reserved_count": row[4],
                "expires_at": row[5],
            } for row in rows]
            
            if reservations:
                logger.info("get_expired_reservations: найдено %d просроченных резервов", len(reservations))
            else:
                logger.debug("get_expired_reservations: просроченных резервов нет")
            return reservations
            
        except Exception as e:
            logger.error("get_expired_reservations завершился с ошибкой: %s", e)
            raise DbLayerError("get_expired_reservations failed: %s" % e) from e

    def expire_reservation_direct(
        self,
        session: Session,
        reservation_id: int,
        user_id: int = 999999,
    ) -> int:
        """
        Истечение резерва: освободить заказы + FSM переход.
        """
        logger.debug("expire_reservation_direct вызван: reservation_id=%s", reservation_id)
        try:
            # 1. Освобождаем заказы (возврат в пул)
            released_count = self.release_orders_from_reservation(session, reservation_id)
            
            # 2. FSM переход: reservation_active → reservation_expired
            self.driver_reservation_expire(session, reservation_id, user_id)
            
            logger.info(
                "expire_reservation_direct: reservation_id=%s, released=%d заказов",
                reservation_id, released_count
            )
            return released_count
            
        except Exception as e:
            logger.error("expire_reservation_direct завершился с ошибкой: %s", e)
            raise DbLayerError("expire_reservation_direct failed: %s" % e) from e

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
            # 1. Получаем старого водителя
            old_driver = session.execute(
                text("SELECT driver_user_id FROM trips WHERE id = :trip_id"),
                {"trip_id": trip_id}
            ).scalar_one_or_none()
            
            # 2. Обновляем водителя
            result = session.execute(
                text("UPDATE trips SET driver_user_id = :driver_id WHERE id = :trip_id"),
                {"driver_id": driver_id, "trip_id": trip_id}
            )
            
            updated = result.rowcount > 0
            if updated:
                # 3. Логируем смену водителя
                if old_driver and old_driver != driver_id:
                    logger.info(
                        "Водитель рейса %s изменён: %s → %s",
                        trip_id, old_driver, driver_id
                    )
                else:
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
        """
        Вернуть рейсы водителя, находящиеся в процессе выполнения (trip_in_progress).
        """
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
                        delivery_locker_id,
                        created_at
                    FROM trips  
                    WHERE driver_user_id = :driver_id 
                    AND status = 'trip_in_progress'
                    ORDER BY created_at DESC
                """),
                {"driver_id": driver_id},
            ).fetchall()

            trips = [dict(row._mapping) for row in rows]
            logger.debug("get_active_trips_for_driver: найдено %d рейсов в trip_in_progress", len(trips))
            return trips
        except Exception as e:
            logger.error(
                "get_active_trips_for_driver завершился с ошибкой для driver_id=%s: %s",
                driver_id, e
            )
            raise DbLayerError(f"Failed to fetch trips for driver {driver_id}: {e}") from e

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
            return result 
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
        Привязывает заказ к КОНКРЕТНОМУ рейсу (trip_id).
        Используется при разделении рейса после погрузки.
        """
        # Обновляет stage_orders.trip_id
        session.execute(text("""
            UPDATE stage_orders
            SET trip_id = :trip_id
            WHERE order_id = :order_id
            AND leg IN ('pickup', 'delivery')
        """), {"trip_id": trip_id, "order_id": order_id})

    def get_or_create_direction(
        self,
        session: Session,
        from_city: str,
        to_city: str,
        pickup_locker_id: int,
        delivery_locker_id: int,
    ) -> int:
        # 1. Ищем существующее
        existing = session.execute(text("""
            SELECT id FROM directions
            WHERE from_city = :from_city
            AND to_city = :to_city
            AND pickup_locker_id = :pickup_locker_id
            AND delivery_locker_id = :delivery_locker_id
        """), {
            "from_city": from_city,
            "to_city": to_city,
            "pickup_locker_id": pickup_locker_id,
            "delivery_locker_id": delivery_locker_id,
        }).fetchone()
        
        if existing:
            return existing[0]
        
        # 2. Создаём новое
        session.execute(text("""
            INSERT INTO directions (
                from_city, to_city, pickup_locker_id, delivery_locker_id,
                orders_reserved, orders_available
            ) VALUES (
                :from_city, :to_city, :pickup_locker_id, :delivery_locker_id,
                0, 0
            )
        """), {
            "from_city": from_city,
            "to_city": to_city,
            "pickup_locker_id": pickup_locker_id,
            "delivery_locker_id": delivery_locker_id,
        })
        
        direction_id = session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
        return direction_id

    def assign_order_to_direction(
        self,
        session: Session,
        order_id: int,
        from_city: str,
        to_city: str,
        pickup_locker_id: int,
        delivery_locker_id: int,
    ) -> Tuple[int, bool, str]:
        """
        Привязывает заказ к направлению.
        """
        # 1. Найти или создать направление
        direction_id = self.get_or_create_direction(
            session, from_city, to_city, pickup_locker_id, delivery_locker_id
        )
        
        # 2. Привязать заказ к направлению (через stage_orders)
        result = session.execute(text("""
            UPDATE stage_orders
            SET direction_id = :direction_id
            WHERE order_id = :order_id
            AND leg IN ('pickup', 'delivery')
        """), {
            "direction_id": direction_id,
            "order_id": order_id,
        })
        
        if result.rowcount != 2:
            logger.warning(
                f"assign_order_to_direction: обновлено {result.rowcount} "
                f"строк вместо 2 для order_id={order_id}"
            )
        
        # 3. Обновить счётчик в directions
        self.recalculate_direction_counters(session, direction_id)
        
        logger.info(f"Заказ {order_id} привязан к направлению {direction_id}")
        
        return direction_id, True, "Заказ привязан к направлению"    

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
            
            # 4. Проверка заказов            
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

    # ==================== FSM ЭМУЛЯТОР ====================

    def get_emulator_entities(
        self,
        session: Session,
        entity_type: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Возвращает список сущностей для эмулятора.
        """
        logger.debug(
            "get_emulator_entities вызван: entity_type=%s, limit=%s",
            entity_type, limit
        )
        
        try:
            if entity_type == "order":
                rows = session.execute(
                    text("""
                        SELECT id, status, description, created_at
                        FROM orders
                        ORDER BY id DESC
                        LIMIT :limit
                    """),
                    {"limit": limit}
                ).fetchall()
            elif entity_type == "trip":
                rows = session.execute(
                    text("""
                        SELECT id, status, 
                            CONCAT(from_city, ' → ', to_city) AS description,
                            created_at
                        FROM trips
                        ORDER BY id DESC
                        LIMIT :limit
                    """),
                    {"limit": limit}
                ).fetchall()
            elif entity_type == "locker":
                rows = session.execute(
                    text("""
                        SELECT id, status, cell_code AS description, created_at
                        FROM locker_cells
                        ORDER BY id DESC
                        LIMIT :limit
                    """),
                    {"limit": limit}
                ).fetchall()
            else:
                logger.error("get_emulator_entities: неизвестный entity_type=%s", entity_type)
                raise DbLayerError(f"Неизвестный entity_type: {entity_type}")
            
            entities = []
            for row in rows:
                entities.append({
                    "id": row[0],
                    "status": row[1],
                    "description": row[2] if row[2] else f"{entity_type} #{row[0]}",
                    "created_at": row[3].isoformat() if row[3] else None,
                })
            
            logger.debug(
                "get_emulator_entities: %s → %d сущностей",
                entity_type, len(entities)
            )
            return entities
            
        except Exception as e:
            logger.error(
                "get_emulator_entities завершился с ошибкой: %s, error=%s",
                entity_type, e
            )
            raise DbLayerError(f"Failed to get entities for emulator: {e}") from e


    def get_entity_current_state(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
    ) -> Optional[str]:
        """
        Возвращает текущее состояние сущности (order/trip/locker).
        """
        logger.debug(
            "get_entity_current_state вызван: entity_type=%s, entity_id=%s",
            entity_type, entity_id
        )
        
        try:
            if entity_type == "order":
                result = session.execute(
                    text("SELECT status FROM orders WHERE id = :id"),
                    {"id": entity_id}
                ).scalar()
            elif entity_type == "trip":
                result = session.execute(
                    text("SELECT status FROM trips WHERE id = :id"),
                    {"id": entity_id}
                ).scalar()
            elif entity_type == "locker":
                result = session.execute(
                    text("SELECT status FROM locker_cells WHERE id = :id"),
                    {"id": entity_id}
                ).scalar()
            else:
                logger.error("get_entity_current_state: неизвестный entity_type=%s", entity_type)
                raise DbLayerError(f"Неизвестный entity_type: {entity_type}")
            
            if result:
                logger.debug(
                    "get_entity_current_state: %s:%s → %s",
                    entity_type, entity_id, result
                )
            else:
                logger.warning(
                    "get_entity_current_state: сущность %s:%s не найдена",
                    entity_type, entity_id
                )
            
            return result
            
        except Exception as e:
            logger.error(
                "get_entity_current_state завершился с ошибкой: %s:%s, error=%s",
                entity_type, entity_id, e
            )
            raise DbLayerError(f"Failed to get state for {entity_type}:{entity_id}: {e}") from e


    def get_available_fsm_actions(
        self,
        session: Session,
        entity_type: str,
        current_state: str,
    ) -> List[str]:
        """
        Возвращает все доступные FSM-действия для текущего состояния.
        """
        logger.debug(
            "get_available_fsm_actions вызван: entity_type=%s, current_state=%s",
            entity_type, current_state
        )
        
        try:
            # 1. Получаем ID текущего состояния
            state_row = session.execute(
                text("SELECT id FROM fsm_states WHERE name = :name"),
                {"name": current_state}
            ).fetchone()
            
            if not state_row:
                logger.warning(
                    "get_available_fsm_actions: состояние '%s' не найдено в fsm_states",
                    current_state
                )
                return []
            
            from_state_id = state_row[0]
            
            # 2. Получаем все действия, доступные из этого состояния
            rows = session.execute(
                text("""
                    SELECT fa.name
                    FROM fsm_transitions ft
                    JOIN fsm_actions fa ON fa.id = ft.action_id
                    WHERE ft.from_state_id = :from_state_id
                    ORDER BY fa.name
                """),
                {"from_state_id": from_state_id}
            ).fetchall()
            
            actions = [row[0] for row in rows]
            
            logger.debug(
                "get_available_fsm_actions: %s в состоянии '%s' → %d действий: %s",
                entity_type, current_state, len(actions), actions
            )
            return actions
            
        except Exception as e:
            logger.error(
                "get_available_fsm_actions завершился с ошибкой: %s:%s, error=%s",
                entity_type, current_state, e
            )
            raise DbLayerError(f"Failed to get available actions: {e}") from e


    def get_fsm_action_history(
        self,
        session: Session,
        entity_type: str,
        entity_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Возвращает историю FSM-переходов для конкретной сущности из fsm_action_logs.
        """
        logger.debug(
            "get_fsm_action_history вызван: entity_type=%s, entity_id=%s, limit=%s",
            entity_type, entity_id, limit
        )
        
        try:
            rows = session.execute(
                text("""
                    SELECT 
                        id,
                        action_name,
                        from_state,
                        to_state,
                        user_id,
                        created_at
                    FROM fsm_action_logs
                    WHERE entity_type = :entity_type
                    AND entity_id = :entity_id
                    ORDER BY id DESC
                    LIMIT :limit
                """),
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "limit": limit
                }
            ).fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "action_name": row[1],
                    "from_state": row[2],
                    "to_state": row[3],
                    "user_id": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                })
            
            logger.debug(
                "get_fsm_action_history: %s:%s → %d записей",
                entity_type, entity_id, len(history)
            )
            return history
            
        except Exception as e:
            logger.error(
                "get_fsm_action_history завершился с ошибкой: %s:%s, error=%s",
                entity_type, entity_id, e
            )
            raise DbLayerError(f"Failed to get FSM history: {e}") from e

    # ==================== СЕРВИСНЫЕ ПРОЦЕДУРЫ ====================

    # ==================== Сброс ячеек постааматов ================
    
    def ensure_locker_cleanup_instance(
        self,
        session: Session,
        threshold_minutes: int = 30,
        user_id: int = 999999
    ) -> bool:
        logger.debug(
            f"ensure_locker_cleanup_instance: threshold={threshold_minutes} мин"
        )
        
        try:
            existing = session.execute(text("""
                SELECT id FROM server_fsm_instances
                WHERE process_name = 'locker_cleanup'
                AND fsm_state NOT IN ('COMPLETED', 'FAILED')
                LIMIT 1
            """)).fetchone()
            
            if existing:
                logger.debug("ensure_locker_cleanup_instance: активный инстанс уже существует (пропущено)")
                return False
            
            self.enqueue_fsm_instance(
                session=session,
                entity_type="locker",
                entity_id=0,
                process_name="locker_cleanup",
                fsm_state="PENDING",
                requested_by_user_id=user_id,
                requested_user_role="system",
                metadata={"threshold_minutes": threshold_minutes}
            )
            
            logger.debug("ensure_locker_cleanup_instance: создан новый инстанс locker_cleanup")
            return True
            
        except Exception as e:
            logger.error(f"ensure_locker_cleanup_instance failed: {e}")
            return False

    def cleanup_closed_empty_lockers(
        self,
        session: Session,
        threshold_minutes: int = 30,
        user_id: int = 999999
    ) -> Tuple[int, Optional[str]]:
        logger.debug(f"cleanup_closed_empty_lockers: threshold={threshold_minutes} мин")
        
        try:
            rows = session.execute(text("""
                SELECT lc.id
                FROM locker_cells lc
                JOIN fsm_action_logs fal ON fal.entity_id = lc.id AND fal.entity_type = 'locker'
                WHERE lc.status = 'locker_closed_empty'
                AND fal.action_name = 'locker_close_pickup'
                AND fal.created_at < NOW() - INTERVAL :threshold MINUTE
                AND lc.id NOT IN (
                    SELECT fal2.entity_id
                    FROM fsm_action_logs fal2
                    WHERE fal2.entity_type = 'locker'
                    AND fal2.action_name IN ('locker_reset', 'locker_open_locker')
                    AND fal2.created_at > fal.created_at
                )
            """), {"threshold": threshold_minutes}).fetchall()
            
            cell_ids = [row[0] for row in rows]
            
            if not cell_ids:
                logger.debug("cleanup_closed_empty_lockers: нет ячеек для очистки")
                return 0, None
            
            cleaned_count = 0
            for cell_id in cell_ids:
                try:
                    self.reset_locker(session, cell_id, user_id)
                    cleaned_count += 1
                except Exception as e:
                    logger.error(f"cleanup_closed_empty_lockers: failed to reset cell {cell_id}: {e}")
            
            logger.debug(f"cleanup_closed_empty_lockers: очищено {cleaned_count} ячеек")
            return cleaned_count, None
            
        except Exception as e:
            logger.error(f"cleanup_closed_empty_lockers failed: {e}")
            return 0, str(e)
    
    # ====================== Очистка базы данных ===================  
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
    
# ==================== CORE USER MAPPING ====================
    
    def create_user_core_mapping(
        self,
        session: Session,
        user_id: int,
        core_u_id: int,
        core_role: int,
    ) -> bool:
        logger.debug("create_user_core_mapping: user_id=%s, core_u_id=%s", user_id, core_u_id)
        try:
            session.execute(
                text("""
                    INSERT INTO core_user_mapping 
                        (local_user_id, core_u_id, core_role, sync_status, registered_at, last_sync_at)
                    VALUES 
                        (:local_id, :core_id, :core_role, 'success', NOW(), NOW())
                    ON DUPLICATE KEY UPDATE 
                        core_u_id = VALUES(core_u_id),
                        core_role = VALUES(core_role),
                        last_sync_at = NOW(),
                        sync_status = 'success'
                """),
                {
                    "local_id": user_id,
                    "core_id": core_u_id,
                    "core_role": core_role,
                }
            )
            logger.info("create_user_core_mapping: user_id=%s ↔ core_u_id=%s", user_id, core_u_id)
            return True
        except Exception as e:
            logger.error("create_user_core_mapping failed: %s", e)
            raise DbLayerError(f"create_user_core_mapping failed: {e}") from e

    def create_user_record(
        self,
        session: Session,
        phone: str,
        name: str,
        role_name: str, 
        city: Optional[str] = None,
    ) -> int:
        """
        Создать пользователя в локальной БД.
        Returns: user_id
        """
        logger.debug("create_user_record вызван: phone=%s, role_name=%s", phone, role_name)
        try:
            result = session.execute(
                text("""
                    INSERT INTO users (phone, name, role_name, city)
                    VALUES (:phone, :name, :role_name, :city)
                """),
                {
                    "phone": phone,
                    "name": name,
                    "role_name": role_name,
                    "city": city,
                }
            )
            user_id = result.lastrowid
            logger.info("create_user_record: создан user_id=%s", user_id)
            return user_id
        except Exception as e:
            logger.error("create_user_record завершился с ошибкой: %s", e)
            raise DbLayerError(f"create_user_record failed: {e}") from e

    def get_local_user_id_by_core_u_id(
        self,
        session: Session,
        core_u_id: int
    ) -> Optional[int]:
        """Получить local_user_id по core_u_id из core_user_mapping."""
        logger.debug("get_local_user_id_by_core_u_id вызван: core_u_id=%s", core_u_id)
        try:
            row = session.execute(
                text("SELECT local_user_id FROM core_user_mapping WHERE core_u_id = :core_u_id"),
                {"core_u_id": core_u_id}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_local_user_id_by_core_u_id: core_u_id=%s → %s", core_u_id, result)
            return result
        except Exception as e:
            logger.error("get_local_user_id_by_core_u_id завершился с ошибкой: %s", e)
            raise DbLayerError(f"get_local_user_id_by_core_u_id failed: {e}") from e

    def get_core_u_id_by_local_user_id(self, session: Session, local_user_id: int) -> Optional[int]:
        """Получить core_u_id по local_user_id из core_user_mapping."""
        row = session.execute(
            text("SELECT core_u_id FROM core_user_mapping WHERE local_user_id = :local_id"),
            {"local_id": local_user_id}
        ).fetchone()
        return row[0] if row else None

    def get_user_core_tokens(self, session: Session, core_u_id: int) -> Tuple[Optional[str], Optional[str]]:
        row = session.execute(
            text("SELECT token, u_hash FROM core_user_mapping WHERE core_u_id = :core_id"),
            {"core_id": core_u_id}
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def update_user_core_tokens(self, session: Session, core_u_id: int, token: str, u_hash: str) -> None:
        session.execute(
            text("""
                UPDATE core_user_mapping
                SET token = :token, u_hash = :u_hash, last_sync_at = NOW()
                WHERE core_u_id = :core_u_id
            """),
            {"token": token, "u_hash": u_hash, "core_u_id": core_u_id}
        )

    def get_user_tokens(self, session: Session, local_user_id: int) -> Tuple[Optional[str], Optional[str]]:
        """Возвращает (token, u_hash) для локального пользователя."""
        logger.debug("get_user_tokens: local_user_id=%s", local_user_id)
        row = session.execute(
            text("SELECT token, u_hash FROM core_user_mapping WHERE local_user_id = :uid"),
            {"uid": local_user_id}
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def clear_user_u_hash(self, session: Session, local_user_id: int) -> None:
        """Очищает u_hash для пользователя."""
        logger.info("clear_user_u_hash: local_user_id=%s", local_user_id)
        try:
            session.execute(
                text("UPDATE core_user_mapping SET u_hash = NULL WHERE local_user_id = :uid"),
                {"uid": local_user_id}
            )
        except Exception as e:
            logger.error("clear_user_u_hash failed: %s", e)
            raise DbLayerError(f"Failed to clear u_hash: {e}")    

# ==================== CORE ORDERS MAPPING ===================
    
    def get_locker_address_by_cell(self, session: Session, cell_id: int) -> str:
        logger.debug("get_locker_address_by_cell: cell_id=%s", cell_id)
        row = session.execute(
            text("""
                SELECT l.location_address
                FROM locker_cells lc
                JOIN lockers l ON l.id = lc.locker_id
                WHERE lc.id = :cell_id
            """),
            {"cell_id": cell_id}
        ).fetchone()
        if not row or not row[0]:
            logger.error("No address found for cell_id=%s", cell_id)
            raise DbLayerError(f"No address for cell {cell_id}")
        address = row[0]
        logger.debug("get_locker_address_by_cell: cell_id=%s -> address='%s'", cell_id, address)
        return address

    def update_order_cells(self, session: Session, order_id: int, src_cell_id: int, dst_cell_id: int) -> None:
        session.execute(
            text("UPDATE orders SET source_cell_id = :src, dest_cell_id = :dst WHERE id = :oid"),
            {"src": src_cell_id, "dst": dst_cell_id, "oid": order_id}
        )    
        
    def get_or_create_order_by_core_id(
        self,
        session: Session,
        core_order_id: int,
        client_user_id: int,
        recipient_user_id: Optional[int],
        description: str,
        parcel_type: str,
        cell_size: str,
        pickup_type: str,
        delivery_type: str,
        role: str,
        kind: Optional[int],
        upper: Optional[int],
        b_state: int,
        performer_local_user_id: Optional[int] = None,
    ) -> int:
        logger.debug("get_or_create_order_by_core_id: core=%s, role=%s, kind=%s, upper=%s, b_state=%s",
                    core_order_id, role, kind, upper, b_state)
        try:
            # Проверяем существующий маппинг
            row = session.execute(
                text("SELECT local_order_id FROM core_order_mapping WHERE core_order_id = :core_id"),
                {"core_id": core_order_id}
            ).fetchone()
            if row:
                return row[0]

            # Создаём локальный заказ
            order_id = self.create_order_record(
                session=session,
                description=description,
                pickup_type=pickup_type,
                delivery_type=delivery_type,
                client_user_id=client_user_id,
                recipient_user_id=recipient_user_id,
                source_cell_id=None,
                dest_cell_id=None,
            )

            # Сохраняем маппинг
            self.save_core_order_mapping(
                session=session,
                local_order_id=order_id,
                core_order_id=core_order_id,
                role=role,
                kind=kind,
                upper=upper,
                b_state=b_state,
                client_local_user_id=client_user_id if role == "main" else None,
                performer_local_user_id=performer_local_user_id if role != "main" else None,
            )
            logger.info("Created mapping: local=%s, core=%s", order_id, core_order_id)
            return order_id
        except Exception as e:
            logger.exception("get_or_create_order_by_core_id failed")
            raise DbLayerError(f"get_or_create_order_by_core_id failed: {e}") from e

    def save_core_order_mapping(
        self,
        session: Session,
        local_order_id: int,
        core_order_id: int,
        role: str,
        kind: int,
        upper: Optional[int],
        b_state: int,
        client_local_user_id: Optional[int] = None,
        performer_local_user_id: Optional[int] = None,  
    ) -> None:
        logger.debug("save_core_order_mapping: local=%s, core=%s, role=%s, client=%s, performer=%s",
                    local_order_id, core_order_id, role, client_local_user_id, performer_local_user_id)
        try:
            session.execute(
                text("""
                    INSERT INTO core_order_mapping
                        (local_order_id, core_order_id, role, kind, upper, b_state,
                        client_local_user_id, performer_local_user_id, created_at, updated_at)
                    VALUES (:local_id, :core_id, :role, :kind, :upper, :b_state,
                            :client_id, :performer_id, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE
                        core_order_id = VALUES(core_order_id),
                        role = VALUES(role),
                        kind = VALUES(kind),
                        upper = VALUES(upper),
                        b_state = VALUES(b_state),
                        client_local_user_id = VALUES(client_local_user_id),
                        performer_local_user_id = VALUES(performer_local_user_id),
                        updated_at = NOW()
                """),
                {
                    "local_id": local_order_id,
                    "core_id": core_order_id,
                    "role": role,
                    "kind": kind,
                    "upper": upper,
                    "b_state": b_state,
                    "client_id": client_local_user_id,
                    "performer_id": performer_local_user_id,
                }
            )
            logger.info("Mapping saved: local=%s, core=%s", local_order_id, core_order_id)
        except Exception as e:
            logger.error("Database error in save_core_order_mapping: %s", e)
            raise DbLayerError(f"save_core_order_mapping failed: {e}") from e

    def get_main_core_order_id(self, session: Session, local_order_id: int) -> Optional[int]:
        logger.debug("get_main_core_order_id: local=%s", local_order_id)
        try:
            row = session.execute(
                text("SELECT core_order_id FROM core_order_mapping WHERE local_order_id = :local_id AND role = 'main' AND kind = 1 LIMIT 1"),
                {"local_id": local_order_id}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_main_core_order_id: local=%s -> core=%s", local_order_id, result)
            return result
        except SQLAlchemyError as e:
            logger.error("Database error in get_main_core_order_id: %s", e)
            raise DbLayerError(f"Database error: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error in get_main_core_order_id")
            raise DbLayerError(f"Unexpected error: {e}") from e

    def get_suborder_core_id(self, session: Session, local_order_id: int, role: str, upper: int) -> Optional[int]:
        logger.debug("get_suborder_core_id: local=%s, role=%s, upper=%s", local_order_id, role, upper)
        try:
            row = session.execute(
                text("SELECT core_order_id FROM core_order_mapping WHERE local_order_id = :local_id AND role = :role AND upper = :upper LIMIT 1"),
                {"local_id": local_order_id, "role": role, "upper": upper}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_suborder_core_id: local=%s, role=%s -> core=%s", local_order_id, role, result)
            return result
        except SQLAlchemyError as e:
            logger.error("Database error in get_suborder_core_id: %s", e)
            raise DbLayerError(f"Database error: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error in get_suborder_core_id")
            raise DbLayerError(f"Unexpected error: {e}") from e       

    def get_core_suborder_id_by_performer(
        self,
        session: Session,
        local_order_id: int,
        performer_local_user_id: int,
    ) -> Optional[int]:
        """
        Возвращает core_order_id подзаказа по локальному заказу и исполнителю.
        """
        logger.debug("get_core_suborder_id_by_performer: local_order_id=%s, performer=%s",
                    local_order_id, performer_local_user_id)
        try:
            row = session.execute(
                text("""
                    SELECT core_order_id FROM core_order_mapping
                    WHERE local_order_id = :local_id
                    AND performer_local_user_id = :performer_id
                    LIMIT 1
                """),
                {"local_id": local_order_id, "performer_id": performer_local_user_id}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_core_suborder_id_by_performer: result=%s", result)
            return result
        except Exception as e:
            logger.error("get_core_suborder_id_by_performer failed: %s", e)
            raise DbLayerError(f"Failed to get core suborder id: {e}") from e

    def get_core_order_completion_info(
        self,
        session: Session,
        local_order_id: int,
        user_id: int,
        is_main: bool = False,
    ) -> Tuple[Optional[int], Optional[int], Optional[int], str]:
        """
        Возвращает информацию, необходимую для завершения заказа в Core.

        Для главного заказа (is_main=True):
        - проверяет, что user_id является клиентом или получателем заказа
        - возвращает core_order_id и текущий b_state

        Для подзаказа (is_main=False):
        - ищет подзаказ, связанный с исполнителем (по performer_local_user_id)
        - возвращает core_order_id, b_state, performer_local_user_id

        Returns:
            (core_order_id, b_state, assigned_performer, error_message)
        """
        logger.debug("get_core_order_completion_info: local_order_id=%s, user_id=%s, is_main=%s",
                    local_order_id, user_id, is_main)
        try:
            if is_main:
                # Проверка прав: клиент или получатель
                order = self.get_order(session, local_order_id)
                if not order:
                    return None, None, None, "ORDER_NOT_FOUND"
                if user_id not in (order.get("client_user_id"), order.get("recipient_user_id")):
                    return None, None, None, "USER_NOT_AUTHORIZED_FOR_MAIN_ORDER"

                core_order_id = self.get_main_core_order_id(session, local_order_id)
                if not core_order_id:
                    return None, None, None, "MAIN_CORE_ORDER_NOT_FOUND"

                row = session.execute(
                    text("SELECT b_state FROM core_order_mapping WHERE core_order_id = :core_id"),
                    {"core_id": core_order_id}
                ).fetchone()
                b_state = row[0] if row else None
                return core_order_id, b_state, None, ""

            else:
                # Подзаказ: прямой поиск по performer_local_user_id
                row = session.execute(
                    text("""
                        SELECT core_order_id, b_state, performer_local_user_id
                        FROM core_order_mapping
                        WHERE local_order_id = :local_id
                        AND performer_local_user_id = :performer_id
                        LIMIT 1
                    """),
                    {"local_id": local_order_id, "performer_id": user_id}
                ).fetchone()

                if not row:
                    return None, None, None, "SUBORDER_NOT_FOUND"

                core_order_id, b_state, assigned_performer = row
                if assigned_performer != user_id:
                    return None, None, None, "PERFORMER_MISMATCH"

                return core_order_id, b_state, assigned_performer, ""
        except Exception as e:
            logger.error("get_core_order_completion_info failed: %s", e)
            raise DbLayerError(f"Failed to get core order completion info: {e}") from e

    def update_core_order_b_state(self, session: Session, core_order_id: int, b_state: int) -> None:
        logger.debug("update_core_order_b_state: core_order_id=%s, b_state=%s", core_order_id, b_state)
        try:
            session.execute(
                text("""
                    UPDATE core_order_mapping
                    SET b_state = :b_state, updated_at = NOW()
                    WHERE core_order_id = :core_id
                """),
                {"b_state": b_state, "core_id": core_order_id}
            )
            logger.info("Updated b_state to %s for core_order_id=%s", b_state, core_order_id)
        except Exception as e:
            logger.error("update_core_order_b_state failed: %s", e)
            raise DbLayerError(f"Failed to update b_state: {e}") from e

    def get_core_order_b_state(self, session: Session, core_order_id: int) -> Optional[int]:
        row = session.execute(
            text("SELECT b_state FROM core_order_mapping WHERE core_order_id = :core_id"),
            {"core_id": core_order_id}
        ).fetchone()
        return row[0] if row else None

    def get_core_order_mapping_kind(self, session: Session, core_order_id: int) -> Optional[int]:
        row = session.execute(
            text("SELECT kind FROM core_order_mapping WHERE core_order_id = :cid"),
            {"cid": core_order_id}
        ).fetchone()
        return row[0] if row else None

    def clear_core_order_performer(self, session: Session, core_order_id: int) -> None:
        session.execute(
            text("UPDATE core_order_mapping SET performer_local_user_id = NULL WHERE core_order_id = :cid"),
            {"cid": core_order_id}
        )

# ===================== Создание авто ========================
    def get_car_core_id(self, session: Session, local_user_id: int) -> Optional[int]:
        """
        Возвращает car_core_id для локального пользователя из core_user_mapping.
        """
        logger.debug("get_car_core_id: local_user_id=%s", local_user_id)
        try:
            row = session.execute(
                text("SELECT car_core_id FROM core_user_mapping WHERE local_user_id = :uid"),
                {"uid": local_user_id}
            ).fetchone()
            car_core_id = row[0] if row else None
            logger.debug("get_car_core_id: local_user_id=%s -> car_core_id=%s", local_user_id, car_core_id)
            return car_core_id
        except Exception as e:
            logger.error("get_car_core_id failed for local_user_id=%s: %s", local_user_id, e)
            raise DbLayerError(f"Failed to get car_core_id: {e}") from e

    def update_car_core_id(self, session: Session, local_user_id: int, car_core_id: int) -> None:
        logger.debug("update_car_core_id: local_user_id=%s, car_id=%s", local_user_id, car_core_id)
        try:
            result = session.execute(
                text("UPDATE core_user_mapping SET car_core_id = :car_id WHERE local_user_id = :uid"),
                {"car_id": car_core_id, "uid": local_user_id}
            )
            if result.rowcount == 0:
                logger.warning("update_car_core_id: no mapping found for local_user_id=%s", local_user_id)
            else:
                logger.info("update_car_core_id: updated car_core_id=%s for user %s", car_core_id, local_user_id)
        except Exception as e:
            logger.error("update_car_core_id failed: %s", e)
            raise DbLayerError(f"Failed to update car_core_id: {e}")
    
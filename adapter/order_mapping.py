import os
import logging
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from db_layer import DatabaseLayer
from .core_adapter import CoreAdapter
from .mappers.order import to_core_drive_payload
from .exceptions import CoreAdapterError, CoreValidationError

logger = logging.getLogger(__name__)

class OrderMapping:
    def __init__(self, db: DatabaseLayer, core_adapter: CoreAdapter):
        self.db = db
        self.core_adapter = core_adapter

    def create_order_in_core(
        self,
        session: Session,
        request_id: int,
        src_cell_id: int,
        dst_cell_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        logger.info("create_order_in_core: request_id=%s, src=%s, dst=%s", request_id, src_cell_id, dst_cell_id)
        try:
            req = self.db.get_order_request(session, request_id)
            if not req:
                logger.error("create_order_in_core: request %s not found", request_id)
                return False, None, "REQ_NOT_FOUND"

            client_user_id = req["client_user_id"]
            recipient_user_id = req.get("recipient_user_id")

            # 1. Получаем core_u_id и токены клиента
            core_u_id = self.db.get_core_u_id_by_local_user_id(session, client_user_id)
            if not core_u_id:
                logger.error("create_order_in_core: client %s not mapped to Core", client_user_id)
                return False, None, "CLIENT_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                logger.error("create_order_in_core: missing tokens for core_u_id=%s", core_u_id)
                return False, None, "MISSING_CORE_TOKENS"

            # 2. Подготовка данных
            parcel_type = req["parcel_type"]
            cell_size = req["cell_size"]
            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]
            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            client_city = self.db.get_user_city(session, client_user_id)
            recipient_city = self.db.get_user_city(session, recipient_user_id) if recipient_user_id else client_city
            logger.debug("create_order_in_core: cities client=%s recipient=%s", client_city, recipient_city)

            start_address = self.db.get_locker_address_by_cell(session, src_cell_id)
            dest_address = self.db.get_locker_address_by_cell(session, dst_cell_id)
            logger.debug("create_order_in_core: addresses start=%s dest=%s", start_address, dest_address)

            # Определяем, нужен ли статус 6 (предложение водителям)
            only_offer = (pickup_type == "courier")

            core_order_data = to_core_drive_payload(
                start_address, dest_address, client_city, recipient_city,
                only_offer=only_offer,
            )

            # 3. Вызов Core с токенами
            try:
                core_response = self.core_adapter.create_drive_order(core_order_data, token, u_hash)
                core_order_id = core_response["data"]["b_id"]
                logger.info("create_order_in_core: core_order_id=%s created (only_offer=%s)", core_order_id, only_offer)
            except CoreAdapterError as e:
                logger.error("create_order_in_core: Core call failed: %s", e)
                return False, None, f"CORE_ERROR: {e}"

            return True, core_order_id, ""

        except Exception as e:
            logger.exception("create_order_in_core failed for request %s: %s", request_id, e)
            return False, None, f"EXCEPTION: {e}"

# ======================= Отмена заказа ============================
    def cancel_order_in_core(self, session: Session, local_order_id: int, user_id: int, reason: str = None) -> Tuple[bool, str]:
        """
        Отмена заказа в Core по локальному ID заказа.
        Возвращает (успех, сообщение_об_ошибке).
        """
        logger.info("cancel_order_in_core: local_order_id=%s, user_id=%s", local_order_id, user_id)
        try:
            # 1. Получить core_order_id
            core_order_id = self.db.get_core_order_id_by_local_order_id(session, local_order_id)
            if not core_order_id:
                logger.warning("cancel_order_in_core: core_order_id not found for local_order_id=%s", local_order_id)
                return False, "CORE_ORDER_ID_NOT_FOUND"

            # 2. Получить core_u_id пользователя, инициирующего отмену
            core_u_id = self.db.get_core_u_id_by_local_user_id(session, user_id)
            if not core_u_id:
                logger.warning("cancel_order_in_core: user %s not mapped to Core", user_id)
                return False, "USER_NOT_MAPPED_TO_CORE"

            # 3. Получить токены пользователя
            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                logger.warning("cancel_order_in_core: missing tokens for core_u_id=%s", core_u_id)
                return False, "MISSING_CORE_TOKENS"

            # 4. Вызвать Core API
            self.core_adapter.cancel_drive_order(core_order_id, token, u_hash, reason=reason)
            logger.info("cancel_order_in_core: successfully cancelled core order %s", core_order_id)
            return True, ""

        except CoreAdapterError as e:
            logger.error("cancel_order_in_core: Core error: %s", e)
            return False, f"CORE_ERROR: {e}"
        except Exception as e:
            logger.exception("cancel_order_in_core: unexpected error")
            return False, f"EXCEPTION: {e}"

# ======================= Назначение курьера ==================
    def assign_courier_in_core(
        self,
        session: Session,
        local_order_id: int,
        courier_local_user_id: int,
        role: str,
    ) -> Tuple[bool, str]:
        """
        Назначить курьера (performer) в Core.
        """
        logger.info(
            "assign_courier_in_core: local_order=%s, courier=%s, role=%s",
            local_order_id, courier_local_user_id, role
        )

        try:
            # 1. Получить core_order_id
            core_order_id = self.db.get_core_order_id_by_local_order_id(session, local_order_id)
            if not core_order_id:
                logger.warning("assign_courier_in_core: core_order_id not found for local_order=%s", local_order_id)
                return False, "CORE_ORDER_ID_NOT_FOUND"

            # 2. Получить core_u_id курьера
            core_courier_id = self.db.get_core_u_id_by_local_user_id(session, courier_local_user_id)
            if not core_courier_id:
                logger.warning("assign_courier_in_core: courier %s not mapped to Core", courier_local_user_id)
                return False, "COURIER_NOT_MAPPED_TO_CORE"

            # 3. Получить car_core_id (машина курьера)
            car_core_id = self.db.get_car_core_id(session, courier_local_user_id)
            if not car_core_id:
                logger.warning("assign_courier_in_core: courier %s has no car_core_id", courier_local_user_id)
                return False, "COURIER_HAS_NO_CAR_IN_CORE"

            # 4. Получить токены курьера
            token, u_hash = self.db.get_user_core_tokens(session, core_courier_id)
            if not token or not u_hash:
                logger.warning("assign_courier_in_core: missing tokens for core_u_id=%s", core_courier_id)
                return False, "COURIER_CORE_TOKENS_MISSING"

            # 5. Вызвать Core set_performer
            self.core_adapter.perform_drive_order(
                core_order_id,
                core_courier_id,
                token,
                u_hash,
                c_id=car_core_id,
                c_payment_way=2
            )
            logger.info("assign_courier_in_core success: core_order=%s, courier=%s, car=%s",
                        core_order_id, core_courier_id, car_core_id)
            return True, ""

        except CoreValidationError as e:
            logger.error("assign_courier_in_core validation error: %s", e)
            return False, f"CORE_VALIDATION_ERROR: {e}"
        except CoreAuthError as e:
            logger.error("assign_courier_in_core auth error: %s", e)
            return False, f"CORE_AUTH_ERROR: {e}"
        except CoreAdapterError as e:
            logger.error("assign_courier_in_core adapter error: %s", e)
            return False, f"CORE_ADAPTER_ERROR: {e}"
        except Exception as e:
            logger.exception("assign_courier_in_core unexpected error")
            return False, f"UNEXPECTED_ERROR: {e}"
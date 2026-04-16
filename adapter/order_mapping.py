import os
import logging
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from db_layer import DatabaseLayer, DbLayerError
from .core_adapter import CoreAdapter
from .mappers.order import to_core_drive_payload, from_core_order_response, to_core_suborder_payload, from_core_order_response
from .exceptions import CoreAdapterError, CoreValidationError, CoreAuthError

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
    ) -> Tuple[bool, Optional[int], Optional[int], Optional[int], Optional[int], str]:
        logger.info("create_order_in_core: request_id=%s", request_id)
        try:
            req = self.db.get_order_request(session, request_id)
            if not req:
                return False, None, None, None, None, "REQ_NOT_FOUND"

            client_user_id = req["client_user_id"]
            core_u_id = self.db.get_core_u_id_by_local_user_id(session, client_user_id)
            if not core_u_id:
                return False, None, None, None, None, "CLIENT_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                return False, None, None, None, None, "MISSING_CORE_TOKENS"

            client_city = self.db.get_user_city(session, client_user_id)
            recipient_city = self.db.get_user_city(session, req["recipient_user_id"]) if req["recipient_user_id"] else client_city
            start_address = self.db.get_locker_address_by_cell(session, src_cell_id)
            dest_address = self.db.get_locker_address_by_cell(session, dst_cell_id)

            payload = to_core_drive_payload(
                start_address, dest_address, client_city, recipient_city,
                kind=1,
            )
            response = self.core_adapter.create_drive_order(payload, token, u_hash)
            core_order_id = response["data"]["b_id"]

            # Извлекаем данные из ответа Core
            core_data = from_core_order_response(response, core_order_id)
            b_state = core_data["b_state"]
            kind = 1
            upper = core_data["upper"]

            return True, core_order_id, b_state, kind, upper, ""
        except Exception as e:
            logger.exception("create_order_in_core failed")
            return False, None, None, None, None, str(e) 

    def _get_order_addresses(self, session: Session, local_order_id: int) -> Tuple[str, str]:
        """
        Возвращает (start_address, dest_address) для заказа.
        Адреса берутся из ячеек source_cell_id и dest_cell_id.
        """
        order = self.db.get_order(session, local_order_id)
        if not order:
            raise DbLayerError(f"Заказ {local_order_id} не найден")
        
        src_cell_id = order.get("source_cell_id")
        dst_cell_id = order.get("dest_cell_id")
        
        if not src_cell_id or not dst_cell_id:
            raise DbLayerError(f"У заказа {local_order_id} отсутствуют source_cell_id или dest_cell_id")
        
        start_address = self.db.get_locker_address_by_cell(session, src_cell_id)
        dest_address = self.db.get_locker_address_by_cell(session, dst_cell_id)
        
        return start_address, dest_address

    def create_suborder_in_core(
        self,
        session: Session,
        local_order_id: int,
        role: str,
        performer_local_user_id: int,
        main_core_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        logger.info("create_suborder_in_core: local=%s, role=%s, main=%s",
                    local_order_id, role, main_core_id)
        try:
            # 1. Получаем заказ и его владельца-клиента
            order = self.db.get_order(session, local_order_id)
            if not order:
                return False, None, "ORDER_NOT_FOUND"
            client_local_id = order["client_user_id"]
            client_core_id = self.db.get_core_u_id_by_local_user_id(session, client_local_id)
            if not client_core_id:
                return False, None, "CLIENT_NOT_MAPPED_TO_CORE"

            # 2. Токен клиента для создания подзаказа
            token, u_hash = self.db.get_user_core_tokens(session, client_core_id)
            if not token or not u_hash:
                return False, None, "MISSING_CLIENT_CORE_TOKENS"

            # 3. Создаём подзаказ от имени клиента
            kind = 2 if role == "driver" else 3
            start_address, dest_address = self._get_order_addresses(session, local_order_id)

            payload = to_core_suborder_payload(start_address, dest_address, kind, main_core_id)
            response = self.core_adapter.create_drive_order(payload, token, u_hash)
            if response.get("status") != "success":
                return False, None, f"Core error: {response.get('message')}"

            core_sub_id = response["data"]["b_id"]

            # 4. Назначаем исполнителя
            performer_core_id = self.db.get_core_u_id_by_local_user_id(session, performer_local_user_id)
            if not performer_core_id:
                return False, None, "PERFORMER_NOT_MAPPED_TO_CORE"

            performer_token, performer_u_hash = self.db.get_user_core_tokens(session, performer_core_id)
            if not performer_token or not performer_u_hash:
                return False, None, "MISSING_PERFORMER_CORE_TOKENS"

            car_core_id = self.db.get_car_core_id(session, performer_local_user_id)
            if not car_core_id:
                return False, None, "MISSING_CAR_FOR_PERFORMER"

            set_performer_response = self.core_adapter.perform_drive_order(
                core_sub_id,
                performer_core_id,
                performer_token,
                performer_u_hash,
                c_id=car_core_id
            )
            logger.info("set_performer response: %s", set_performer_response)

            data = set_performer_response.get('data', {})
            b_state_transition = data.get('b_state', '')
            if '->' in b_state_transition:
                b_state = int(b_state_transition.split('->')[-1])
            else:
                b_state = 2 
            upper = main_core_id  

            # 5. Сохраняем маппинг
            self.db.save_core_order_mapping(
                session=session,
                local_order_id=local_order_id,
                core_order_id=core_sub_id,
                role=role,
                kind=kind,
                upper=upper,
                b_state=b_state,
            )

            logger.info("create_suborder_in_core success: local=%s, core_sub_id=%s, b_state=%s",
                        local_order_id, core_sub_id, b_state)
            return True, core_sub_id, ""

        except DbLayerError as e:
            logger.error("DB error in create_suborder_in_core: %s", e)
            return False, None, f"DB_ERROR: {e}"
        except CoreValidationError as e:
            logger.error("Core validation error in create_suborder_in_core: %s", e)
            return False, None, f"CORE_VALIDATION_ERROR: {e}"
        except CoreAdapterError as e:
            logger.error("Core adapter error in create_suborder_in_core: %s", e)
            return False, None, f"CORE_ADAPTER_ERROR: {e}"
        except Exception as e:
            logger.exception("Unexpected error in create_suborder_in_core")
            return False, None, f"UNEXPECTED_ERROR: {e}"

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
        logger.info("assign_courier_in_core: local=%s, courier=%s, role=%s",
                    local_order_id, courier_local_user_id, role)
        try:
            main_core_id = self.db.get_main_core_order_id(session, local_order_id)
            if not main_core_id:
                logger.error("Main core order not found for local_order=%s", local_order_id)
                return False, "MAIN_ORDER_NOT_FOUND"

            existing = self.db.get_suborder_core_id(session, local_order_id, role, main_core_id)
            if existing:
                logger.info("Подзаказ для роли %s уже существует: core_id=%s", role, existing)
                return True, ""

            success, core_sub_id, err = self.create_suborder_in_core(
                session, local_order_id, role, courier_local_user_id, main_core_id
            )
            if not success:
                logger.error("create_suborder_in_core failed: %s", err)
                return False, f"CREATE_SUBORDER_FAILED: {err}"
            return True, ""

        except DbLayerError as e:
            logger.error("DB error in assign_courier_in_core: %s", e)
            return False, f"DB_ERROR: {e}"
        except CoreAdapterError as e:
            logger.error("Core adapter error: %s", e)
            return False, f"CORE_ERROR: {e}"
        except Exception as e:
            logger.exception("Unexpected error in assign_courier_in_core")
            return False, f"UNEXPECTED_ERROR: {e}"

    
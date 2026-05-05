import os
import logging
from typing import Tuple, Optional, List
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
            recipient_user_id = req.get("recipient_user_id")
            parcel_type = req["parcel_type"]
            cell_size = req["cell_size"]
            sender_delivery = req["sender_delivery"]
            recipient_delivery = req["recipient_delivery"]
            description = f"{parcel_type} ({cell_size})"
            pickup_type = "self" if sender_delivery == "self" else "courier"
            delivery_type = "self" if recipient_delivery == "self" else "courier"

            core_u_id = self.db.get_core_u_id_by_local_user_id(session, client_user_id)
            if not core_u_id:
                return False, None, None, None, None, "CLIENT_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                return False, None, None, None, None, "MISSING_CORE_TOKENS"

            client_city = self.db.get_user_city(session, client_user_id)
            if recipient_user_id:
                recipient_city = self.db.get_user_city(session, recipient_user_id)
            else:
                recipient_city = client_city

            start_address = self.db.get_locker_address_by_cell(session, src_cell_id)
            dest_address = self.db.get_locker_address_by_cell(session, dst_cell_id)

            b_options = {
                "parcel_type": parcel_type,
                "cell_size": cell_size,
                "sender_delivery": sender_delivery,
                "recipient_delivery": recipient_delivery,
                "client_user_id": client_user_id,
                "recipient_user_id": recipient_user_id,
                "description": description,
                "pickup_type": pickup_type,
                "delivery_type": delivery_type,
            }
            kind = 1
            payload = to_core_drive_payload(
                start_address=start_address,
                dest_address=dest_address,
                start_city=client_city,
                dest_city=recipient_city,
                b_options=b_options,
                kind=kind,
                upper=None,
            )

            response = self.core_adapter.create_drive_order(payload, token, u_hash)
            core_order_id = response["data"]["b_id"]
            try:
                core_data = from_core_order_response(response, core_order_id)
                b_state = core_data["b_state"]
                upper = core_data.get("upper")
            except:
                b_state = None
                upper = None

            return True, core_order_id, b_state, kind, upper, ""

        except Exception as e:
            logger.exception("create_order_in_core failed")
            return False, None, None, None, None, str(e) 

    def create_suborder_in_core(
        self,
        session: Session,
        local_order_id: int,
        role: str,
        main_core_id: int,
    ) -> Tuple[bool, Optional[int], str]:
        logger.info("Создание подзаказа в Core: local=%s, role=%s, main=%s", local_order_id, role, main_core_id)
        try:
            order = self.db.get_order(session, local_order_id)
            if not order:
                return False, None, "ЗАКАЗ_НЕ_НАЙДЕН"

            client_local_id = order["client_user_id"]
            client_core_id = self.db.get_core_u_id_by_local_user_id(session, client_local_id)
            if not client_core_id:
                return False, None, "КЛИЕНТ_НЕ_ПРИВЯЗАН_К_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, client_core_id)
            if not token or not u_hash:
                return False, None, "ОТСУТСТВУЮТ_ТОКЕНЫ_КЛИЕНТА"

            kind = 2 if role == "driver" else 3
            start_address, dest_address = self._get_order_addresses(session, local_order_id)
            payload = to_core_suborder_payload(start_address, dest_address, kind, main_core_id)
            response = self.core_adapter.create_drive_order(payload, token, u_hash)

            if response.get("status") != "success":
                return False, None, f"Ошибка Core: {response.get('message')}"

            core_sub_id = response["data"]["b_id"]

            try:
                parsed = from_core_order_response(response, core_sub_id)
                b_state = parsed["b_state"]
            except Exception:
                b_state = 1

            self.db.save_core_order_mapping(
                session=session,
                local_order_id=local_order_id,
                core_order_id=core_sub_id,
                role=role,
                kind=kind,
                upper=main_core_id,
                b_state=b_state,
                client_local_user_id=None,
                performer_local_user_id=None,
            )
            logger.info("Подзаказ создан и замаплен: core_sub_id=%s", core_sub_id)
            return True, core_sub_id, ""

        except Exception as e:
            logger.exception("Ошибка создания подзаказа в Core")
            return False, None, f"ИСКЛЮЧЕНИЕ: {e}"

# ======================= Отмена заказа ============================
    def cancel_main_order_in_core(
        self,
        session: Session,
        local_order_id: int,
        user_id: int,
        reason: str = None
    ) -> Tuple[bool, str]:
        logger.info("Отмена главного заказа в Core: local=%s, user=%s", local_order_id, user_id)
        try:
            core_order_id = self.db.get_main_core_order_id(session, local_order_id)
            if not core_order_id:
                return False, "MAIN_ORDER_NOT_FOUND"

            # Проверка, не отменён ли уже
            current_b_state = self.db.get_core_order_b_state(session, core_order_id)
            if current_b_state == 3:
                logger.info("Главный заказ %s уже отменён", core_order_id)
                return True, ""

            core_u_id = self.db.get_core_u_id_by_local_user_id(session, user_id)
            if not core_u_id:
                return False, "USER_NOT_MAPPED_TO_CORE"
            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                return False, "MISSING_CORE_TOKENS"

            self.core_adapter.cancel_drive_order(core_order_id, token, u_hash, reason=reason)

            order_info = self.core_adapter.get_drive_order(core_order_id, token, u_hash, kind=1)
            parsed = from_core_order_response(order_info, core_order_id)
            new_b_state = parsed["b_state"]

            self.db.update_core_order_b_state(session, core_order_id, new_b_state)
            logger.info("Главный заказ %s отменён, b_state=%s", core_order_id, new_b_state)
            return True, ""

        except Exception as e:
            logger.exception("cancel_main_order_in_core failed")
            return False, f"EXCEPTION: {e}"

    def remove_suborder_performer_in_core(
        self,
        session: Session,
        local_order_id: int,
        performer_local_user_id: int,
        user_id: int,  
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        logger.info(
            "Снятие исполнителя с подзаказа: local=%s, performer=%s, initiator=%s",
            local_order_id, performer_local_user_id, user_id
        )
        try:
            # 1. Найти подзаказ в Core
            core_order_id = self.db.get_core_suborder_id_by_performer(
                session, local_order_id, performer_local_user_id
            )
            if not core_order_id:
                return False, "SUBORDER_NOT_FOUND"

            # 2. Проверить, не снят ли уже исполнитель
            current_b_state = self.db.get_core_order_b_state(session, core_order_id)
            if current_b_state == 1:
                logger.info("Подзаказ %s уже в статусе b_state=1, исполнитель снят ранее", core_order_id)
                return True, ""

            # 3. Получить токены самого исполнителя (курьера/водителя)
            performer_core_id = self.db.get_core_u_id_by_local_user_id(session, performer_local_user_id)
            if not performer_core_id:
                return False, "PERFORMER_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, performer_core_id)
            if not token or not u_hash:
                return False, "MISSING_PERFORMER_TOKENS"

            # 4. Отменить используем токены исполнителя
            self.core_adapter.cancel_drive_order(core_order_id, token, u_hash, reason=reason)

            # 5. Обновить маппинг
            self.db.update_core_order_b_state(session, core_order_id, 1)
            self.db.clear_core_order_performer(session, core_order_id)

            logger.info("Исполнитель снят, подзаказ %s перешёл в b_state=1", core_order_id)
            return True, ""

        except Exception as e:
            logger.exception("Ошибка при снятии исполнителя с подзаказа в Core")
            return False, f"EXCEPTION: {e}"

# ======================= Назначение исполнителя ==================
    def assign_executor_in_core(
        self,
        session: Session,
        local_order_id: int,
        performer_local_user_id: int,
        role: str,
    ) -> Tuple[bool, str]:
        logger.info(
            "Назначение исполнителя в Core: local=%s, performer=%s, role=%s",
            local_order_id, performer_local_user_id, role,
        )
        try:
            main_core_id = self.db.get_main_core_order_id(session, local_order_id)
            if not main_core_id:
                return False, "ГЛАВНЫЙ_ЗАКАЗ_НЕ_НАЙДЕН"

            kind = 2 if role == "driver" else 3
            existing_core_id = self.db.get_suborder_core_id(
                session, local_order_id, role, main_core_id
            )

            can_reuse = False
            if existing_core_id:
                current_state = self.db.get_core_order_b_state(session, existing_core_id)
                if current_state == 1:
                    can_reuse = True
                    logger.info("Найден подзаказ core_id=%s в b_state=1, будет переназначен", existing_core_id)
                else:
                    logger.info("Подзаказ core_id=%s имеет b_state=%s – будет создан новый",
                                existing_core_id, current_state)
                    existing_core_id = None

            if can_reuse:
                core_order_id = existing_core_id
            else:
                # Создаём новый подзаказ (без исполнителя)
                success, core_order_id, err = self.create_suborder_in_core(
                    session, local_order_id, role, main_core_id
                )
                if not success:
                    return False, f"ОШИБКА_СОЗДАНИЯ_ПОДЗАКАЗА: {err}"

            # Назначаем исполнителя на подзаказ (новый или переиспользуемый)
            car_core_id = self.db.get_car_core_id(session, performer_local_user_id)
            if not car_core_id:
                return False, "У_ИСПОЛНИТЕЛЯ_НЕТ_МАШИНЫ"

            success, msg = self.assign_performer_to_suborder(
                session,
                core_order_id=core_order_id,
                performer_local_user_id=performer_local_user_id,
                car_core_id=car_core_id,
                local_order_id=local_order_id,
                main_core_id=main_core_id,
                role=role,
                kind=kind,
            )
            if not success:
                return False, msg

            logger.info("Назначение исполнителя выполнено, core_order_id=%s", core_order_id)
            return True, ""

        except Exception as e:
            logger.exception("Ошибка при назначении исполнителя в Core")
            return False, str(e)

    def assign_performer_to_suborder(
        self,
        session: Session,
        core_order_id: int,
        performer_local_user_id: int,
        car_core_id: int,
        local_order_id: int,
        main_core_id: int,
        role: str,
        kind: int,
    ) -> Tuple[bool, str]:
        """Назначает исполнителя в Core и обновляет локальный маппинг (использует токены исполнителя)."""
        logger.info(
            "Назначение исполнителя в Core: core_order=%s, performer_local=%s",
            core_order_id,
            performer_local_user_id,
        )

        performer_core_id = self.db.get_core_u_id_by_local_user_id(session, performer_local_user_id)
        if not performer_core_id:
            return False, "ИСПОЛНИТЕЛЬ_НЕ_ПРИВЯЗАН_К_CORE"

        performer_token, performer_u_hash = self.db.get_user_core_tokens(session, performer_core_id)
        if not performer_token or not performer_u_hash:
            return False, "ОТСУТСТВУЮТ_ТОКЕНЫ_ИСПОЛНИТЕЛЯ"

        if not car_core_id:
            return False, "У_ИСПОЛНИТЕЛЯ_НЕТ_МАШИНЫ"

        try:
            response = self.core_adapter.perform_drive_order(
                core_order_id,
                performer_core_id,
                performer_token,
                performer_u_hash,
                c_id=car_core_id,
            )
        except Exception as e:
            logger.exception("Ошибка вызова perform_drive_order")
            return False, f"ОШИБКА_CORE_SET_PERFORMER: {e}"

        if response.get("status") != "success":
            logger.error("Core set_performer вернул ошибку: %s", response)
            return False, f"ОШИБКА_CORE_SET_PERFORMER: {response.get('message')}"

        # Обновить b_state
        data = response.get("data", {})
        b_state_transition = data.get("b_state", "")
        if "->" in b_state_transition:
            new_b_state = int(b_state_transition.split("->")[-1])
        else:
            new_b_state = self.db.get_core_order_b_state(session, core_order_id) or 2

        self.db.update_core_order_b_state(session, core_order_id, new_b_state)

        # Сохранить маппинг с новым исполнителем
        try:
            self.db.save_core_order_mapping(
                session=session,
                local_order_id=local_order_id,
                core_order_id=core_order_id,
                role=role,
                kind=kind,
                upper=main_core_id,
                b_state=new_b_state,
                performer_local_user_id=performer_local_user_id,
            )
        except Exception as e:
            logger.exception("Ошибка сохранения маппинга core_order")
            return False, f"ОШИБКА_СОХРАНЕНИЯ_МАППИНГА: {e}"

        logger.info("Исполнитель успешно назначен, b_state=%s", new_b_state)
        return True, ""

# ======================= Завершение заказа ===================
    def complete_main_order_in_core(
        self,
        session: Session,
        local_order_id: int,
        user_id: int, 
    ) -> Tuple[bool, str]:
        logger.info("complete_main_order_in_core: local_order_id=%s, initiator_user_id=%s",
                    local_order_id, user_id)

        try:
            core_order_id = self.db.get_main_core_order_id(session, local_order_id)
            if not core_order_id:
                return False, "MAIN_ORDER_NOT_FOUND_IN_CORE"

            # Проверяем b_state
            b_state = self.db.get_core_order_b_state(session, core_order_id)
            if b_state == 4:
                logger.info("Main order already completed in Core")
                return True, ""

            order = self.db.get_order(session, local_order_id)
            if not order:
                return False, "ORDER_NOT_FOUND"

            client_local_id = order["client_user_id"]
            client_core_id = self.db.get_core_u_id_by_local_user_id(session, client_local_id)
            if not client_core_id:
                return False, "CLIENT_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, client_core_id)
            if not token or not u_hash:
                return False, "MISSING_CLIENT_CORE_TOKENS"

            self.core_adapter.complete_drive_order(core_order_id, token, u_hash)
            self.db.update_core_order_b_state(session, core_order_id, 4)

            logger.info("complete_main_order_in_core success: core_order_id=%s", core_order_id)
            return True, ""

        except Exception as e:
            logger.exception("complete_main_order_in_core failed")
            return False, str(e)

    def complete_suborder_in_core(
        self,
        session: Session,
        local_order_id: int,
        performer_user_id: int,
    ) -> Tuple[bool, str]:
        """
        Завершить подзаказ исполнителя в Core (b_state=4).
        """
        logger.info("complete_suborder_in_core: local_order_id=%s, performer=%s",
                    local_order_id, performer_user_id)
        try:
            core_order_id, current_b_state, _, err = self.db.get_core_order_completion_info(
                session, local_order_id, performer_user_id, is_main=False
            )
            if err:
                return False, err

            if current_b_state == 4:
                logger.info("Suborder already completed in Core")
                return True, ""

            core_u_id = self.db.get_core_u_id_by_local_user_id(session, performer_user_id)
            if not core_u_id:
                return False, "PERFORMER_NOT_MAPPED_TO_CORE"

            token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
            if not token or not u_hash:
                return False, "MISSING_PERFORMER_CORE_TOKENS"

            self.core_adapter.complete_drive_order(core_order_id, token, u_hash)
            self.db.update_core_order_b_state(session, core_order_id, 4)

            logger.info("complete_suborder_in_core success: core_order_id=%s", core_order_id)
            return True, ""

        except Exception as e:
            logger.exception("complete_suborder_in_core failed")
            return False, str(e)

# ======================Вспомогательные методы ================
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

    def _get_operator_tokens(self, session: Session, operator_local_user_id: int) -> Tuple[Optional[str], Optional[str]]:
        # Проверим, что пользователь — оператор (или админ)
        role = self.db.get_user_role(session, operator_local_user_id)
        if role not in ("operator", "admin"):
            logger.warning("Пользователь %s не является оператором (роль: %s)", operator_local_user_id, role)
            return None, None

        core_u_id = self.db.get_core_u_id_by_local_user_id(session, operator_local_user_id)
        if not core_u_id:
            return None, None
        return self.db.get_user_core_tokens(session, core_u_id)
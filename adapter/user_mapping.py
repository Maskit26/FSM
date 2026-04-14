"""
UserMapping — оркестратор. Координирует CoreAdapter и DatabaseLayer.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from .core_adapter import CoreAdapter
from db_layer import DatabaseLayer 
from .mappers.user import to_core_car_payload 
from .exceptions import CoreAuthError, CoreMappingError, CoreAdapterError, CoreValidationError, CoreUnavailableError

logger = logging.getLogger(__name__)

class UserMapping:
    def __init__(self, core_adapter: CoreAdapter, db: DatabaseLayer):
        self.core_adapter = core_adapter
        self.db = db

    def register_user(self, session: Session, user_data: Dict[str, Any]) -> Tuple[int, int]:
        role_name = user_data.get("role_name", "client")
        logger.info("register_user: role=%s, phone=%s", role_name, user_data.get("phone"))

        # 1. Регистрация в Core
        try:
            core_u_id, token, u_hash = self.core_adapter.register_user_in_core(user_data)
            logger.info("Core user created: core_u_id=%s", core_u_id)
        except CoreValidationError as e:
            logger.error("Ошибка валидации Core: %s", e)
            raise
        except CoreAdapterError as e:
            logger.error("Ошибка адаптера Core: %s", e)
            raise
        except Exception as e:
            logger.exception("Неожиданная ошибка при регистрации в Core")
            raise CoreAdapterError(f"Неожиданная ошибка при регистрации в Core: {e}")

        # 2. Создание локального пользователя
        try:
            local_user_id = self.db.create_user_record(
                session=session,
                phone=user_data["phone"],
                name=user_data["name"],
                role_name=role_name,
                city=user_data.get("city"),
            )
            logger.info("Local user created: local_user_id=%s", local_user_id)
        except Exception as e:
            logger.error("Создание локального пользователя не удалось: %s", e)
            raise DbLayerError(f"Local user creation failed: {e}")

        # 3. Сохранение mapping
        try:
            core_role = 2 if role_name in ("courier", "driver") else 1
            self.db.create_user_core_mapping(
                session=session,
                user_id=local_user_id,
                core_u_id=core_u_id,
                core_role=core_role,
            )
            if token and u_hash:
                self.db.update_user_core_tokens(session, core_u_id, token, u_hash)
            session.commit()
            logger.info("Mapping сохранён: local=%s ↔ core=%s", local_user_id, core_u_id)
        except Exception as e:
            session.rollback()
            logger.error("Сохранение mapping не удалось: %s", e)
            raise DbLayerError(f"Mapping save failed: {e}")

        return local_user_id, core_u_id

    def get_or_create_by_core_id(
        self, 
        session: Session, 
        core_u_id: int, 
        auth_data: Optional[Dict[str, Any]] = None
    ) -> int:
        logger.debug("get_or_create_by_core_id: core_u_id=%s", core_u_id)

        existing_id = self.db.get_local_user_id_by_core_u_id(session, core_u_id)
        if existing_id:
            return existing_id

        if not auth_data:
            raise ValueError("auth_data is required for creating new user mapping")

        user_name = auth_data.get("user_name", f"User_{core_u_id}")
        phone = auth_data.get("login", "")
        core_role = auth_data.get("core_role", 1)

        # Определяем локальную роль
        local_role = auth_data.get("local_role")
        if local_role is None:
            if core_role == 1:
                local_role = "client"
            elif core_role == 2:
                local_role = "driver"
            elif core_role == 3:
                local_role = "operator"
            else:
                local_role = "client"

        local_user_id = self.db.create_user_record(
            session=session,
            phone=phone,
            name=user_name,
            role_name=local_role,
            city=auth_data.get("city"),
        )

        self.db.create_user_core_mapping(
            session=session,
            user_id=local_user_id,
            core_u_id=core_u_id,
            core_role=core_role,
        )

        logger.info("get_or_create_by_core_id: создан local=%s из auth_data", local_user_id)
        return local_user_id

    def _map_role_to_core(self, role_name: str) -> int:
        from .mappers.user import ROLE_TO_CORE
        return ROLE_TO_CORE.get(role_name, 1)

# ==================== Авторизация ===============================
    def authenticate_user(self, session: Session, login: str, password: str, type: str = "phone") -> Dict[str, Any]:
        logger.info("authenticate_user: login=%s", login)
        try:
            auth_data = self.core_adapter.authenticate_user(login, password, type)
            core_u_id = auth_data["core_u_id"]
            auth_hash = auth_data["auth_hash"]

            # Получаем токены
            token_data = self.core_adapter.get_token(auth_hash)
            logger.info(f"get_token response: {token_data}")

            if isinstance(token_data, dict) and token_data.get("status") != "success":
                raise CoreAdapterError(f"Failed to get token: {token_data.get('message')}")

            if isinstance(token_data, list):
                if not token_data:
                    raise CoreAdapterError("Empty token response")
                token_data = token_data[0]

            data = token_data.get("data")
            if not isinstance(data, dict):
                raise CoreAdapterError(f"Invalid token response data: {data}")

            token = data.get("token")
            u_hash = data.get("u_hash")
            if not token or not u_hash:
                raise CoreAdapterError("Missing token or u_hash in response")

            # Создаём/получаем локального пользователя
            local_user_id = self.get_or_create_by_core_id(session, core_u_id, auth_data)

            # Сохраняем токены
            self.db.update_user_core_tokens(session, core_u_id, token, u_hash)

            # ===== получаем и сохраняем car_core_id =====
            car_ids = self.core_adapter.get_user_cars(core_u_id, token, u_hash)
            if car_ids:
                car_core_id = car_ids[0]
                self.db.update_car_core_id(session, local_user_id, car_core_id)
                logger.info("Updated car_core_id=%s for user %s", car_core_id, local_user_id)
            else:
                logger.debug("No cars found for core_u_id=%s", core_u_id)

            session.commit()
            return {
                "local_user_id": local_user_id,
                "core_user_id": core_u_id,
                "auth_hash": auth_hash,
                "role": auth_data.get("core_role"),
                "message": "Успешно"
            }
        except CoreValidationError as e:
            logger.error("Auth validation error: %s", e)
            raise
        except CoreAdapterError as e:
            logger.error("Auth adapter error: %s", e)
            raise
        except Exception as e:
            logger.exception("Unexpected error in authenticate_user")
            raise CoreAdapterError(f"Auth failed: {e}")

# ===================== Деаторизация ============================
    def logout_user_by_id(self, session: Session, local_user_id: int) -> Dict[str, Any]:
        logger.info("logout_user_by_id: user_id=%s", local_user_id)
        token, u_hash = self.db.get_user_tokens(session, local_user_id)
        if not token or not u_hash:
            raise CoreAdapterError("No active tokens for user")
        result = self.core_adapter.logout_user_with_token(token, u_hash)
        
        self.db.clear_user_u_hash(session, local_user_id)
        return result

# ================== Создание авто ======================== 
    def create_car_for_core_user(
        self,
        session: Session,
        core_u_id: int,
        car_type: str,
        seats: int = 1,
        custom_body_ru: Optional[str] = None,
        custom_body_en: Optional[str] = None,
        custom_make_ru: Optional[str] = None,
        custom_make_en: Optional[str] = None,
        custom_model_ru: Optional[str] = None,
        custom_model_en: Optional[str] = None,
        custom_model_year: Optional[int] = None,
        custom_model_doors: Optional[int] = None,
    ) -> int:
        # 1. Найти local_user_id
        local_user_id = self.db.get_local_user_id_by_core_u_id(session, core_u_id)
        if not local_user_id:
            raise CoreMappingError(f"Core user {core_u_id} not mapped locally")
        # 2. Проверить, нет ли машины
        if self.db.get_car_core_id(session, local_user_id):
            raise CoreMappingError("User already has a car")
        # 3. Получить токены
        token, u_hash = self.db.get_user_core_tokens(session, core_u_id)
        if not token or not u_hash:
            raise CoreAuthError(f"Missing tokens for core_u_id {core_u_id}")
        # 4. Сформировать данные машины
        prefix = "BIKE" if car_type == "courier" else "CAR"
        registration_plate = f"{prefix}-{core_u_id}"
        car_data = to_core_car_payload(
            registration_plate=registration_plate,
            car_type=car_type,
            seats=seats,
            custom_body_ru=custom_body_ru,
            custom_body_en=custom_body_en,
            custom_make_ru=custom_make_ru,
            custom_make_en=custom_make_en,
            custom_model_ru=custom_model_ru,
            custom_model_en=custom_model_en,
            custom_model_year=custom_model_year,
            custom_model_doors=custom_model_doors,
        )
        # 5. Вызвать Core
        core_car_id = self.core_adapter.create_car(token, u_hash, core_u_id, car_data)
        # 6. Обновить car_core_id
        self.db.update_car_core_id(session, local_user_id, core_car_id)
        return core_car_id, registration_plate
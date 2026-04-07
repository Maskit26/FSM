"""
UserMapping — оркестратор. Координирует CoreAdapter и DatabaseLayer.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from .core_adapter import CoreAdapter
from db_layer import DatabaseLayer  
from .exceptions import CoreAdapterError

logger = logging.getLogger(__name__)

class UserMapping:
    def __init__(self, core_adapter: CoreAdapter, db: DatabaseLayer):
        self.core_adapter = core_adapter
        self.db = db

    def register_user(self, session: Session, user_data: Dict[str, Any]) -> Tuple[int, int, str]:
        logger.info("register_user: начало для phone=%s", user_data.get("phone"))

        # 1. Запрос в Core (прокси)
        core_u_id, performer_type = self.core_adapter.register_user_in_core(user_data)

        # 2. Определяем локальную роль для таблицы users
        role_name = user_data.get("role_name", "client")
        transport_type = user_data.get("transport_type")
        if role_name == "driver" and transport_type == "bike":
            local_role = "courier"
        else:
            local_role = role_name

        # 3. Синхронизация (создаст или обновит пользователя и mapping)
        local_user_id = self.get_or_create_by_core_id(
            session,
            core_u_id,
            auth_data={
                "user_name": user_data.get("name"),
                "login": user_data.get("phone") or user_data.get("email"),
                "core_role": self._map_role_to_core(role_name),
                "phone": user_data.get("phone"),
                "email": user_data.get("email"),
                "city": user_data.get("city"),
                "performer_type": "driver" if self._map_role_to_core(role_name) == 2 else None,
                "transport_type": transport_type,
                "capabilities": user_data.get("capabilities"),
            }
        )

        logger.info("register_user: успешно local=%s, core=%s", local_user_id, core_u_id)
        return local_user_id, core_u_id, performer_type

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

        if auth_data:
            user_name = auth_data.get("user_name", f"User_{core_u_id}")
            phone = auth_data.get("login", "")
            core_role = auth_data.get("core_role", 1)

            # Определяем локальную роль
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

            # Берём performer_type, transport_type, capabilities из auth_data
            performer_type = auth_data.get("performer_type")
            transport_type = auth_data.get("transport_type")
            capabilities = auth_data.get("capabilities")

            self.db.create_user_core_mapping(
                session=session,
                user_id=local_user_id,
                core_u_id=core_u_id,
                core_role=core_role,
                performer_type=performer_type,
                transport_type=transport_type,
                capabilities=capabilities,
            )

            logger.info("get_or_create_by_core_id: создан local=%s из auth_data", local_user_id)
            return local_user_id

        # Старая логика (если нет auth_data) – используем get_user_info
        info = self.core_adapter.get_user_info(core_u_id)
        core_role = info.get("core_role", 1)
        if core_role == 2:
            performer_type = "driver"
            transport_type = info.get("transport_type")
            if transport_type == "bike":
                local_role = "courier"
            else:
                local_role = "driver"
        elif core_role == 3:
            local_role = "operator"
            performer_type = None
        else:
            local_role = "client"
            performer_type = None

        local_user_id = self.db.create_user_record(
            session=session,
            phone=info.get("phone", ""),
            name=info.get("name", f"User_{core_u_id}"),
            role_name=local_role,
            city=info.get("city"),
        )

        self.db.create_user_core_mapping(
            session=session,
            user_id=local_user_id,
            core_u_id=core_u_id,
            core_role=core_role,
            performer_type=performer_type,
            transport_type=info.get("transport_type"),
            capabilities=info.get("capabilities"),
        )

        logger.info("get_or_create_by_core_id: создан local=%s", local_user_id)
        return local_user_id

    def _map_role_to_core(self, role_name: str) -> int:
        from .mappers.user import ROLE_TO_CORE
        return ROLE_TO_CORE.get(role_name, 1)

# ==================== Авторизация ===============================
    def authenticate_user(
        self,
        session: Session,
        login: str,
        password: str,
        type: str = "phone"
    ) -> Dict[str, Any]:
        """
        Авторизация: Core → Lazy Create Local → Return.
        """
        logger.info("authenticate_user: login=%s", login)

        # 1. Проверка в Core        
        auth_data = self.core_adapter.authenticate_user(login, password, type)
        logger.info("auth_data received: %s", auth_data)
        core_u_id = auth_data["core_u_id"]

        # 2. Ленивое создание локальной проекции (если ещё нет) с передачей auth_data
        local_user_id = self.get_or_create_by_core_id(session, core_u_id, auth_data)

        logger.info("authenticate_user: success local=%s, core=%s", local_user_id, core_u_id)

        return {
            "local_user_id": local_user_id,
            "core_user_id": core_u_id,
            "auth_hash": auth_data.get("auth_hash"),
            "role": auth_data.get("core_role"),
            "message": "Успешно"
        }

# ===================== Деаторизация ============================
    def logout_user(self, auth_hash: str) -> Dict[str, Any]:
        """Выход пользователя."""
        logger.info("logout_user")
        return self.core_adapter.logout_user(auth_hash)
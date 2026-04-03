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
        """
        Регистрация: Core → Локальная БД → Маппинг.
        Возвращает: (local_user_id, core_u_id, performer_type)
        """
        logger.info("register_user: начало для phone=%s", user_data.get("phone"))

        # 1. Запрос в Core
        core_u_id, performer_type = self.core_adapter.register_user_in_core(user_data)

        # 2. Создание локального пользователя (только после успеха Core)
        local_user_id = self.db.create_user_record(
            session=session,
            phone=user_data.get("phone", ""),
            name=user_data.get("name", f"User_{core_u_id}"),
            role_name=user_data.get("role_name", "client"),
            city=user_data.get("city"),
        )

        # 3. Создание связи
        self.db.create_user_core_mapping(
            session=session,
            user_id=local_user_id,
            core_u_id=core_u_id,
            core_role=self._map_role_to_core(user_data.get("role_name")),
            performer_type=performer_type,
            transport_type=user_data.get("transport_type"),
            capabilities=user_data.get("capabilities"),
        )

        logger.info("register_user: успешно local=%s, core=%s", local_user_id, core_u_id)
        return local_user_id, core_u_id, performer_type

    def get_or_create_by_core_id(self, session: Session, core_u_id: int) -> int:
        """Ленивое создание локальной проекции при первом обращении."""
        logger.debug("get_or_create_by_core_id: core_u_id=%s", core_u_id)

        # Проверка через db_layer (без прямого SQL)
        existing_id = self.db.get_local_user_id_by_core_u_id(session, core_u_id)
        if existing_id:
            return existing_id

        # Получаем данные из Core
        info = self.core_adapter.get_user_info_from_core(core_u_id)
        
        # Маппинг роли Core -> FSM
        core_role = info.get("core_role", 1)
        local_role = "client"
        if core_role == 2:
            local_role = info.get("performer_type", "driver")
        elif core_role == 3:
            local_role = "operator"

        # Создание в БД
        local_user_id = self.db.create_user_record(
            session=session,
            phone=info.get("phone", ""),
            name=info.get("name", f"User_{core_u_id}"),
            role=local_role,
            city=info.get("city"),
        )

        self.db.create_user_core_mapping(
            session=session,
            user_id=local_user_id,
            core_u_id=core_u_id,
            core_role=core_role,
            performer_type=info.get("performer_type", "client"),
            transport_type=info.get("transport_type"),
            capabilities=info.get("capabilities"),
        )

        logger.info("get_or_create_by_core_id: создан local=%s", local_user_id)
        return local_user_id

    def _map_role_to_core(self, role_name: str) -> int:
        from .mappers.user import ROLE_TO_CORE
        return ROLE_TO_CORE.get(role_name, 1)
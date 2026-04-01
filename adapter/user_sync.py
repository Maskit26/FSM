"""
Логика синхронизации пользователей с Core.
"""

from sqlalchemy.orm import Session
from typing import Tuple, Optional, List
import logging

from .core_client import CoreClient
from .user_mapping import UserMapping
from .mappers.user import to_core_register, from_core_register, get_performer_type_from_core
from .exceptions import CoreUnavailableError, CoreMappingError

logger = logging.getLogger(__name__)


class UserSync:
    def __init__(self, core_client: CoreClient, user_mapping: UserMapping):
        self.client = core_client
        self.mapping = user_mapping
    
    def sync_user_to_core(
        self,
        session: Session,
        user_id: int,
        user_data: dict
    ) -> Tuple[int, str]:
        """
        Синхронизировать пользователя с Core.
        
        Args:
            user_data: {
                "name": "...",
                "role_name": "driver" | "courier" | "client",
                "phone": "...",
                "email": "...",
                "performer_type": "driver" | "courier" (для исполнителей),
                "transport_type": "car" | "bike" | "foot" (опционально),
                "capabilities": ["delivery"] (опционально),
            }
        
        Returns:
            (core_u_id, performer_type)
        
        Raises:
            CoreUnavailableError: если Core не отвечает (нужно откатывать транзакцию!)
        """
        logger.info("sync_user_to_core: user_id=%s, role=%s", user_id, user_data.get("role_name"))
        
        # 1. Проверяем локальный mapping
        core_u_id = self.mapping.get_core_user_id(session, user_id)
        if core_u_id:
            performer_type = self.mapping.get_performer_type(session, user_id)
            logger.info("sync_user_to_core: mapping найден для user_id=%s", user_id)
            return core_u_id, performer_type or "client"
        
        # 2. Создаём в Core (может выбросить CoreUnavailableError!)
        logger.info("sync_user_to_core: создаём пользователя в Core для user_id=%s", user_id)
        core_response = self.client.post(
            "api/v1/register/",
            to_core_register(
                local_user_id=user_id,
                name=user_data.get("name", ""),
                phone=user_data.get("phone"),
                email=user_data.get("email"),
                role_name=user_data.get("role_name", "client"),
                performer_type=user_data.get("performer_type"),
                transport_type=user_data.get("transport_type"),
                capabilities=user_data.get("capabilities"),
            )
        )
        
        parsed = from_core_register(core_response)
        core_u_id = parsed.get("core_u_id")
        
        if not core_u_id:
            raise CoreMappingError("Core did not return u_id")
        
        # 3. Сохраняем mapping (в той же транзакции!)
        self.mapping.create_mapping(
            session=session,
            user_id=user_id,
            core_u_id=core_u_id,
            core_role=parsed.get("core_role", 2),
            performer_type=parsed.get("performer_type", "client"),
            transport_type=parsed.get("transport_type"),
            capabilities=parsed.get("capabilities"),
        )
        
        logger.info(
            "sync_user_to_core: user_id=%s synced as core_u_id=%s (performer_type=%s)",
            user_id, core_u_id, parsed.get("performer_type")
        )
        return core_u_id, parsed.get("performer_type", "client")
    
    def get_core_performer_type(self, session: Session, user_id: int) -> Optional[str]:
        """
        Получить performer_type из Core (с кэшем в mapping).
        """
        # Сначала пробуем локально
        performer_type = self.mapping.get_performer_type(session, user_id)
        if performer_type:
            return performer_type
        
        # Если нет — запрашиваем из Core
        core_u_id = self.mapping.get_core_user_id(session, user_id)
        if not core_u_id:
            return None
        
        core_user = self.client.get(f"api/v1/user/{core_u_id}")
        performer_type = get_performer_type_from_core(core_user)
        
        # Обновляем кэш
        if performer_type:
            self.mapping.update_performer_type(session, user_id, performer_type)
        
        return performer_type
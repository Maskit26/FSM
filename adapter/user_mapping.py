"""
Операции с таблицей core_user_mapping.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class UserMapping:
    def __init__(self):
        pass
    
    def get_core_user_id(self, session: Session, user_id: int) -> Optional[int]:
        """Получить core_u_id по local_user_id"""
        logger.debug("get_core_user_id: user_id=%s", user_id)
        try:
            row = session.execute(
                text("SELECT core_u_id FROM core_user_mapping WHERE local_user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_core_user_id: user_id=%s → %s", user_id, result)
            return result
        except Exception as e:
            logger.error("get_core_user_id failed: %s", e)
            raise
    
    def get_user_id(self, session: Session, core_u_id: int) -> Optional[int]:
        """Получить local_user_id по core_u_id (для вебхуков)"""
        logger.debug("get_user_id: core_u_id=%s", core_u_id)
        try:
            row = session.execute(
                text("SELECT local_user_id FROM core_user_mapping WHERE core_u_id = :core_u_id"),
                {"core_u_id": core_u_id}
            ).fetchone()
            result = row[0] if row else None
            logger.debug("get_user_id: core_u_id=%s → %s", core_u_id, result)
            return result
        except Exception as e:
            logger.error("get_user_id failed: %s", e)
            raise
    
    def get_performer_type(self, session: Session, user_id: int) -> Optional[str]:
        """Получить performer_type локально (без запроса к Core)"""
        try:
            row = session.execute(
                text("SELECT performer_type FROM core_user_mapping WHERE local_user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error("get_performer_type failed: %s", e)
            raise
    
    def create_mapping(
        self,
        session: Session,
        user_id: int,
        core_u_id: int,
        core_role: int,
        performer_type: str,
        transport_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> bool:
        """
        Создать соответствие (идемпотентно с UPSERT).
        Returns: True если создано, False если обновлено
        """
        logger.debug("create_mapping: user_id=%s, core_u_id=%s", user_id, core_u_id)
        try:
            import json
            session.execute(
                text("""
                    INSERT INTO core_user_mapping 
                        (local_user_id, core_u_id, core_role, performer_type, transport_type, 
                         capabilities, sync_status, registered_at, last_sync_at)
                    VALUES 
                        (:local_id, :core_id, :core_role, :performer_type, :transport_type, 
                         :capabilities, 'success', NOW(), NOW())
                    ON DUPLICATE KEY UPDATE 
                        core_u_id = VALUES(core_u_id),
                        core_role = VALUES(core_role),
                        performer_type = VALUES(performer_type),
                        transport_type = VALUES(transport_type),
                        capabilities = VALUES(capabilities),
                        last_sync_at = NOW(),
                        sync_status = 'success'
                """),
                {
                    "local_id": user_id,
                    "core_id": core_u_id,
                    "core_role": core_role,
                    "performer_type": performer_type,
                    "transport_type": transport_type,
                    "capabilities": json.dumps(capabilities) if capabilities else None,
                }
            )
            logger.info("create_mapping: user_id=%s ↔ core_u_id=%s", user_id, core_u_id)
            return True
        except Exception as e:
            logger.error("create_mapping failed: %s", e)
            raise
    
    def update_sync_status(self, session: Session, user_id: int, status: str, error_msg: Optional[str] = None):
        """Обновить статус синхронизации (для мониторинга)"""
        try:
            session.execute(
                text("""
                    UPDATE core_user_mapping 
                    SET sync_status = :status, 
                        error_message = :error,
                        last_sync_at = NOW()
                    WHERE local_user_id = :user_id
                """),
                {"status": status, "error": error_msg, "user_id": user_id}
            )
        except Exception as e:
            logger.error("update_sync_status failed: %s", e)
            raise

    def update_performer_type(self, session: Session, user_id: int, performer_type: str):
        """
        Обновить performer_type в кэше (для синхронизации с Core).
        """
        logger.debug("update_performer_type вызван: user_id=%s, performer_type=%s", user_id, performer_type)
        try:
            session.execute(
                text("""
                    UPDATE core_user_mapping 
                    SET performer_type = :performer_type, last_sync_at = NOW()
                    WHERE local_user_id = :user_id
                """),
                {"user_id": user_id, "performer_type": performer_type}
            )
            logger.debug("update_performer_type: user_id=%s обновлён", user_id)
        except Exception as e:
            logger.error("update_performer_type завершился с ошибкой: user_id=%s, error=%s", user_id, e)
            raise
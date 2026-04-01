"""
CoreAdapter — единая точка входа для интеграции с Core.
"""

from .core_client import CoreClient
from .user_mapping import UserMapping
from .user_sync import UserSync
from .exceptions import CoreUnavailableError, CoreMappingError, CoreValidationError, CoreAuthError, CoreAdapterError


class CoreAdapter:
    """Единая точка входа для интеграции с Core"""
    
    def __init__(self, core_url: str, core_api_key: str, core_timeout: int = 5):
        self.client = CoreClient(core_url, core_api_key, timeout=core_timeout)
        self.user_mapping = UserMapping()
        self.user_sync = UserSync(self.client, self.user_mapping)
    
    def sync_user_to_core(self, session, user_id: int, user_data: dict):
        """
        Синхронизировать пользователя с Core.
        ⚠️ Может выбросить CoreUnavailableError — нужно откатывать транзакцию!
        """
        return self.user_sync.sync_user_to_core(session, user_id, user_data)
    
    def get_core_user_id(self, session, user_id: int):
        """Получить core_u_id (без обращения к Core)"""
        return self.user_mapping.get_core_user_id(session, user_id)
    
    def get_user_id(self, session, core_u_id: int):
        """Получить local_user_id по core_u_id (для вебхуков)"""
        return self.user_mapping.get_user_id(session, core_u_id)
    
    def get_performer_type(self, session, user_id: int):
        """Получить performer_type локально"""
        return self.user_mapping.get_performer_type(session, user_id)
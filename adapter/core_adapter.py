"""
Фасад для Core API.
Только HTTP-запросы, без работы с БД.
"""
import logging
from typing import Dict, Any, Tuple
from .core_client import CoreClient
from .mappers.user import to_core_register, from_core_register, to_core_login, from_core_login
from .exceptions import CoreUnavailableError, CoreValidationError, CoreAdapterError

logger = logging.getLogger(__name__)

class CoreAdapter:
    def __init__(self, core_url: str, core_api_key: str, core_timeout: int = 5):
        self.client = CoreClient(core_url, core_api_key, timeout=core_timeout)

    def register_user_in_core(self, user_data: Dict[str, Any]) -> Tuple[int, str]:
        """Регистрация в Core. Возвращает (core_u_id, performer_type)."""
        logger.info("register_user_in_core: phone=%s, role=%s", 
                    user_data.get("phone"), user_data.get("role_name"))
        
        try:
            payload = to_core_register(user_data)
            
            logger.info("Core register payload (without password): %s", 
                    {k: v for k, v in payload.items() if k != "password"})
            logger.debug("Core API request: POST /api/v1/register/ with payload: %s", 
                        {k: v for k, v in payload.items() if k != "password"}) 
            
            response = self.client.post_form("/api/v1/register/", payload)
            
            parsed = from_core_register(response)
            logger.info("Core registration success: core_u_id=%s", parsed.get("core_u_id"))
            return parsed["core_u_id"], parsed["performer_type"]
            
        except (CoreUnavailableError, CoreValidationError):
            raise
        except Exception as e:
            logger.exception("register_user_in_core failed for user_data: %s", 
                            {k: v for k, v in user_data.items() if k != "password"})
            raise CoreAdapterError(f"Core error: {e}") from e

    def get_user_info(self, core_u_id: int) -> Dict[str, Any]:
        """Получение данных пользователя из Core."""
        logger.debug("get_user_info: core_u_id=%s", core_u_id)
        try:
            response = self.client.get(f"/api/v1/user/{core_u_id}")
            return from_core_register(response)
        except Exception as e:
            logger.error("get_user_info failed: %s", e)
            raise CoreAdapterError(f"Core fetch error: {e}") from e

# ========================== Авторизация ===================
    def authenticate_user(
        self, 
        login: str, 
        password: str, 
        type: str = "phone"
    ) -> Dict[str, Any]:
        """
        Авторизация пользователя через Core.
        Возвращает: {"core_u_id": int, "auth_hash": str, ...}
        """
        logger.info("authenticate_user: login=%s, type=%s", login, type)
        try:
            payload = to_core_login(login, password, type)
            masked_payload = {k: ('***' if k == 'password' else v) for k, v in payload.items()}
            logger.info("Core login payload: %s", masked_payload)
            response = self.client.post_form("/api/v1/auth/", payload)
            return from_core_login(response)
        except (CoreUnavailableError, CoreValidationError):
            raise
        except Exception as e:
            logger.exception("authenticate_user failed")
            raise CoreAdapterError(f"Auth failed: {e}") from e
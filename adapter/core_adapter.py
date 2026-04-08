"""
Фасад для Core API.
Только HTTP-запросы, без работы с БД.
"""
import logging
import json
from typing import Dict, Any, Tuple, Optional
from .core_client import CoreClient
from .mappers.user import to_core_register, from_core_register, to_core_login, from_core_login
from .exceptions import CoreUnavailableError, CoreValidationError, CoreAuthError, CoreAdapterError

logger = logging.getLogger(__name__)

class CoreAdapter:
    def __init__(self, core_url: str, core_api_key: str, core_timeout: int = 5):
        self.client = CoreClient(core_url, core_api_key, timeout=core_timeout)
        self.token = None
        self.u_hash = None

    def register_user_in_core(self, user_data: Dict[str, Any]) -> Tuple[int, str, Optional[str], Optional[str]]:
        """Регистрация в Core. Возвращает (core_u_id, performer_type, token, u_hash)."""
        logger.info("register_user_in_core: phone=%s, role=%s", 
                    user_data.get("phone"), user_data.get("role_name"))
        try:
            payload = to_core_register(user_data)
            logger.info("Core register payload (without password): %s", 
                        {k: v for k, v in payload.items() if k != "password"})
            response = self.client.post_form("/api/v1/register/", payload)
            parsed = from_core_register(response)
            logger.info("Core registration success: core_u_id=%s, transport_type=%s, token=%s", 
                        parsed.get("core_u_id"), parsed.get("transport_type"), 
                        "yes" if parsed.get("token") else "no")
            return (
                parsed["core_u_id"],
                parsed["performer_type"],
                parsed.get("token"),
                parsed.get("u_hash"),
            )
        except (CoreUnavailableError, CoreValidationError):
            raise
        except Exception as e:
            logger.exception("register_user_in_core failed")
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

    def get_token(self, auth_hash: str) -> Dict[str, Any]:
        return self.client.get_token(auth_hash)

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

# ========================= Деавторизация =========================
    def logout_user(self, auth_hash: str) -> Dict[str, Any]:
        """Деавторизация пользователя в Core."""
        logger.info("logout_user: auth_hash=%s", auth_hash[:10] + "...")
        try:
            response = self.client.logout(auth_hash)
            return response
        except Exception as e:
            logger.error("logout_user failed: %s", e)
            raise CoreAdapterError(f"Logout failed: {e}") from e

# ======================== CORE ORDER ==============================
    def create_drive_order(self, order_data: Dict[str, Any], token: str, u_hash: str) -> Dict[str, Any]:
        """Создать поездку в Core от имени пользователя."""
        logger.info("create_drive_order: using token=%s..., u_hash=%s...",
                    token[:10] if token else "None", u_hash[:10] if u_hash else "None")
        try:
            logger.info(f"Order data for Core: {json.dumps(order_data, ensure_ascii=False)}")
            payload = {
                "data": json.dumps(order_data, ensure_ascii=False),
                "token": token,
                "u_hash": u_hash,
            }
            response = self.client.post_form_without_auth("/api/v1/drive", payload)
            if response.get("status") != "success":
                error_msg = response.get("message", "Unknown error")
                logger.error("Core drive order error: %s", error_msg)
                raise CoreValidationError(f"Core returned error: {error_msg}")
            return response
        except CoreUnavailableError as e:
            logger.error("Core unavailable while creating drive order: %s", e)
            raise
        except CoreValidationError as e:
            logger.error("Core validation error: %s", e)
            raise
        except CoreAuthError as e:
            logger.error("Core auth error (token may be expired): %s", e)
            raise
        except Exception as e:
            logger.exception("Unexpected error in create_drive_order")
            raise CoreAdapterError(f"Create drive order failed: {e}") from e

# ====================== Отмена заказа =========================
    def cancel_drive_order(self, b_id: int, token: str, u_hash: str, reason: str = None, cancel_states: str = None) -> Dict[str, Any]:
        """
        Отмена заказа в Core.
        """
        logger.info("cancel_drive_order: b_id=%s, token=%s..., u_hash=%s...", b_id, token[:10] if token else "None", u_hash[:10] if u_hash else "None")
        try:
            payload = {
                "action": "set_cancel_state",
                "token": token,
                "u_hash": u_hash,
            }
            if reason:
                payload["reason"] = reason
                logger.debug("cancel_drive_order: reason=%s", reason)
            if cancel_states:
                payload["cancel_states"] = cancel_states
                logger.debug("cancel_drive_order: cancel_states=%s", cancel_states)

            response = self.client.post_form_without_auth(f"/api/v1/drive/get/{b_id}", payload)
            if response.get("status") != "success":
                error_msg = response.get("message", "Unknown error")
                logger.error("Core cancel order error: %s", error_msg)
                raise CoreValidationError(f"Core returned error: {error_msg}")
            logger.info("cancel_drive_order: success for b_id=%s", b_id)
            return response
        except CoreUnavailableError as e:
            logger.error("Core unavailable while canceling drive order: %s", e)
            raise
        except CoreValidationError as e:
            logger.error("Core validation error during cancel: %s", e)
            raise
        except CoreAuthError as e:
            logger.error("Core auth error (token may be expired): %s", e)
            raise
        except Exception as e:
            logger.exception("Unexpected error in cancel_drive_order")
            raise CoreAdapterError(f"Cancel drive order failed: {e}") from e
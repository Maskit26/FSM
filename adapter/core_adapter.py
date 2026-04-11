"""
Фасад для Core API.
Только HTTP-запросы, без работы с БД.
"""
import logging
import json
from typing import Dict, Any, Tuple, Optional, List
from .core_client import CoreClient
from .mappers.user import to_core_register, from_core_register, to_core_login, from_core_login
from .exceptions import CoreUnavailableError, CoreValidationError, CoreAuthError, CoreAdapterError

logger = logging.getLogger(__name__)

class CoreAdapter:
    def __init__(self, core_url: str, core_api_key: str, core_timeout: int = 5):
        self.client = CoreClient(core_url, core_api_key, timeout=core_timeout)
        self.token = None
        self.u_hash = None

    def register_user_in_core(self, user_data: Dict[str, Any]) -> Tuple[int, Optional[str], Optional[str]]:
        logger.info("register_user_in_core: phone=%s, role=%s", 
                    user_data.get("phone"), user_data.get("role_name"))
        try:
            payload = to_core_register(user_data)
            logger.debug("Core register payload (without password): %s", 
                        {k: v for k, v in payload.items() if k != "password"})
            response = self.client.post_form("/api/v1/register/", payload)
            parsed = from_core_register(response)
            core_u_id = parsed["core_u_id"]
            token = parsed.get("token")
            u_hash = parsed.get("u_hash")
            logger.info("Core registration success: core_u_id=%s, token=%s", 
                        core_u_id, "yes" if token else "no")
            return core_u_id, token, u_hash
        except CoreValidationError as e:
            logger.error("Ошибка валидации Core при регистрации: %s", e)
            raise
        except CoreUnavailableError as e:
            logger.error("Core недоступен при регистрации: %s", e)
            raise
        except Exception as e:
            logger.exception("Неожиданная ошибка при регистрации в Core")
            raise CoreAdapterError(f"Core registration error: {e}")

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

    def get_user_cars(self, core_u_id: int, token: str, u_hash: str) -> List[int]:
        logger.info("get_user_cars: core_u_id=%s", core_u_id)
        endpoint = f"/api/v1/user/{core_u_id}/car/"
        try:
            response = self.client.post_form_with_token(endpoint, token, u_hash)
            if response.get("status") != "success":
                logger.warning("Failed to get cars: %s", response.get("message"))
                return []
            data = response.get("data", {})
            cars = data.get("car", {})
            return [int(cid) for cid in cars.keys()] if cars else []
        except Exception as e:
            logger.error("get_user_cars failed: %s", e)
            return []

# ========================= Деавторизация =========================
    def logout_user_with_token(self, token: str, u_hash: str) -> Dict[str, Any]:
        logger.info("logout_user_with_token")
        return self.client.logout_with_token(token, u_hash)

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

# ===================== Назначение курьера ========================
    def perform_drive_order(
        self,
        core_order_id: int,
        performer_core_u_id: int,
        token: str,
        u_hash: str,
    ) -> Dict[str, Any]:
        """
        Вызов set_performer в Core: утвердить исполнителя (курьера/водителя).
        """
        logger.info("perform_drive_order: order=%s, performer=%s", core_order_id, performer_core_u_id)
        endpoint = f"/api/v1/drive/get/{core_order_id}"
        params = {
            "action": "set_performer",
            "u_id": performer_core_u_id,
            "performer": 1,
            "token": token,
            "u_hash": u_hash,
        }
        try:
            response = self.client.post_form_with_params(endpoint, params)
            if response.get("status") != "success":
                logger.error("Core set_performer error: %s", response)
                raise CoreValidationError(f"Core set_performer failed: {response.get('message')}")
            return response
        except CoreAdapterError:
            raise
        except Exception as e:
            logger.exception("perform_drive_order failed")
            raise CoreAdapterError(f"perform_drive_order failed: {e}")

    def get_drive_order(self, b_id: int, token: str, u_hash: str) -> Dict[str, Any]:
        """Получить данные заказа из Core (GET /api/v1/drive/get/{b_id})."""
        endpoint = f"/api/v1/drive/get/{b_id}"
        params = {"token": token, "u_hash": u_hash}
        try:
            response = self.client.get_with_params(endpoint, params)
            return response
        except CoreAdapterError:
            raise
        except Exception as e:
            logger.exception("get_drive_order failed")
            raise CoreAdapterError(f"get_drive_order failed: {e}")

    
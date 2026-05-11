# core_client.py
import requests
import logging
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import CoreUnavailableError, CoreAuthError, CoreValidationError

logger = logging.getLogger(__name__)

class CoreClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/") + "/"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10),
        retry=retry_if_exception_type(CoreUnavailableError)
    )
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST запрос с JSON (стандарт для большинства эндпоинтов)."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {**self.headers, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: raise CoreAuthError(...)
            if e.response.status_code == 400: raise CoreValidationError(...)
            if e.response.status_code >= 500: raise CoreUnavailableError(...)
            raise
        except Exception as e:
            logger.error("Core JSON POST error: %s", e)
            raise CoreUnavailableError(str(e)) from e
    
    def post_form(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST запрос с application/x-www-form-urlencoded (для регистрации в Core)."""
        logger.debug("CoreClient.post_form: endpoint=%s, data=%s", endpoint, {k: v for k, v in data.items() if k != "password"})
        
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {**self.headers, "Content-Type": "application/x-www-form-urlencoded"}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError(f"Core auth error: {endpoint}") from e
            if e.response.status_code == 400:
                raise CoreValidationError(f"Core validation error: {e.response.text}") from e
            if e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core 5xx: {e.response.status_code}") from e
            raise
        except Exception as e:
            logger.error("Core FORM POST error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10),
        retry=retry_if_exception_type(CoreUnavailableError)
    )
    def get(self, endpoint: str) -> Dict[str, Any]:
        """GET запрос."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {**self.headers}
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError("Unauthorized")
            if e.response.status_code == 400:
                raise CoreValidationError("Bad request")
            if e.response.status_code >= 500:
                raise CoreUnavailableError("Core server error")
            raise
        except Exception as e:
            logger.error("Core GET error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    def logout_with_token(self, token: str, u_hash: str) -> Dict[str, Any]:
        url = f"{self.base_url}api/v1/logout/"
        params = {"token": token, "u_hash": u_hash}
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            logger.info("Core logout response: status=%s, body=%s", resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("Core logout HTTP error: %s", e.response.text)
            raise CoreAuthError("Logout failed")
        except Exception as e:
            logger.error("Core logout error: %s", e)
            raise CoreUnavailableError(str(e))

    def get_token(self, auth_hash: str) -> Dict[str, Any]:
        url = f"{self.base_url}api/v1/token/"
        data = {"auth_hash": auth_hash}
        try:
            resp = requests.post(url, data=data, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError("Invalid or expired auth_hash")
            if e.response.status_code >= 500:
                raise CoreUnavailableError("Core server error")
            raise
        except Exception as e:
            logger.error("Core get_token error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    def get_cache_data(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Загружает и парсит публичный кэш Core (data_postamat.json).
        Если key указан, возвращает только указанный раздел словаря (например, 'cities').
        Если key не указан, возвращает весь распарсенный словарь.
        """
        try:
            resp = requests.get(
                "https://ibronevik.ru/taxi/cache/data_postamat.json",
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            # data может быть словарём, где сразу лежат нужные разделы
            if isinstance(data, dict):
                if key:
                    # Ищем key на верхнем уровне или внутри data.data
                    section = data.get(key) or data.get("data", {}).get(key)
                    if isinstance(section, dict):
                        logger.info("Загружен раздел '%s' (%d записей)", key, len(section))
                        return section
                    else:
                        logger.warning("Раздел '%s' не найден или имеет неверный формат", key)
                        return {}
                else:
                    return data
            else:
                logger.error("Неожиданный формат data_postamat.json: %s", type(data))
                return {}
        except Exception as e:
            logger.error("Не удалось загрузить data_postamat.json: %s", e)
            return {}

# ===================== CORE ORDER ======================
    
    def post_form_without_auth(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST с form-urlencoded, без заголовка Authorization."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            logger.info(f"Core response status: {resp.status_code}, body: {resp.text}") 
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            error_body = e.response.text if e.response else 'No response body'
            logger.error(f"Core HTTP {e.response.status_code}: {error_body}")
            if e.response.status_code == 401:
                raise CoreAuthError(f"Authentication failed for {endpoint}")
            if e.response.status_code == 400:
                raise CoreValidationError(f"Bad request: {error_body}")
            if e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core 5xx: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error("Core POST form without auth error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    def get_without_auth(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET запрос без заголовка Authorization, параметры в URL."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            logger.info("Core GET without auth response: status=%s, body=%s", resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error("Core GET without auth HTTP error: %s", e.response.text)
            raise CoreAuthError("Request failed")
        except Exception as e:
            logger.error("Core GET without auth error: %s", e)
            raise CoreUnavailableError(str(e))

    def post_form_with_params(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """POST с application/x-www-form-urlencoded, параметры в теле запроса."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {**self.headers, "Content-Type": "application/x-www-form-urlencoded"}
        try:
            resp = requests.post(url, data=params, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError(f"Core auth error: {endpoint}")
            if e.response.status_code == 400:
                raise CoreValidationError(f"Core validation error: {e.response.text}")
            if e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core 5xx: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error("Core POST form with params error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    def get_with_params(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET запрос с параметрами в URL."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {**self.headers}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: raise CoreAuthError(...)
            if e.response.status_code == 400: raise CoreValidationError(...)
            if e.response.status_code >= 500: raise CoreUnavailableError(...)
            raise
        except Exception as e:
            logger.error("Core GET with params error: %s", e)
            raise CoreUnavailableError(str(e)) from e

    def get_with_token(self, endpoint: str, token: str, u_hash: str) -> Dict[str, Any]:
        """GET запрос с авторизацией через Bearer token и передачей u_hash как параметр."""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {"u_hash": u_hash}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError("Unauthorized")
            raise
        except Exception as e:
            logger.error("GET with token error: %s", e)
            raise CoreUnavailableError(str(e))

    def post_form_with_token(self, endpoint: str, token: str, u_hash: str) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        data = {"token": token, "u_hash": u_hash}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            logger.info("POST with token response: status=%s, body=%s", resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("POST with token error: %s", e)
            raise CoreUnavailableError(str(e))

# =================== Создание авто =====================
    def create_car(
        self,
        token: str,
        u_hash: str,
        core_u_id: int,
        car_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.debug("CoreClient.create_car: core_u_id=%s, token=%s..., u_hash=%s...",
                    core_u_id, token[:10] if token else "None", u_hash[:10] if u_hash else "None")
        url = f"{self.base_url}api/v1/user/{core_u_id}/car/"
        payload = {
            "token": token,
            "u_hash": u_hash,
            "data": json.dumps(car_data, ensure_ascii=False),
        }
        try:
            resp = requests.post(url, data=payload, timeout=self.timeout)
            resp.raise_for_status()
            result = resp.json()
            logger.info("Core create_car raw response: %s", json.dumps(result, indent=2))
            if result.get("status") != "success":
                error_msg = result.get("message", "Unknown error")
                logger.error("Core create_car error: %s", error_msg)
                raise CoreValidationError(f"Core create_car failed: {error_msg}")
            logger.info("Core create_car success: core_car_id=%s",
                        result.get("data", {}).get("cteated_car", {}).get("c_id"))
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError("Invalid or expired token")
            if e.response.status_code >= 500:
                raise CoreUnavailableError("Core server error")
            raise
        except Exception as e:
            logger.error("Core create_car error: %s", e)
            raise CoreUnavailableError(str(e)) from e

# =============== верификация пользователя =============
    def update_user(
        self,
        core_u_id: int,
        token: str,
        u_hash: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """POST /api/v1/user/{u_id}/ с data=JSON.stringify(obj)."""
        logger.debug("CoreClient.update_user: core_u_id=%s, payload_keys=%s", core_u_id, list(payload.keys()))
        
        endpoint = f"api/v1/user/{core_u_id}/"
        form_payload = {
            "token": token,
            "u_hash": u_hash,
            "data": json.dumps(payload, ensure_ascii=False),
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}{endpoint}",
                data=form_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout
            )
            resp.raise_for_status()
            result = resp.json()
            logger.info("Core update_user response: %s", json.dumps(result, indent=2))
            return result
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise CoreAuthError("Invalid or expired token")
            if e.response is not None and e.response.status_code == 400:
                raise CoreValidationError(f"Bad request: {e.response.text}")
            if e.response is not None and e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core server error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error("Core update_user error: %s", e)
            raise CoreUnavailableError(str(e)) from e
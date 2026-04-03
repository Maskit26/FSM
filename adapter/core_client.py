# core_client.py
import requests
import logging
from typing import Dict, Any
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10),
        retry=retry_if_exception_type(CoreUnavailableError)
    )
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
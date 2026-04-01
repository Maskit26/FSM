"""
HTTP клиент для взаимодействия с Core API.
"""

import requests
import logging
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .exceptions import CoreUnavailableError, CoreAuthError, CoreValidationError

logger = logging.getLogger(__name__)


class CoreClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/") + "/"
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self.timeout = timeout
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=2, max=10),
        retry=retry_if_exception_type(CoreUnavailableError)
    )
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST запрос к Core API с retry.
        """
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        try:
            resp = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        
        except requests.exceptions.Timeout:
            logger.error("Core timeout: POST %s", endpoint)
            raise CoreUnavailableError(f"Core timeout: {endpoint}")
        
        except requests.exceptions.ConnectionError:
            logger.error("Core connection error: POST %s", endpoint)
            raise CoreUnavailableError(f"Core connection error: {endpoint}")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError(f"Core auth error: {endpoint}")
            if e.response.status_code == 400:
                raise CoreValidationError(f"Core validation error: {e.response.text}")
            if e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core 5xx: {e.response.status_code}")
            raise
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """
        GET запрос к Core API.
        """
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        
        except requests.exceptions.Timeout:
            logger.error("Core timeout: GET %s", endpoint)
            raise CoreUnavailableError(f"Core timeout: {endpoint}")
        
        except requests.exceptions.ConnectionError:
            logger.error("Core connection error: GET %s", endpoint)
            raise CoreUnavailableError(f"Core connection error: {endpoint}")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise CoreAuthError(f"Core auth error: {endpoint}")
            if e.response.status_code >= 500:
                raise CoreUnavailableError(f"Core 5xx: {e.response.status_code}")
            raise
"""HTTP client for FSM Platform Public API (multi-tenant)."""

from __future__ import annotations

from typing import Any

import requests


class ApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        domain_admin_token: str,
        platform_admin_token: str,
        actor_bearer_token: str = "",
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.domain_admin_token = domain_admin_token.strip()
        self.platform_admin_token = platform_admin_token.strip()
        self.actor_bearer_token = actor_bearer_token.strip()
        self._session = requests.Session()
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )
    def health(self) -> tuple[int, dict[str, Any]]:
        r = self._session.get(
            f"{self.base_url}/v1/health",
            headers={"X-Admin-Token": self.platform_admin_token},
            timeout=self.timeout,
        )
        return r.status_code, _json_or_text(r)

    def _domain_headers(self) -> dict[str, str]:
        headers = {"X-Admin-Token": self.domain_admin_token}
        if self.actor_bearer_token:
            headers["Authorization"] = f"Bearer {self.actor_bearer_token}"
        return headers

    def invoke(
        self,
        service_id: str,
        operation: str,
        params: dict[str, Any],
        actor: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}/v1/{service_id}/invoke"
        r = self._session.post(
            url,
            json={"operation": operation, "params": params, "actor": actor},
            headers=self._domain_headers(),
            timeout=self.timeout,
        )
        return r.status_code, _json_or_text(r)

    def get_instance(
        self, service_id: str, instance_id: int
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}/v1/{service_id}/fsm/instances/{instance_id}"
        r = self._session.get(
            url, headers=self._domain_headers(), timeout=self.timeout
        )
        return r.status_code, _json_or_text(r)


def _json_or_text(r: requests.Response) -> dict[str, Any]:
    try:
        data = r.json()
        if isinstance(data, dict):
            return data
        return {"_value": data}
    except ValueError:
        return {"_raw": r.text}

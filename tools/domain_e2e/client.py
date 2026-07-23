"""HTTP client for FSM Platform Public API."""

from __future__ import annotations

from typing import Any

import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )

    def health(self) -> tuple[int, dict[str, Any]]:
        r = self._session.get(f"{self.base_url}/v1/health", timeout=self.timeout)
        return r.status_code, _json_or_text(r)

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
            timeout=self.timeout,
        )
        return r.status_code, _json_or_text(r)

    def get_instance(
        self, service_id: str, instance_id: int
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}/v1/{service_id}/fsm/instances/{instance_id}"
        r = self._session.get(url, timeout=self.timeout)
        return r.status_code, _json_or_text(r)


def _json_or_text(r: requests.Response) -> dict[str, Any]:
    try:
        data = r.json()
        if isinstance(data, dict):
            return data
        return {"_value": data}
    except ValueError:
        return {"_raw": r.text}

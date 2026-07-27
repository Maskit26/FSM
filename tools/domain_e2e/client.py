"""HTTP client for FSM Platform Public API."""

from __future__ import annotations

from typing import Any, Optional

import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )
        self._token_by_actor: dict[str, str] = {}
        self._auth_mode: Optional[str] = None  # None | "on" | "off"

    def health(self) -> tuple[int, dict[str, Any]]:
        r = self._session.get(f"{self.base_url}/v1/health", timeout=self.timeout)
        return r.status_code, _json_or_text(r)

    def _authorization_for_actor(self, actor: dict[str, Any]) -> dict[str, str]:
        """
        Если PLATFORM_AUTH включён и DEV_TOKENS=1 — Bearer из GET /v1/auth/token.
        Если auth выключен — пустой dict (actor остаётся в body).
        """
        actor_type = str((actor or {}).get("actor_type") or "user").strip() or "user"
        actor_id = str((actor or {}).get("actor_id") or "").strip()
        if not actor_id:
            return {}

        cache_key = f"{actor_type}:{actor_id}"
        if cache_key in self._token_by_actor:
            return {"Authorization": self._token_by_actor[cache_key]}

        if self._auth_mode == "off":
            return {}

        r = self._session.get(
            f"{self.base_url}/v1/auth/token",
            params={"actor_id": actor_id, "actor_type": actor_type},
            timeout=self.timeout,
        )
        if r.status_code == 200:
            data = _json_or_text(r)
            auth = str(data.get("authorization") or "").strip()
            if not auth:
                return {}
            self._auth_mode = "on"
            self._token_by_actor[cache_key] = auth
            return {"Authorization": auth}

        # 400 PLATFORM_AUTH_SECRET not set; 403 DEV_TOKENS disabled
        self._auth_mode = "off"
        return {}

    def invoke(
        self,
        service_id: str,
        operation: str,
        params: dict[str, Any],
        actor: dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        url = f"{self.base_url}/v1/{service_id}/invoke"
        headers = self._authorization_for_actor(actor)
        r = self._session.post(
            url,
            json={"operation": operation, "params": params, "actor": actor},
            headers=headers or None,
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

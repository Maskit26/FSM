"""
HTTP-клиент Domain Contract API (platform → domain service).

Подпись: X-Service-Id, X-Contract-Timestamp, X-Contract-Signature (см. docs/domain-contract-api-v1.md).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urljoin

import requests

from fsm_platform.core.domain_errors import DomainError
from fsm_platform.host.retry_policy import backoff_seconds

logger = logging.getLogger(__name__)

CONTRACT_PREFIX = "/contract/v1"

_DEFAULT_GUARD_EFFECT_TIMEOUT = float(
    os.environ.get("CONTRACT_TIMEOUT_GUARD_EFFECT", "5")
)
_DEFAULT_COMMAND_QUERY_TIMEOUT = float(
    os.environ.get("CONTRACT_TIMEOUT_COMMAND", "10")
)
_DEFAULT_CATALOG_TIMEOUT = float(os.environ.get("CONTRACT_TIMEOUT_CATALOG", "5"))
_MAX_ATTEMPTS = max(1, int(os.environ.get("CONTRACT_MAX_ATTEMPTS", "3")))


class ContractError(Exception):
    """
    Ошибка вызова Contract API.
    transient=True → код CONTRACT_UNAVAILABLE (retry в FSM worker).
    """

    def __init__(
        self,
        code: str,
        message: str = "",
        *,
        status_code: Optional[int] = None,
        transient: bool = False,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self.transient = bool(transient)
        self.message = message or code
        prefix = "CONTRACT_UNAVAILABLE" if self.transient else "CONTRACT_ERROR"
        super().__init__(f"{prefix}:{code}:{self.message}")


@dataclass(frozen=True)
class ContractConfig:
    service_id: str
    base_url: str
    secret: str


def _service_env_suffix(service_id: str) -> str:
    return service_id.upper().replace("-", "_")


def resolve_contract_config(service_id: str) -> ContractConfig:
    """
    Конфиг remote-домена для service_id.
    base_url: CONTRACT_BASE_URL_{SVC} → CONTRACT_BASE_URL
    secret: CONTRACT_SECRET_{SVC} → CONTRACT_SHARED_SECRET
            → domain_secrets key contract_shared_secret (Fernet)
    """
    sid = str(service_id or "").strip()
    if not sid:
        raise ContractError("SERVICE_ID_REQUIRED", "service_id is empty")

    suf = _service_env_suffix(sid)
    base = (
        os.environ.get(f"CONTRACT_BASE_URL_{suf}", "").strip()
        or os.environ.get("CONTRACT_BASE_URL", "").strip()
    ).rstrip("/")
    if not base:
        raise ContractError(
            "CONTRACT_BASE_URL_MISSING",
            f"set CONTRACT_BASE_URL or CONTRACT_BASE_URL_{suf}",
        )

    secret = (
        os.environ.get(f"CONTRACT_SECRET_{suf}", "").strip()
        or os.environ.get("CONTRACT_SHARED_SECRET", "").strip()
    )
    if not secret:
        try:
            from fsm_platform.host.runtime_context import service_scope
            from fsm_platform.host.secrets import get_domain_secret

            with service_scope(sid):
                secret = (get_domain_secret("contract_shared_secret") or "").strip()
        except Exception:
            secret = ""
    if not secret:
        raise ContractError(
            "CONTRACT_SECRET_MISSING",
            f"set CONTRACT_SHARED_SECRET or CONTRACT_SECRET_{suf} "
            f"or domain_secrets.contract_shared_secret",
        )

    return ContractConfig(service_id=sid, base_url=base, secret=secret)


def sign_contract_request(
    secret: str,
    *,
    method: str,
    path: str,
    body: bytes,
    timestamp: str,
) -> str:
    """hex(HMAC-SHA256(secret, METHOD\\nPATH\\nSHA256(body)\\nTIMESTAMP))."""
    path_only = path.split("?")[0]
    if not path_only.startswith("/"):
        path_only = "/" + path_only
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{method.upper()}\n{path_only}\n{body_hash}\n{timestamp}"
    return hmac.new(
        secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def _encode_json_body(payload: Optional[dict[str, Any]]) -> bytes:
    if not payload:
        return b""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _parse_error_body(text: str) -> tuple[str, str]:
    if not text.strip():
        return "CONTRACT_HTTP_ERROR", text[:300]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return "CONTRACT_HTTP_ERROR", text[:300]
    if isinstance(data, dict):
        code = str(data.get("error_code") or data.get("code") or "CONTRACT_HTTP_ERROR")
        msg = str(data.get("message") or data.get("detail") or text[:300])
        return code, msg
    return "CONTRACT_HTTP_ERROR", text[:300]


def _classify_http_error(status_code: int, text: str) -> ContractError:
    code, msg = _parse_error_body(text)
    if status_code == 409:
        return ContractError(code, msg, status_code=status_code, transient=False)
    if status_code in (401, 403):
        return ContractError(
            "CONTRACT_AUTH_FAILED",
            msg,
            status_code=status_code,
            transient=False,
        )
    if status_code == 404:
        return ContractError(
            code or "CONTRACT_NOT_FOUND",
            msg,
            status_code=status_code,
            transient=False,
        )
    if status_code == 503 or status_code >= 500:
        return ContractError(
            "HTTP_" + str(status_code),
            msg,
            status_code=status_code,
            transient=True,
        )
    return ContractError(
        code,
        msg,
        status_code=status_code,
        transient=False,
    )


_client_cache: dict[str, ContractClient] = {}


class ContractClient:
    """Sync HTTP client for one remote domain (service_id)."""

    def __init__(self, config: ContractConfig) -> None:
        self._config = config

    @property
    def service_id(self) -> str:
        return self._config.service_id

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def catalog(self) -> dict[str, Any]:
        data = self._request("GET", f"{CONTRACT_PREFIX}/catalog", timeout=_DEFAULT_CATALOG_TIMEOUT)
        if not isinstance(data, dict):
            raise ContractError("CATALOG_INVALID", "expected JSON object")
        return data

    def call_context(
        self,
        name: str,
        *,
        runtime_ctx: dict[str, Any],
        instance: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"runtime_ctx": runtime_ctx, "instance": instance}
        data = self._request(
            "POST",
            f"{CONTRACT_PREFIX}/context/{name}",
            json_body=body,
            timeout=_DEFAULT_GUARD_EFFECT_TIMEOUT,
        )
        if not isinstance(data, dict):
            raise ContractError("CONTEXT_INVALID", f"{name}: expected object")
        return data

    def call_guard(
        self,
        name: str,
        *,
        context: dict[str, Any],
        guard_params: dict[str, Any],
        instance: dict[str, Any],
    ) -> dict[str, Any]:
        body = {
            "context": context,
            "guard_params": guard_params,
            "instance": instance,
        }
        data = self._request(
            "POST",
            f"{CONTRACT_PREFIX}/guards/{name}",
            json_body=body,
            timeout=_DEFAULT_GUARD_EFFECT_TIMEOUT,
        )
        if not isinstance(data, dict):
            raise ContractError("GUARD_INVALID", f"{name}: expected object")
        return data

    def call_effect(
        self,
        name: str,
        *,
        context: dict[str, Any],
        effect_params: dict[str, Any],
        instance: dict[str, Any],
    ) -> dict[str, Any]:
        body = {
            "context": context,
            "effect_params": effect_params,
            "instance": instance,
        }
        data = self._request(
            "POST",
            f"{CONTRACT_PREFIX}/effects/{name}",
            json_body=body,
            timeout=_DEFAULT_GUARD_EFFECT_TIMEOUT,
        )
        if not isinstance(data, dict):
            raise ContractError("EFFECT_INVALID", f"{name}: expected object")
        return data

    def call_command(
        self,
        operation: str,
        *,
        params: dict[str, Any],
        actor: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"params": params, "actor": actor}
        data = self._request(
            "POST",
            f"{CONTRACT_PREFIX}/commands/{operation}",
            json_body=body,
            timeout=_DEFAULT_COMMAND_QUERY_TIMEOUT,
        )
        if not isinstance(data, dict):
            raise ContractError("COMMAND_INVALID", f"{operation}: expected object")
        return data

    def call_query(
        self,
        operation: str,
        *,
        params: dict[str, Any],
        actor: dict[str, Any],
    ) -> dict[str, Any]:
        body = {"params": params, "actor": actor}
        data = self._request(
            "POST",
            f"{CONTRACT_PREFIX}/queries/{operation}",
            json_body=body,
            timeout=_DEFAULT_COMMAND_QUERY_TIMEOUT,
        )
        if not isinstance(data, dict):
            raise ContractError("QUERY_INVALID", f"{operation}: expected object")
        return data

    def call_on_failed(
        self,
        process_name: str,
        *,
        instance: dict[str, Any],
        last_error: str,
    ) -> None:
        body = {"instance": instance, "last_error": last_error}
        self._request(
            "POST",
            f"{CONTRACT_PREFIX}/processes/{process_name}/on-failed",
            json_body=body,
            timeout=_DEFAULT_COMMAND_QUERY_TIMEOUT,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict[str, Any]] = None,
        timeout: float,
    ) -> Any:
        method_u = method.upper()
        path_only = path if path.startswith("/") else f"/{path}"
        url = urljoin(self._config.base_url.rstrip("/") + "/", path.lstrip("/"))
        raw = _encode_json_body(json_body if method_u != "GET" else None)

        last_err: Optional[ContractError] = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            ts = str(int(time.time()))
            sig = sign_contract_request(
                self._config.secret,
                method=method_u,
                path=path_only,
                body=raw,
                timestamp=ts,
            )
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "X-Service-Id": self._config.service_id,
                "X-Contract-Timestamp": ts,
                "X-Contract-Signature": sig,
                "User-Agent": "fsm-platform-contract/1",
            }
            try:
                resp = requests.request(
                    method_u,
                    url,
                    data=raw if raw else None,
                    headers=headers,
                    timeout=timeout,
                )
            except requests.Timeout as exc:
                last_err = ContractError("TIMEOUT", str(exc), transient=True)
                logger.warning(
                    "contract timeout attempt=%s/%s %s %s",
                    attempt,
                    _MAX_ATTEMPTS,
                    method_u,
                    path_only,
                )
            except requests.RequestException as exc:
                last_err = ContractError("CONNECTION", str(exc), transient=True)
                logger.warning(
                    "contract connection attempt=%s/%s %s %s err=%s",
                    attempt,
                    _MAX_ATTEMPTS,
                    method_u,
                    path_only,
                    exc,
                )
            else:
                text = resp.text or ""
                if resp.status_code == 409:
                    code, msg = _parse_error_body(text)
                    raise DomainError(code, msg)
                if resp.status_code >= 400:
                    err = _classify_http_error(resp.status_code, text)
                    if err.transient and attempt < _MAX_ATTEMPTS:
                        last_err = err
                        logger.warning(
                            "contract http=%s attempt=%s/%s %s",
                            resp.status_code,
                            attempt,
                            _MAX_ATTEMPTS,
                            path_only,
                        )
                    else:
                        raise err
                else:
                    if not text.strip():
                        return {} if method_u != "GET" else None
                    try:
                        return resp.json()
                    except ValueError as exc:
                        raise ContractError(
                            "INVALID_JSON",
                            text[:300],
                            status_code=resp.status_code,
                        ) from exc

            if attempt < _MAX_ATTEMPTS and last_err is not None:
                time.sleep(backoff_seconds(attempt))

        assert last_err is not None
        raise last_err


def get_contract_client(service_id: str) -> ContractClient:
    """Cached ContractClient per service_id (config from env / domain_secrets)."""
    sid = str(service_id or "").strip()
    if sid not in _client_cache:
        _client_cache[sid] = ContractClient(resolve_contract_config(sid))
    return _client_cache[sid]


def clear_contract_clients() -> None:
    """Сброс кэша (тесты)."""
    _client_cache.clear()

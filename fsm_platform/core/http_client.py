"""
Generic исходящий HTTP для доменов (Tier 1).

Credential хранится в domain_secrets под именем credential_key как JSON:

  {
    "type": "bearer_token" | "api_key_header" | "basic_auth" | "custom",
    "base_url": "https://api.example.com",
    ...поля типа...
  }

Типы:
  bearer_token:     token
  api_key_header:   api_key, header_name (default x-api-key)
  basic_auth:       username, password
  custom:           fields (dict) + signer="module.path:func"

Signer (custom):
  sign(fields, *, method, path, headers, json=None, params=None, data=None)
  → dict с опциональными ключами headers/json/params/data (merge).

service_id — только из runtime_context (Фаза 0).
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional
from urllib.parse import urljoin

import requests

from fsm_platform.host.runtime_context import current_service_id
from fsm_platform.host.secrets import get_domain_secret

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = float(os.environ.get("EXTERNAL_API_TIMEOUT", "15"))
_MAX_ATTEMPTS = int(os.environ.get("EXTERNAL_API_MAX_ATTEMPTS", "3"))

_AUTH_TYPES = frozenset(
    {"bearer_token", "api_key_header", "basic_auth", "custom"}
)


class ExternalApiError(Exception):
    """
    Ошибка внешнего API.
    transient=True → в str есть EXTERNAL_API_TRANSIENT (FSM retry).
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
        prefix = "EXTERNAL_API_TRANSIENT" if self.transient else "EXTERNAL_API"
        detail = message or code
        super().__init__(f"{prefix}:{code}: {detail}")


@dataclass
class ApiResponse:
    status_code: int
    headers: dict[str, str]
    text: str
    data: Any  # parsed JSON или None

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        """Совместимость с requests-стилем; data уже распарсен."""
        return self.data


SignerFn = Callable[..., Mapping[str, Any]]


def _load_signer(path: str) -> SignerFn:
    """module.sub:func → callable."""
    raw = (path or "").strip()
    if ":" not in raw:
        raise ExternalApiError(
            "SIGNER_INVALID",
            "signer must be 'module.path:function'",
        )
    mod_name, func_name = raw.rsplit(":", 1)
    mod_name = mod_name.strip()
    func_name = func_name.strip()
    if not mod_name or not func_name:
        raise ExternalApiError("SIGNER_INVALID", f"bad signer path: {path!r}")
    try:
        mod = importlib.import_module(mod_name)
    except ImportError as exc:
        raise ExternalApiError(
            "SIGNER_IMPORT_FAILED", str(exc)
        ) from exc
    fn = getattr(mod, func_name, None)
    if not callable(fn):
        raise ExternalApiError(
            "SIGNER_NOT_CALLABLE",
            f"{path!r} is not callable",
        )
    return fn  # type: ignore[return-value]


def _parse_credential(credential_key: str) -> dict[str, Any]:
    raw = get_domain_secret(credential_key)
    if raw is None:
        raise ExternalApiError(
            "CREDENTIAL_NOT_FOUND",
            f"secret {credential_key!r} missing for {current_service_id()}",
        )
    try:
        cred = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExternalApiError(
            "CREDENTIAL_INVALID_JSON",
            f"{credential_key!r} must be JSON credential object",
        ) from exc
    if not isinstance(cred, dict):
        raise ExternalApiError(
            "CREDENTIAL_INVALID",
            f"{credential_key!r} must be a JSON object",
        )
    auth_type = str(cred.get("type") or "").strip().lower()
    if auth_type not in _AUTH_TYPES:
        raise ExternalApiError(
            "CREDENTIAL_TYPE_UNKNOWN",
            f"type must be one of {sorted(_AUTH_TYPES)}, got {auth_type!r}",
        )
    base_url = str(cred.get("base_url") or "").strip()
    if not base_url:
        raise ExternalApiError(
            "CREDENTIAL_BASE_URL_REQUIRED",
            f"{credential_key!r} needs base_url",
        )
    cred["type"] = auth_type
    cred["base_url"] = base_url.rstrip("/") + "/"
    return cred


def _apply_auth(
    cred: dict[str, Any],
    headers: dict[str, str],
) -> tuple[dict[str, str], Optional[tuple[str, str]]]:
    """Возвращает (headers, basic_auth_tuple|None)."""
    auth_type = cred["type"]
    if auth_type == "bearer_token":
        token = str(cred.get("token") or "").strip()
        if not token:
            raise ExternalApiError(
                "CREDENTIAL_TOKEN_REQUIRED", "bearer_token needs token"
            )
        headers = {**headers, "Authorization": f"Bearer {token}"}
        return headers, None

    if auth_type == "api_key_header":
        key = str(cred.get("api_key") or "").strip()
        if not key:
            raise ExternalApiError(
                "CREDENTIAL_API_KEY_REQUIRED", "api_key_header needs api_key"
            )
        name = str(cred.get("header_name") or "x-api-key").strip() or "x-api-key"
        headers = {**headers, name: key}
        return headers, None

    if auth_type == "basic_auth":
        user = str(cred.get("username") or "")
        password = str(cred.get("password") or "")
        if not user:
            raise ExternalApiError(
                "CREDENTIAL_USERNAME_REQUIRED", "basic_auth needs username"
            )
        return headers, (user, password)

    # custom — auth через signer
    return headers, None


def _classify_http_error(status: int, body: str) -> ExternalApiError:
    snippet = (body or "")[:500]
    if status in (408, 429) or status >= 500:
        return ExternalApiError(
            f"HTTP_{status}",
            snippet,
            status_code=status,
            transient=True,
        )
    if status in (401, 403):
        return ExternalApiError(
            "HTTP_AUTH",
            snippet,
            status_code=status,
            transient=False,
        )
    return ExternalApiError(
        f"HTTP_{status}",
        snippet,
        status_code=status,
        transient=False,
    )


def _sleep_backoff(attempt: int) -> None:
    # 0.5s, 1.5s, 4.5s … cap 10s (локальные ретраи внутри одного effect)
    delay = min(10.0, 0.5 * (3 ** max(0, attempt - 1)))
    time.sleep(delay)


def call_api(
    credential_key: str,
    method: str,
    path: str,
    *,
    json_body: Any = None,
    params: Optional[Mapping[str, Any]] = None,
    data: Any = None,
    headers: Optional[Mapping[str, str]] = None,
    signer: Optional[str] = None,
    timeout: Optional[float] = None,
    max_attempts: Optional[int] = None,
) -> ApiResponse:
    """
    Исходящий HTTP от имени текущего арендатора.

    credential_key — имя секрета (JSON credential).
    path — относительный путь к base_url (или абсолютный URL).
    signer — optional override; иначе берётся из credential.type=custom → credential.signer.
    """
    # гарантируем bound context (иначе SecretsError/RuntimeContextError)
    _ = current_service_id()

    cred = _parse_credential(str(credential_key or "").strip())
    method_u = str(method or "GET").strip().upper() or "GET"
    rel = str(path or "").strip()
    if rel.startswith("http://") or rel.startswith("https://"):
        url = rel
    else:
        url = urljoin(cred["base_url"], rel.lstrip("/"))

    req_headers: dict[str, str] = dict(headers or {})
    req_headers, basic = _apply_auth(cred, req_headers)

    body_json = json_body
    body_data = data
    body_params: Optional[dict[str, Any]] = (
        dict(params) if params is not None else None
    )

    signer_path = (signer or "").strip() or str(cred.get("signer") or "").strip()
    if cred["type"] == "custom" or signer_path:
        if not signer_path:
            raise ExternalApiError(
                "SIGNER_REQUIRED",
                "custom credential needs signer='module:func'",
            )
        sign_fn = _load_signer(signer_path)
        fields = cred.get("fields") if isinstance(cred.get("fields"), dict) else {}
        try:
            updates = sign_fn(
                fields,
                method=method_u,
                path=rel,
                headers=req_headers,
                json=body_json,
                params=body_params,
                data=body_data,
            )
        except ExternalApiError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ExternalApiError(
                "SIGNER_FAILED", str(exc), transient=False
            ) from exc
        if updates:
            if not isinstance(updates, Mapping):
                raise ExternalApiError(
                    "SIGNER_BAD_RETURN",
                    "signer must return a mapping",
                )
            if "headers" in updates and updates["headers"] is not None:
                req_headers = {**req_headers, **dict(updates["headers"])}
            if "json" in updates:
                body_json = updates["json"]
            if "params" in updates:
                body_params = (
                    dict(updates["params"])
                    if updates["params"] is not None
                    else None
                )
            if "data" in updates:
                body_data = updates["data"]

    if body_json is not None and not any(
        k.lower() == "content-type" for k in req_headers
    ):
        req_headers["Content-Type"] = "application/json"

    t_out = float(timeout) if timeout is not None else _DEFAULT_TIMEOUT
    attempts = max(1, int(max_attempts if max_attempts is not None else _MAX_ATTEMPTS))

    last_err: Optional[ExternalApiError] = None
    for attempt in range(1, attempts + 1):
        try:
            req_kwargs: dict[str, Any] = {
                "headers": req_headers,
                "params": body_params,
                "auth": basic,
                "timeout": t_out,
            }
            if body_data is not None:
                req_kwargs["data"] = body_data
            elif body_json is not None:
                req_kwargs["json"] = body_json
            resp = requests.request(method_u, url, **req_kwargs)
        except requests.Timeout as exc:
            last_err = ExternalApiError(
                "TIMEOUT", str(exc), transient=True
            )
            logger.warning(
                "call_api timeout attempt=%s/%s url=%s", attempt, attempts, url
            )
            if attempt < attempts:
                _sleep_backoff(attempt)
                continue
            raise last_err from exc
        except requests.RequestException as exc:
            last_err = ExternalApiError(
                "CONNECTION", str(exc), transient=True
            )
            logger.warning(
                "call_api connection attempt=%s/%s url=%s err=%s",
                attempt,
                attempts,
                url,
                exc,
            )
            if attempt < attempts:
                _sleep_backoff(attempt)
                continue
            raise last_err from exc

        text = resp.text or ""
        parsed: Any = None
        if text.strip():
            try:
                parsed = resp.json()
            except ValueError:
                parsed = None

        if resp.status_code >= 400:
            err = _classify_http_error(resp.status_code, text)
            if err.transient and attempt < attempts:
                last_err = err
                logger.warning(
                    "call_api http=%s attempt=%s/%s url=%s",
                    resp.status_code,
                    attempt,
                    attempts,
                    url,
                )
                _sleep_backoff(attempt)
                continue
            raise err

        return ApiResponse(
            status_code=int(resp.status_code),
            headers={str(k): str(v) for k, v in resp.headers.items()},
            text=text,
            data=parsed,
        )

    assert last_err is not None
    raise last_err


# alias для доменов, привыкших к имени json=
def call_api_json(
    credential_key: str,
    method: str,
    path: str,
    *,
    json: Any = None,
    **kwargs: Any,
) -> ApiResponse:
    """То же что call_api, параметр json= вместо json_body=."""
    return call_api(
        credential_key, method, path, json_body=json, **kwargs
    )

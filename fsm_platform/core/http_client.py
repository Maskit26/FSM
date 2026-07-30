"""
Generic исходящий HTTP для доменов (Tier 1).

Credential хранится в domain_secrets под именем credential_key как JSON:

  {
    "type": "bearer_token" | "api_key_header" | "basic_auth" | "custom" | "none",
    "base_url": "https://api.example.com",
    ...поля типа...
  }

Типы:
  bearer_token:     token
  api_key_header:   api_key, header_name (default x-api-key)
  basic_auth:       username, password
  custom:           fields (dict) + signer="module.path:func"
  none:             только base_url (публичный API, напр. ibronevik Core)

Signer (custom):
  sign(fields, *, method, path, headers, json=None, params=None, data=None)
  → dict с опциональными ключами headers/json/params/data (merge).

service_id — только из runtime_context (Фаза 0).

Domain process: при PLATFORM_API_BASE_URL исходящий вызов идёт на
platform POST /v1/{service_id}/external/call (HMAC). Platform process
читает domain_secrets локально (PLATFORM_DATABASE_URL / PLATFORM_SECRETS_KEY).
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

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = float(os.environ.get("EXTERNAL_API_TIMEOUT", "15"))
_MAX_ATTEMPTS = int(os.environ.get("EXTERNAL_API_MAX_ATTEMPTS", "3"))

_AUTH_TYPES = frozenset(
    {"bearer_token", "api_key_header", "basic_auth", "custom", "none"}
)


def _use_platform_proxy() -> bool:
    """Domain process: PLATFORM_API_BASE_URL set → credentials stay on platform."""
    return bool((os.environ.get("PLATFORM_API_BASE_URL") or "").strip())


def _is_domain_cartridge_process() -> bool:
    """
    Domain service process имеет DOMAIN_DATABASE_URL.
    Platform API / worker — нет (только PLATFORM_DATABASE_URL).
    """
    return bool((os.environ.get("DOMAIN_DATABASE_URL") or "").strip())


def _platform_proxy_base() -> str:
    return (os.environ.get("PLATFORM_API_BASE_URL") or "").strip().rstrip("/")


def _contract_shared_secret() -> str:
    secret = (os.environ.get("CONTRACT_SHARED_SECRET") or "").strip()
    if not secret:
        raise ExternalApiError(
            "CONTRACT_SECRET_MISSING",
            "CONTRACT_SHARED_SECRET required for platform external/call proxy",
        )
    return secret



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
    from fsm_platform.host.secrets import get_domain_secret

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

    if auth_type == "none":
        # Публичный API: без Authorization (ibronevik Core register/auth и т.п.)
        return headers, None

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

    Domain process (PLATFORM_API_BASE_URL): HMAC proxy на platform /external/call.
    Platform process: читает domain_secrets локально и ходит во внешний API.
    """
    if _use_platform_proxy():
        return call_api_via_platform(
            credential_key,
            method,
            path,
            json_body=json_body,
            params=params,
            data=data,
            headers=headers,
            signer=signer,
            timeout=timeout,
            max_attempts=max_attempts,
        )
    if _is_domain_cartridge_process():
        raise ExternalApiError(
            "PLATFORM_API_BASE_URL_REQUIRED",
            "domain process must set PLATFORM_API_BASE_URL; "
            "credentials are resolved by platform POST /v1/{service_id}/external/call "
            "(do not set PLATFORM_DATABASE_URL / PLATFORM_SECRETS_KEY on domain)",
        )
    return call_api_local(
        credential_key,
        method,
        path,
        json_body=json_body,
        params=params,
        data=data,
        headers=headers,
        signer=signer,
        timeout=timeout,
        max_attempts=max_attempts,
    )


def call_api_via_platform(
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
    """Domain → platform HMAC proxy; secrets never leave the platform process."""
    from fsm_platform.host.contract_client import sign_contract_request

    sid = current_service_id()
    base = _platform_proxy_base()
    if not base:
        raise ExternalApiError(
            "PLATFORM_API_BASE_URL_MISSING",
            "PLATFORM_API_BASE_URL is required in domain process",
        )
    secret = _contract_shared_secret()
    api_path = f"/v1/{sid}/external/call"
    url = f"{base}{api_path}"
    payload = {
        "credential_key": str(credential_key or "").strip(),
        "method": str(method or "GET").strip().upper() or "GET",
        "path": str(path or "").strip(),
        "json_body": json_body,
        "params": dict(params) if params is not None else None,
        "data": data,
        "headers": dict(headers) if headers is not None else None,
        "signer": signer,
        "timeout": timeout,
        "max_attempts": max_attempts,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ts = str(int(time.time()))
    sig = sign_contract_request(
        secret,
        method="POST",
        path=api_path,
        body=raw,
        timestamp=ts,
    )
    # Platform still retries vendor HTTP; give headroom for nested call.
    t_out = float(timeout) if timeout is not None else _DEFAULT_TIMEOUT
    attempts = max(1, int(max_attempts if max_attempts is not None else _MAX_ATTEMPTS))
    proxy_timeout = max(t_out * attempts + 5.0, 30.0)

    try:
        resp = requests.post(
            url,
            data=raw,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "X-Service-Id": sid,
                "X-Contract-Timestamp": ts,
                "X-Contract-Signature": sig,
            },
            timeout=proxy_timeout,
        )
    except requests.Timeout as exc:
        raise ExternalApiError("TIMEOUT", str(exc), transient=True) from exc
    except requests.RequestException as exc:
        raise ExternalApiError("CONNECTION", str(exc), transient=True) from exc

    body: Any
    try:
        body = resp.json() if resp.text else {}
    except ValueError:
        body = {"_raw": resp.text}

    if resp.status_code >= 400:
        detail = body.get("detail") if isinstance(body, dict) else None
        if isinstance(detail, dict):
            code = str(detail.get("error_code") or f"HTTP_{resp.status_code}")
            msg = str(detail.get("message") or code)
            transient = bool(detail.get("transient"))
            vendor = detail.get("vendor_status")
            raise ExternalApiError(
                code,
                msg,
                status_code=int(vendor) if vendor is not None else resp.status_code,
                transient=transient,
            )
        if isinstance(detail, str):
            raise ExternalApiError(
                "PLATFORM_PROXY_ERROR",
                detail,
                status_code=resp.status_code,
                transient=resp.status_code >= 500,
            )
        raise ExternalApiError(
            f"HTTP_{resp.status_code}",
            (resp.text or "")[:500],
            status_code=resp.status_code,
            transient=resp.status_code >= 500,
        )

    if not isinstance(body, dict):
        raise ExternalApiError(
            "PLATFORM_PROXY_BAD_RESPONSE",
            "external/call response must be an object",
        )
    return ApiResponse(
        status_code=int(body.get("status_code") or 200),
        headers={str(k): str(v) for k, v in dict(body.get("headers") or {}).items()},
        text=str(body.get("text") or ""),
        data=body.get("data"),
    )


def call_api_local(
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
    Platform-local outbound HTTP: resolve credential from domain_secrets, then request.
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

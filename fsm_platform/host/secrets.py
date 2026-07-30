"""
Per-tenant domain secrets (encrypted at rest).

Доменный код:
  get_domain_secret(key) / set_domain_secret(key, value) / delete_domain_secret(key)
  — service_id берётся из runtime_context (платформа биндит перед вызовом).

Admin API биндит service_id из URL и вызывает те же функции.
Шифрование: scoped Secret Broker (HKDF DEK per service_id) — см. secret_broker.py.
"""

from __future__ import annotations

import hmac
import os
from typing import Optional

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.engines import platform_session
from fsm_platform.host.runtime_context import current_service_id
from fsm_platform.host.secret_broker import (
    SecretBrokerError,
    unwrap,
    wrap,
)


class SecretsError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def _broker_error(exc: SecretBrokerError) -> SecretsError:
    return SecretsError(exc.code, str(exc) or exc.code)


def _encrypt(service_id: str, value: str) -> str:
    try:
        return wrap(service_id, value)
    except SecretBrokerError as exc:
        raise _broker_error(exc) from exc


def _decrypt(service_id: str, value_enc: str) -> str:
    try:
        return unwrap(service_id, value_enc)
    except SecretBrokerError as exc:
        raise _broker_error(exc) from exc


def require_admin(x_admin_token: Optional[str]) -> None:
    """
    Проверка X-Admin-Token против PLATFORM_ADMIN_TOKEN.
    Без токена в env — admin-поверхность выключена.
    """
    expected = (os.environ.get("PLATFORM_ADMIN_TOKEN") or "").strip()
    if not expected:
        raise SecretsError(
            "ADMIN_DISABLED",
            "PLATFORM_ADMIN_TOKEN is not set",
        )
    got = (x_admin_token or "").strip()
    if not got or not hmac.compare_digest(got, expected):
        raise SecretsError("ADMIN_FORBIDDEN", "invalid admin token")


def get_domain_secret(key: str) -> Optional[str]:
    """Читает секрет текущего арендатора. None если ключа нет."""
    service_id = current_service_id()
    k = str(key or "").strip()
    if not k:
        raise SecretsError("SECRET_KEY_REQUIRED")
    sp = platform_session()
    try:
        row = default_db_layer.get_domain_secret(sp, service_id=service_id, key=k)
        if row is None:
            return None
        return _decrypt(service_id, str(row["value_enc"]))
    finally:
        sp.close()


def set_domain_secret(key: str, value: str) -> None:
    """Upsert секрета текущего арендатора (value шифруется scoped DEK)."""
    service_id = current_service_id()
    k = str(key or "").strip()
    if not k:
        raise SecretsError("SECRET_KEY_REQUIRED")
    if value is None or str(value) == "":
        raise SecretsError("SECRET_VALUE_REQUIRED")
    enc = _encrypt(service_id, str(value))
    sp = platform_session()
    try:
        default_db_layer.upsert_domain_secret(
            sp, service_id=service_id, key=k, value_enc=enc
        )
        sp.commit()
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def delete_domain_secret(key: str) -> bool:
    """Удаляет секрет текущего арендатора. True если строка была."""
    service_id = current_service_id()
    k = str(key or "").strip()
    if not k:
        raise SecretsError("SECRET_KEY_REQUIRED")
    sp = platform_session()
    try:
        ok = default_db_layer.delete_domain_secret(
            sp, service_id=service_id, key=k
        )
        sp.commit()
        return ok
    except Exception:
        sp.rollback()
        raise
    finally:
        sp.close()


def list_domain_secret_keys() -> list[str]:
    """Имена ключей текущего арендатора (без значений)."""
    service_id = current_service_id()
    sp = platform_session()
    try:
        return default_db_layer.list_domain_secret_keys(sp, service_id=service_id)
    finally:
        sp.close()

"""
Scoped secret broker (§7.6.3).

PLATFORM_SECRETS_KEY — master KEK (process env). Per-tenant DEK = HKDF(KEK, service_id).
Ciphertext: ``v2.<service_id>.<fernet_token>`` — only that tenant DEK can decrypt.

Worker with WORKER_SERVICE_ID set may unwrap only its own service_id (fail-closed).
Platform API (no WORKER_SERVICE_ID) may unwrap any tenant.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_V2_PREFIX = "v2."


class SecretBrokerError(Exception):
    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def _master_key_bytes() -> bytes:
    raw = (os.environ.get("PLATFORM_SECRETS_KEY") or "").strip()
    if not raw:
        raise SecretBrokerError(
            "SECRETS_KEY_MISSING",
            "PLATFORM_SECRETS_KEY is not set",
        )
    try:
        decoded = base64.urlsafe_b64decode(raw.encode("utf-8"))
        if len(decoded) >= 32:
            return decoded[:32]
    except Exception:
        pass
    return hashlib.sha256(raw.encode("utf-8")).digest()


def _tenant_fernet(service_id: str) -> Fernet:
    sid = str(service_id or "").strip()
    if not sid:
        raise SecretBrokerError("SERVICE_ID_REQUIRED", "service_id required for scoped DEK")
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"fsm-platform-secrets-v2",
        info=f"domain_secrets:{sid}".encode("utf-8"),
    )
    dek = hkdf.derive(_master_key_bytes())
    return Fernet(base64.urlsafe_b64encode(dek))


def worker_scope_service_id() -> Optional[str]:
    """WORKER_SERVICE_ID if this process is a dedicated worker; else None (API)."""
    return (os.environ.get("WORKER_SERVICE_ID") or "").strip() or None


def assert_unwrap_allowed(service_id: str) -> None:
    """
    Worker may decrypt only its own tenant.
    Platform API (no WORKER_SERVICE_ID) may decrypt any.
    """
    sid = str(service_id or "").strip()
    scoped = worker_scope_service_id()
    if scoped and not hmac.compare_digest(scoped, sid):
        raise SecretBrokerError(
            "SECRETS_SCOPE_DENIED",
            f"worker scoped to {scoped!r} cannot unwrap secrets for {sid!r}",
        )


def wrap(service_id: str, plaintext: str) -> str:
    """Encrypt plaintext under tenant-scoped DEK (v2 envelope)."""
    sid = str(service_id or "").strip()
    assert_unwrap_allowed(sid)
    token = _tenant_fernet(sid).encrypt(plaintext.encode("utf-8")).decode("utf-8")
    return f"{_V2_PREFIX}{sid}.{token}"


def unwrap(service_id: str, ciphertext: str) -> str:
    """Decrypt ``v2.<service_id>.<token>`` for service_id. No other formats."""
    sid = str(service_id or "").strip()
    assert_unwrap_allowed(sid)
    raw = str(ciphertext or "")
    if not raw.startswith(_V2_PREFIX):
        raise SecretBrokerError(
            "SECRETS_CIPHER_INVALID",
            "ciphertext must be v2.<service_id>.<token>",
        )
    rest = raw[len(_V2_PREFIX) :]
    parts = rest.split(".", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise SecretBrokerError("SECRETS_CIPHER_INVALID", "malformed v2 ciphertext")
    enc_sid, token = parts[0], parts[1]
    if not hmac.compare_digest(enc_sid, sid):
        raise SecretBrokerError(
            "SECRETS_SERVICE_MISMATCH",
            "ciphertext service_id does not match request",
        )
    try:
        return _tenant_fernet(sid).decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise SecretBrokerError(
            "SECRETS_DECRYPT_FAILED",
            "cannot decrypt secret (wrong key or corrupt token)",
        ) from exc

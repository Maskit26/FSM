"""Central log redaction for platform/worker processes (§7.6.1)."""

from __future__ import annotations

import logging
import os
import re
from typing import Iterable, Optional
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url

# driver://user:password@host/db  (password may contain URL-encoded chars)
_URI_RE = re.compile(
    r"(?i)\b([a-z][a-z0-9+.-]*://[^:\s/]+:)([^@\s]+)(@[^\s]+)"
)
# key=value / key: value for secret-looking keys
_KV_RE = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API[_-]?KEY)[A-Z0-9_]*)"
    r"(\s*[=:]\s*)([^\s,;\"']+)"
)
_REDACTED = "***"


def safe_db_url(url: str) -> str:
    """Diagnostic form of a DB URL with password hidden."""
    raw = (url or "").strip()
    if not raw:
        return ""
    try:
        return make_url(raw).render_as_string(hide_password=True)
    except Exception:
        return _URI_RE.sub(rf"\1{_REDACTED}\3", raw)


def _env_secret_values() -> list[str]:
    keys = (
        "PLATFORM_DATABASE_URL",
        "DOMAIN_DATABASE_URL",
        "DATABASE_URL",
        "PLATFORM_SECRETS_KEY",
        "PLATFORM_ADMIN_TOKEN",
        "CONTRACT_SHARED_SECRET",
        "TENANT_AUTH_SECRET",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_LINK_SECRET",
    )
    out: list[str] = []
    for key in keys:
        val = (os.environ.get(key) or "").strip()
        if len(val) >= 8:
            out.append(val)
            # Also mask password segment of JDBC URLs if present
            try:
                parts = urlsplit(val)
                if parts.password:
                    out.append(parts.password)
            except Exception:
                pass
    return out


def redact_text(text: str, *, extra_values: Optional[Iterable[str]] = None) -> str:
    if not text:
        return text
    out = text
    values = list(_env_secret_values())
    if extra_values:
        values.extend(v for v in extra_values if v and len(v) >= 8)
    # Longest first so partial overlaps don't leave remnants
    for val in sorted(set(values), key=len, reverse=True):
        if val in out:
            out = out.replace(val, _REDACTED)
    out = _URI_RE.sub(rf"\1{_REDACTED}\3", out)
    out = _KV_RE.sub(rf"\1\2{_REDACTED}", out)
    return out


class RedactingFilter(logging.Filter):
    """Masks secrets in log records (message + exception text)."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            redacted = redact_text(msg)
            if redacted != msg:
                record.msg = redacted
                record.args = ()
            if record.exc_text:
                record.exc_text = redact_text(record.exc_text)
            if record.stack_info:
                record.stack_info = redact_text(str(record.stack_info))
        except Exception:
            # Never break logging
            pass
        return True


_installed = False


def install_log_redaction(logger: Optional[logging.Logger] = None) -> None:
    """Attach RedactingFilter to root (or given) logger and its handlers."""
    global _installed
    target = logger or logging.getLogger()
    filt = RedactingFilter()
    # Avoid duplicate filters on re-import / reload
    for existing in list(target.filters):
        if isinstance(existing, RedactingFilter):
            target.removeFilter(existing)
    target.addFilter(filt)
    for handler in target.handlers:
        for existing in list(handler.filters):
            if isinstance(existing, RedactingFilter):
                handler.removeFilter(existing)
        handler.addFilter(filt)
    _installed = True

"""Резолв per-tenant конфига из domain_secrets (не из platform .env)."""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Стандартные ключи domain_secrets при онбординге tenant
SECRET_GRAPH_DATABASE_URL = "graph_database_url"
SECRET_GRAPH_WRITE_DATABASE_URL = "graph_write_database_url"
SECRET_CONTRACT_BASE_URL = "contract_base_url"
SECRET_CONTRACT_SHARED_SECRET = "contract_shared_secret"


def resolve_tenant_ref(service_id: str, ref: str) -> Optional[str]:
    """
    Разрешает ref для арендатора:
    1) литерал URL (содержит ://)
    2) значение domain_secrets[ref] для service_id
    3) os.environ[ref] — только legacy; warning в лог
    """
    sid = str(service_id or "").strip()
    key = str(ref or "").strip()
    if not sid or not key:
        return None

    if "://" in key:
        return key

    from fsm_platform.host.runtime.runtime_context import service_scope
    from fsm_platform.host.security.secrets import get_domain_secret

    try:
        with service_scope(sid):
            val = get_domain_secret(key)
    except Exception:
        logger.exception(
            "domain_secrets lookup failed service_id=%s key=%s", sid, key
        )
        val = None

    if val is not None and str(val).strip():
        return str(val).strip()

    env_val = (os.environ.get(key) or "").strip()
    if env_val:
        logger.warning(
            "tenant ref %r for %s resolved from process env — "
            "migrate to domain_secrets",
            key,
            sid,
        )
        return env_val

    return None

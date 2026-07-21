"""Boot platform: engines + domain register_all."""

from __future__ import annotations

import logging
import os

from domains.bootstrap import bootstrap_from_env
from fsm_host.engines import platform_session, register_domain_engine
from fsm_platform.db_layer import default_db_layer

logger = logging.getLogger(__name__)


def boot() -> None:
    """
    1) Register domain engines from DOMAIN_DATABASE_URL + SERVICE_ID (dev)
       and/or domain_services rows (status=active).
    2) register_all from FSM_DOMAINS.
    """
    _register_engines_from_env()
    _register_engines_from_domain_services()
    bootstrap_from_env()
    logger.info("boot complete")


def _register_engines_from_env() -> None:
    service_id = os.environ.get("SERVICE_ID", "").strip()
    url = os.environ.get("DOMAIN_DATABASE_URL", "").strip()
    if service_id and url:
        register_domain_engine(service_id, url)
        logger.info("domain engine from env service_id=%s", service_id)


def _register_engines_from_domain_services() -> None:
    try:
        sp = platform_session()
    except Exception:
        logger.warning("platform DB not available for domain_services boot")
        return
    try:
        rows = default_db_layer.list_active_domain_services(sp)
        for row in rows:
            sid = str(row["service_id"])
            ref = str(row["db_secret_ref"])
            # v1: db_secret_ref holds SQLAlchemy URL or env var name
            url = os.environ.get(ref, ref)
            if "://" not in url:
                logger.warning("skip domain_services %s: not a URL and env missing", sid)
                continue
            register_domain_engine(sid, url)
            logger.info("domain engine from registry service_id=%s", sid)
    finally:
        sp.close()

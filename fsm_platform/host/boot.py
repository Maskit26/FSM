"""Boot платформы: graph engines из domain_services + bootstrap Contract API."""

from __future__ import annotations

import logging

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.domain_bootstrap import bootstrap_active_domains
from fsm_platform.host.engines import (
    platform_session,
    register_graph_read_engine,
    register_graph_write_engine,
)
from fsm_platform.host.tenant_config import resolve_tenant_ref

logger = logging.getLogger(__name__)


def boot() -> None:
    """
    Platform always starts:
    - graph engines per active tenant (domain_services → domain_secrets)
    - domain catalog bootstrap (best-effort, domain service may be offline)
    """
    _register_graph_engines_from_domain_services()
    bootstrap_active_domains()
    logger.info("boot complete")


def _register_graph_engines_from_domain_services() -> None:
    """Graph engines для active domain_services; сбой одного tenant не блокирует platform."""
    try:
        sp = platform_session()
    except Exception:
        logger.warning(
            "platform DB not available — skip graph engines from domain_services"
        )
        return
    try:
        rows = [dict(r) for r in default_db_layer.list_active_domain_services(sp)]
    finally:
        sp.close()

    for row in rows:
        sid = str(row["service_id"])
        try:
            graph_ref = row.get("db_graph_secret_ref")
            if not graph_ref:
                logger.warning(
                    "skip graph read engine service_id=%s: "
                    "db_graph_secret_ref missing",
                    sid,
                )
                continue
            graph_url = resolve_tenant_ref(sid, str(graph_ref))
            if graph_url is None:
                logger.warning(
                    "skip graph read engine service_id=%s: cannot resolve %r",
                    sid,
                    graph_ref,
                )
                continue
            register_graph_read_engine(sid, graph_url)
            logger.info("graph read engine service_id=%s", sid)

            graph_write_ref = row.get("db_graph_write_secret_ref")
            if not graph_write_ref:
                logger.warning(
                    "skip graph write engine service_id=%s: "
                    "db_graph_write_secret_ref missing",
                    sid,
                )
                continue
            graph_write_url = resolve_tenant_ref(sid, str(graph_write_ref))
            if graph_write_url is None:
                logger.warning(
                    "skip graph write engine service_id=%s: cannot resolve %r",
                    sid,
                    graph_write_ref,
                )
                continue
            register_graph_write_engine(sid, graph_write_url)
            logger.info("graph write engine service_id=%s", sid)
        except Exception:
            logger.exception("graph engine registration failed service_id=%s", sid)

"""Boot платформы: graph DB engines (best-effort) и bootstrap доменов через Contract API."""

from __future__ import annotations

import logging
import os

from domains.bootstrap import bootstrap_active_domains
from fsm_platform.host.engines import (
    platform_session,
    register_graph_read_engine,
    register_graph_write_engine,
)
from fsm_platform.core.db_layer import default_db_layer

logger = logging.getLogger(__name__)


def boot() -> None:
    """
    Platform always starts:
    - graph engines per tenant (best-effort)
    - domain catalog bootstrap (best-effort, domain service may be offline)
    """
    _register_graph_engines_from_env()
    _register_graph_engines_from_domain_services()
    bootstrap_active_domains()
    logger.info("boot complete")


def _resolve_db_url(ref: str) -> str | None:
    """Env key → URL, или ref как URL. None если не резолвится."""
    url = os.environ.get(ref, ref).strip()
    if "://" not in url:
        return None
    return url


def _register_graph_engines_from_env() -> None:
    """Graph read/write engines из env (опционально для dev single-tenant)."""
    service_id = os.environ.get("SERVICE_ID", "").strip()
    if not service_id:
        return

    graph_ro = os.environ.get("DOMAIN_GRAPH_DATABASE_URL", "").strip()
    if graph_ro:
        register_graph_read_engine(service_id, graph_ro)
        logger.info("graph read engine from env service_id=%s", service_id)

    graph_rw = os.environ.get("DOMAIN_GRAPH_WRITE_DATABASE_URL", "").strip()
    if graph_rw:
        register_graph_write_engine(service_id, graph_rw)
        logger.info("graph write engine from env service_id=%s", service_id)


def _register_graph_engines_from_domain_services() -> None:
    """Graph engines для active domain_services; сбой одного tenant не блокирует platform."""
    try:
        sp = platform_session()
    except Exception:
        logger.warning("platform DB not available — skip graph engines from domain_services")
        return
    try:
        rows = default_db_layer.list_active_domain_services(sp)
        for row in rows:
            sid = str(row["service_id"])
            try:
                graph_ref = row.get("db_graph_secret_ref")
                if not graph_ref:
                    logger.warning(
                        "skip graph read engine service_id=%s: db_graph_secret_ref missing",
                        sid,
                    )
                    continue
                graph_url = _resolve_db_url(str(graph_ref))
                if graph_url is None:
                    logger.warning(
                        "skip graph read engine service_id=%s: cannot resolve %r",
                        sid,
                        graph_ref,
                    )
                    continue
                register_graph_read_engine(sid, graph_url)
                logger.info("graph read engine from registry service_id=%s", sid)

                graph_write_ref = row.get("db_graph_write_secret_ref")
                if not graph_write_ref:
                    logger.warning(
                        "skip graph write engine service_id=%s: "
                        "db_graph_write_secret_ref missing",
                        sid,
                    )
                    continue
                graph_write_url = _resolve_db_url(str(graph_write_ref))
                if graph_write_url is None:
                    logger.warning(
                        "skip graph write engine service_id=%s: cannot resolve %r",
                        sid,
                        graph_write_ref,
                    )
                    continue
                register_graph_write_engine(sid, graph_write_url)
                logger.info("graph write engine from registry service_id=%s", sid)
            except Exception:
                logger.exception(
                    "graph engine registration failed service_id=%s", sid
                )
    finally:
        sp.close()

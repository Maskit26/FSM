"""Boot платформы: graph engines из domain_services + bootstrap Contract API."""

from __future__ import annotations

import logging

from fsm_platform.core.db_layer import default_db_layer
from fsm_platform.host.tenant.domain_bootstrap import bootstrap_active_domains
from fsm_platform.host.runtime.engines import (
    platform_session,
    register_graph_read_engine,
    register_graph_write_engine,
)
from fsm_platform.host.tenant.tenant_config import resolve_tenant_ref

logger = logging.getLogger(__name__)


def boot(*, service_id: str | None = None) -> None:
    """
    Platform always starts:
    - graph engines per active tenant (domain_services → domain_secrets)
    - domain catalog bootstrap (best-effort, domain service may be offline)
    """
    _register_graph_engines_from_domain_services(service_id=service_id)
    bootstrap_active_domains(service_id=service_id)
    logger.info("boot complete service_id=%s", service_id or "*")


def _register_graph_engines_from_domain_services(
    *, service_id: str | None = None
) -> None:
    """Graph engines для active domain_services; сбой одного tenant не блокирует platform."""
    try:
        sp = platform_session()
    except Exception:
        logger.warning(
            "platform DB not available — skip graph engines from domain_services"
        )
        return
    try:
        rows = [
            dict(r)
            for r in default_db_layer.list_active_domain_services(
                sp, service_id=service_id
            )
        ]
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


def configure_graph_engines(service_id: str) -> None:
    """Configure graph engines for a newly registered domain before activation."""
    sp = platform_session()
    try:
        row = default_db_layer.get_domain_service(sp, service_id=service_id)
    finally:
        sp.close()
    if row is None:
        raise LookupError("DOMAIN_NOT_FOUND")
    graph_ref = row.get("db_graph_secret_ref")
    if not graph_ref:
        raise RuntimeError("db_graph_secret_ref missing")
    graph_url = resolve_tenant_ref(service_id, str(graph_ref))
    if not graph_url:
        raise RuntimeError(f"cannot resolve graph ref {graph_ref!r}")
    register_graph_read_engine(service_id, graph_url)
    graph_write_ref = row.get("db_graph_write_secret_ref")
    if graph_write_ref:
        graph_write_url = resolve_tenant_ref(service_id, str(graph_write_ref))
        if not graph_write_url:
            raise RuntimeError(f"cannot resolve graph write ref {graph_write_ref!r}")
        register_graph_write_engine(service_id, graph_write_url)

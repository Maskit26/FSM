"""Boot платформы: engines БД и регистрация доменов."""

from __future__ import annotations

import logging
import os

from domains.bootstrap import bootstrap_from_env
from fsm_platform.host.engines import (
    has_graph_read_engine,
    has_graph_write_engine,
    platform_session,
    register_domain_engine,
    register_graph_read_engine,
    register_graph_write_engine,
)
from fsm_platform.core.db_layer import default_db_layer

logger = logging.getLogger(__name__)


class BootConfigError(RuntimeError):
    """Неверная конфигурация DB engines при старте."""


def boot() -> None:
    """
    Поднимает domain engines (env + domain_services) и вызывает register_all доменов.
    Вызывается при старте API и worker.
    """
    _register_engines_from_env()
    _register_engines_from_domain_services()
    _validate_graph_engines()
    bootstrap_from_env()
    logger.info("boot complete")


def _resolve_db_url(ref: str) -> str | None:
    """Env key → URL, или ref как URL. None если не резолвится."""
    url = os.environ.get(ref, ref).strip()
    if "://" not in url:
        return None
    return url


def _register_engines_from_env() -> None:
    """Регистрирует domain/graph engines из env (dev / single-tenant)."""
    service_id = os.environ.get("SERVICE_ID", "").strip()
    if not service_id:
        return

    url = os.environ.get("DOMAIN_DATABASE_URL", "").strip()
    if url:
        register_domain_engine(service_id, url)
        logger.info("domain engine from env service_id=%s", service_id)

    graph_ro = os.environ.get("DOMAIN_GRAPH_DATABASE_URL", "").strip()
    if graph_ro:
        register_graph_read_engine(service_id, graph_ro)
        logger.info("graph read engine from env service_id=%s", service_id)

    graph_rw = os.environ.get("DOMAIN_GRAPH_WRITE_DATABASE_URL", "").strip()
    if graph_rw:
        register_graph_write_engine(service_id, graph_rw)
        logger.info("graph write engine from env service_id=%s", service_id)


def _register_engines_from_domain_services() -> None:
    """Читает active строки domain_services и регистрирует engines по secret refs."""
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
            url = _resolve_db_url(ref)
            if url is None:
                logger.warning(
                    "skip domain_services %s: db_secret_ref not a URL and env missing",
                    sid,
                )
            else:
                register_domain_engine(sid, url)
                logger.info("domain engine from registry service_id=%s", sid)

            graph_ref = row.get("db_graph_secret_ref")
            if not graph_ref:
                raise BootConfigError(
                    f"domain_services.db_graph_secret_ref is required for active "
                    f"service_id={sid!r} (e.g. DOMAIN_GRAPH_DATABASE_URL)"
                )
            graph_url = _resolve_db_url(str(graph_ref))
            if graph_url is None:
                raise BootConfigError(
                    f"cannot resolve graph read URL for service_id={sid!r} "
                    f"from ref={graph_ref!r}"
                )
            register_graph_read_engine(sid, graph_url)
            logger.info("graph read engine from registry service_id=%s", sid)

            graph_write_ref = row.get("db_graph_write_secret_ref")
            if not graph_write_ref:
                raise BootConfigError(
                    f"domain_services.db_graph_write_secret_ref is required for "
                    f"active service_id={sid!r} (e.g. DOMAIN_GRAPH_WRITE_DATABASE_URL)"
                )
            graph_write_url = _resolve_db_url(str(graph_write_ref))
            if graph_write_url is None:
                raise BootConfigError(
                    f"cannot resolve graph write URL for service_id={sid!r} "
                    f"from ref={graph_write_ref!r}"
                )
            register_graph_write_engine(sid, graph_write_url)
            logger.info("graph write engine from registry service_id=%s", sid)
    finally:
        sp.close()


def _validate_graph_engines() -> None:
    """Каждый активный tenant из env должен иметь graph read/write engines."""
    service_id = os.environ.get("SERVICE_ID", "").strip()
    if not service_id:
        return
    if not has_graph_read_engine(service_id):
        raise BootConfigError(
            f"DOMAIN_GRAPH_DATABASE_URL is required for SERVICE_ID={service_id!r}"
        )
    if not has_graph_write_engine(service_id):
        raise BootConfigError(
            f"DOMAIN_GRAPH_WRITE_DATABASE_URL is required for "
            f"SERVICE_ID={service_id!r}"
        )

"""Engines SQLAlchemy: platform DB и graph DB по service_id (без business domain DB)."""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_graph_read_engine_by_service_id: dict[str, Engine] = {}
_graph_read_sessionmaker_by_service_id: dict[str, sessionmaker] = {}
_graph_write_engine_by_service_id: dict[str, Engine] = {}
_graph_write_sessionmaker_by_service_id: dict[str, sessionmaker] = {}
# Один pool на URL (Clever Cloud max_user_connections≈5).
_engine_by_url: dict[str, Engine] = {}
_sessionmaker_by_url: dict[str, sessionmaker] = {}
_platform_engine: Optional[Engine] = None
_platform_sessionmaker: Optional[sessionmaker] = None


def _default_engine_kwargs() -> dict[str, object]:
    return {
        "pool_pre_ping": True,
        "pool_size": 1,
        "max_overflow": 0,
        "hide_parameters": True,
    }


def _engine_for_url(url: str, **engine_kwargs: object) -> tuple[Engine, sessionmaker]:
    """Reuse SQLAlchemy engine when several refs resolve to the same JDBC URL."""
    key = url.strip()
    if key not in _engine_by_url:
        kwargs = _default_engine_kwargs()
        kwargs.update(engine_kwargs)
        engine = create_engine(key, **kwargs)  # type: ignore[arg-type]
        _engine_by_url[key] = engine
        _sessionmaker_by_url[key] = sessionmaker(bind=engine, autoflush=False)
    return _engine_by_url[key], _sessionmaker_by_url[key]


def _register_engine_pair(
    target_engine: dict[str, Engine],
    target_sm: dict[str, sessionmaker],
    service_id: str,
    url: str,
    **engine_kwargs: object,
) -> Engine:
    engine, sm = _engine_for_url(url, **engine_kwargs)
    target_engine[service_id] = engine
    target_sm[service_id] = sm
    return engine


def get_platform_engine() -> Engine:
    """Лениво создаёт engine platform DB из PLATFORM_DATABASE_URL. Один на процесс."""
    global _platform_engine, _platform_sessionmaker
    if _platform_engine is None:
        url = os.environ.get("PLATFORM_DATABASE_URL") or os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("PLATFORM_DATABASE_URL (or DATABASE_URL) is not set")
        kwargs = _default_engine_kwargs()
        _platform_engine = create_engine(url, **kwargs)  # type: ignore[arg-type]
        _platform_sessionmaker = sessionmaker(bind=_platform_engine, autoflush=False)
    return _platform_engine


def platform_session() -> Session:
    """Новая SQLAlchemy-сессия к platform DB. Caller обязан commit/rollback/close."""
    get_platform_engine()
    assert _platform_sessionmaker is not None
    return _platform_sessionmaker()


def register_graph_read_engine(
    service_id: str, url: str, **engine_kwargs: object
) -> Engine:
    """Read-only graph tables (fsm_states/transitions/meta/actions)."""
    return _register_engine_pair(
        _graph_read_engine_by_service_id,
        _graph_read_sessionmaker_by_service_id,
        service_id,
        url,
        **engine_kwargs,
    )


def register_graph_write_engine(
    service_id: str, url: str, **engine_kwargs: object
) -> Engine:
    """Graph publish: INSERT/UPDATE on graph tables."""
    return _register_engine_pair(
        _graph_write_engine_by_service_id,
        _graph_write_sessionmaker_by_service_id,
        service_id,
        url,
        **engine_kwargs,
    )


def graph_session(service_id: str) -> Session:
    """Сессия к domain DB для чтения FSM-графа."""
    if service_id not in _graph_read_sessionmaker_by_service_id:
        raise RuntimeError(
            f"graph read engine not configured for service_id={service_id!r}; "
            f"set domain_secrets.graph_database_url (domain_services.db_graph_secret_ref)"
        )
    return _graph_read_sessionmaker_by_service_id[service_id]()


def graph_write_session(service_id: str) -> Session:
    """Сессия для graph/publish."""
    if service_id not in _graph_write_sessionmaker_by_service_id:
        raise RuntimeError(
            f"graph write engine not configured for service_id={service_id!r}; "
            f"set domain_secrets.graph_write_database_url "
            f"(domain_services.db_graph_write_secret_ref)"
        )
    return _graph_write_sessionmaker_by_service_id[service_id]()

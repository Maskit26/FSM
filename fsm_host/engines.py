"""engine_by_service_id — domain DB engines from Domain Registry / env (§4.14)."""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine_by_service_id: dict[str, Engine] = {}
_sessionmaker_by_service_id: dict[str, sessionmaker] = {}
_platform_engine: Optional[Engine] = None
_platform_sessionmaker: Optional[sessionmaker] = None


def get_platform_engine() -> Engine:
    global _platform_engine, _platform_sessionmaker
    if _platform_engine is None:
        url = os.environ.get("PLATFORM_DATABASE_URL") or os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("PLATFORM_DATABASE_URL (or DATABASE_URL) is not set")
        _platform_engine = create_engine(url, pool_pre_ping=True)
        _platform_sessionmaker = sessionmaker(bind=_platform_engine, autoflush=False)
    return _platform_engine


def platform_session() -> Session:
    get_platform_engine()
    assert _platform_sessionmaker is not None
    return _platform_sessionmaker()


def register_domain_engine(service_id: str, url: str, **engine_kwargs: object) -> Engine:
    engine = create_engine(url, pool_pre_ping=True, **engine_kwargs)  # type: ignore[arg-type]
    _engine_by_service_id[service_id] = engine
    _sessionmaker_by_service_id[service_id] = sessionmaker(bind=engine, autoflush=False)
    return engine


def get_domain_engine(service_id: str) -> Engine:
    if service_id not in _engine_by_service_id:
        raise KeyError(f"no domain engine for service_id={service_id!r}")
    return _engine_by_service_id[service_id]


def domain_session(service_id: str) -> Session:
    if service_id not in _sessionmaker_by_service_id:
        raise KeyError(f"no domain engine for service_id={service_id!r}")
    return _sessionmaker_by_service_id[service_id]()


def clear_engines() -> None:
    global _platform_engine, _platform_sessionmaker
    for eng in list(_engine_by_service_id.values()):
        eng.dispose()
    _engine_by_service_id.clear()
    _sessionmaker_by_service_id.clear()
    if _platform_engine is not None:
        _platform_engine.dispose()
    _platform_engine = None
    _platform_sessionmaker = None

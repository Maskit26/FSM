"""Engines SQLAlchemy: platform DB и domain DB по service_id."""

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
    """Лениво создаёт engine platform DB из PLATFORM_DATABASE_URL. Один на процесс."""
    global _platform_engine, _platform_sessionmaker
    if _platform_engine is None:
        url = os.environ.get("PLATFORM_DATABASE_URL") or os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("PLATFORM_DATABASE_URL (or DATABASE_URL) is not set")
        # Хостинг часто даёт max_user_connections≈5 на юзера (API+worker делят лимит).
        _platform_engine = create_engine(
            url, pool_pre_ping=True, pool_size=1, max_overflow=0
        )
        _platform_sessionmaker = sessionmaker(bind=_platform_engine, autoflush=False)
    return _platform_engine


def platform_session() -> Session:
    """Новая SQLAlchemy-сессия к platform DB. Caller обязан commit/rollback/close."""
    get_platform_engine()
    assert _platform_sessionmaker is not None
    return _platform_sessionmaker()


def register_domain_engine(service_id: str, url: str, **engine_kwargs: object) -> Engine:
    """Регистрирует domain engine для service_id. Нужен до любых domain_session вызовов."""
    kwargs = {"pool_pre_ping": True, "pool_size": 1, "max_overflow": 0}
    kwargs.update(engine_kwargs)
    engine = create_engine(url, **kwargs)  # type: ignore[arg-type]
    _engine_by_service_id[service_id] = engine
    _sessionmaker_by_service_id[service_id] = sessionmaker(bind=engine, autoflush=False)
    return engine


def get_domain_engine(service_id: str) -> Engine:
    """Возвращает уже зарегистрированный domain engine или KeyError."""
    if service_id not in _engine_by_service_id:
        raise KeyError(f"no domain engine for service_id={service_id!r}")
    return _engine_by_service_id[service_id]


def domain_session(service_id: str) -> Session:
    """Новая сессия к domain DB сервиса. Caller обязан commit/rollback/close."""
    if service_id not in _sessionmaker_by_service_id:
        raise KeyError(f"no domain engine for service_id={service_id!r}")
    return _sessionmaker_by_service_id[service_id]()


def clear_engines() -> None:
    """Сбрасывает все engines (для тестов). Закрывает пулы соединений."""
    global _platform_engine, _platform_sessionmaker
    for eng in list(_engine_by_service_id.values()):
        eng.dispose()
    _engine_by_service_id.clear()
    _sessionmaker_by_service_id.clear()
    if _platform_engine is not None:
        _platform_engine.dispose()
    _platform_engine = None
    _platform_sessionmaker = None

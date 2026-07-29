"""Domain DB session для domain service (отдельный процесс)."""

from __future__ import annotations

import os
from typing import Any, Optional

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Optional[Engine] = None
_sessionmaker: Optional[sessionmaker] = None


def domain_session() -> Session:
    global _engine, _sessionmaker
    if _sessionmaker is None:
        from sqlalchemy import create_engine

        url = os.environ.get("DOMAIN_DATABASE_URL", "").strip()
        if not url:
            raise RuntimeError("DOMAIN_DATABASE_URL is not set")
        _engine = create_engine(url, pool_pre_ping=True, pool_size=2, max_overflow=0)
        _sessionmaker = sessionmaker(bind=_engine, autoflush=False)
    return _sessionmaker()


def make_db(session_domain: Session) -> dict[str, Any]:
    return {"domain": session_domain}

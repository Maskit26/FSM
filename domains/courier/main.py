"""Entrypoint courier domain service.

    uvicorn domains.courier.main:app --port 8100
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# .env картриджа перекрывает унаследованный shell env (иначе e2e/dev ломается на 127.0.0.1)
_load = Path(__file__).resolve().parent / ".env"
if _load.is_file():
    load_dotenv(_load, override=True)
else:
    load_dotenv(override=True)

from fsm_platform.domain_runtime import create_app  # noqa: E402

app = create_app(entry="domains.courier.processes:register_all")

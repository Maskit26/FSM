"""API entrypoint: uvicorn main:app --reload --port 8000"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

from fsm_platform.host.log_redaction import install_log_redaction  # noqa: E402

install_log_redaction()

from fsm_platform.host.http.app import app  # noqa: E402

__all__ = ["app"]

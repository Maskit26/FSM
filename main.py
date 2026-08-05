"""API entrypoint: uvicorn main:app --reload --port 8000"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format=(
        "%(asctime)s %(levelname)s %(name)s "
        "corr=%(correlation_id)s cmd=%(command_id)s %(message)s"
    ),
)

from fsm_platform.host.runtime.correlation import (  # noqa: E402
    install_correlation_logging,
)
from fsm_platform.host.security.log_redaction import install_log_redaction  # noqa: E402

install_correlation_logging()
install_log_redaction()

from fsm_platform.host.http.app import app  # noqa: E402

__all__ = ["app"]

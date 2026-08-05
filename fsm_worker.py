"""Process entrypoint: FSM worker loop."""

from __future__ import annotations

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

logger = logging.getLogger(__name__)


def resolve_worker_service_id() -> str:
    """
    Fail-closed: каждый worker обслуживает ровно один WORKER_SERVICE_ID.
    """
    scoped = (os.environ.get("WORKER_SERVICE_ID") or "").strip()
    if scoped:
        return scoped

    logger.error(
        "WORKER_SERVICE_ID is required. "
        "Set WORKER_SERVICE_ID=<service_id> for the dedicated worker."
    )
    raise SystemExit(2)


def main() -> None:
    from fsm_platform.host.tenant.boot import boot
    from fsm_platform.host.workers.worker import run_loop

    service_id = resolve_worker_service_id()
    boot(service_id=service_id)
    poll = float(os.environ.get("FSM_WORKER_POLL_SECONDS", "1"))
    logger.info("fsm worker scoped to service_id=%s", service_id)
    run_loop(poll_seconds=poll, service_id=service_id)


if __name__ == "__main__":
    main()

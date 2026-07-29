"""Process entrypoint: FSM worker loop."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def _truthy(raw: str | None) -> bool:
    return (raw or "").strip().lower() in ("1", "true", "yes", "on")


def resolve_worker_service_id() -> str | None:
    """
    Fail-closed: без WORKER_SERVICE_ID воркер не стартует,
    кроме явного opt-in WORKER_ALLOW_ALL_TENANTS=1 (dev / миграция).
    """
    scoped = (os.environ.get("WORKER_SERVICE_ID") or "").strip()
    if scoped:
        return scoped

    if _truthy(os.environ.get("WORKER_ALLOW_ALL_TENANTS")):
        logger.warning(
            "WORKER_SERVICE_ID unset; WORKER_ALLOW_ALL_TENANTS=1 — "
            "worker claims ALL tenants (dev/migration only)"
        )
        return None

    logger.error(
        "WORKER_SERVICE_ID is required. "
        "Set WORKER_SERVICE_ID=<tenant> for one-tenant worker, "
        "or WORKER_ALLOW_ALL_TENANTS=1 for explicit all-tenants mode."
    )
    raise SystemExit(2)


def main() -> None:
    from fsm_platform.host.boot import boot
    from fsm_platform.host.worker import run_loop

    service_id = resolve_worker_service_id()
    boot()
    poll = float(os.environ.get("FSM_WORKER_POLL_SECONDS", "1"))
    if service_id:
        logger.info("fsm worker scoped to service_id=%s", service_id)
    run_loop(poll_seconds=poll, service_id=service_id)


if __name__ == "__main__":
    main()

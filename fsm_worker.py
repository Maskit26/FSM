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


def main() -> None:
    from fsm_platform.host.boot import boot
    from fsm_platform.host.worker import run_loop

    boot()
    poll = float(os.environ.get("FSM_WORKER_POLL_SECONDS", "1"))
    # Один процесс воркера на тенанта: задать WORKER_SERVICE_ID=svc_courier_01
    # Без переменной — прежнее поведение (все тенанты).
    service_id = (os.environ.get("WORKER_SERVICE_ID") or "").strip() or None
    run_loop(poll_seconds=poll, service_id=service_id)


if __name__ == "__main__":
    main()

"""Local dedicated-worker lifecycle used by tenant connect."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any


_lock = threading.Lock()
_processes: dict[str, subprocess.Popen[Any]] = {}


def _command() -> list[str]:
    configured = str(os.environ.get("WORKER_PROVISION_COMMAND") or "").strip()
    if configured:
        return shlex.split(configured, posix=os.name != "nt")
    root = Path(__file__).resolve().parents[2]
    return [sys.executable, str(root / "fsm_worker.py")]


def provision_worker(service_id: str) -> dict[str, Any]:
    """Start or return the one local worker process assigned to service_id."""
    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id is required")
    with _lock:
        current = _processes.get(sid)
        if current is not None and current.poll() is None:
            return {"service_id": sid, "status": "running", "pid": current.pid}
        env = os.environ.copy()
        env["WORKER_SERVICE_ID"] = sid
        env.pop("WORKER_ALLOW_ALL_TENANTS", None)
        root = Path(__file__).resolve().parents[2]
        process = subprocess.Popen(
            _command(),
            cwd=str(root),
            env=env,
            stdin=subprocess.DEVNULL,
        )
        _processes[sid] = process
        return {"service_id": sid, "status": "started", "pid": process.pid}


def worker_status(service_id: str) -> dict[str, Any]:
    with _lock:
        process = _processes.get(service_id)
        if process is None:
            return {"service_id": service_id, "status": "not_started", "pid": None}
        code = process.poll()
        return {
            "service_id": service_id,
            "status": "running" if code is None else "exited",
            "pid": process.pid,
            "exit_code": code,
        }


def stop_worker(service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
    with _lock:
        process = _processes.get(service_id)
        if process is None or process.poll() is not None:
            return {"service_id": service_id, "status": "stopped", "pid": None}
        process.terminate()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        _processes.pop(service_id, None)
        return {
            "service_id": service_id,
            "status": "stopped",
            "pid": process.pid,
        }


def restart_worker(service_id: str) -> dict[str, Any]:
    stop_worker(service_id)
    return provision_worker(service_id)

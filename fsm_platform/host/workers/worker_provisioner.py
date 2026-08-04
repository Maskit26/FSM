"""
Worker lifecycle backends for tenant connect (§7.1).

Env:
  WORKER_PROVISION_BACKEND=local|systemd|docker|kubernetes  (default: local)
  WORKER_PROVISION_COMMAND=...   # local: override argv for fsm_worker.py
  WORKER_SYSTEMD_UNIT_TEMPLATE=fsm-worker-{service_id}.service
  WORKER_DOCKER_IMAGE=fsm-platform-worker:latest
  WORKER_DOCKER_NETWORK=...
  WORKER_K8S_NAMESPACE=fsm-platform
  WORKER_K8S_DEPLOYMENT_PREFIX=fsm-worker-

Public API (stable): provision_worker / worker_status / stop_worker / restart_worker
"""

from __future__ import annotations

import os
import shlex
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Protocol


class WorkerBackend(Protocol):
    def provision(self, service_id: str) -> dict[str, Any]: ...
    def status(self, service_id: str) -> dict[str, Any]: ...
    def stop(self, service_id: str, *, timeout: float = 10.0) -> dict[str, Any]: ...


def _backend_name() -> str:
    return (os.environ.get("WORKER_PROVISION_BACKEND") or "local").strip().lower() or "local"


def _repo_root() -> Path:
    # host/workers/this.py → parents[3] = repository root (…/FSM_Platform)
    return Path(__file__).resolve().parents[3]


def _pid_dir() -> Path:
    return _repo_root() / ".worker-pids"


def _pid_path(service_id: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in service_id)
    return _pid_dir() / f"{safe}.pid"


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _write_pid(service_id: str, pid: int) -> None:
    path = _pid_path(service_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(int(pid)), encoding="utf-8")


def _read_pid(service_id: str) -> int | None:
    path = _pid_path(service_id)
    if not path.is_file():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _clear_pid(service_id: str) -> None:
    path = _pid_path(service_id)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def _worker_command() -> list[str]:
    configured = str(os.environ.get("WORKER_PROVISION_COMMAND") or "").strip()
    if configured:
        return shlex.split(configured, posix=os.name != "nt")
    return [sys.executable, str(_repo_root() / "fsm_worker.py")]


def _worker_env(service_id: str) -> dict[str, str]:
    env = os.environ.copy()
    env["WORKER_SERVICE_ID"] = service_id
    env.pop("WORKER_ALLOW_ALL_TENANTS", None)
    return env


class LocalSubprocessBackend:
    """Dev default: child process of the Platform API (+ pid-file across reloads)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._processes: dict[str, subprocess.Popen[Any]] = {}

    def provision(self, service_id: str) -> dict[str, Any]:
        sid = str(service_id or "").strip()
        with self._lock:
            current = self._processes.get(sid)
            if current is not None and current.poll() is None:
                _write_pid(sid, int(current.pid))
                return {"service_id": sid, "status": "running", "pid": current.pid}
            file_pid = _read_pid(sid)
            if file_pid is not None and _pid_alive(file_pid):
                return {"service_id": sid, "status": "running", "pid": file_pid}
            cmd = _worker_command()
            worker_script = Path(cmd[1]) if len(cmd) > 1 else None
            if worker_script is not None and not worker_script.is_file():
                raise FileNotFoundError(f"worker entry not found: {worker_script}")
            process = subprocess.Popen(
                cmd,
                cwd=str(_repo_root()),
                env=_worker_env(sid),
                stdin=subprocess.DEVNULL,
            )
            self._processes[sid] = process
            _write_pid(sid, int(process.pid))
            return {"service_id": sid, "status": "started", "pid": process.pid}

    def status(self, service_id: str) -> dict[str, Any]:
        sid = str(service_id or "").strip()
        with self._lock:
            process = self._processes.get(sid)
            if process is not None:
                code = process.poll()
                if code is None:
                    _write_pid(sid, int(process.pid))
                    return {
                        "service_id": sid,
                        "status": "running",
                        "pid": process.pid,
                    }
                self._processes.pop(sid, None)
                _clear_pid(sid)
                return {
                    "service_id": sid,
                    "status": "exited",
                    "pid": process.pid,
                    "exit_code": code,
                }
            file_pid = _read_pid(sid)
            if file_pid is not None and _pid_alive(file_pid):
                return {"service_id": sid, "status": "running", "pid": file_pid}
            if file_pid is not None:
                _clear_pid(sid)
            return {"service_id": sid, "status": "not_started", "pid": None}

    def stop(self, service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
        sid = str(service_id or "").strip()
        with self._lock:
            process = self._processes.get(sid)
            pid: int | None = None
            if process is not None and process.poll() is None:
                pid = int(process.pid)
                process.terminate()
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                self._processes.pop(sid, None)
            else:
                self._processes.pop(sid, None)
                file_pid = _read_pid(sid)
                if file_pid is not None and _pid_alive(file_pid):
                    pid = file_pid
                    try:
                        os.kill(file_pid, signal.SIGTERM)
                    except OSError:
                        if os.name == "nt":
                            subprocess.run(
                                ["taskkill", "/PID", str(file_pid), "/F", "/T"],
                                check=False,
                                capture_output=True,
                            )
                        else:
                            try:
                                os.kill(file_pid, signal.SIGKILL)
                            except OSError:
                                pass
            _clear_pid(sid)
            return {"service_id": sid, "status": "stopped", "pid": pid}


class SystemdBackend:
    """
    Linux: systemctl start/stop/status for unit per service_id.
    Unit name: WORKER_SYSTEMD_UNIT_TEMPLATE (default fsm-worker-{service_id}.service).
    Units must be pre-installed; this backend only controls lifecycle.
    """

    def _unit(self, service_id: str) -> str:
        tmpl = (
            os.environ.get("WORKER_SYSTEMD_UNIT_TEMPLATE")
            or "fsm-worker-{service_id}.service"
        )
        return tmpl.replace("{service_id}", service_id)

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["systemctl", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def provision(self, service_id: str) -> dict[str, Any]:
        unit = self._unit(service_id)
        r = self._run("start", unit)
        if r.returncode != 0:
            raise RuntimeError(f"systemctl start {unit}: {r.stderr or r.stdout}")
        return {"service_id": service_id, "status": "started", "unit": unit}

    def status(self, service_id: str) -> dict[str, Any]:
        unit = self._unit(service_id)
        r = self._run("is-active", unit)
        active = (r.stdout or "").strip()
        if active == "active":
            st = "running"
        elif active in ("inactive", "failed"):
            st = "exited" if active == "failed" else "not_started"
        else:
            st = active or "unknown"
        return {"service_id": service_id, "status": st, "unit": unit}

    def stop(self, service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
        unit = self._unit(service_id)
        r = self._run("stop", unit)
        if r.returncode != 0:
            raise RuntimeError(f"systemctl stop {unit}: {r.stderr or r.stdout}")
        return {"service_id": service_id, "status": "stopped", "unit": unit}


class DockerBackend:
    """
    One container per service_id: name fsm-worker-{service_id}.
    Image: WORKER_DOCKER_IMAGE (required for provision).
    """

    def _name(self, service_id: str) -> str:
        return f"fsm-worker-{service_id}"

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["docker", *args], capture_output=True, text=True, check=False
        )

    def provision(self, service_id: str) -> dict[str, Any]:
        name = self._name(service_id)
        image = (os.environ.get("WORKER_DOCKER_IMAGE") or "").strip()
        if not image:
            raise RuntimeError("WORKER_DOCKER_IMAGE is required for docker backend")
        # Reuse running container
        insp = self._run(["inspect", "-f", "{{.State.Running}}", name])
        if insp.returncode == 0 and (insp.stdout or "").strip().lower() == "true":
            return {"service_id": service_id, "status": "running", "container": name}
        self._run(["rm", "-f", name])
        args = [
            "run",
            "-d",
            "--name",
            name,
            "-e",
            f"WORKER_SERVICE_ID={service_id}",
        ]
        network = (os.environ.get("WORKER_DOCKER_NETWORK") or "").strip()
        if network:
            args.extend(["--network", network])
        # Pass through platform DB/secrets from host env if present
        for key in (
            "PLATFORM_DATABASE_URL",
            "PLATFORM_SECRETS_KEY",
            "PLATFORM_ADMIN_TOKEN",
            "LOG_LEVEL",
            "FSM_WORKER_POLL_SECONDS",
        ):
            val = (os.environ.get(key) or "").strip()
            if val:
                args.extend(["-e", f"{key}={val}"])
        args.append(image)
        r = self._run(args)
        if r.returncode != 0:
            raise RuntimeError(f"docker run failed: {r.stderr or r.stdout}")
        return {
            "service_id": service_id,
            "status": "started",
            "container": name,
            "id": (r.stdout or "").strip(),
        }

    def status(self, service_id: str) -> dict[str, Any]:
        name = self._name(service_id)
        insp = self._run(["inspect", "-f", "{{.State.Status}}", name])
        if insp.returncode != 0:
            return {"service_id": service_id, "status": "not_started", "container": name}
        st = (insp.stdout or "").strip().lower()
        mapped = {
            "running": "running",
            "exited": "exited",
            "dead": "exited",
            "created": "not_started",
        }.get(st, st or "unknown")
        return {"service_id": service_id, "status": mapped, "container": name}

    def stop(self, service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
        name = self._name(service_id)
        r = self._run(["stop", "-t", str(int(timeout)), name])
        self._run(["rm", "-f", name])
        if r.returncode != 0 and "No such container" not in (r.stderr or ""):
            raise RuntimeError(f"docker stop failed: {r.stderr or r.stdout}")
        return {"service_id": service_id, "status": "stopped", "container": name}


class KubernetesBackend:
    """
    Scale Deployment fsm-worker-{service_id} (or WORKER_K8S_DEPLOYMENT_PREFIX).
    Assumes Deployment + template already exist in the cluster; this only scales 0/1.
    """

    def _deployment(self, service_id: str) -> str:
        prefix = os.environ.get("WORKER_K8S_DEPLOYMENT_PREFIX") or "fsm-worker-"
        return f"{prefix}{service_id}"

    def _ns(self) -> list[str]:
        ns = (os.environ.get("WORKER_K8S_NAMESPACE") or "fsm-platform").strip()
        return ["-n", ns] if ns else []

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["kubectl", *args], capture_output=True, text=True, check=False
        )

    def provision(self, service_id: str) -> dict[str, Any]:
        dep = self._deployment(service_id)
        r = self._run([*_ns(), "scale", f"deployment/{dep}", "--replicas=1"])
        if r.returncode != 0:
            raise RuntimeError(f"kubectl scale up failed: {r.stderr or r.stdout}")
        return {"service_id": service_id, "status": "started", "deployment": dep}

    def status(self, service_id: str) -> dict[str, Any]:
        dep = self._deployment(service_id)
        r = self._run(
            [
                *_ns(),
                "get",
                f"deployment/{dep}",
                "-o",
                "jsonpath={.status.readyReplicas}",
            ]
        )
        if r.returncode != 0:
            return {
                "service_id": service_id,
                "status": "not_started",
                "deployment": dep,
            }
        ready = (r.stdout or "").strip()
        try:
            n = int(ready or "0")
        except ValueError:
            n = 0
        return {
            "service_id": service_id,
            "status": "running" if n >= 1 else "not_started",
            "deployment": dep,
            "ready_replicas": n,
        }

    def stop(self, service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
        dep = self._deployment(service_id)
        r = self._run([*_ns(), "scale", f"deployment/{dep}", "--replicas=0"])
        if r.returncode != 0:
            raise RuntimeError(f"kubectl scale down failed: {r.stderr or r.stdout}")
        return {"service_id": service_id, "status": "stopped", "deployment": dep}


_backends: dict[str, WorkerBackend] = {}
_lock = threading.Lock()


def _get_backend() -> WorkerBackend:
    name = _backend_name()
    with _lock:
        if name not in _backends:
            if name == "local":
                _backends[name] = LocalSubprocessBackend()
            elif name == "systemd":
                _backends[name] = SystemdBackend()
            elif name == "docker":
                _backends[name] = DockerBackend()
            elif name in ("kubernetes", "k8s"):
                _backends[name] = KubernetesBackend()
            else:
                raise RuntimeError(
                    f"Unknown WORKER_PROVISION_BACKEND={name!r}; "
                    f"use local|systemd|docker|kubernetes"
                )
        return _backends[name]


def provision_worker(service_id: str) -> dict[str, Any]:
    """Start or return the worker assigned to service_id."""
    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id is required")
    out = _get_backend().provision(sid)
    out.setdefault("backend", _backend_name())
    return out


def worker_status(service_id: str) -> dict[str, Any]:
    sid = str(service_id or "").strip()
    out = _get_backend().status(sid)
    out.setdefault("backend", _backend_name())
    return out


def stop_worker(service_id: str, *, timeout: float = 10.0) -> dict[str, Any]:
    sid = str(service_id or "").strip()
    out = _get_backend().stop(sid, timeout=timeout)
    out.setdefault("backend", _backend_name())
    return out


def restart_worker(service_id: str) -> dict[str, Any]:
    stop_worker(service_id)
    return provision_worker(service_id)

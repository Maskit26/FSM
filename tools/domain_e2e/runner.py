"""
CLI: run YAML domain scenarios against live API.

  python -m tools.domain_e2e.runner scenarios/courier/client_self_pickup.yaml
  python -m tools.domain_e2e.runner scenarios/courier/ --report reports/run.md
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Optional

from tools.domain_e2e.client import ApiClient
from tools.domain_e2e.report import (
    ScenarioResult,
    StepResult,
    print_console,
    write_report,
)
from tools.domain_e2e.scenario import (
    assert_expect,
    assert_instance,
    capture_vars,
    discover_scenarios,
    load_scenario,
    substitute,
)

_TERMINAL = frozenset({"COMPLETED", "FAILED", "CANCELLED"})


def _package_root() -> Path:
    """tools/domain_e2e/"""
    return Path(__file__).resolve().parent


def _resolve_scenario_path(raw: str) -> Path:
    """CWD → package → package/scenarios."""
    p = Path(raw)
    if p.is_absolute() and p.exists():
        return p
    for c in (
        Path.cwd() / p,
        _package_root() / p,
        _package_root() / "scenarios" / p,
    ):
        if c.exists():
            return c
    return Path.cwd() / p


def run_step(
    client: ApiClient,
    *,
    service_id: str,
    step: dict[str, Any],
    vars_map: dict[str, Any],
    poll_timeout: float,
    poll_interval: float,
) -> StepResult:
    name = str(step.get("name") or step.get("operation") or "step")
    t0 = time.perf_counter()

    try:
        operation = str(step["operation"])
        actor = substitute(step.get("actor") or {}, vars_map)
        params = substitute(step.get("params") or {}, vars_map)
        expect = substitute(step.get("expect") or {}, vars_map)
        expect_instance = substitute(step.get("expect_instance") or {}, vars_map)
    except KeyError as exc:
        return StepResult(
            name=name,
            ok=False,
            duration_ms=(time.perf_counter() - t0) * 1000,
            errors=[str(exc)],
        )

    status_code, body = client.invoke(service_id, operation, params, actor)
    errors = assert_expect(status_code=status_code, body=body, expect=expect)

    wait_until = bool(step.get("wait_until", False))
    if wait_until and expect and status_code < 400:
        deadline = time.monotonic() + poll_timeout
        while errors and time.monotonic() < deadline:
            time.sleep(poll_interval)
            status_code, body = client.invoke(
                service_id, operation, params, actor
            )
            errors = assert_expect(
                status_code=status_code, body=body, expect=expect
            )

    captured: dict[str, Any] = {}
    capture_spec = step.get("capture") or {}
    if capture_spec and status_code < 400:
        try:
            captured = capture_vars(body, capture_spec)
            vars_map.update(captured)
        except KeyError as exc:
            errors.append(f"capture failed: {exc}")

    instance_id = body.get("instance_id")
    instance_ids_raw = body.get("instance_ids")
    instance_ids: list[int] = []
    if isinstance(instance_ids_raw, list):
        instance_ids = [int(x) for x in instance_ids_raw if x is not None]
    elif instance_id is not None:
        instance_ids = [int(instance_id)]

    instance_status: Optional[str] = None
    last_error: Optional[str] = None
    wait_instance = bool(step.get("wait_instance", False))
    if wait_instance and instance_ids and not errors:
        for iid in instance_ids:
            inst_body, inst_errors = _wait_instance(
                client,
                service_id,
                iid,
                timeout=poll_timeout,
                interval=poll_interval,
            )
            errors.extend(inst_errors)
            if inst_body:
                instance_status = str(inst_body.get("status") or "")
                last_error = (
                    str(inst_body.get("last_error"))
                    if inst_body.get("last_error")
                    else None
                )
                errors.extend(assert_instance(inst_body, expect_instance or None))
                cap_inst = step.get("capture_instance") or {}
                if cap_inst and instance_status == "COMPLETED":
                    try:
                        more = capture_vars(inst_body, cap_inst)
                        captured.update(more)
                        vars_map.update(more)
                    except KeyError as exc:
                        errors.append(f"capture_instance failed: {exc}")
            if errors:
                break
    elif wait_instance and not instance_ids:
        # Sync command без enqueue (напр. create_order bind по request_id).
        pass

    ok = not errors
    return StepResult(
        name=name,
        ok=ok,
        duration_ms=(time.perf_counter() - t0) * 1000,
        status_code=status_code,
        operation=operation,
        instance_id=instance_ids[0] if instance_ids else None,
        instance_status=instance_status,
        last_error=last_error,
        captured=captured,
        errors=errors,
    )


def _wait_instance(
    client: ApiClient,
    service_id: str,
    instance_id: int,
    *,
    timeout: float,
    interval: float,
) -> tuple[Optional[dict[str, Any]], list[str]]:
    deadline = time.monotonic() + timeout
    last: Optional[dict[str, Any]] = None
    while time.monotonic() < deadline:
        code, body = client.get_instance(service_id, instance_id)
        if code != 200:
            time.sleep(interval)
            continue
        last = body
        status = str(body.get("status") or "")
        if status in _TERMINAL:
            return body, []
        time.sleep(interval)
    status = (last or {}).get("status")
    return last, [
        f"instance {instance_id} poll timeout ({timeout}s), last status={status!r}"
    ]


def run_scenario(
    client: ApiClient,
    path: Path,
    *,
    service_id_override: Optional[str] = None,
    poll_timeout: float,
    poll_interval: float,
    stop_on_fail: bool = True,
) -> ScenarioResult:
    t0 = time.perf_counter()
    try:
        scenario = load_scenario(path)
    except Exception as exc:
        return ScenarioResult(
            name=path.stem,
            path=str(path),
            ok=False,
            duration_ms=(time.perf_counter() - t0) * 1000,
            error=str(exc),
        )

    name = str(scenario.get("name") or path.stem)
    # YAML service_id обязателен (load_scenario); CLI --service-id только override.
    service_id = str(service_id_override or "").strip() or str(
        scenario["service_id"]
    )
    defaults = scenario.get("defaults") or {}
    poll_timeout = float(defaults.get("poll_timeout", poll_timeout))
    poll_interval = float(defaults.get("poll_interval", poll_interval))

    vars_map: dict[str, Any] = dict(scenario.get("vars") or {})
    steps_out: list[StepResult] = []
    aborted = False

    for step in scenario["steps"]:
        if aborted:
            steps_out.append(
                StepResult(
                    name=str(step.get("name") or "step"),
                    ok=False,
                    duration_ms=0,
                    skipped=True,
                    errors=["skipped after previous failure"],
                )
            )
            continue
        if not isinstance(step, dict):
            steps_out.append(
                StepResult(
                    name="invalid",
                    ok=False,
                    duration_ms=0,
                    errors=["step must be a mapping"],
                )
            )
            aborted = stop_on_fail
            continue
        result = run_step(
            client,
            service_id=service_id,
            step=step,
            vars_map=vars_map,
            poll_timeout=poll_timeout,
            poll_interval=poll_interval,
        )
        steps_out.append(result)
        if not result.ok and stop_on_fail:
            aborted = True

    ok = not any((not s.ok and not s.skipped) for s in steps_out)

    return ScenarioResult(
        name=name,
        path=str(path),
        ok=ok,
        duration_ms=(time.perf_counter() - t0) * 1000,
        steps=steps_out,
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run YAML domain E2E scenarios against FSM Platform API"
    )
    parser.add_argument(
        "path",
        type=str,
        help="Scenario YAML file or directory",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base URL (default http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--service-id",
        default="",
        help="Override YAML service_id (optional; scenarios must declare service_id)",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Write Markdown report to this path",
    )
    parser.add_argument(
        "--poll-timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for FSM instance terminal status",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.5,
        help="Poll interval seconds",
    )
    parser.add_argument(
        "--continue-on-fail",
        action="store_true",
        help="Do not skip remaining steps after a failure",
    )
    args = parser.parse_args(argv)

    target = _resolve_scenario_path(args.path)

    try:
        files = discover_scenarios(target)
    except FileNotFoundError:
        print(f"Path not found: {args.path}", file=sys.stderr)
        return 2

    if not files:
        print(f"No YAML scenarios under {target}", file=sys.stderr)
        return 2

    client = ApiClient(args.base_url)
    try:
        code, _ = client.health()
        if code != 200:
            print(f"API health check failed: HTTP {code} at {args.base_url}", file=sys.stderr)
            return 2
    except Exception as exc:
        print(f"Cannot reach API at {args.base_url}: {exc}", file=sys.stderr)
        return 2

    results: list[ScenarioResult] = []
    for f in files:
        print(f"Running {f} ...")
        results.append(
            run_scenario(
                client,
                f,
                service_id_override=args.service_id or None,
                poll_timeout=args.poll_timeout,
                poll_interval=args.poll_interval,
                stop_on_fail=not args.continue_on_fail,
            )
        )

    print_console(results)

    report_path = args.report.strip()
    if not report_path:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = str(_package_root() / "reports" / f"e2e_{stamp}.md")
    else:
        rp = Path(report_path)
        if not rp.is_absolute():
            rp = _package_root() / rp
        report_path = str(rp)
    write_report(Path(report_path), results)
    print(f"Report: {report_path}")

    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

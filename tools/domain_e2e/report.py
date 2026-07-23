"""Console + Markdown report for domain e2e runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class StepResult:
    name: str
    ok: bool
    duration_ms: float
    status_code: Optional[int] = None
    operation: Optional[str] = None
    instance_id: Optional[int] = None
    instance_status: Optional[str] = None
    last_error: Optional[str] = None
    captured: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    skipped: bool = False


@dataclass
class ScenarioResult:
    name: str
    path: str
    ok: bool
    duration_ms: float
    steps: list[StepResult] = field(default_factory=list)
    error: Optional[str] = None


def render_markdown(results: list[ScenarioResult], *, title: str = "Domain E2E Report") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    failed = total - passed
    lines = [
        f"# {title}",
        "",
        f"Generated: {now}",
        "",
        f"**Summary:** {passed}/{total} passed, {failed} failed",
        "",
    ]
    for sc in results:
        mark = "PASS" if sc.ok else "FAIL"
        lines.append(f"## [{mark}] {sc.name}")
        lines.append("")
        lines.append(f"- file: `{sc.path}`")
        lines.append(f"- duration: {sc.duration_ms:.0f} ms")
        if sc.error:
            lines.append(f"- error: `{sc.error}`")
        lines.append("")
        if sc.steps:
            lines.append("| Step | Result | HTTP | Instance | ms | Notes |")
            lines.append("|------|--------|------|----------|----|-------|")
            for st in sc.steps:
                if st.skipped:
                    res = "SKIP"
                elif st.ok:
                    res = "PASS"
                else:
                    res = "FAIL"
                http = str(st.status_code) if st.status_code is not None else "-"
                inst = st.instance_status or "-"
                if st.instance_id is not None:
                    inst = f"{inst} (#{st.instance_id})"
                notes = "; ".join(st.errors) if st.errors else ""
                if st.last_error and st.last_error not in notes:
                    notes = (notes + "; " if notes else "") + st.last_error
                if st.captured:
                    cap = ", ".join(f"{k}={v!r}" for k, v in st.captured.items())
                    notes = (notes + "; " if notes else "") + f"capture: {cap}"
                notes = notes.replace("|", "\\|")
                lines.append(
                    f"| {st.name} | {res} | {http} | {inst} | {st.duration_ms:.0f} | {notes} |"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def print_console(results: list[ScenarioResult]) -> None:
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    print()
    print(f"=== Domain E2E: {passed}/{total} passed ===")
    for sc in results:
        mark = "PASS" if sc.ok else "FAIL"
        print(f"[{mark}] {sc.name} ({sc.duration_ms:.0f} ms)")
        if sc.error:
            print(f"  ERROR: {sc.error}")
        for st in sc.steps:
            if st.skipped:
                tag = "SKIP"
            elif st.ok:
                tag = "PASS"
            else:
                tag = "FAIL"
            extra = ""
            if st.errors:
                extra = " — " + "; ".join(st.errors)
            elif st.instance_status:
                extra = f" — instance={st.instance_status}"
            print(f"  [{tag}] {st.name}{extra}")
    print()


def write_report(path: Path, results: list[ScenarioResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(results), encoding="utf-8")

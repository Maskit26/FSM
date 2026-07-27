"""YAML scenario load, variable substitution, JSON-path helpers, assertions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

import yaml

_VAR_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def load_scenario(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"scenario root must be a mapping: {path}")
    if not data.get("name"):
        data["name"] = path.stem
    sid = str(data.get("service_id") or "").strip()
    if not sid:
        raise ValueError(
            f"scenario requires service_id (multi-tenant): {path}"
        )
    data["service_id"] = sid
    if not isinstance(data.get("steps"), list) or not data["steps"]:
        raise ValueError(f"scenario requires non-empty steps: {path}")
    return data


def discover_scenarios(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(str(path))
    return sorted(path.glob("**/*.yaml")) + sorted(path.glob("**/*.yml"))


def substitute(value: Any, vars_map: dict[str, Any]) -> Any:
    """Replace {{var}} in strings; recurse into dict/list."""
    if isinstance(value, str):
        return _substitute_string(value, vars_map)
    if isinstance(value, dict):
        return {k: substitute(v, vars_map) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute(v, vars_map) for v in value]
    return value


def _substitute_string(text: str, vars_map: dict[str, Any]) -> Any:
    """If the whole string is one {{var}}, return typed value; else string replace."""
    m = _VAR_RE.fullmatch(text.strip())
    if m:
        key = m.group(1)
        if key not in vars_map:
            raise KeyError(f"undefined variable: {key}")
        return vars_map[key]

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in vars_map:
            raise KeyError(f"undefined variable: {key}")
        return str(vars_map[key])

    return _VAR_RE.sub(repl, text)


def get_by_path(data: Any, path: str) -> Any:
    """Dot-path into nested dicts/lists. Numeric parts index lists. Missing → KeyError."""
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(path)
            cur = cur[part]
            continue
        if isinstance(cur, list):
            try:
                idx = int(part)
            except ValueError as exc:
                raise KeyError(path) from exc
            if idx < 0 or idx >= len(cur):
                raise KeyError(path)
            cur = cur[idx]
            continue
        raise KeyError(path)
    return cur


def capture_vars(body: dict[str, Any], capture: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, path in (capture or {}).items():
        out[name] = get_by_path(body, path)
    return out


def assert_expect(
    *,
    status_code: int,
    body: dict[str, Any],
    expect: Optional[dict[str, Any]],
) -> list[str]:
    """Return list of failure messages (empty = ok)."""
    errors: list[str] = []
    if not expect:
        return errors

    want_code = expect.get("status_code")
    if want_code is not None and int(status_code) != int(want_code):
        detail = ""
        if isinstance(body, dict):
            err = body.get("detail")
            if isinstance(err, dict):
                code = err.get("error_code") or err.get("message")
                if code:
                    detail = f" ({code})"
            elif err is not None:
                detail = f" ({err})"
        errors.append(f"status_code: expected {want_code}, got {status_code}{detail}")

    body_expect = expect.get("body") or {}
    if isinstance(body_expect, dict):
        for path, want in body_expect.items():
            try:
                got = get_by_path(body, path)
            except KeyError:
                errors.append(f"body.{path}: missing")
                continue
            if _normalize(got) != _normalize(want):
                errors.append(f"body.{path}: expected {want!r}, got {got!r}")
    return errors


def assert_instance(
    instance: dict[str, Any], expect_instance: Optional[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    if not expect_instance:
        return errors
    want_status = expect_instance.get("status")
    if want_status is not None:
        got = instance.get("status")
        if str(got) != str(want_status):
            err = instance.get("last_error") or ""
            suffix = f" ({err})" if err else ""
            errors.append(
                f"instance.status: expected {want_status}, got {got}{suffix}"
            )
    return errors


def _normalize(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return value

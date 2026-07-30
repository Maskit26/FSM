"""
Static checks for risky dynamic SQL in fsm_platform/.

Flags Python that builds SQL via f-string / concat / %-format / .format
when the string clearly contains a SQL verb (SELECT/INSERT/UPDATE/DELETE).

Whitelist: paths relative to repo root (forward slashes).
Exit 1 on findings.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = ROOT / "fsm_platform"

# SQL verb inside a string; avoid bare FROM/WHERE (too many English false positives).
_SQL_VERB = r"(?:SELECT|INSERT|UPDATE|DELETE)\b"

_FSTRING_SQL = re.compile(
    rf"""f["'][^"']*{_SQL_VERB}""",
    re.IGNORECASE,
)
_CONCAT_SQL = re.compile(
    rf"""["'][^"']*{_SQL_VERB}[^"']*["']\s*\+""",
    re.IGNORECASE,
)
_PERCENT_SQL = re.compile(
    rf"""["'][^"']*{_SQL_VERB}[^"']*["']\s*%\s*[^\n]*""",
    re.IGNORECASE,
)
_FORMAT_SQL = re.compile(
    rf"""["'][^"']*{_SQL_VERB}[^"']*["']\s*\.format\s*\(""",
    re.IGNORECASE,
)

# Reviewed exceptions: static column lists + bind params only (:name).
WHITELIST: set[str] = {
    # cols come from a closed whitelist in the same function; values are bound.
    "fsm_platform/core/transition_repository.py",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    rel = _rel(path)
    if rel in WHITELIST:
        return []
    findings: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [(0, "READ_ERROR", str(exc))]
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for name, rx in (
            ("FSTRING_SQL", _FSTRING_SQL),
            ("CONCAT_SQL", _CONCAT_SQL),
            ("PERCENT_SQL", _PERCENT_SQL),
            ("FORMAT_SQL", _FORMAT_SQL),
        ):
            if rx.search(line):
                findings.append((i, name, stripped[:200]))
                break
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCAN_ROOT,
        help="Directory to scan (default: fsm_platform/)",
    )
    args = parser.parse_args(argv)
    root: Path = args.root
    if not root.is_dir():
        print(f"scan root missing: {root}", file=sys.stderr)
        return 2

    all_findings: list[tuple[str, int, str, str]] = []
    for path in sorted(root.rglob("*.py")):
        for line_no, code, snippet in scan_file(path):
            all_findings.append((_rel(path), line_no, code, snippet))

    if not all_findings:
        print("OK: no risky dynamic SQL patterns under", root)
        return 0

    print(f"FAIL: {len(all_findings)} potential dynamic SQL issue(s):", file=sys.stderr)
    for path, line_no, code, snippet in all_findings:
        print(f"  {path}:{line_no}: [{code}] {snippet}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

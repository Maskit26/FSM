"""Классификация ошибок FSM-инстанса: retry vs terminal FAILED."""

from __future__ import annotations

import os
import re
from typing import Optional

# Сколько раз можно вернуть инстанс в PENDING (после этого — FAILED).
MAX_INSTANCE_ATTEMPTS = int(os.environ.get("FSM_INSTANCE_MAX_ATTEMPTS", "5"))

# Подстроки last_error → временная ошибка (можно retry).
_TRANSIENT_SUBSTRINGS = (
    "WORKER_CRASH",
    "DOMAIN_COMMIT_FAILED",
    "APPLY_FAILED",
    "Deadlock",
    "deadlock",
    "Lock wait timeout",
    "try restarting transaction",
    "ConnectionReset",
    "OperationalError",
    "InterfaceError",
    "TimeoutError",
    "timed out",
    "MySQL server has gone away",
    "Lost connection",
    "2013:",  # MySQL lost connection
    "2006:",  # MySQL server gone away
    "1213:",  # deadlock
    "EXTERNAL_API_TRANSIENT",  # call_api: timeout / 5xx / connection
)

# Явно постоянные коды — даже если попали под общий EFFECT_FAILED.
_PERMANENT_PATTERNS = (
    re.compile(r"NO_GUARD_MATCHED"),
    re.compile(r"NO_CANDIDATE_TRANSITIONS"),
    re.compile(r"STATE_MISMATCH"),
    re.compile(r"UNKNOWN_(PROCESS|GUARD|EFFECT)"),
    re.compile(r"ENTITY_STATE_NOT_FOUND"),
    re.compile(r"MISSING_"),
    re.compile(r"AMBIGUOUS_TRANSITION"),
    re.compile(r"INVALID_COMPANION"),
    re.compile(r"ALREADY_TAKEN"),
    re.compile(r"RESERVE_CELL_FAILED"),
    re.compile(r"ORDER_STATUS_CAS_FAILED"),
    re.compile(r"SYNC_LOCKER_STATUS_FAILED"),
    re.compile(r"CLEAR_STAGE_FAILED"),
    re.compile(r"NOT_A_(COURIER|DRIVER)"),
    re.compile(r"USER_NOT_FOUND"),
    re.compile(r"ORDER_NOT_FOUND"),
    re.compile(r"CELL_NOT_FREE"),
    re.compile(r"SAGA_"),
)


def is_transient_error(last_error: Optional[str]) -> bool:
    """True если ошибку имеет смысл повторить (инфраструктура / краш)."""
    err = str(last_error or "")
    if not err.strip():
        return False
    for pat in _PERMANENT_PATTERNS:
        if pat.search(err):
            return False
    return any(s in err for s in _TRANSIENT_SUBSTRINGS)


def backoff_seconds(attempts: int) -> int:
    """5s, 15s, 45s, … cap 15m (как outbox)."""
    return min(900, 5 * (3 ** max(0, attempts - 1)))


def should_retry(last_error: Optional[str], *, attempts_after: int) -> bool:
    """attempts_after — значение attempts после инкремента текущей неудачи."""
    if attempts_after >= MAX_INSTANCE_ATTEMPTS:
        return False
    return is_transient_error(last_error)

"""Correlation envelope для Public API (invoke / enqueue) и downstream."""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any, Optional

PAYLOAD_KEY = "_correlation"

_current: ContextVar[Optional["CorrelationEnvelope"]] = ContextVar(
    "correlation_envelope", default=None
)


@dataclass(frozen=True)
class CorrelationEnvelope:
    """
    command_id — id этого запроса/команды клиента
    correlation_id — id всей цепочки
    causation_id — id причины (предыдущая команда/событие), если есть
    idempotency_key — Idempotency-Key на enqueue (если был)
    """

    command_id: str
    correlation_id: str
    causation_id: Optional[str] = None
    idempotency_key: Optional[str] = None

    def to_public(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "commandId": self.command_id,
            "correlationId": self.correlation_id,
        }
        if self.causation_id:
            out["causationId"] = self.causation_id
        if self.idempotency_key:
            out["idempotencyKey"] = self.idempotency_key
        return out

    def to_storage(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "idempotency_key": self.idempotency_key,
        }

    def log_extra(self) -> dict[str, str]:
        extra = {
            "command_id": self.command_id,
            "correlation_id": self.correlation_id,
        }
        if self.causation_id:
            extra["causation_id"] = self.causation_id
        return extra


def new_id() -> str:
    return uuid.uuid4().hex


def current_envelope() -> Optional[CorrelationEnvelope]:
    return _current.get()


def bind_envelope(envelope: CorrelationEnvelope) -> Token:
    return _current.set(envelope)


def reset_envelope(token: Token) -> None:
    _current.reset(token)


def _pick(*values: Any) -> Optional[str]:
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s[:128]
    return None


def resolve_envelope(
    *,
    headers: Optional[dict[str, Any]] = None,
    body: Optional[dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
) -> CorrelationEnvelope:
    """
    Клиентские поля (header и/или body) + генерация недостающих.
    Headers: X-Command-Id, X-Correlation-Id, X-Causation-Id
    Body: commandId / correlationId / causationId (или snake_case).
    """
    h = {str(k).lower(): v for k, v in (headers or {}).items()}
    b = body if isinstance(body, dict) else {}
    nested = b.get("correlation") if isinstance(b.get("correlation"), dict) else {}

    idem = _pick(idempotency_key)
    command_id = _pick(
        h.get("x-command-id"),
        b.get("commandId"),
        b.get("command_id"),
        nested.get("commandId"),
        nested.get("command_id"),
        idem,
    ) or new_id()

    correlation_id = _pick(
        h.get("x-correlation-id"),
        b.get("correlationId"),
        b.get("correlation_id"),
        nested.get("correlationId"),
        nested.get("correlation_id"),
    ) or command_id

    causation_id = _pick(
        h.get("x-causation-id"),
        b.get("causationId"),
        b.get("causation_id"),
        nested.get("causationId"),
        nested.get("causation_id"),
    )

    return CorrelationEnvelope(
        command_id=command_id,
        correlation_id=correlation_id,
        causation_id=causation_id,
        idempotency_key=idem,
    )


def attach_to_payload(payload: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Кладёт envelope в payload инстанса (для worker → events/outbox)."""
    out = dict(payload or {})
    env = current_envelope()
    if env is None:
        return out
    out[PAYLOAD_KEY] = env.to_storage()
    return out


def envelope_from_payload(
    payload: Optional[dict[str, Any]],
) -> Optional[CorrelationEnvelope]:
    raw = (payload or {}).get(PAYLOAD_KEY)
    if not isinstance(raw, dict):
        return None
    cid = _pick(raw.get("command_id"), raw.get("commandId"))
    corr = _pick(raw.get("correlation_id"), raw.get("correlationId"))
    if not cid or not corr:
        return None
    return CorrelationEnvelope(
        command_id=cid,
        correlation_id=corr,
        causation_id=_pick(raw.get("causation_id"), raw.get("causationId")),
        idempotency_key=_pick(raw.get("idempotency_key"), raw.get("idempotencyKey")),
    )


def merge_into_dict(target: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Добавляет public-поля envelope в dict (ответ API / webhook body)."""
    out = dict(target or {})
    env = current_envelope()
    if env is None:
        return out
    out["correlation"] = env.to_public()
    return out


def event_ids_from_envelope(
    envelope: Optional[CorrelationEnvelope],
) -> tuple[Optional[str], Optional[str]]:
    """(correlation_id, client_request_id=command_id) для platform_events."""
    if envelope is None:
        return None, None
    return envelope.correlation_id, envelope.command_id


class CorrelationLogFilter(logging.Filter):
    """Добавляет correlation_id / command_id в LogRecord (пустые если нет envelope)."""

    def filter(self, record: logging.LogRecord) -> bool:
        env = current_envelope()
        if env is None:
            record.correlation_id = "-"  # type: ignore[attr-defined]
            record.command_id = "-"  # type: ignore[attr-defined]
            record.causation_id = "-"  # type: ignore[attr-defined]
        else:
            record.correlation_id = env.correlation_id  # type: ignore[attr-defined]
            record.command_id = env.command_id  # type: ignore[attr-defined]
            record.causation_id = env.causation_id or "-"  # type: ignore[attr-defined]
        return True


def install_correlation_logging() -> None:
    """Вешает filter на root handlers (идемпотентно).

    Filter только на Logger недостаточно: при propagate у child logger
    вызываются handlers родителя без filter родителя.
    """
    root = logging.getLogger()
    existing: CorrelationLogFilter | None = None
    for f in root.filters:
        if isinstance(f, CorrelationLogFilter):
            existing = f
            break
    filt = existing or CorrelationLogFilter()
    if existing is None:
        root.addFilter(filt)
    for h in root.handlers:
        if not any(isinstance(f, CorrelationLogFilter) for f in h.filters):
            h.addFilter(filt)

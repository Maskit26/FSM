"""
Bootstrap доменов платформы: GET /contract/v1/catalog → RAM-реестры → Domain Validator.

Платформа не импортирует доменный Python-код.
Bootstrap best-effort: сбой одного tenant не блокирует старт platform API.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from fsm_platform import ProcessDef
from fsm_platform.core.registry import (
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from fsm_platform.core.remote import (
    remote_command,
    remote_context,
    remote_effect,
    remote_guard,
    remote_on_failed,
    remote_query,
)
from fsm_platform.host.tenant.domain_validator import (
    DomainValidationError,
    default_domain_validator,
)
from fsm_platform.host.runtime.engines import graph_session, platform_session
from fsm_platform.host.tenant.hook_registry import default_webhook_registry
from fsm_platform.host.tenant.operations import default_operation_registry

logger = logging.getLogger(__name__)


@dataclass
class DomainBootstrapStatus:
    """Состояние подключения tenant domain service (in-memory, per process)."""

    service_id: str
    ok: bool = False
    error: Optional[str] = None
    checked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    stats: dict[str, Any] = field(default_factory=dict)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_id": self.service_id,
            "ok": self.ok,
            "error": self.error,
            "checked_at": self.checked_at,
            "stats": self.stats,
            "warnings": list(self.warnings),
        }


_bootstrap_status: dict[str, DomainBootstrapStatus] = {}


def get_bootstrap_status(service_id: Optional[str] = None) -> dict[str, Any]:
    """Статус bootstrap tenant(ов). None → все известные."""
    if service_id is not None:
        sid = str(service_id).strip()
        st = _bootstrap_status.get(sid)
        return st.to_dict() if st else {"service_id": sid, "ok": False, "error": "NOT_BOOTSTRAPPED"}
    return {sid: st.to_dict() for sid, st in sorted(_bootstrap_status.items())}


def is_domain_ready(service_id: str) -> bool:
    st = _bootstrap_status.get(str(service_id).strip())
    return bool(st and st.ok)


def _unregister_service(service_id: str) -> None:
    default_guard_registry.unregister(service_id)
    default_effect_registry.unregister(service_id)
    default_process_registry.unregister(service_id)
    default_operation_registry.unregister(service_id)
    default_webhook_registry.unregister(service_id)


def register_catalog(service_id: str, catalog: dict[str, Any]) -> None:
    """Наполняет RAM-реестры из ответа Contract API catalog."""
    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id is required")

    _unregister_service(sid)

    for op in catalog.get("operations") or []:
        if not isinstance(op, dict):
            continue
        name = str(op.get("operation") or "").strip()
        kind = str(op.get("kind") or "").strip()
        if not name or kind not in ("command", "query"):
            continue
        ref = remote_command(sid, name) if kind == "command" else remote_query(sid, name)
        default_operation_registry.register(sid, name, kind, ref)

    for gname in catalog.get("guards") or []:
        name = str(gname or "").strip()
        if name:
            default_guard_registry.register(sid, name, remote_guard(sid, name))

    for ename in catalog.get("effects") or []:
        name = str(ename or "").strip()
        if name:
            default_effect_registry.register(sid, name, remote_effect(sid, name))

    for proc in catalog.get("processes") or []:
        if not isinstance(proc, dict):
            continue
        process_name = str(proc.get("process_name") or "").strip()
        if not process_name:
            continue
        cb_name = str(proc.get("context_builder") or "").strip()
        on_failed_flag = bool(proc.get("on_failed"))
        default_process_registry.register(
            ProcessDef(
                service_id=sid,
                process_name=process_name,
                entity_type=str(proc.get("entity_type") or "") or None,
                event_name=str(proc.get("event_name") or "") or None,
                initial_state=str(proc.get("initial_state") or "") or None,
                context_builder=remote_context(sid, cb_name) if cb_name else None,
                on_failed=remote_on_failed(sid, process_name)
                if on_failed_flag
                else None,
            )
        )

    for channel in catalog.get("hooks") or []:
        ch = str(channel or "").strip().lower()
        if ch:
            default_webhook_registry.register_channel(sid, ch)


def _record_status(
    service_id: str,
    *,
    ok: bool,
    error: Optional[str] = None,
    stats: Optional[dict[str, Any]] = None,
    warnings: Optional[list[dict[str, Any]]] = None,
) -> DomainBootstrapStatus:
    st = DomainBootstrapStatus(
        service_id=service_id,
        ok=ok,
        error=error,
        stats=dict(stats or {}),
        warnings=list(warnings or []),
    )
    _bootstrap_status[service_id] = st
    return st


def bootstrap_domain(service_id: str, *, raise_on_error: bool = False) -> bool:
    """
    Catalog remote-домена + Domain Validator.
    Returns True если tenant готов к invoke/FSM.
    По умолчанию не бросает — platform продолжает работать.
    """
    from fsm_platform.host.contract.contract_client import get_contract_client
    from fsm_platform.host.tenant.domain_validator import ValidationReport

    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id is required")

    logger.info("bootstrap domain service_id=%s (contract catalog)", sid)
    try:
        catalog = get_contract_client(sid).catalog()
    except Exception as exc:
        msg = f"CATALOG_FETCH_FAILED: {exc}"
        _record_status(sid, ok=False, error=msg)
        logger.warning("domain bootstrap skipped service_id=%s: %s", sid, msg)
        if raise_on_error:
            report = ValidationReport(service_id=sid)
            report.add_error("CATALOG_FETCH_FAILED", str(exc))
            raise DomainValidationError(report) from exc
        return False

    if not isinstance(catalog, dict):
        msg = "CATALOG_INVALID: expected JSON object"
        _record_status(sid, ok=False, error=msg)
        logger.warning("domain bootstrap skipped service_id=%s: %s", sid, msg)
        if raise_on_error:
            report = ValidationReport(service_id=sid)
            report.add_error("CATALOG_INVALID", "expected JSON object")
            raise DomainValidationError(report)
        return False

    register_catalog(sid, catalog)

    session_graph = _try_graph_session(sid)
    try:
        report = default_domain_validator.validate(
            sid,
            catalog=catalog,
            session_graph=session_graph,
        )
    finally:
        if session_graph is not None:
            session_graph.close()

    if not report.ok:
        err = "; ".join(e.code for e in report.errors) or "VALIDATION_FAILED"
        _record_status(
            sid,
            ok=False,
            error=err,
            stats=report.stats,
            warnings=[w.to_dict() for w in report.warnings],
        )
        logger.warning(
            "domain validation failed service_id=%s errors=%s",
            sid,
            report.to_dict()["errors"],
        )
        if raise_on_error:
            raise DomainValidationError(report)
        return False

    warn_dicts = [w.to_dict() for w in report.warnings]
    if warn_dicts:
        logger.warning(
            "domain validation warnings service_id=%s warnings=%s",
            sid,
            warn_dicts,
        )
    _record_status(sid, ok=True, stats=report.stats, warnings=warn_dicts)
    logger.info(
        "domain bootstrap ok service_id=%s stats=%s",
        sid,
        report.stats,
    )
    return True


def _list_service_ids(service_id: Optional[str] = None) -> list[str]:
    ids: list[str] = []
    try:
        from fsm_platform.core.db_layer import default_db_layer

        sp = platform_session()
        try:
            for row in default_db_layer.list_active_domain_services(
                sp, service_id=service_id
            ):
                ids.append(str(row["service_id"]))
        finally:
            sp.close()
    except Exception:
        logger.warning("platform DB unavailable — no tenants from domain_services")

    return ids


def _try_graph_session(service_id: str) -> Optional[object]:
    try:
        return graph_session(service_id)
    except (KeyError, RuntimeError):
        logger.warning(
            "no graph engine for %s — Validator skips graph DB checks",
            service_id,
        )
        return None


def bootstrap_active_domains(*, service_id: Optional[str] = None) -> None:
    """
    Best-effort bootstrap всех active domain_services.
    Ошибки логируются; platform API/worker стартуют в любом случае.
    """
    service_ids = _list_service_ids(service_id)
    if not service_ids:
        logger.info("no active domain_services — platform starts without remote domains")
        return
    ok_count = 0
    for sid in service_ids:
        if bootstrap_domain(sid):
            ok_count += 1
    logger.info(
        "domain bootstrap finished: %s/%s tenants ready",
        ok_count,
        len(service_ids),
    )


def reload_domain(service_id: str) -> dict[str, Any]:
    """
    Повторный bootstrap одного tenant (admin / после старта domain service).
    Raises DomainValidationError при неудаче.
    """
    sid = str(service_id or "").strip()
    if not sid:
        raise ValueError("service_id is required")
    bootstrap_domain(sid, raise_on_error=True)
    return get_bootstrap_status(sid)

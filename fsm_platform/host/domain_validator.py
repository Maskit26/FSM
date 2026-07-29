"""Domain Validator: catalog ↔ RAM-реестры и FSM-граф (SQL) для remote domain."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text

from fsm_platform.core.registry import (
    EffectRegistry,
    GuardRegistry,
    ProcessRegistry,
    default_effect_registry,
    default_guard_registry,
    default_process_registry,
)
from fsm_platform.core.transition_repository import TransitionRepository
from fsm_platform.core.types import ProcessDef
from fsm_platform.core.remote import RemoteRef
from fsm_platform.host.operations import OperationRegistry, default_operation_registry

logger = logging.getLogger(__name__)

_OPERATION_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass
class ValidationIssue:
    """Одна ошибка или предупреждение Validator."""

    code: str
    message: str
    where: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализация в JSON-отчёт."""
        d: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.where:
            d["where"] = self.where
        return d


@dataclass
class ValidationReport:
    """Результат Domain Validator для одного service_id."""

    service_id: str
    cartridge_type: Optional[str] = None
    ok: bool = True
    checked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add_error(
        self, code: str, message: str, where: Optional[str] = None
    ) -> None:
        """Добавляет fail-issue и помечает отчёт как неуспешный."""
        self.errors.append(ValidationIssue(code, message, where))
        self.ok = False

    def add_warning(
        self, code: str, message: str, where: Optional[str] = None
    ) -> None:
        """Добавляет warning (не блокирует active)."""
        self.warnings.append(ValidationIssue(code, message, where))

    def to_dict(self) -> dict[str, Any]:
        """Формат validation_report из §7.9."""
        return {
            "service_id": self.service_id,
            "cartridge_type": self.cartridge_type,
            "ok": self.ok,
            "checked_at": self.checked_at,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "stats": self.stats,
        }


class DomainValidationError(Exception):
    """Boot/Accept останавливается: домен не прошёл Validator."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__(
            f"domain validation failed service_id={report.service_id}: "
            f"{[e.code for e in report.errors]}"
        )


class DomainValidator:
    """
    Проверяет catalog ↔ RAM-реестры и FSM-граф (SQL) для remote domain service.
    Не исполняет handlers и не читает Python-пакет домена.
    """
    def __init__(
        self,
        *,
        operations: Optional[OperationRegistry] = None,
        processes: Optional[ProcessRegistry] = None,
        guards: Optional[GuardRegistry] = None,
        effects: Optional[EffectRegistry] = None,
        transition_repo: Optional[TransitionRepository] = None,
    ) -> None:
        self._ops = operations or default_operation_registry
        self._processes = processes or default_process_registry
        self._guards = guards or default_guard_registry
        self._effects = effects or default_effect_registry
        self._repo = transition_repo or TransitionRepository()

    def validate(
        self,
        service_id: str,
        *,
        catalog: dict[str, Any],
        session_graph: Any = None,
    ) -> ValidationReport:
        """Catalog → RAM → (опционально) graph DB."""
        report = ValidationReport(service_id=service_id)
        report.cartridge_type = str(catalog.get("cartridge_type") or "") or None

        self._validate_catalog(report, catalog)
        self._validate_catalog_vs_ram(report, service_id, catalog)
        self._validate_ram(report, service_id)

        if session_graph is not None and report.ok:
            self._validate_graph_db(report, service_id, session_graph)

        ops = self._ops.items(service_id)
        procs = self._processes.list_for_service(service_id)
        report.stats = {
            "operations": len(ops),
            "processes": len(procs),
            "guards": len(self._guards.list_names(service_id)),
            "effects": len(self._effects.list_names(service_id)),
            "transitions_scanned": report.stats.get("transitions_scanned", 0),
        }
        return report

    def validate_or_raise(self, *args: Any, **kwargs: Any) -> ValidationReport:
        """Как validate, но при errors бросает DomainValidationError."""
        report = self.validate(*args, **kwargs)
        if not report.ok:
            raise DomainValidationError(report)
        return report

    def _validate_catalog(
        self, report: ValidationReport, catalog: dict[str, Any]
    ) -> None:
        for key in ("cartridge_type", "version"):
            if not str(catalog.get(key) or "").strip():
                report.add_error(
                    "CATALOG_INVALID",
                    f"catalog missing required field {key!r}",
                )

    def _validate_catalog_vs_ram(
        self,
        report: ValidationReport,
        service_id: str,
        catalog: dict[str, Any],
    ) -> None:
        """Catalog (Contract API) ↔ RAM после register_catalog."""
        catalog_ops: dict[str, str] = {}
        for item in catalog.get("operations") or []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("operation") or "").strip()
            kind = str(item.get("kind") or "").strip()
            if name:
                catalog_ops[name] = kind

        ram_ops = {
            str(item["operation"]): str(item["kind"])
            for item in self._ops.items(service_id)
        }
        for name, kind in catalog_ops.items():
            if name not in ram_ops:
                report.add_error(
                    "CATALOG_OPERATION_NOT_REGISTERED",
                    f"catalog operation {name!r} missing in OperationRegistry",
                )
            elif ram_ops[name] != kind:
                report.add_error(
                    "CATALOG_OPERATION_KIND_MISMATCH",
                    f"operation {name!r}: catalog kind={kind!r} ram={ram_ops[name]!r}",
                )
        for name in sorted(set(ram_ops) - set(catalog_ops)):
            report.add_warning(
                "RAM_OPERATION_NOT_IN_CATALOG",
                f"operation {name!r} registered but absent from catalog",
            )

        catalog_guards = {
            str(g).strip()
            for g in (catalog.get("guards") or [])
            if str(g or "").strip()
        }
        catalog_effects = {
            str(e).strip()
            for e in (catalog.get("effects") or [])
            if str(e or "").strip()
        }
        ram_guards = set(self._guards.list_names(service_id))
        ram_effects = set(self._effects.list_names(service_id))

        for g in sorted(catalog_guards - ram_guards):
            report.add_error(
                "CATALOG_GUARD_NOT_REGISTERED",
                f"catalog guard {g!r} missing in GuardRegistry",
            )
        for e in sorted(catalog_effects - ram_effects):
            report.add_error(
                "CATALOG_EFFECT_NOT_REGISTERED",
                f"catalog effect {e!r} missing in EffectRegistry",
            )

        catalog_processes: dict[str, dict[str, Any]] = {}
        for proc in catalog.get("processes") or []:
            if not isinstance(proc, dict):
                continue
            pname = str(proc.get("process_name") or "").strip()
            if pname:
                catalog_processes[pname] = proc

        ram_processes = {
            p.process_name: p for p in self._processes.list_for_service(service_id)
        }
        for pname, proc in catalog_processes.items():
            if pname not in ram_processes:
                report.add_error(
                    "CATALOG_PROCESS_NOT_REGISTERED",
                    f"catalog process {pname!r} missing in ProcessRegistry",
                )
                continue
            ram_p = ram_processes[pname]
            cb = str(proc.get("context_builder") or "").strip()
            if cb and ram_p.context_builder is not None:
                if ram_p.context_builder.name != cb:
                    report.add_error(
                        "CATALOG_CONTEXT_BUILDER_MISMATCH",
                        f"process {pname!r}: catalog context_builder={cb!r} "
                        f"ram={ram_p.context_builder.name!r}",
                    )
            if bool(proc.get("on_failed")) and ram_p.on_failed is None:
                report.add_error(
                    "CATALOG_ON_FAILED_MISMATCH",
                    f"process {pname!r}: catalog on_failed=true but RAM has none",
                )

        for pname in sorted(set(ram_processes) - set(catalog_processes)):
            report.add_warning(
                "RAM_PROCESS_NOT_IN_CATALOG",
                f"process {pname!r} registered but absent from catalog",
            )

    def _validate_ram(self, report: ValidationReport, service_id: str) -> None:
        ops = self._ops.items(service_id)
        procs = self._processes.list_for_service(service_id)

        if not ops and not procs:
            report.add_error(
                "EMPTY_REGISTRATION",
                "no operations and no ProcessDef registered",
            )
            return

        for item in ops:
            name = str(item["operation"])
            kind = str(item["kind"])
            handler = item["handler"]
            if not _OPERATION_NAME_RE.match(name):
                report.add_error(
                    "INVALID_OPERATION_NAME",
                    f"operation name {name!r} must match [a-z][a-z0-9_]*",
                )
            if kind not in ("query", "command"):
                report.add_error(
                    "INVALID_OPERATION_KIND",
                    f"operation {name!r} has kind={kind!r}",
                )
            if not isinstance(handler, RemoteRef):
                report.add_error(
                    "OPERATION_HANDLER_NOT_REMOTE",
                    f"operation {name!r} handler must be RemoteRef",
                )

        for p in procs:
            self._validate_process_def(report, service_id, p)

        for gname in self._guards.list_names(service_id):
            fn = self._guards.get(service_id, gname)
            if not isinstance(fn, RemoteRef):
                report.add_error(
                    "GUARD_NOT_REMOTE",
                    f"guard {gname!r} must be RemoteRef",
                )
        for ename in self._effects.list_names(service_id):
            fn = self._effects.get(service_id, ename)
            if not isinstance(fn, RemoteRef):
                report.add_error(
                    "EFFECT_NOT_REMOTE",
                    f"effect {ename!r} must be RemoteRef",
                )

    def _validate_process_def(
        self, report: ValidationReport, service_id: str, p: ProcessDef
    ) -> None:
        if p.service_id != service_id:
            report.add_error(
                "SERVICE_ID_MISMATCH",
                f"ProcessDef.service_id={p.service_id!r} != register arg {service_id!r}",
                where=p.process_name,
            )
        missing = []
        if not p.process_name:
            missing.append("process_name")
        if not p.entity_type:
            missing.append("entity_type")
        if not (p.event_name or p.process_name):
            missing.append("event_name")
        if p.context_builder is None:
            missing.append("context_builder")
        if missing:
            report.add_error(
                "PROCESS_FIELDS_MISSING",
                f"ProcessDef {p.process_name!r} missing: {', '.join(missing)}",
            )
        if p.context_builder is not None and not isinstance(
            p.context_builder, RemoteRef
        ):
            report.add_error(
                "CONTEXT_BUILDER_NOT_REMOTE",
                f"ProcessDef {p.process_name!r} context_builder must be RemoteRef",
            )
        if p.on_failed is not None and not isinstance(p.on_failed, RemoteRef):
            report.add_error(
                "ON_FAILED_NOT_REMOTE",
                f"ProcessDef {p.process_name!r} on_failed must be RemoteRef",
            )

    def _validate_graph_db(
        self,
        report: ValidationReport,
        service_id: str,
        session_graph: Any,
    ) -> None:
        self._validate_domain_db(
            report,
            service_id,
            session_graph,
            graph_scope="registered_processes",
            required_tables=[],
            required_routines=[],
        )

    def _validate_domain_db(
        self,
        report: ValidationReport,
        service_id: str,
        session_domain: Any,
        *,
        graph_scope: str,
        required_tables: list[str],
        required_routines: list[str],
    ) -> None:
        try:
            session_domain.execute(text("SELECT 1"))
        except Exception as exc:  # noqa: BLE001
            report.add_error("DB_CONNECT_FAILED", str(exc))
            return

        if not self._repo._has_table(session_domain, "fsm_transitions"):
            report.add_error(
                "FSM_TABLE_MISSING",
                "fsm_transitions not found in domain DB",
            )
            return
        if not self._repo._has_table(session_domain, "fsm_states"):
            report.add_error(
                "FSM_TABLE_MISSING",
                "fsm_states not found in domain DB",
            )
            return
        if not (
            self._repo._has_table(session_domain, "fsm_events")
            or self._repo._has_table(session_domain, "fsm_actions")
        ):
            report.add_error(
                "FSM_TABLE_MISSING",
                "neither fsm_events nor fsm_actions found in domain DB",
            )
            return

        for table in required_tables:
            if table in ("fsm_states", "fsm_transitions", "fsm_events", "fsm_actions"):
                continue
            if not self._repo._has_table(session_domain, table):
                report.add_error(
                    "REQUIRED_TABLE_MISSING",
                    f"required table {table!r} missing",
                    where=table,
                )

        for routine in required_routines:
            if not self._routine_exists(session_domain, routine):
                report.add_error(
                    "REQUIRED_ROUTINE_MISSING",
                    f"required routine {routine!r} missing",
                    where=routine,
                )

        procs = self._processes.list_for_service(service_id)
        guards_ram = set(self._guards.list_names(service_id))
        effects_ram = set(self._effects.list_names(service_id))

        transitions_scanned = 0
        graph_guards: set[str] = set()
        graph_effects: set[str] = set()

        if graph_scope == "all":
            g, e = self._repo.list_guard_effect_names(session_domain)
            graph_guards |= g
            graph_effects |= e
            # count approximate
            transitions_scanned = -1
        else:
            # registered_processes (default): только рёбра зарегистрированных ProcessDef
            for p in procs:
                et = p.entity_type or ""
                ev = p.runtime_event_name
                rows = self._repo.list_transitions_for_event(
                    session_domain, et, ev
                )
                transitions_scanned += len(rows)
                if not rows:
                    report.add_error(
                        "NO_CANDIDATES_FOR_PROCESS",
                        f"no transitions for entity_type={et!r} event={ev!r}",
                        where=p.process_name,
                    )
                    continue
                self._check_default_guards(report, rows, p.process_name)
                for r in rows:
                    gn = r.get("guard_name")
                    en = r.get("effect_name")
                    if gn is not None and str(gn).strip():
                        graph_guards.add(str(gn).strip())
                    if en is not None and str(en).strip():
                        graph_effects.add(str(en).strip())

                if p.initial_state:
                    names = set(self._repo.list_state_names(session_domain, et))
                    if names and p.initial_state not in names:
                        # fallback: all states without entity_type filter
                        names = set(self._repo.list_state_names(session_domain))
                    if names and p.initial_state not in names:
                        report.add_error(
                            "INITIAL_STATE_UNKNOWN",
                            f"initial_state={p.initial_state!r} not in fsm_states",
                            where=p.process_name,
                        )

                initials = self._repo.get_initial_state(session_domain, et)
                if len(initials) > 1:
                    report.add_error(
                        "AMBIGUOUS_INITIAL_STATE",
                        f"entity_type={et!r} has {len(initials)} is_initial states",
                        where=p.process_name,
                    )

        report.stats["transitions_scanned"] = transitions_scanned

        for g in sorted(graph_guards):
            if g not in guards_ram:
                report.add_error(
                    "UNKNOWN_GUARD_IN_GRAPH",
                    f"guard_name={g!r} not in GuardRegistry",
                    where=f"service_id={service_id}",
                )
        for e in sorted(graph_effects):
            if e not in effects_ram:
                report.add_error(
                    "UNKNOWN_EFFECT_IN_GRAPH",
                    f"effect_name={e!r} not in EffectRegistry",
                    where=f"service_id={service_id}",
                )

        for g in sorted(guards_ram - graph_guards):
            report.add_warning(
                "ORPHAN_GUARD_IN_REGISTRY",
                f"guard {g!r} registered but unused in validated graph scope",
            )
        for e in sorted(effects_ram - graph_effects):
            report.add_warning(
                "ORPHAN_EFFECT_IN_REGISTRY",
                f"effect {e!r} registered but unused in validated graph scope",
            )

    def _check_default_guards(
        self,
        report: ValidationReport,
        rows: list[dict],
        process_name: str,
    ) -> None:
        """AMBIGUOUS_DEFAULT_GUARD / DEFAULT_GUARD_PRIORITY на наборах кандидатов."""
        from collections import defaultdict

        groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
        for r in rows:
            key = (
                str(r.get("entity_type")),
                str(r.get("from_state")),
                str(r.get("event_name")),
            )
            groups[key].append(r)

        for key, candidates in groups.items():
            nulls = [
                c
                for c in candidates
                if c.get("guard_name") is None
                or str(c.get("guard_name") or "").strip() == ""
            ]
            if len(nulls) > 1:
                report.add_error(
                    "AMBIGUOUS_DEFAULT_GUARD",
                    f"more than one NULL guard for {key}",
                    where=process_name,
                )
                continue
            if len(nulls) == 1:
                null_pri = int(nulls[0].get("priority") or 0)
                max_pri = max(int(c.get("priority") or 0) for c in candidates)
                if null_pri < max_pri:
                    report.add_error(
                        "DEFAULT_GUARD_PRIORITY",
                        f"NULL guard priority={null_pri} < max={max_pri} for {key}",
                        where=f"{process_name}/transition:{nulls[0].get('id')}",
                    )

    @staticmethod
    def _routine_exists(session: Any, routine: str) -> bool:
        from sqlalchemy import text

        row = session.execute(
            text(
                """
                SELECT 1 FROM information_schema.routines
                WHERE routine_schema = DATABASE()
                  AND routine_name = :n
                LIMIT 1
                """
            ),
            {"n": routine},
        ).first()
        return row is not None


default_domain_validator = DomainValidator()

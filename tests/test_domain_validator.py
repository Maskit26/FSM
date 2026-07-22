"""Unit tests for Domain Validator (без domain DB)."""

from __future__ import annotations

from pathlib import Path

from fsm_platform import ProcessDef
from fsm_platform.core.registry import EffectRegistry, GuardRegistry, ProcessRegistry
from fsm_platform.core.types import EffectResult, GuardResult
from fsm_platform.host.domain_validator import DomainValidator, load_manifest
from fsm_platform.host.operations import OperationRegistry


def _ok_guard(*_a, **_k):
    return GuardResult(ok=True)


def _ok_effect(*_a, **_k):
    return EffectResult(ok=True)


def _ctx(*_a, **_k):
    return {}


def test_load_courier_manifest():
    root = Path(__file__).resolve().parents[1]
    man = load_manifest(root / "domains" / "courier")
    assert man["cartridge_type"] == "courier"
    assert man["entry"].endswith("register_all")
    assert man["graph_scope"] == "registered_processes"
    assert "orders" in man["required_tables"]


def test_validator_ram_ok():
    ops = OperationRegistry()
    procs = ProcessRegistry()
    guards = GuardRegistry()
    effects = EffectRegistry()

    def list_q(session, params, actor):
        return []

    ops.register("svc_t", "list_things", "query", list_q)
    procs.register(
        ProcessDef(
            service_id="svc_t",
            process_name="do_thing",
            entity_type="order",
            event_name="do_thing_event",
            context_builder=_ctx,
            initial_state="order_created",
        )
    )
    guards.register("svc_t", "can_do", _ok_guard)
    effects.register("svc_t", "do_effect", _ok_effect)

    v = DomainValidator(
        operations=ops, processes=procs, guards=guards, effects=effects
    )
    report = v.validate(
        "svc_t",
        manifest={
            "cartridge_type": "test",
            "version": "0.0.1",
            "entry": "domains.courier.processes:register_all",
            "graph_scope": "registered_processes",
            "required_modules": [],
        },
        package_dir=Path(__file__).resolve().parents[1] / "domains" / "courier",
        session_domain=None,
    )
    assert report.ok, report.to_dict()
    assert report.stats["operations"] == 1
    assert report.stats["processes"] == 1


def test_validator_empty_registration():
    v = DomainValidator(
        operations=OperationRegistry(),
        processes=ProcessRegistry(),
        guards=GuardRegistry(),
        effects=EffectRegistry(),
    )
    report = v.validate(
        "svc_empty",
        manifest={
            "cartridge_type": "x",
            "version": "1",
            "entry": "domains.courier.processes:register_all",
            "required_modules": [],
        },
        package_dir=Path(__file__).resolve().parents[1] / "domains" / "courier",
    )
    assert not report.ok
    assert any(e.code == "EMPTY_REGISTRATION" for e in report.errors)


def test_validator_invalid_kind_caught_at_register():
    ops = OperationRegistry()
    try:
        ops.register("svc", "bad", "mutation", lambda *a: None)  # type: ignore[arg-type]
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_courier_register_all_passes_ram_validator():
    from domains.courier.processes import register_all
    from fsm_platform.core import registry as reg
    from fsm_platform.host import operations as ops_mod
    from fsm_platform.host.domain_validator import DomainValidator

    reg.default_process_registry.unregister("svc_courier_test")
    reg.default_guard_registry.unregister("svc_courier_test")
    reg.default_effect_registry.unregister("svc_courier_test")
    ops_mod.default_operation_registry.unregister("svc_courier_test")

    register_all("svc_courier_test")
    report = DomainValidator().validate(
        "svc_courier_test",
        entry="domains.courier.processes:register_all",
        session_domain=None,
    )
    assert report.ok, report.to_dict()
    assert report.stats["operations"] == 9
    assert report.stats["processes"] == 3
    names = set(reg.default_process_registry.list_process_names("svc_courier_test"))
    assert names == {"assign_executor", "remove_executor", "open_cell"}

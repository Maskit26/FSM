"""Unit tests without DB."""

from __future__ import annotations

from fsm_platform.core.registry import GuardRegistry, ProcessRegistry
from fsm_platform.core.types import (
    GuardResult,
    ProcessDef,
    normalize_effect_result,
    normalize_guard_result,
)


def test_process_def_service_id_and_event():
    p = ProcessDef(
        service_id="svc_1",
        process_name="create",
        entity_type="order",
        event_name=None,
    )
    assert p.runtime_event_name == "create"
    reg = ProcessRegistry()
    reg.register(p)
    assert reg.get("svc_1", "create") is p
    assert reg.has("svc_1", "missing") is False


def test_normalize_guard_result():
    assert normalize_guard_result(True).ok is True
    assert normalize_guard_result(False).ok is False
    assert normalize_guard_result(GuardResult(ok=True)).ok is True
    assert normalize_guard_result((False, "nope")).reason == "nope"


def test_normalize_effect_result():
    assert normalize_effect_result(True).ok is True
    assert normalize_effect_result({"ok": False, "error": "x"}).error == "x"


def test_guard_registry_per_service():
    g = GuardRegistry()

    def ok(*_a, **_k):
        return GuardResult(ok=True)

    g.register("svc_a", "can", ok)
    assert g.get("svc_a", "can") is ok
    assert g.get("svc_b", "can") is None

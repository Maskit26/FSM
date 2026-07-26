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


class _MemStateStore:
    def __init__(self, states: dict[tuple[str, str, int], str]):
        self.states = dict(states)

    def get(self, _sp, service_id, entity_type, entity_id, *, for_update: bool = False):
        _ = for_update
        return self.states.get((service_id, entity_type, int(entity_id)))


class _MemRepo:
    def __init__(self, by_key: dict[tuple[str, str, str], list]):
        self.by_key = by_key

    def list_candidates(self, _sd, entity_type, from_state, event_name):
        return list(self.by_key.get((entity_type, from_state, event_name), []))


class _MemExecutor:
    def __init__(self, store: _MemStateStore):
        self.store = store
        self.applied: list[tuple[str, int, str]] = []

    def apply(self, _sp, *, service_id, entity_type, entity_id, transition, **_k):
        key = (service_id, entity_type, int(entity_id))
        self.store.states[key] = transition.to_state
        self.applied.append((entity_type, int(entity_id), transition.to_state))


def test_transition_runner_companions_success():
    from fsm_platform.core.errors import FsmErrorCodes
    from fsm_platform.core.registry import EffectRegistry, GuardRegistry
    from fsm_platform.core.transition_runner import TransitionRunner
    from fsm_platform.core.types import EffectResult, ProcessDef, TransitionDef

    _ = FsmErrorCodes
    order_edge = TransitionDef(
        id=1,
        entity_type="order",
        from_state="order_a",
        to_state="order_b",
        event_name="open_cell",
        effect_name="order_effect",
        effect_params={
            "leg": "pickup",
            "companions": [
                {
                    "entity_type": "locker",
                    "event_name": "locker_open_locker",
                    "entity_id_key": "cell_id",
                }
            ],
        },
    )
    locker_edge = TransitionDef(
        id=2,
        entity_type="locker",
        from_state="locker_reserved",
        to_state="locker_opened",
        event_name="locker_open_locker",
        effect_name="locker_effect",
        effect_params={},
    )

    store = _MemStateStore(
        {
            ("svc", "order", 10): "order_a",
            ("svc", "locker", 99): "locker_reserved",
        }
    )
    repo = _MemRepo(
        {
            ("order", "order_a", "open_cell"): [order_edge],
            ("locker", "locker_reserved", "locker_open_locker"): [locker_edge],
        }
    )
    executor = _MemExecutor(store)
    effects = EffectRegistry()
    calls: list[str] = []

    def order_effect(_sd, _db, ctx, _inst, params):
        assert "companions" not in params
        assert ctx["to_state"] == "order_b"
        calls.append("order")
        return EffectResult(ok=True, payload={"order": True})

    def locker_effect(_sd, _db, ctx, _inst, _params):
        assert ctx["applied_entity_type"] == "locker"
        assert ctx["to_state"] == "locker_opened"
        calls.append("locker")
        return EffectResult(ok=True, payload={"locker": True})

    effects.register("svc", "order_effect", order_effect)
    effects.register("svc", "locker_effect", locker_effect)

    runner = TransitionRunner(
        GuardRegistry(),
        effects,
        store,
        repo,
        executor,
    )
    result = runner.run(
        session_platform=None,
        session_domain=None,
        db={},
        runtime_ctx={},
        instance={
            "id": 1,
            "service_id": "svc",
            "entity_type": "order",
            "entity_id": 10,
            "actor_id": 5,
        },
        process_def=ProcessDef(
            service_id="svc",
            process_name="open_cell",
            entity_type="order",
            event_name="open_cell",
            context_builder=lambda *_a, **_k: {"cell_id": 99, "leg": "pickup"},
        ),
    )
    assert result.new_state == "COMPLETED", result.last_error
    assert calls == ["order", "locker"]
    assert executor.applied == [
        ("order", 10, "order_b"),
        ("locker", 99, "locker_opened"),
    ]
    assert result.payload["companions"][0]["entity_id"] == 99
    assert result.payload["companions"][0]["to_state"] == "locker_opened"


def test_transition_runner_companion_fail_returns_failed():
    from fsm_platform.core.errors import FsmErrorCodes
    from fsm_platform.core.registry import EffectRegistry, GuardRegistry
    from fsm_platform.core.transition_runner import TransitionRunner
    from fsm_platform.core.types import EffectResult, ProcessDef, TransitionDef

    order_edge = TransitionDef(
        id=1,
        entity_type="order",
        from_state="order_a",
        to_state="order_b",
        event_name="open_cell",
        effect_name="order_effect",
        effect_params={
            "companions": [
                {
                    "entity_type": "locker",
                    "event_name": "locker_open_locker",
                    "entity_id_key": "cell_id",
                }
            ],
        },
    )
    store = _MemStateStore({("svc", "order", 10): "order_a"})
    repo = _MemRepo({("order", "order_a", "open_cell"): [order_edge]})
    executor = _MemExecutor(store)
    effects = EffectRegistry()
    effects.register(
        "svc",
        "order_effect",
        lambda *_a, **_k: EffectResult(ok=True),
    )
    runner = TransitionRunner(
        GuardRegistry(), effects, store, repo, executor
    )
    result = runner.run(
        None,
        None,
        {},
        {},
        {
            "id": 1,
            "service_id": "svc",
            "entity_type": "order",
            "entity_id": 10,
        },
        ProcessDef(
            service_id="svc",
            process_name="open_cell",
            entity_type="order",
            event_name="open_cell",
            context_builder=lambda *_a, **_k: {"cell_id": 99},
        ),
    )
    assert result.new_state == "FAILED"
    assert FsmErrorCodes.COMPANION_FAILED in (result.last_error or "")
    assert FsmErrorCodes.ENTITY_STATE_NOT_FOUND in (result.last_error or "")
# --- Block 0: CAS / race tests ---

class _CasDbLayer:
    """In-memory db_layer stub for TransitionExecutor CAS tests."""

    def __init__(self, state: str):
        self.state = state
        self.cas_calls: list[tuple[str, str]] = []
        self.logs: list[dict] = []

    def get_entity_state(self, _sp, service_id, entity_type, entity_id, *, for_update=False):
        _ = (service_id, entity_type, entity_id, for_update)
        return self.state

    def cas_entity_state(
        self, _sp, service_id, entity_type, entity_id, *, from_state, to_state
    ):
        _ = (service_id, entity_type, entity_id)
        self.cas_calls.append((from_state, to_state))
        if self.state != from_state:
            return False
        self.state = to_state
        return True

    def insert_transition_log(self, _sp, **kwargs):
        self.logs.append(kwargs)

    def insert_transition_log_idempotent(self, _sp, **kwargs):
        self.logs.append(kwargs)
        return True


def test_transition_executor_cas_success():
    from fsm_platform.core.transition_executor import TransitionExecutor
    from fsm_platform.core.types import TransitionDef

    db = _CasDbLayer("A")
    ex = TransitionExecutor(db_layer=db)
    tr = TransitionDef(
        id=1,
        entity_type="order",
        from_state="A",
        to_state="B",
        event_name="go",
    )
    ex.apply(
        None,
        service_id="svc",
        entity_type="order",
        entity_id=1,
        transition=tr,
        event_name="go",
        instance_id=10,
    )
    assert db.state == "B"
    assert db.cas_calls == [("A", "B")]
    assert len(db.logs) == 1


def test_transition_executor_cas_race_loses():
    from fsm_platform.core.errors import FsmErrorCodes
    from fsm_platform.core.transition_executor import (
        TransitionApplyError,
        TransitionExecutor,
    )
    from fsm_platform.core.types import TransitionDef

    db = _CasDbLayer("A")

    # Simulate concurrent winner: state moves before our CAS.
    class _RaceDb(_CasDbLayer):
        def cas_entity_state(self, *a, **k):
            self.state = "C"  # other worker won
            return False

    race = _RaceDb("A")
    ex = TransitionExecutor(db_layer=race)
    tr = TransitionDef(
        id=2,
        entity_type="order",
        from_state="A",
        to_state="B",
        event_name="go",
    )
    try:
        ex.apply(
            None,
            service_id="svc",
            entity_type="order",
            entity_id=1,
            transition=tr,
            event_name="go",
            instance_id=11,
        )
        assert False, "expected TransitionApplyError"
    except TransitionApplyError as exc:
        assert exc.code == FsmErrorCodes.STATE_MISMATCH
    assert race.state == "C"
    assert race.logs == []


def test_transition_executor_idempotent_already_to_state():
    from fsm_platform.core.transition_executor import TransitionExecutor
    from fsm_platform.core.types import TransitionDef

    db = _CasDbLayer("B")
    ex = TransitionExecutor(db_layer=db)
    tr = TransitionDef(
        id=3,
        entity_type="order",
        from_state="A",
        to_state="B",
        event_name="go",
    )
    ex.apply(
        None,
        service_id="svc",
        entity_type="order",
        entity_id=1,
        transition=tr,
        event_name="go",
        instance_id=12,
        allow_idempotent=True,
    )
    assert db.state == "B"
    assert db.cas_calls == []
    assert len(db.logs) == 1

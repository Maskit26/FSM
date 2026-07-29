"""Dispatch Contract API → локальные Callables домена."""

from __future__ import annotations

import inspect
import json
import logging
from typing import Any, Callable, Optional

from fsm_platform.core.domain_errors import DomainError
from fsm_platform.core.types import normalize_effect_result, normalize_guard_result
from fsm_platform.domain_runtime import registry
from fsm_platform.domain_runtime.session import domain_session, make_db
from fsm_platform.host.runtime_context import service_scope

logger = logging.getLogger(__name__)


def _service_id(instance: dict[str, Any], default: str) -> str:
    return str(instance.get("service_id") or default).strip() or default


def _guard_to_json(value: Any) -> dict[str, Any]:
    gr = normalize_guard_result(value)
    return {"ok": gr.ok, "reason": gr.reason, "payload": gr.payload}


def _effect_to_json(value: Any) -> dict[str, Any]:
    er = normalize_effect_result(value)
    out: dict[str, Any] = {
        "ok": er.ok,
        "error": er.error,
        "payload": er.payload,
    }
    if er.notify:
        out["notify"] = er.notify
    if er.cancel_instances:
        out["cancel_instances"] = er.cancel_instances
    if er.entity_states:
        out["entity_states"] = er.entity_states
    return out


def run_context(
    service_id: str,
    name: str,
    *,
    runtime_ctx: dict,
    instance: dict,
) -> dict[str, Any]:
    sid = _service_id(instance, service_id)
    fn: Optional[Callable[..., Any]] = None
    for p in registry.processes.list_for_service(sid):
        if p.context_builder_name == name and p.context_builder is not None:
            fn = p.context_builder
            break
    if fn is None:
        raise KeyError(name)

    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(sid):
            out = fn(sd, db, runtime_ctx, instance) or {}
        sd.commit()
        return json.loads(json.dumps(out, default=str))
    except DomainError:
        sd.rollback()
        raise
    except Exception:
        sd.rollback()
        logger.exception("context %s failed", name)
        raise
    finally:
        sd.close()


def run_guard(
    service_id: str,
    name: str,
    *,
    context: dict,
    guard_params: dict,
    instance: dict,
) -> dict[str, Any]:
    sid = _service_id(instance, service_id)
    fn = registry.guards.get(sid, name)
    if fn is None:
        raise KeyError(name)
    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(sid):
            raw = fn(sd, db, context, instance, guard_params or {})
        sd.commit()
        return _guard_to_json(raw)
    except DomainError:
        sd.rollback()
        raise
    except Exception:
        sd.rollback()
        logger.exception("guard %s failed", name)
        raise
    finally:
        sd.close()


def run_effect(
    service_id: str,
    name: str,
    *,
    context: dict,
    effect_params: dict,
    instance: dict,
) -> dict[str, Any]:
    sid = _service_id(instance, service_id)
    fn = registry.effects.get(sid, name)
    if fn is None:
        raise KeyError(name)
    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(sid):
            raw = fn(sd, db, context, instance, effect_params or {})
        sd.commit()
        return _effect_to_json(raw)
    except DomainError:
        sd.rollback()
        raise
    except Exception:
        sd.rollback()
        logger.exception("effect %s failed", name)
        raise
    finally:
        sd.close()


def _run_invoke(
    service_id: str, fn: Callable[..., Any], params: dict, actor: dict
) -> dict[str, Any]:
    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(service_id):
            sig = inspect.signature(fn)
            kwargs: dict[str, Any] = {}
            if "db" in sig.parameters:
                kwargs["db"] = db
            if "platform_session" in sig.parameters:
                kwargs["platform_session"] = None
            result = fn(sd, params, actor, **kwargs)
        sd.commit()
        if isinstance(result, dict):
            return result
        return {"data": result}
    except DomainError:
        sd.rollback()
        raise
    except Exception:
        sd.rollback()
        raise
    finally:
        sd.close()


def run_command(
    service_id: str, operation: str, *, params: dict, actor: dict
) -> dict[str, Any]:
    meta = registry.operations.get(service_id, operation)
    if meta is None or meta["kind"] != "command":
        raise KeyError(operation)
    return _run_invoke(service_id, meta["handler"], params, actor)


def run_query(
    service_id: str, operation: str, *, params: dict, actor: dict
) -> dict[str, Any]:
    meta = registry.operations.get(service_id, operation)
    if meta is None or meta["kind"] != "query":
        raise KeyError(operation)
    return _run_invoke(service_id, meta["handler"], params, actor)


def run_on_failed(
    service_id: str,
    process_name: str,
    *,
    instance: dict,
    last_error: str,
) -> dict[str, Any]:
    sid = _service_id(instance, service_id)
    proc = registry.processes.get(sid, process_name)
    if proc is None or proc.on_failed is None:
        raise KeyError(process_name)
    fn = proc.on_failed
    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(sid):
            out = fn(None, sd, db, instance, last_error or "")
        sd.commit()
        if out is None:
            return {}
        if isinstance(out, dict):
            return out
        return {}
    except Exception:
        sd.rollback()
        logger.exception("on_failed %s failed", process_name)
        raise
    finally:
        sd.close()


def run_hook(
    service_id: str,
    channel: str,
    *,
    body: Any,
    headers: dict[str, str],
    query: dict[str, str],
    raw_body: bytes = b"",
) -> dict[str, Any]:
    ch = str(channel or "").strip().lower()
    if not registry.hooks.has(service_id, ch):
        raise KeyError(ch)
    fn = registry.hooks.get(service_id, ch)
    if fn is None:
        raise KeyError(ch)

    sd = domain_session()
    db = make_db(sd)
    try:
        with service_scope(service_id):
            sig = inspect.signature(fn)
            kwargs: dict[str, Any] = {}
            available = {
                "body": body,
                "headers": headers,
                "query": query,
                "raw_body": raw_body,
                "domain_session": sd,
                "session_domain": sd,
                "db": db,
                "service_id": service_id,
                "channel": ch,
            }
            for name in sig.parameters:
                if name in available:
                    kwargs[name] = available[name]
            params = list(sig.parameters.values())
            if params and params[0].name not in kwargs:
                result = fn(body, **kwargs)
            else:
                result = fn(**kwargs) if kwargs else fn(body)
        sd.commit()
        if result is None:
            return {"ok": True, "service_id": service_id, "channel": ch}
        if isinstance(result, dict):
            return result
        return {
            "ok": True,
            "service_id": service_id,
            "channel": ch,
            "data": result,
        }
    except DomainError:
        sd.rollback()
        raise
    except Exception:
        sd.rollback()
        logger.exception("hook %s failed", ch)
        raise
    finally:
        sd.close()


def run_outbox_deliver(service_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Vendor outbox (channel=core): handler из register_all / set_outbox_handler."""
    fn = registry.get_outbox_handler()
    if fn is None:
        raise RuntimeError("OUTBOX_HANDLER_NOT_REGISTERED")

    body = dict(payload or {})
    body.setdefault("service_id", service_id)
    with service_scope(service_id):
        fn(body)
    return {"ok": True, "op": body.get("op")}

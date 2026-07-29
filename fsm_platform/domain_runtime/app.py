"""Generic Contract API FastAPI app для любого доменного картриджа."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from fsm_platform.core.domain_errors import DomainError
from fsm_platform.domain_runtime import catalog, contract_auth, dispatch
from fsm_platform.domain_runtime.boot import bootstrap_domain

logger = logging.getLogger(__name__)


class ContextBody(BaseModel):
    runtime_ctx: dict[str, Any] = Field(default_factory=dict)
    instance: dict[str, Any] = Field(default_factory=dict)


class GuardBody(BaseModel):
    context: dict[str, Any] = Field(default_factory=dict)
    guard_params: dict[str, Any] = Field(default_factory=dict)
    instance: dict[str, Any] = Field(default_factory=dict)


class EffectBody(BaseModel):
    context: dict[str, Any] = Field(default_factory=dict)
    effect_params: dict[str, Any] = Field(default_factory=dict)
    instance: dict[str, Any] = Field(default_factory=dict)


class InvokeBody(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)
    actor: dict[str, Any] = Field(default_factory=dict)


class OnFailedBody(BaseModel):
    instance: dict[str, Any] = Field(default_factory=dict)
    last_error: str = ""


class HookBody(BaseModel):
    body: Any = None
    headers: dict[str, str] = Field(default_factory=dict)
    query: dict[str, str] = Field(default_factory=dict)
    raw_body_b64: Optional[str] = None


class OutboxDeliverBody(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


def _domain_http(exc: DomainError) -> HTTPException:
    return HTTPException(
        409,
        detail={"error_code": exc.code, "message": exc.message},
    )


def create_app(
    *,
    entry: str,
    service_id: Optional[str] = None,
    title: Optional[str] = None,
) -> FastAPI:
    """
    Поднимает Contract API поверх register_all домена.

    entry: domains.courier.processes:register_all
    """
    sid = bootstrap_domain(entry=entry, service_id=service_id)
    cat = catalog.build_catalog(sid, entry=entry)
    cartridge = cat.get("cartridge_type") or "domain"

    app = FastAPI(
        title=title or f"{str(cartridge).title()} Domain Service",
        version=str(cat.get("version") or "0.1.0"),
    )
    app.state.service_id = sid
    app.state.entry = entry

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service_id": sid}

    @app.get("/contract/v1/catalog")
    def get_catalog() -> dict[str, Any]:
        return catalog.build_catalog(sid, entry=entry)

    @app.middleware("http")
    async def contract_hmac_middleware(request: Request, call_next):
        if not request.url.path.startswith("/contract/v1"):
            return await call_next(request)
        if request.method == "GET" and request.url.path.endswith("/catalog"):
            return await call_next(request)
        raw = await request.body()

        async def receive():
            return {"type": "http.request", "body": raw, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]
        try:
            contract_auth.verify_incoming(request, raw)
        except HTTPException as exc:
            # BaseHTTPMiddleware иначе превращает HTTPException в 500 ExceptionGroup
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        return await call_next(request)

    @app.post("/contract/v1/context/{name}")
    def post_context(name: str, body: ContextBody) -> dict[str, Any]:
        try:
            return dispatch.run_context(
                sid, name, runtime_ctx=body.runtime_ctx, instance=body.instance
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_CONTEXT:{name}") from None
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/guards/{name}")
    def post_guard(name: str, body: GuardBody) -> dict[str, Any]:
        try:
            return dispatch.run_guard(
                sid,
                name,
                context=body.context,
                guard_params=body.guard_params,
                instance=body.instance,
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_GUARD:{name}") from None
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/effects/{name}")
    def post_effect(name: str, body: EffectBody) -> dict[str, Any]:
        try:
            return dispatch.run_effect(
                sid,
                name,
                context=body.context,
                effect_params=body.effect_params,
                instance=body.instance,
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_EFFECT:{name}") from None
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/commands/{operation}")
    def post_command(operation: str, body: InvokeBody) -> dict[str, Any]:
        try:
            return dispatch.run_command(
                sid, operation, params=body.params, actor=body.actor
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_COMMAND:{operation}") from None
        except ValueError as exc:
            raise HTTPException(400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/queries/{operation}")
    def post_query(operation: str, body: InvokeBody) -> dict[str, Any]:
        try:
            return dispatch.run_query(
                sid, operation, params=body.params, actor=body.actor
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_QUERY:{operation}") from None
        except ValueError as exc:
            raise HTTPException(400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/processes/{process_name}/on-failed")
    def post_on_failed(process_name: str, body: OnFailedBody) -> dict[str, Any]:
        try:
            return dispatch.run_on_failed(
                sid,
                process_name,
                instance=body.instance,
                last_error=body.last_error,
            )
        except KeyError:
            raise HTTPException(
                404, detail=f"ON_FAILED_NOT_REGISTERED:{process_name}"
            ) from None
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/hooks/{channel}")
    def post_hook(channel: str, body: HookBody) -> dict[str, Any]:
        import base64

        raw = b""
        if body.raw_body_b64:
            try:
                raw = base64.b64decode(body.raw_body_b64)
            except Exception as exc:
                raise HTTPException(400, detail=f"INVALID_RAW_BODY:{exc}") from exc
        try:
            return dispatch.run_hook(
                sid,
                channel,
                body=body.body,
                headers=body.headers,
                query=body.query,
                raw_body=raw,
            )
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except KeyError:
            raise HTTPException(404, detail=f"UNKNOWN_HOOK:{channel}") from None
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    @app.post("/contract/v1/outbox/deliver")
    def post_outbox_deliver(body: OutboxDeliverBody) -> dict[str, Any]:
        try:
            return dispatch.run_outbox_deliver(sid, body.payload)
        except DomainError as exc:
            raise _domain_http(exc) from exc
        except Exception as exc:
            raise HTTPException(500, detail=str(exc)) from exc

    logger.info(
        "domain_runtime ready service_id=%s cartridge=%s ops=%s",
        sid,
        cartridge,
        len(cat.get("operations") or []),
    )
    return app

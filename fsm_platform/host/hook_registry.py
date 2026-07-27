"""
Inbound hook registry: сторонние API → домен (снаружи внутрь).

Не путать с host/webhooks.py (outbound webhook_subscriptions → клиент).

Домен в register_all:
  default_webhook_registry.register(service_id, "leo4", handle_leo4)

HTTP: POST /v1/{service_id}/hooks/{channel}
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

WebhookHandler = Callable[..., Any]


class WebhookRegistry:
    """(service_id, channel) → handler. Channel — короткое имя источника (leo4, tinkoff, …)."""

    def __init__(self) -> None:
        self._hooks: dict[tuple[str, str], WebhookHandler] = {}

    def register(
        self, service_id: str, channel: str, handler: WebhookHandler
    ) -> None:
        """Регистрирует inbound-обработчик для channel."""
        sid = str(service_id or "").strip()
        ch = str(channel or "").strip().lower()
        if not sid or not ch:
            raise ValueError("service_id and channel required")
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._hooks[(sid, ch)] = handler

    def get(self, service_id: str, channel: str) -> Optional[WebhookHandler]:
        """Handler или None."""
        return self._hooks.get(
            (str(service_id).strip(), str(channel or "").strip().lower())
        )

    def has(self, service_id: str, channel: str) -> bool:
        return self.get(service_id, channel) is not None

    def list_channels(self, service_id: str) -> list[str]:
        """Имена channel для catalog / диагностики."""
        sid = str(service_id).strip()
        return sorted(ch for (s, ch) in self._hooks if s == sid)

    def clear(self) -> None:
        self._hooks.clear()

    def unregister(self, service_id: str) -> None:
        """Удаляет все hooks одного service_id."""
        for key in [k for k in self._hooks if k[0] == service_id]:
            del self._hooks[key]


default_webhook_registry = WebhookRegistry()


class HookError(Exception):
    """Доменный отказ inbound hook → HTTP status."""

    def __init__(
        self,
        code: str,
        message: str = "",
        *,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.status_code = int(status_code)
        super().__init__(message or code)


def _call_handler(
    handler: WebhookHandler,
    *,
    body: Any,
    headers: dict[str, str],
    query: dict[str, str],
    raw_body: bytes,
    domain_session: Any,
    platform_session: Any,
    service_id: str,
    channel: str,
) -> Any:
    """Подбирает args/kwargs по сигнатуре handler."""
    available = {
        "body": body,
        "headers": headers,
        "query": query,
        "raw_body": raw_body,
        "domain_session": domain_session,
        "platform_session": platform_session,
        "service_id": service_id,
        "channel": channel,
    }
    sig = inspect.signature(handler)
    params = list(sig.parameters.values())
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    skip_name: Optional[str] = None

    if params:
        first = params[0]
        if first.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            # def handle(body, *, headers=...): или def handle(payload, ...):
            args.append(available.get(first.name, body))
            skip_name = first.name

    for p in params:
        if p.name == skip_name:
            continue
        if p.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        if p.name in available:
            kwargs[p.name] = available[p.name]
        elif has_var_kw and p.name in available:
            kwargs[p.name] = available[p.name]

    if has_var_kw:
        for k, v in available.items():
            if k == skip_name:
                continue
            kwargs.setdefault(k, v)

    return handler(*args, **kwargs)


def dispatch_inbound_hook(
    service_id: str,
    channel: str,
    *,
    body: Any,
    headers: dict[str, str],
    query: dict[str, str],
    raw_body: bytes = b"",
) -> dict[str, Any]:
    """
    Биндит service_scope, открывает sessions, вызывает handler домена, commit.

    Типичный handler:
      def handle(body, *, headers, query, domain_session, platform_session):
          ...
          return {"ok": True}
    """
    from fsm_platform.host.engines import domain_session, platform_session
    from fsm_platform.host.runtime_context import service_scope

    ch = str(channel or "").strip().lower()
    handler = default_webhook_registry.get(service_id, ch)
    if handler is None:
        raise HookError(
            "UNKNOWN_HOOK_CHANNEL",
            f"no inbound hook for channel={ch!r}",
            status_code=404,
        )

    sp = platform_session()
    sd = domain_session(service_id)
    try:
        with service_scope(service_id):
            result = _call_handler(
                handler,
                body=body,
                headers=headers,
                query=query,
                raw_body=raw_body,
                domain_session=sd,
                platform_session=sp,
                service_id=service_id,
                channel=ch,
            )
        sd.commit()
        sp.commit()
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
    except HookError:
        sd.rollback()
        sp.rollback()
        raise
    except Exception:
        sd.rollback()
        sp.rollback()
        raise
    finally:
        sd.close()
        sp.close()

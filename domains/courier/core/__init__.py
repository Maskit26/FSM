"""ibronevik Core integration for courier domain (outbox channel=core)."""

from domains.courier.core.deliver import handle_core_outbox
from domains.courier.core.enqueue import core_notify

__all__ = ["core_notify", "handle_core_outbox"]

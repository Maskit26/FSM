"""HTTP webhook delivery (HMAC-signed POST)."""

from .sender import deliver_webhook

__all__ = ["deliver_webhook"]

"""Live tenant onboarding/security E2E for a locally configured platform."""

from __future__ import annotations

import argparse
import secrets
import sys
from typing import Any

import requests


def _expect(response: requests.Response, expected: int) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        body = {"_raw": response.text}
    if response.status_code != expected:
        raise RuntimeError(
            f"{response.request.method} {response.url}: "
            f"expected {expected}, got {response.status_code}: {body}"
        )
    return body if isinstance(body, dict) else {"_value": body}


def _create_account(
    session: requests.Session, base_url: str, email: str, password: str
) -> tuple[str, str]:
    registered = _expect(
        session.post(
            f"{base_url}/v1/auth/register",
            json={"email": email, "password": password},
            timeout=30,
        ),
        201,
    )
    verification_token = str(registered.get("verification_token") or "")
    if not verification_token:
        raise RuntimeError(
            "registration did not expose verification_token; run API with "
            "TENANT_AUTH_EXPOSE_TOKENS=1 for this local E2E"
        )
    _expect(
        session.post(
            f"{base_url}/v1/auth/verify-email",
            json={"token": verification_token},
            timeout=30,
        ),
        200,
    )
    login = _expect(
        session.post(
            f"{base_url}/v1/auth/login",
            json={"email": email, "password": password},
            timeout=30,
        ),
        200,
    )
    access = str(login["access_token"])
    issued = _expect(
        session.post(
            f"{base_url}/v1/tenant/admin-tokens",
            headers={"Authorization": f"Bearer {access}"},
            json={"name": "tenant-e2e", "expires_in_days": 1},
            timeout=30,
        ),
        201,
    )
    return access, str(issued["token"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run tenant onboarding E2E")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--email", default="")
    parser.add_argument("--password", default="Local-e2e-password-42")
    parser.add_argument("--cartridge-type", default="courier")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--contract-base-url", required=True)
    parser.add_argument("--contract-shared-secret", required=True)
    parser.add_argument("--graph-database-url", required=True)
    parser.add_argument("--graph-write-database-url", required=True)
    args = parser.parse_args(argv)

    base = args.base_url.rstrip("/")
    nonce = secrets.token_hex(5)
    first_email = args.email or f"tenant-e2e-{nonce}@example.test"
    second_email = f"tenant-e2e-other-{nonce}@example.test"
    session = requests.Session()
    session.headers["Accept"] = "application/json"

    try:
        _, first_token = _create_account(
            session, base, first_email, args.password
        )
        _, second_token = _create_account(
            session, base, second_email, args.password
        )
        registered = _expect(
            session.post(
                f"{base}/v1/tenant/domains",
                headers={"X-Admin-Token": first_token},
                json={
                    "cartridge_type": args.cartridge_type,
                    "version": args.version,
                },
                timeout=30,
            ),
            201,
        )
        service_id = str(registered["service_id"])
        denied = session.get(
            f"{base}/v1/{service_id}/catalog",
            headers={"X-Admin-Token": second_token},
            timeout=30,
        )
        if denied.status_code != 404:
            raise RuntimeError(
                f"cross-tenant request must be hidden with 404, got {denied.status_code}"
            )
        secrets_to_write = {
            "contract_base_url": args.contract_base_url,
            "contract_shared_secret": args.contract_shared_secret,
            "graph_database_url": args.graph_database_url,
            "graph_write_database_url": args.graph_write_database_url,
        }
        for key, value in secrets_to_write.items():
            _expect(
                session.put(
                    f"{base}/v1/{service_id}/secrets",
                    headers={"X-Admin-Token": first_token},
                    json={"key": key, "value": value},
                    timeout=30,
                ),
                200,
            )
        connected = _expect(
            session.post(
                f"{base}/v1/{service_id}/connect",
                headers={"X-Admin-Token": first_token},
                timeout=60,
            ),
            200,
        )
        print(
            {
                "tenant": first_email,
                "service_id": service_id,
                "cross_tenant": "denied",
                "connect": connected,
            }
        )
        return 0
    except Exception as exc:
        print(f"tenant E2E failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

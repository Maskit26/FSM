from __future__ import annotations

import os
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from fastapi.routing import APIRoute, APIWebSocketRoute

from fsm_platform.host.http.app import app
from fsm_platform.host.http.dependencies import authenticate_domain_request
from fsm_platform.host.tenant_auth import (
    TenantAuthError,
    authenticate_domain_token,
    hash_opaque_token,
    hash_password,
    issue_access_token,
    issue_domain_token,
    utcnow,
    verify_access_token,
    verify_password,
)


class FakeDomainTokenDb:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, object]] = {}
        self.next_id = 1
        self.touched: list[int] = []
        self.owned: set[tuple[int, str]] = set()
        self.audits: list[dict[str, object]] = []

    def create_domain_admin_token(self, _session: object, **values: object) -> int:
        token_id = self.next_id
        self.next_id += 1
        self.rows[str(values["token_hash"])] = {
            "id": token_id,
            "tenant_account_id": values["tenant_account_id"],
            "token_hash": values["token_hash"],
            "expires_at": values["expires_at"],
            "revoked_at": None,
        }
        return token_id

    def get_domain_admin_token(
        self, _session: object, *, token_hash: str
    ) -> dict[str, object] | None:
        return self.rows.get(token_hash)

    def touch_domain_admin_token(self, _session: object, *, token_id: int) -> None:
        self.touched.append(token_id)

    def tenant_owns_service(
        self,
        _session: object,
        *,
        tenant_account_id: int,
        service_id: str,
    ) -> bool:
        return (int(tenant_account_id), service_id) in self.owned

    def insert_platform_audit_event(self, _session: object, **values: object) -> None:
        self.audits.append(values)


class TenantAuthTests(unittest.TestCase):
    def test_password_hash_and_policy(self) -> None:
        encoded = hash_password("correct-horse-42")
        self.assertTrue(verify_password(encoded, "correct-horse-42"))
        self.assertFalse(verify_password(encoded, "wrong-password-42"))
        with self.assertRaises(TenantAuthError):
            hash_password("short1")

    def test_access_token_is_signed_and_scoped(self) -> None:
        with patch.dict(os.environ, {"TENANT_AUTH_SECRET": "x" * 48}, clear=False):
            raw, ttl = issue_access_token(17)
            principal = verify_access_token(raw)
        self.assertEqual(principal.tenant_account_id, 17)
        self.assertGreaterEqual(ttl, 60)
        with patch.dict(os.environ, {"TENANT_AUTH_SECRET": "y" * 48}, clear=False):
            with self.assertRaises(TenantAuthError):
                verify_access_token(raw)

    def test_domain_token_is_tenant_scoped_and_revocable(self) -> None:
        db = FakeDomainTokenDb()
        raw, metadata = issue_domain_token(
            db,  # type: ignore[arg-type]
            object(),
            tenant_account_id=9,
            name="automation",
            expires_in_days=30,
        )
        principal = authenticate_domain_token(
            db,  # type: ignore[arg-type]
            object(),
            raw_token=raw,
        )
        self.assertEqual(principal.tenant_account_id, 9)
        row = db.rows[hash_opaque_token(raw)]
        self.assertEqual(metadata["id"], row["id"])
        row["revoked_at"] = utcnow()
        with self.assertRaises(TenantAuthError) as caught:
            authenticate_domain_token(
                db,  # type: ignore[arg-type]
                object(),
                raw_token=raw,
            )
        self.assertEqual(caught.exception.code, "DOMAIN_TOKEN_REVOKED")

    def test_expired_domain_token_is_rejected(self) -> None:
        db = FakeDomainTokenDb()
        raw, _ = issue_domain_token(
            db,  # type: ignore[arg-type]
            object(),
            tenant_account_id=3,
            name=None,
            expires_in_days=None,
        )
        db.rows[hash_opaque_token(raw)]["expires_at"] = (
            utcnow() - timedelta(seconds=1)
        )
        with self.assertRaises(TenantAuthError) as caught:
            authenticate_domain_token(
                db,  # type: ignore[arg-type]
                object(),
                raw_token=raw,
            )
        self.assertEqual(caught.exception.code, "DOMAIN_TOKEN_EXPIRED")

    def test_platform_admin_token_is_not_accepted_as_domain_token(self) -> None:
        db = FakeDomainTokenDb()
        with self.assertRaises(TenantAuthError) as caught:
            authenticate_domain_token(
                db,  # type: ignore[arg-type]
                object(),
                raw_token="MCwHGqu4AnwFUr3xgvIXUir3ryYBXLTX",
            )
        self.assertEqual(caught.exception.code, "DOMAIN_TOKEN_INVALID")


class DomainRequestAuthTests(unittest.TestCase):
    def test_cross_tenant_service_is_hidden(self) -> None:
        db = FakeDomainTokenDb()
        raw, _ = issue_domain_token(
            db,  # type: ignore[arg-type]
            object(),
            tenant_account_id=11,
            name="a",
            expires_in_days=None,
        )
        db.owned.add((11, "svc_mine"))
        session = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.close = MagicMock()
        with patch(
            "fsm_platform.host.http.dependencies.default_db_layer", db
        ), patch(
            "fsm_platform.host.http.dependencies.platform_session",
            return_value=session,
        ):
            allowed = authenticate_domain_request(
                raw_token=raw,
                service_id="svc_mine",
                source_ip="127.0.0.1",
                user_agent="test",
            )
            self.assertEqual(allowed.tenant_account_id, 11)
            with self.assertRaises(TenantAuthError) as caught:
                authenticate_domain_request(
                    raw_token=raw,
                    service_id="svc_other",
                    source_ip="127.0.0.1",
                    user_agent="test",
                )
        self.assertEqual(caught.exception.code, "DOMAIN_NOT_FOUND")
        self.assertEqual(caught.exception.status_code, 404)


class RouteAuthorizationMatrixTests(unittest.TestCase):
    def test_all_service_http_routes_have_domain_dependency(self) -> None:
        routes = [
            route
            for route in app.routes
            if isinstance(route, APIRoute)
            and route.path.startswith("/v1/{service_id}/")
        ]
        self.assertTrue(routes)
        for route in routes:
            dependency_names = {
                dependency.call.__name__
                for dependency in route.dependant.dependencies
                if dependency.call is not None
            }
            self.assertIn(
                "require_domain_service_access",
                dependency_names,
                msg=f"{route.path} is missing domain authorization",
            )

    def test_service_websocket_exists_and_auth_is_in_handler(self) -> None:
        routes = [
            route
            for route in app.routes
            if isinstance(route, APIWebSocketRoute)
            and route.path == "/v1/{service_id}/ws/events"
        ]
        self.assertEqual(len(routes), 1)
        names = set(routes[0].endpoint.__code__.co_names)
        self.assertIn("authenticate_domain_request", names)

    def test_platform_routes_have_platform_dependency(self) -> None:
        paths = {"/v1/health", "/v1/metrics", "/v1/admin/domains/{service_id}/reload"}
        routes = [
            route
            for route in app.routes
            if isinstance(route, APIRoute) and route.path in paths
        ]
        self.assertEqual({route.path for route in routes}, paths)
        for route in routes:
            dependency_names = {
                dependency.call.__name__
                for dependency in route.dependant.dependencies
                if dependency.call is not None
            }
            self.assertIn("require_platform_admin", dependency_names)

    def test_public_auth_routes_have_no_admin_dependency(self) -> None:
        for route in app.routes:
            if not isinstance(route, APIRoute) or not route.path.startswith(
                "/v1/auth/"
            ):
                continue
            dependency_names = {
                dependency.call.__name__
                for dependency in route.dependant.dependencies
                if dependency.call is not None
            }
            self.assertNotIn("require_platform_admin", dependency_names)
            self.assertNotIn("require_domain_service_access", dependency_names)

    def test_tenant_token_routes_require_access_token(self) -> None:
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            if not route.path.startswith("/v1/tenant/admin-tokens"):
                continue
            dependency_names = {
                dependency.call.__name__
                for dependency in route.dependant.dependencies
                if dependency.call is not None
            }
            self.assertIn("require_tenant_access", dependency_names)

    def test_domain_register_requires_domain_token(self) -> None:
        routes = [
            route
            for route in app.routes
            if isinstance(route, APIRoute) and route.path == "/v1/tenant/domains"
        ]
        self.assertEqual(len(routes), 1)
        dependency_names = {
            dependency.call.__name__
            for dependency in routes[0].dependant.dependencies
            if dependency.call is not None
        }
        self.assertIn("require_domain_token", dependency_names)


class WorkerProvisionerTests(unittest.TestCase):
    def test_provision_sets_worker_service_id(self) -> None:
        from fsm_platform.host import worker_provisioner as wp

        fake = MagicMock()
        fake.poll.return_value = None
        fake.pid = 4242
        with patch.object(wp, "_processes", {}), patch.object(
            wp.subprocess, "Popen", return_value=fake
        ) as popen:
            result = wp.provision_worker("svc_demo_01")
        self.assertEqual(result["status"], "started")
        env = popen.call_args.kwargs["env"]
        self.assertEqual(env["WORKER_SERVICE_ID"], "svc_demo_01")
        self.assertNotIn("WORKER_ALLOW_ALL_TENANTS", env)


if __name__ == "__main__":
    unittest.main()

"""Worker provisioner backend selection."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fsm_platform.host import worker_provisioner as wp


class WorkerProvisionerBackendTests(unittest.TestCase):
    def tearDown(self) -> None:
        wp._backends.clear()

    def test_default_is_local(self) -> None:
        with patch.dict(os.environ, {"WORKER_PROVISION_BACKEND": ""}, clear=False):
            os.environ.pop("WORKER_PROVISION_BACKEND", None)
            wp._backends.clear()
            backend = wp._get_backend()
        self.assertIsInstance(backend, wp.LocalSubprocessBackend)

    def test_select_docker(self) -> None:
        with patch.dict(os.environ, {"WORKER_PROVISION_BACKEND": "docker"}, clear=False):
            wp._backends.clear()
            backend = wp._get_backend()
        self.assertIsInstance(backend, wp.DockerBackend)

    def test_unknown_backend(self) -> None:
        with patch.dict(os.environ, {"WORKER_PROVISION_BACKEND": " Nomad "}, clear=False):
            # normalize lower
            pass
        with patch.dict(os.environ, {"WORKER_PROVISION_BACKEND": "nomad"}, clear=False):
            wp._backends.clear()
            with self.assertRaises(RuntimeError):
                wp._get_backend()


if __name__ == "__main__":
    unittest.main()

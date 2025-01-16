# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
from ops import testing

from charm import Iperf3K8SOperatorCharm


class Iperf3UnitTestFixtures:
    @pytest.fixture(autouse=True)
    def setup(self, request):  # type: ignore[reportMissingParameterType]
        yield
        request.addfinalizer(self.teardown)

    @staticmethod
    def teardown() -> None:
        patch.stopall()

    @pytest.fixture(autouse=True)
    def context(self):
        self.ctx = testing.Context(
            charm_type=Iperf3K8SOperatorCharm,
        )

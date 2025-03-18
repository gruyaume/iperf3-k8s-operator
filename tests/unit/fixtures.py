# Copyright 2024 Guillaume Belanger.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest
from ops import testing

from charm import Iperf3K8SOperatorCharm


class Iperf3UnitTestFixtures:
    patcher_k8s_multus = patch(
        "charm.KubernetesMultusCharmLib",
    )

    @pytest.fixture(autouse=True)
    def setup(self, request):  # type: ignore[reportMissingParameterType]
        self.mock_k8s_multus = Iperf3UnitTestFixtures.patcher_k8s_multus.start().return_value
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

# Copyright 2024 Guillaume Belanger
# See LICENSE file for licensing details.


from ops import testing
from ops.model import ActiveStatus, WaitingStatus

from tests.unit.fixtures import Iperf3UnitTestFixtures


class TestCharmCollectStatus(Iperf3UnitTestFixtures):
    def test_given_container_not_ready_when_collect_unit_status_then_status_is_waiting(self):
        container = testing.Container(
            name="iperf3",
        )
        state_in = testing.State(
            containers=[container],
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == WaitingStatus("Waiting for container to be ready")

    def test_given_container_ready_when_collect_unit_status_then_status_is_active(self):
        container = testing.Container(
            name="iperf3",
            can_connect=True,
        )
        state_in = testing.State(
            containers=[container],
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.collect_unit_status(), state_in)

        assert state_out.unit_status == ActiveStatus()

# Copyright 2024 Guillaume Belanger
# See LICENSE file for licensing details.


from ops import testing
from ops.pebble import Layer

from tests.unit.fixtures import Iperf3UnitTestFixtures


class TestCharmConfigure(Iperf3UnitTestFixtures):
    def test_given_ready_when_configure_then_pebble_plan_is_applied(
        self,
    ):
        container = testing.Container(
            name="iperf3",
            can_connect=True,
        )
        state_in = testing.State(
            containers=[container],
            leader=True,
        )

        state_out = self.ctx.run(self.ctx.on.pebble_ready(container=container), state_in)

        container = state_out.get_container("iperf3")

        assert container.layers["iperf3"] == Layer(
            {
                "summary": "iperf3 layer",
                "description": "pebble config layer for iperf3",
                "services": {
                    "iperf3": {
                        "summary": "iperf3",
                        "startup": "enabled",
                        "override": "replace",
                        "command": "iperf3 -s --bind 192.168.250.22 -p 5201",
                    }
                },
            }
        )

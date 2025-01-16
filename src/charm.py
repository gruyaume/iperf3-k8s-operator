#!/usr/bin/env python3
# Copyright 2025 Guillaume Belanger
# See LICENSE file for licensing details.

"""Kubernetes Charm for iperf3."""

import logging

import ops

logger = logging.getLogger(__name__)

IPERF3_PORT = 5201


class Iperf3K8SOperatorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self._container_name = self._service_name = "iperf3"
        self._container = self.unit.get_container(self._container_name)
        self.unit.set_ports(IPERF3_PORT)
        self.framework.observe(self.on.collect_unit_status, self._on_collect_status)
        framework.observe(self.on["iperf3"].pebble_ready, self._on_configure)
        framework.observe(self.on.config_changed, self._on_configure)

    def _on_collect_status(self, event: ops.CollectStatusEvent):
        """Handle the collect status event."""
        if not self._container.can_connect():
            event.add_status(ops.WaitingStatus("Waiting for container to be ready"))
            return
        event.add_status(ops.ActiveStatus())

    def _on_configure(self, event: ops.PebbleReadyEvent):
        """Start iperf3 using the Pebble API."""
        plan = self._container.get_plan()
        if plan.services != self._pebble_layer.services:
            self._container.add_layer(self._service_name, self._pebble_layer, combine=True)
            self._container.replan()

    @property
    def _pebble_layer(self) -> ops.pebble.Layer:
        """Return the Pebble layer definition."""
        return ops.pebble.Layer(
            {
                "summary": "iperf3 layer",
                "description": "pebble config layer for iperf3",
                "services": {
                    "iperf3": {
                        "override": "replace",
                        "summary": "iperf3",
                        "command": f"iperf3 -s -p {IPERF3_PORT}",
                        "startup": "enabled",
                    }
                },
            }
        )


if __name__ == "__main__":  # pragma: nocover
    ops.main(Iperf3K8SOperatorCharm)  # type: ignore

#!/usr/bin/env python3
# Copyright 2025 Guillaume Belanger
# See LICENSE file for licensing details.

"""Kubernetes Charm for iperf3."""

import json
import logging
from typing import Any, Dict, List

import ops
from charms.kubernetes_charm_libraries.v0.multus import (
    KubernetesMultusCharmLib,
    NetworkAnnotation,
    NetworkAttachmentDefinition,
)
from lightkube.models.meta_v1 import ObjectMeta

logger = logging.getLogger(__name__)

IPERF3_PORT = 5201
CORE_GW_NAD_NAME = "core-iperf3"
CORE_INTERFACE_NAME = "core"
CORE_INTERFACE_BRIDGE_NAME = "core-br"
CNI_VERSION = "0.3.1"
CORE_IP_ADDRESS = "192.168.250.22"
UE_SUBNET = "172.250.0.0/16"


class Iperf3K8SOperatorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self._container_name = self._service_name = "iperf3"
        self._container = self.unit.get_container(self._container_name)
        self.unit.set_ports(IPERF3_PORT)
        self._kubernetes_multus = KubernetesMultusCharmLib(
            namespace=self.model.name,
            statefulset_name=self.model.app.name,
            pod_name="-".join(self.model.unit.name.rsplit("/", 1)),
            container_name=self._container_name,
            cap_net_admin=True,
            privileged=True,
            network_annotations=self._generate_network_annotations(),
            network_attachment_definitions=self._network_attachment_definitions_from_config(),
        )
        framework.observe(self.on.collect_unit_status, self._on_collect_status)
        framework.observe(self.on["iperf3"].pebble_ready, self._on_configure)
        framework.observe(self.on.config_changed, self._on_configure)
        framework.observe(self.on.update_status, self._on_configure)
        framework.observe(self.on.remove, self._on_remove)

    def _on_collect_status(self, event: ops.CollectStatusEvent):
        """Handle the collect status event."""
        if not self._kubernetes_multus.multus_is_available():
            event.add_status(ops.BlockedStatus("Multus is not installed or enabled"))
            logger.info("Multus is not installed or enabled")
            return
        if not self._container.can_connect():
            event.add_status(ops.WaitingStatus("Waiting for container to be ready"))
            return
        if not self._kubernetes_multus.is_ready():
            event.add_status(ops.WaitingStatus("Waiting for Multus to be ready"))
            logger.info("Waiting for Multus to be ready")
            return
        event.add_status(ops.ActiveStatus())

    def _on_configure(self, event: ops.PebbleReadyEvent):
        """Start iperf3 using the Pebble API."""
        if not self._kubernetes_multus.multus_is_available():
            return
        if not self._container.can_connect():
            return
        self._kubernetes_multus.configure()
        if not self._kubernetes_multus.is_ready():
            return
        plan = self._container.get_plan()
        if plan.services != self._pebble_layer.services:
            self._container.add_layer(self._service_name, self._pebble_layer, combine=True)
            self._container.replan()

    def _on_remove(self, _) -> None:
        """Handle the remove event."""
        if not self.unit.is_leader():
            return
        self._kubernetes_multus.remove()

    def _generate_network_annotations(self) -> List[NetworkAnnotation]:
        """Generate a list of NetworkAnnotations to be used by Router's StatefulSet.

        Returns:
            List[NetworkAnnotation]: List of NetworkAnnotations
        """
        return [
            NetworkAnnotation(
                name=CORE_GW_NAD_NAME,
                interface=CORE_INTERFACE_NAME,
            ),
        ]

    def _network_attachment_definitions_from_config(self) -> list[NetworkAttachmentDefinition]:
        """Return list of Multus NetworkAttachmentDefinitions to be created based on config.

        Returns:
            network_attachment_definitions: list[NetworkAttachmentDefinition]

        """
        core_nad_config = self._get_core_nad_config()

        return [
            NetworkAttachmentDefinition(
                metadata=ObjectMeta(name=CORE_GW_NAD_NAME),
                spec={"config": json.dumps(core_nad_config)},
            ),
        ]

    def _get_core_nad_config(self) -> Dict[Any, Any]:
        """Get core interface NAD config.

        Returns:
            config (dict): Core interface NAD config
        """
        config = {
            "cniVersion": CNI_VERSION,
            "type": "bridge",
            "bridge": CORE_INTERFACE_BRIDGE_NAME,
            "ipam": {
                "type": "static",
                "addresses": [
                    {
                        "address": f"{CORE_IP_ADDRESS}/24",
                    }
                ],
            },
            "capabilities": {"mac": True},
        }

        return config

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
                        "command": f"iperf3 -s --bind {CORE_IP_ADDRESS} -p {IPERF3_PORT}",
                        "startup": "enabled",
                    }
                },
            }
        )


if __name__ == "__main__":  # pragma: nocover
    ops.main(Iperf3K8SOperatorCharm)  # type: ignore

# Copyright 2024 Guillaume Belanger.
# See LICENSE file for licensing details.

resource "juju_application" "iperf3" {
  name  = var.app_name
  model = var.model

  charm {
    name     = "iperf3-k8s"
    channel  = var.channel
    revision = var.revision
    base     = var.base
  }

  config      = var.config
  constraints = var.constraints
  resources   = var.resources
  trust       = true
  units       = var.units
}

# Copyright 2024 Guillaume Belanger.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.iperf3.name
}

output "requires" {
  value = {
  }
}

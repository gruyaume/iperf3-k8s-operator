# iPerf3 K8s Terraform Module

This folder contains a base [Terraform][Terraform] module for the iperf3-k8s charm.

The module uses the [Terraform Juju provider][Terraform Juju provider] to model the charm
deployment onto any Kubernetes environment managed by [Juju][Juju].

The base module is not intended to be deployed in separation (it is possible though), but should
rather serve as a building block for higher level modules.

## Module structure

- **main.tf** - Defines the Juju application to be deployed.
- **variables.tf** - Allows customization of the deployment. Except for exposing the deployment
  options (Juju model name, channel or application name) also allows overwriting charm's default
  configuration.
- **output.tf** - Responsible for integrating the module with other Terraform modules, primarily
  by defining potential integration endpoints (charm integrations), but also by exposing
  the application name.
- **versions.tf** - Defines the Terraform provider.

## Using iperf3-k8s base module in higher level modules

If you want to use `iperf3-k8s` base module as part of your Terraform module, import it
like shown below:

```text
data "juju_model" "my_model" {
  name = "my_model_name"
}

module "iperf3" {
  source = "git::https://github.com/canonical/iperf3-k8s-operator//terraform"
  
  model = juju_model.my_model.name
  config = Optional config map
}
```

The complete list of available integrations can be found [here][iperf3-integrations].

[Terraform]: https://www.terraform.io/
[Terraform Juju provider]: https://registry.terraform.io/providers/juju/juju/latest
[Juju]: https://juju.is
[iperf3-integrations]: https://charmhub.io/iperf3-k8s/integrations

# iperf3 (k8s)

iPerf is a speed test tool for TCP, UDP and SCTP.

iperf3-k8s is a Juju charm for operating iPerf3 in Kubernetes.

## Documentation

### Getting Started

```shell
juju deploy iperf3-k8s
```

The charm will use Multus to create a network attachment definition on the "core-br" bridge. The iPerf3 server will listen on this address, on port 5201.

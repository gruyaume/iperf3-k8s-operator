#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import pytest
import yaml
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./charmcraft.yaml").read_text())
APP_NAME = METADATA["name"]

TIMEOUT = 15 * 60


@pytest.fixture(scope="module")
async def deploy(ops_test: OpsTest, request):  # type: ignore[reportMissingParameterType]
    """Deploy the charm-under-test together with related charms.

    Assert on the unit status before any relations/configurations take place.
    """
    assert ops_test.model
    charm = Path(request.config.getoption("--charm_path")).resolve()
    resources = {"iperf3-image": METADATA["resources"]["iperf3-image"]["upstream-source"]}
    await ops_test.model.deploy(
        charm,
        resources=resources,
        application_name=APP_NAME,
        series="jammy",
    )


@pytest.mark.abort_on_fail
async def test_given_charm_is_built_when_deployed_then_status_is_active(
    ops_test: OpsTest,
    deploy,  # type: ignore[reportMissingParameterType]
):
    assert ops_test.model
    await ops_test.model.wait_for_idle(
        apps=[APP_NAME],
        status="active",
        timeout=TIMEOUT,
    )

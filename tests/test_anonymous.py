#!/usr/bin/env python
"""Basic requests that are meaningful for anonymous users

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
import pytest

from rerobots.api import APIClient
from rerobots.api import WrongAuthToken


def test_deployments_list():
    apic = APIClient()
    res = apic.get_deployments()
    assert len(res) > 0
    # len(res) == 0 is also correct in general. However, that would
    # imply that rerobots has no active workspace deployments, which
    # should be rare or never.


def test_deployment_details():
    apic = APIClient()
    workspace_deployments, page_count = apic.get_deployments(page=1, max_per_page=1)

    # This assertion is redundant with test_deployments_list(), but it
    # is among preconditions for the test below.
    assert len(workspace_deployments) > 0

    wdeployment_id = workspace_deployments[0]
    details = apic.get_deployment_info(wdeployment_id)
    assert 'id' in details
    assert 'type' in details


def test_instances_list():
    apic = APIClient()
    with pytest.raises(WrongAuthToken):
        apic.get_instances()


def test_instances_list_badtoken():
    apic = APIClient(api_token='deadbeef')
    with pytest.raises(WrongAuthToken):
        apic.get_instances()

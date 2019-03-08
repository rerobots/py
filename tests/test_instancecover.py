#!/usr/bin/env python
"""Basic requests that are meaningful for any workspace instance

N.B., these tests require a rerobots API token, and the associated
user account WILL BE BILLED FOR ANY COSTS FROM PERFORMING THESE TESTS.


SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
import os
import time

import pytest

from rerobots.api import APIClient
from rerobots.api import BusyWorkspaceDeployment, WrongAuthToken


def test_instance_start_terminate():
    candidate_wtypes = [
        'fixed_brunelhand',
    ]
    apic = APIClient()
    available_wdeployments = apic.get_deployments(types=candidate_wtypes, maxlen=0)
    assert len(available_wdeployments) > 0
    payload = None
    for wdeployment_id in available_wdeployments:
        try:
            payload = apic.request_instance(wdeployment_id, reserve=False)
        except BusyWorkspaceDeployment:
            continue
    assert payload['success']
    for terminate_attempt in range(5):
        try:
            apic.terminate_instance(payload['id'])
            break
        except:
            time.sleep(5)

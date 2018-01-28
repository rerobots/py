#!/usr/bin/env python
"""Basic requests that are meaningful for anonymous users

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
from rerobots.api import APIClient


def test_deployments_list():
    apic = APIClient()
    res = apic.get_deployments()
    assert len(res) > 0
    # len(res) == 0 is also correct in general. However, that would
    # imply that rerobots has no active workspace deployments, which
    # should be rare or never.

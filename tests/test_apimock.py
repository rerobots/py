#!/usr/bin/env python
"""Basic requests against a mock API HTTP server

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
import responses

from rerobots.api import APIClient


@responses.activate
def test_deployments_list():
    responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                  json={'workspace_deployments': ['a6b88b4f-2402-41e4-8e81-b2fd852435eb'],
                        'page_count': 1},
                  status=200)
    apic = APIClient()
    res = apic.get_deployments()
    assert len(res) > 0

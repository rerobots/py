#!/usr/bin/env python
"""Basic requests against a mock API HTTP server

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
import unittest

from nose.tools import assert_raises
import responses

from rerobots.api import APIClient
from rerobots.api import Error


@responses.activate
def test_deployments_list():
    responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                  json={'workspace_deployments': ['a6b88b4f-2402-41e4-8e81-b2fd852435eb'],
                        'page_count': 1},
                  status=200)
    apic = APIClient()
    res = apic.get_deployments()
    assert len(res) > 0


class BasicInstanceTestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @responses.activate
    def test_request_instance(self):
        responses.add(responses.POST, 'https://api.rerobots.net/new/{}'.format('a6b88b4f-2402-41e4-8e81-b2fd852435eb'),
                      json={'id': 'c81613e1-2d4c-4751-b3bc-08e604656c2d',
                            'success': True},
                      status=200)
        responses.add(responses.POST, 'https://api.rerobots.net/new/{}'.format('a6b88b4f-2402-41e4-8e81-b2fd852435eb'),
                      json={'result_message': ('All matching workspace deployments are busy.'
                                               ' Try again later.')},
                      status=503)
        apic = APIClient()
        res = apic.request_instance('a6b88b4f-2402-41e4-8e81-b2fd852435eb', reserve=False)
        assert res['success']
        assert 'id' in res
        with assert_raises(Error):
            apic.request_instance('a6b88b4f-2402-41e4-8e81-b2fd852435eb', reserve=False)

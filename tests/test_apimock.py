#!/usr/bin/env python
"""Basic requests against a mock API HTTP server

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
import json
import unittest

import pytest
import responses

from rerobots.api import APIClient, Instance
from rerobots.api import Error, WrongAuthToken


@responses.activate
def test_wdeployments_list():
    responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                  json={'workspace_deployments': ['a6b88b4f-2402-41e4-8e81-b2fd852435eb'],
                        'page_count': 1},
                  status=200)
    responses.add(responses.GET, 'https://api.rerobots.net/deployment/a6b88b4f-2402-41e4-8e81-b2fd852435eb',
                  json={'id': 'a6b88b4f-2402-41e4-8e81-b2fd852435eb',
                        'type': 'null',
                        'type_version': 1,
                        'supported_addons': [],
                        'desc': '',
                        'region': 'us:cali',
                        'icounter': 1,
                        'created': '2019-06-25 07:21:48.223695',
                        'queuelen': 0},
                  status=200)
    apic = APIClient(ignore_env=True)
    res = apic.get_wdeployments()
    assert len(res) > 0


@responses.activate
def test_instances_list_badtoken():
    responses.add(responses.GET, 'https://api.rerobots.net/instances',
                  json={'error_message': 'wrong authorization token'},
                  status=400)
    apic = APIClient(api_token='deadbeef', ignore_env=True)
    with pytest.raises(WrongAuthToken):
        apic.get_instances()


class BasicInstanceTestCases(unittest.TestCase):
    def setUp(self):
        self.wdeployment_id = 'a6b88b4f-2402-41e4-8e81-b2fd852435eb'
        self.instance_ids_stack = ['c81613e1-2d4c-4751-b3bc-08e604656c2d']
        self.active_instances = []
        responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                      json={'workspace_deployments': [self.wdeployment_id],
                            'page_count': 1},
                      status=200)
        responses.add(responses.GET, 'https://api.rerobots.net/deployment/{}'.format(self.wdeployment_id),
                      json={'id': 'a6b88b4f-2402-41e4-8e81-b2fd852435eb',
                            'type': 'null',
                            'type_version': 1,
                            'supported_addons': [],
                            'desc': '',
                            'region': 'us:cali',
                            'icounter': 1,
                            'created': '2019-06-25 07:21:48.223695',
                            'queuelen': 0},
                      status=200)
        responses.add_callback(responses.POST,
                               'https://api.rerobots.net/new/{}'.format(self.wdeployment_id),
                               callback=self._new_callback,
                               content_type='application/json')

    def tearDown(self):
        pass

    def _new_callback(self, request):
        headers = dict()
        if len(self.instance_ids_stack) == 0:
            message = 'All matching workspace deployments are busy. Try again later.'
            return (503, headers, json.dumps({'result_message': message}))
        else:
            self.active_instances.append(self.instance_ids_stack.pop())
            payload = {
                'id': self.active_instances[-1],
                'success': True,
            }
            return (200, headers, json.dumps(payload))

    @responses.activate
    def test_request_instance(self):
        apic = APIClient(ignore_env=True)
        list_of_wdeployments = apic.get_wdeployments()
        assert len(list_of_wdeployments) > 0
        wdeployment_id = list_of_wdeployments[0]['id']
        res = apic.request_instance(wdeployment_id, reserve=False)
        assert res['success']
        assert 'id' in res
        with pytest.raises(Error):
            apic.request_instance(wdeployment_id, reserve=False)

    @responses.activate
    def test_new_Instance(self):
        apic = APIClient(ignore_env=True)
        list_of_wdeployments = apic.get_wdeployments()
        assert len(list_of_wdeployments) > 0
        wdeployment_id = list_of_wdeployments[0]['id']
        inst = Instance(workspace_types=['null'], wdeployment_id=wdeployment_id, apic=apic)
        assert inst is not None

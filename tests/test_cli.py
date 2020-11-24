#!/usr/bin/env python
"""Basic tests of the command-line interface (CLI)

SCL <scott@rerobots.net>
Copyright (c) 2018 rerobots, Inc.
"""
try:
    from cStringIO import StringIO
except ImportError:  # if Python 3
    from io import StringIO
import sys
import unittest

import pytest
import responses

import rerobots
from rerobots import cli
from rerobots.api import WrongAuthToken


def test_version():
    original_stdout = sys.stdout
    sys.stdout = StringIO()
    cli.main(['version'])
    res = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert rerobots.__version__ == res

def test_help():
    original_stdout = sys.stdout
    sys.stdout = StringIO()
    cli.main(['help'])
    res = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert 'rerobots API command-line client' in res

def test_alternative_help_spellings():
    original_stdout = sys.stdout

    # `help`
    sys.stdout = StringIO()
    cli.main(['help'])
    res_help = sys.stdout.getvalue().strip()

    # `-h`
    sys.stdout = StringIO()
    cli.main(['-h'])
    res_dashh = sys.stdout.getvalue().strip()

    # `--help`
    sys.stdout = StringIO()
    cli.main(['--help'])
    res_dashdashhelp = sys.stdout.getvalue().strip()

    sys.stdout = original_stdout

    assert res_help == res_dashh
    assert res_help == res_dashdashhelp


def test_alternative_version_spellings():
    original_stdout = sys.stdout

    # `version`
    sys.stdout = StringIO()
    cli.main(['version'])
    res_version = sys.stdout.getvalue().strip()

    # `-V`
    sys.stdout = StringIO()
    cli.main(['-V'])
    res_dashV = sys.stdout.getvalue().strip()

    # `--version`
    sys.stdout = StringIO()
    cli.main(['--version'])
    res_dashdashversion = sys.stdout.getvalue().strip()

    sys.stdout = original_stdout

    assert res_version == res_dashV
    assert res_version == res_dashdashversion


@pytest.mark.parametrize('command', [
    'info',
    'list',
    'search',
    'launch',
    'terminate',
])
def test_alternative_command_help_spellings(command):
    original_stdout = sys.stdout

    # form: help COMMAND
    sys.stdout = StringIO()
    cli.main(['help', command])
    res_help_command = sys.stdout.getvalue().strip()

    # form: COMMAND --help
    sys.stdout = StringIO()
    cli.main([command, '--help'])
    res_command_dashdashhelp = sys.stdout.getvalue().strip()

    sys.stdout = original_stdout

    assert res_help_command == res_command_dashdashhelp


@responses.activate
def test_instances_list_badtoken():
    responses.add(responses.GET, 'https://api.rerobots.net/instances',
                  json={'error_message': 'wrong authorization token'},
                  status=400)
    original_stdout = sys.stdout
    sys.stdout = StringIO()
    rc = cli.main(['list'])
    assert rc == 1
    res = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout


class MockSearchTestCases(unittest.TestCase):
    def setUp(self):
        self.wdeployment_id = 'a6b88b4f-2402-41e4-8e81-b2fd852435eb'
        self.instance_ids_stack = ['c81613e1-2d4c-4751-b3bc-08e604656c2d']
        self.active_instances = []
        responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                      json={'workspace_deployments': [self.wdeployment_id],
                            'info': {'a6b88b4f-2402-41e4-8e81-b2fd852435eb': {
                            'type': 'null',
                            'region': 'us:cali',
                            'queuelen': 0,
                        }},
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

    def tearDown(self):
        pass

    @responses.activate
    def test_emptysearch(self):
        original_stdout = sys.stdout
        sys.stdout = StringIO()
        cli.main(['search'])
        res = sys.stdout.getvalue().strip()
        sys.stdout = original_stdout
        assert 'a6b88b4f-2402-41e4-8e81-b2fd852435eb' in res

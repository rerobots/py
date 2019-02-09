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

import responses

import rerobots
from rerobots import cli


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

def test_alternative_spellings():
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


class MockSearchTestCases(unittest.TestCase):
    def setUp(self):
        self.wdeployment_id = 'a6b88b4f-2402-41e4-8e81-b2fd852435eb'
        self.instance_ids_stack = ['c81613e1-2d4c-4751-b3bc-08e604656c2d']
        self.active_instances = []
        responses.add(responses.GET, 'https://api.rerobots.net/deployments',
                      json={'workspace_deployments': [self.wdeployment_id],
                            'page_count': 1},
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

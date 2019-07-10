#!/usr/bin/env python
"""

SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
import os

from rerobots.api import APIClient


def test_init_vs_add_client_headers():
    apic1 = APIClient(ignore_env=True)
    apic1.add_client_headers({'X-Example-1': 'ex1'})
    apic2 = APIClient(headers={'X-Example-1': 'ex1'}, ignore_env=True)
    assert apic1.get_client_headers() == apic2.get_client_headers()


def test_acc_add_client_headers():
    apic1 = APIClient(ignore_env=True)
    apic1.add_client_headers({'X-Example-1': 'ex1'})
    apic1.add_client_headers({'X-Example-2': 'ex2'})
    apic2 = APIClient(ignore_env=True)
    apic2.add_client_headers({
        'X-Example-1': 'ex1',
        'X-Example-2': 'ex2',
    })
    assert apic1.get_client_headers() == apic2.get_client_headers()


def test_clear_client_headers():
    apic = APIClient(ignore_env=True)
    apic.clear_client_headers()
    assert len(apic.get_client_headers()) == 0
    apic.add_client_headers({'X-Example-1': 'ex1'})
    assert len(apic.get_client_headers()) == 1
    apic.clear_client_headers()
    assert len(apic.get_client_headers()) == 0


def test_init_vs_apply_auth_token():
    apic1 = APIClient(ignore_env=True)
    apic1.apply_auth_token('deadbeef')
    apic2 = APIClient(api_token='deadbeef', ignore_env=True)
    assert apic1.get_client_headers() == apic2.get_client_headers()


def test_init_vs_environ_auth_token():
    _prev = os.environ.get('REROBOTS_API_TOKEN', None)
    os.environ['REROBOTS_API_TOKEN'] = 'deadbeef'
    apic1 = APIClient()
    del os.environ['REROBOTS_API_TOKEN']
    apic2 = APIClient()
    assert apic1.get_client_headers() != apic2.get_client_headers()
    apic2 = APIClient(api_token='deadbeef')
    assert apic1.get_client_headers() == apic2.get_client_headers()
    if _prev:
        os.environ['REROBOTS_API_TOKEN'] = _prev

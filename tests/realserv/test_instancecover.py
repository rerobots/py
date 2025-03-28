#!/usr/bin/env python
"""Basic requests that are meaningful for any workspace instance

N.B., these tests require a rerobots API token, and the associated
user account WILL BE BILLED FOR ANY COSTS FROM PERFORMING THESE TESTS.

To perform these tests, assign a rerobots API token to the environment
variable `REROBOTS_API_TOKEN`.


SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
import os
import random
import tempfile
import time


from rerobots.api import APIClient
from rerobots import Instance
from rerobots.api import BusyWorkspaceDeployment, BusyWorkspaceInstance


def test_instance_start_terminate():
    # Instantiate from among a given feasible list
    candidate_wtypes = [
        'fixed_misty2',
    ]
    available_wdeployments = APIClient().get_wdeployments(
        types=candidate_wtypes, maxlen=0
    )
    assert len(available_wdeployments) > 0
    inst = None
    for instantiate_attempt in range(5):
        for wdeployment in available_wdeployments:
            try:
                inst = Instance(wdeployment_id=wdeployment['id'])
            except BusyWorkspaceDeployment:
                continue
            break
        if inst is not None:
            break
    assert inst is not None

    # Wait for instance to be READY
    start_time = time.monotonic()
    while time.monotonic() - start_time < 180:
        if inst.get_status() == 'READY':
            ready_become_duration = time.monotonic() - start_time
            print('become ready duration: {}'.format(ready_become_duration))
            break
        time.sleep(2)
    if inst.get_status() != 'READY':
        raise Exception('timed out waiting for instance to become READY')

    # Put file, and ready it back
    rdata = bytes([random.randint(0, 255) for x in range(16)])
    fd, fname = tempfile.mkstemp()
    fp = os.fdopen(fd, 'wb')
    fp.write(rdata)
    fp.close()
    remotepath = '/root/{}'.format(os.path.basename(fname))
    localdir = tempfile.mkdtemp()
    newlocalpath = os.path.join(localdir, 'out')
    start_time = time.monotonic()
    inst.start_sshclient()
    inst.put_file(fname, remotepath)
    inst.get_file(remotepath, newlocalpath)
    file_cycle_duration = time.monotonic() - start_time
    print('cycle file duration: {}'.format(file_cycle_duration))
    with open(newlocalpath, 'rb') as fp:
        rdata_back = fp.read()
    assert rdata == rdata_back
    os.unlink(fname)
    os.unlink(newlocalpath)
    os.rmdir(localdir)

    # Terminate
    terminated = False
    for terminate_attempt in range(7):
        try:
            inst.terminate()
            terminated = True
            break
        except BusyWorkspaceInstance:
            time.sleep(4)
    assert terminated

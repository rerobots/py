"""
SCL <scott@rerobots.net>
Copyright (c) 2017 rerobots, Inc.
"""
import time

import requests


class APIClient(object):
    def __init__(self, api_token=None, base_uri=None, verify=True):
        """Instantiate API client

        `base_uri` is the string prefix used to create API requests.
        In general the default value works, but special cases might
        motivate changing this, e.g., to use an unofficial proxy.

        `verify` determines whether the TLS certificates of the server
        are checked.  Except possibly during testing, this should not
        be False.
        """
        self.api_token = api_token
        if base_uri is None:
            self.base_uri = 'https://api.rerobots.net'
        else:
            self.base_uri = base_uri
        self.verify_certs = verify

    def add_client_headers(self, headers=None):
        """Add request headers associated with this client.

        This function returns a new headers `dict`. If initial values
        are given, then they are shallow-copied.
        """
        if headers is None:
            headers = dict()
        else:
            headers = headers.copy()
        self.add_token_header(headers)
        return headers

    def add_token_header(self, headers):
        """Add API token associated with this client into request headers

        If there is no API token associated with this client, then
        this function does nothing.

        This function updates the given headers `dict` in-place.
        """
        if self.api_token is not None:
            headers['Authorization'] = 'Bearer ' + self.api_token

    def get_deployments(self, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/deployments', headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        return payload['workspace_deployments']

    def get_deployment_info(self, deployment_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/deployment/' + deployment_id, headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        return payload

    def get_instances(self, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/instances', headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        return payload['workspace_instances']

    def get_instance_info(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/instance/' + instance_id, headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        return payload

    def terminate_instance(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/terminate/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise OSError(res.text)

    def request_instance(self, deployment_id, max_tries=1, headers=None):
        headers = self.add_client_headers(headers)
        max_tries = 5
        counter = 0
        payload = None
        while counter < max_tries:
            counter += 1
            res = requests.post(self.base_uri + '/new/' + deployment_id, headers=headers, verify=self.verify_certs)
            if res.ok:
                payload = res.json()
                break
            elif res.status_code == 503: # => busy, try again later
                if counter >= max_tries:
                    break
                time.sleep(1)
                continue
            else:
                raise OSError(res.text)
        if payload is None:
            return None, None
        res = requests.post(self.base_uri + '/firewall/' + payload['id'], headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise OSError(res.text)
        return payload['id'], payload['sshkey']

"""Classes to manage API access


SCL <scott@rerobots.net>
Copyright (c) 2017, 2018 rerobots, Inc.
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

    def get_deployments(self, q=None, maxlen=None, types=None, page=None, max_per_page=None, headers=None):
        """get list of workspace deployments

        `types`, if given, should be a list of workspace types (str).
        The significance of parameters is described in the HTTP-based
        API documentation.

        The parameters `page` and `max_per_page` can be used for
        pagination, which restricts the maximum number of items in the
        list of instances returned in any one response.
        Cf. documentation of the HTTP API.
        """
        headers = self.add_client_headers(headers)
        params = dict()
        if max_per_page is not None:
            params['max_per_page'] = max_per_page
            if page is not None:
                params['page'] = page
        if q is not None:
            params['q'] = q
        if maxlen is not None:
            params['maxlen'] = maxlen
        if types is not None:
            params['types'] = ','.join(types)
        res = requests.get(self.base_uri + '/deployments', params=params, headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        if max_per_page is None:
            return payload['workspace_deployments']
        else:
            return payload['workspace_deployments'], payload['page_count']

    def get_deployment_info(self, deployment_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/deployment/' + deployment_id, headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        return payload

    def get_instances(self, include_terminated=False, page=None, max_per_page=None, headers=None):
        """get list of your instances

        The parameters `page` and `max_per_page` can be used for
        pagination, which restricts the maximum number of items in the
        list of instances returned in any one response.
        Cf. documentation of the HTTP API.
        """
        headers = self.add_client_headers(headers)
        params = dict()
        if include_terminated:
            params['include_terminated'] = ''
        if max_per_page is not None:
            params['max_per_page'] = max_per_page
            if page is not None:
                params['page'] = page
        res = requests.get(self.base_uri + '/instances', params=params, headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise OSError(res.text)
        if max_per_page is None:
            return payload['workspace_instances']
        else:
            return payload['workspace_instances'], payload['page_count']

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

    def request_instance(self, deployment_id, sshkey=None, max_tries=1, headers=None):
        """Request new workspace instance

        If given, sshkey is the public key of the key pair with which
        the user can sign-in to the instance. Otherwise (default), a
        key pair is automatically generated.
        """
        headers = self.add_client_headers(headers)
        counter = 0
        payload = None
        while counter < max_tries:
            counter += 1
            if sshkey is None:
                res = requests.post(self.base_uri + '/new/' + deployment_id, headers=headers, verify=self.verify_certs)
            else:
                res = requests.post(self.base_uri + '/new/' + deployment_id, data='{"sshkey": "'+sshkey+'"}', headers=headers, verify=self.verify_certs)
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
            # Match length of expected return tuple
            if sshkey is None:
                return None, None
            else:
                return None
        if 'sshkey' in payload:
            return payload['id'], payload['sshkey']
        else:
            return payload['id']

    def get_firewall_rules(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/firewall/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise OSError(res.text)
        return res.json()['rules']

    def add_firewall_rule(self, instance_id, action, source_address=None, headers=None):
        headers = self.add_client_headers(headers)
        if action not in ['ACCEPT', 'DROP', 'REJECT']:
            raise OSError('unrecognized firewall action')
        if source_address is None:
            payload = '{"action": "' + action + '"}'
        else:
            payload = '{"src": "' + source_address + '", "action": "' + action + '"}'
        res = requests.post(self.base_uri + '/firewall/' + instance_id, data=payload,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise OSError(res.text)

    def flush_firewall_rules(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.delete(self.base_uri + '/firewall/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise OSError(res.text)

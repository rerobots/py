"""Classes to manage API access


SCL <scott@rerobots.net>
Copyright (c) 2017, 2018 rerobots, Inc.
"""
import hashlib
import json
import time

import requests


class Error(Exception):
    """Error not otherwise specified

    Where feasible, some diagnostics from the server will be included
    in the exception message.
    """
    pass

class WrongAuthToken(Error):
    """An action requires, but was not given, some valid API token.

    There are several potential solutions, but in most cases it should
    suffice to sign-in to the rerobots Web UI and visit

    https://rerobots.net/tokens

    where you can manage your API tokens.  Use add_token_header() of
    APIClient to automatically send an API token with each request.
    """
    pass


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
            raise Error(res.text)
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
            raise Error(res.text)
        return payload

    def get_access_rules(self, to_user=None, deployment_id=None, headers=None):
        """get list of access control rules of workspace deployments
        """
        headers = self.add_client_headers(headers)
        params = dict()
        if to_user is not None:
            params['to_user'] = to_user
        if deployment_id is not None:
            params['wdeployment'] = deployment_id
        res = requests.get(self.base_uri + '/rules', params=params,
                           headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'error_message' in payload:
                if payload['error_message'] == 'wrong authorization token':
                    raise WrongAuthToken
                else:
                    raise Error(payload['error_message'])
            else:
                raise Error(payload)
        return payload['rules']

    def add_access_rule(self, deployment_id, capability, to_user=None, headers=None):
        self._modify_access_rule(deployment_id=deployment_id, capability=capability, to_user=to_user, action='add', headers=headers)

    def del_access_rule(self, deployment_id, capability, to_user=None, headers=None):
        self._modify_access_rule(deployment_id=deployment_id, capability=capability, to_user=to_user, action='del', headers=headers)

    def _modify_access_rule(self, deployment_id, capability, action, to_user=None, headers=None):
        headers = self.add_client_headers(headers)
        body = {
            'do': action,
            'wd': deployment_id,
            'cap': capability,
        }
        if to_user is not None:
            body['user'] = to_user
        res = requests.post(self.base_uri + '/rule', data=json.dumps(body),
                            headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

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
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'error_message' in payload:
                if payload['error_message'] == 'wrong authorization token':
                    raise WrongAuthToken
                else:
                    raise Error(payload['error_message'])
            else:
                raise Error(payload)
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
            raise Error(res.text)
        return payload

    def terminate_instance(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/terminate/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def request_instance(self, deployment_id, sshkey=None, vpn=False, reserve=False, event_url=None, headers=None):
        """Request new workspace instance

        If given, sshkey is the public key of the key pair with which
        the user can sign-in to the instance. Otherwise (default), a
        key pair is automatically generated.

        If reserve=True, then create a reservation if the workspace
        deployment is not available at the time of this request.
        """
        headers = self.add_client_headers(headers)
        counter = 0
        payload = None
        body = dict()
        if sshkey is not None:
            body['sshkey'] = sshkey
        if vpn:
            body['vpn'] = vpn
        body['reserve'] = reserve
        if event_url is not None:
            body['eurl'] = event_url
        if len(body) == 0:
            res = requests.post(self.base_uri + '/new/' + deployment_id, headers=headers, verify=self.verify_certs)
        else:
            res = requests.post(self.base_uri + '/new/' + deployment_id, data=json.dumps(body), headers=headers, verify=self.verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise Error(res.text)
        return payload

    def get_reservations(self, headers=None):
        """get list of your reservations
        """
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/reservations', headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()['reservations']

    def cancel_reservation(self, reservation_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.delete(self.base_uri + '/reservation/' + reservation_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_firewall_rules(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/firewall/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()['rules']

    def add_firewall_rule(self, instance_id, action, source_address=None, headers=None):
        headers = self.add_client_headers(headers)
        if action not in ['ACCEPT', 'DROP', 'REJECT']:
            raise Error('unrecognized firewall action')
        if source_address is None:
            payload = '{"action": "' + action + '"}'
        else:
            payload = '{"src": "' + source_address + '", "action": "' + action + '"}'
        res = requests.post(self.base_uri + '/firewall/' + instance_id, data=payload,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def flush_firewall_rules(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.delete(self.base_uri + '/firewall/' + instance_id, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_vpn_newclient(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/vpn/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()

    def revoke_token(self, token=None, sha256=None, headers=None):
        if token is None and sha256 is None:
            raise ValueError('token or sha256 must be non-None')
        if token is not None:
            if isinstance(token, str):
                token = bytes(token, encoding='utf-8')
            token_hash = hashlib.sha256(token).hexdigest()
            if sha256 is not None and sha256 != token_hash:
                raise ValueError('both token or sha256 given, '
                                 'but SHA256(token) != sha256')
            sha256 = token_hash
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/revoke/' + sha256, headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def purge(self, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/purge', headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

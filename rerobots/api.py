"""Classes to manage API access


SCL <scott@rerobots.net>
Copyright (c) 2017, 2018 rerobots, Inc.
"""
import base64
from io import BytesIO
import hashlib
import json
import os
import tempfile
import time

import requests

# inline: PIL, numpy
# only required for certain code paths that go beyond core routines.
# e.g., get_snapshot_cam(format='array')

# inline: paramiko
# only required by Instance class


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

    def activate_addon_vnc(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/addon/vnc/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_vnc(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/addon/vnc/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        elif res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def start_addon_vnc(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/addon/vnc/' + instance_id + '/start',  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def stop_addon_vnc(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/addon/vnc/' + instance_id + '/stop',  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def deactivate_addon_vnc(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.delete(self.base_uri + '/addon/vnc/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def activate_addon_cam(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.post(self.base_uri + '/addon/cam/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_cam(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/addon/cam/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        elif res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def deactivate_addon_cam(self, instance_id, headers=None):
        headers = self.add_client_headers(headers)
        res = requests.delete(self.base_uri + '/addon/cam/' + instance_id,  headers=headers, verify=self.verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_snapshot_cam(self, instance_id, camera_id=1, coding=None, format=None, headers=None):
        """Get image from camera via cam add-on

        If coding=None (default), then returned data are not
        encoded. The only coding supported is base64, which can be
        obtained with coding='base64'.

        If format=None (default), then the image format is whatever
        the rerobots API provided. Currently, this can be 'jpeg' or
        'ndarray' (i.e., ndarray type of NumPy).

        Note that some coding and format combinations are not
        compatible. In particular, if format='ndarray', then coding
        must be None.
        """
        if format is not None:
            format = format.lower()
            assert format in ['ndarray', 'jpeg']
        headers = self.add_client_headers(headers)
        res = requests.get(self.base_uri + '/addon/cam/{}/{}/img'.format(instance_id, camera_id),  headers=headers, verify=self.verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        else:
            payload = res.json()
        if not payload['success']:
            return payload
        if 'coding' in payload and payload['coding'] != coding:
            if (coding is None) and payload['coding'] == 'base64':
                payload['data'] = base64.b64decode(payload['data'])
                payload['coding'] = None
        if (format is not None) and (payload['format'].lower() != format):
            if format == 'ndarray':
                assert coding is None
                from PIL import Image
                import numpy as np
                x = BytesIO()
                x.write(payload['data'])
                x.seek(0)
                img = Image.open(x)
                payload['data'] = np.array(img.getdata(), dtype=np.uint8)
                payload['data'] = payload['data'].reshape(img.size[1], img.size[0], 3)
                payload['format'] = 'ndarray'
        return payload

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


class Instance(APIClient):
    def __init__(self, workspace_types=None, wdeployment_id=None, api_token=None, base_uri=None, verify=True):
        """

        Either workspace_types or wdeployment_id must be given.
        """
        super().__init__(api_token=api_token, base_uri=base_uri, verify=verify)
        if ((workspace_types is None and wdeployment_id is None)
            or (workspace_types != None and wdeployment_id != None)):
            raise ValueError('either workspace_types or wdeployment_id must be given, but not both')
        if workspace_types is not None:
            candidates = self.get_deployments(types=workspace_types)
            if len(candidates) < 1:
                raise ValueError('no deployments found with any type in {}'.format(workspace_types))
            self._wdeployment_id = candidates[0]

        else:
            self._wdeployment_id = wdeployment_id

        self._type = None

        payload = self.request_instance(self._wdeployment_id, reserve=False)
        self._id = payload['id']
        self._status = 'INIT'  # Instance always begins at INIT
        self._details = None
        if 'sshkey' in payload:
            self._sshkey = payload['sshkey']
        else:
            self._sshkey = None
        self._conn = None
        self._sshclient = None


    def get_deployment_info(self, headers=None):
        return super().get_deployment_info(self._wdeployment_id, headers=headers)


    def get_access_rules(self, to_user=None, headers=None):
        return super().get_access_rules(to_user=to_user, deployment_id=self._wdeployment_id, headers=headers)

    def add_access_rule(self, capability, to_user=None, headers=None):
        super().add_access_rule(deployment_id=self._wdeployment_id, capability=capability, to_user=to_user, headers=headers)

    def del_access_rule(self, capability, to_user=None, headers=None):
        super().del_access_rule(deployment_id=self._wdeployment_id, capability=capability, to_user=to_user, headers=headers)


    def get_firewall_rules(self, headers=None):
        return super().get_firewall_rules(self._id, headers=headers)

    def add_firewall_rule(self, action, source_address=None, headers=None):
        super().add_firewall_rule(self._id, action=action, source_address=source_address, headers=headers)

    def flush_firewall_rules(self, headers=None):
        super().flush_firewall_rules(self._id, headers=headers)


    def get_vpn_newclient(self, headers=None):
        return super().get_vpn_newclient(self._id, headers=headers)


    def activate_addon_cam(self, headers=None):
        super().activate_addon_cam(self._id, headers=headers)

    def status_addon_cam(self, headers=None):
        return super().status_addon_cam(self._id, headers=headers)

    def get_snapshot_cam(self, camera_id=1, coding=None, format=None, headers=None):
        return super().get_snapshot_cam(self._id, camera_id=camera_id, coding=coding, format=format, headers=headers)

    def deactivate_addon_cam(self, headers=None):
        super().deactivate_addon_cam(self._id, headers=headers)


    def get_status(self):
        payload = self.get_instance_info(self._id)
        if self._wdeployment_id is None:
            self._wdeployment_id = payload['deployment']
        if self._details is None:
            self._details = {
                'type': payload['type'],
                'region': payload['region'],
                'starttime': payload['starttime'],
            }
        self._status = payload['status']
        if 'fwd' in payload:
            self._conn = {
                'type': 'sshtun',
            }
            if 'ipv4' in payload['fwd']:
                self._conn['ipv4'] = payload['fwd']['ipv4']
            if 'port' in payload['fwd']:
                self._conn['port'] = payload['fwd']['port']
            if 'hostkeys' in payload:
                self._conn['hostkeys'] = payload['hostkeys']
        return self._status


    def get_details(self):
        status = self.get_status()
        res = self._details.copy()
        res['status'] = status
        if self._conn is not None:
            res['conn'] = self._conn
        return res


    def terminate(self):
        self.stop_sshclient()
        self.terminate_instance(self._id)


    def stop_sshclient(self):
        if self._sshclient is not None:
            self._sshclient.close()
            self._sshclient = None


    def start_sshclient(self):
        import paramiko
        status = self.get_status()
        if status != 'READY':
            raise Exception('instance not ready')
        host = self._conn['ipv4']
        port = self._conn['port']
        hostkey = self._conn['hostkeys'][0]

        fd, keypath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wt')
        fp.write(self._sshkey)
        fp.close()

        fd, known_hosts = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wt')
        sshhost = '[{IPADDR}]:{PORT}'.format(IPADDR=host, PORT=port)
        fp.write(sshhost + ' ' + hostkey)
        fp.close()

        self._sshclient = paramiko.client.SSHClient()
        self._sshclient.load_system_host_keys(known_hosts)
        pkey = paramiko.rsakey.RSAKey.from_private_key_file(keypath)
        self._sshclient.connect(host, port=port, username='root', pkey=pkey, timeout=5)

        os.unlink(keypath)
        os.unlink(known_hosts)


    def exec_ssh(self, command):
        assert self._sshclient is not None
        stdin, stdout, stderr = self._sshclient.exec_command(command)
        return stdout.read()

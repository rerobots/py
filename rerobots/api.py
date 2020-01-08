"""Classes to manage API access


SCL <scott@rerobots.net>
Copyright (c) 2017-2019 rerobots, Inc.
"""
import base64
from io import BytesIO
import hashlib
import json
import os
import tempfile

import requests

# inline: PIL, numpy
# only required for certain code paths that go beyond core routines.
# e.g., get_snapshot_cam(dformat='array')

# inline: paramiko
# only required by Instance class


class Error(Exception):
    """Error not otherwise specified

    Where feasible, some diagnostics from the server will be included
    in the exception message.
    """

class BusyWorkspaceDeployment(Error):
    """Request failed because all matching workspace deployments are busy.

    This implies that a reservation was not made, e.g., because the
    user specified to not make one during their launch request.
    """

class BusyWorkspaceInstance(Error):
    """Instance is busy, and the request cannot be queued.
    """

class InstanceNotFound(Error):
    """No instance found with given identifier.
    """

class WrongAuthToken(Error):
    """An action requires, but was not given, some valid API token.

    There are several potential solutions, but in most cases it should
    suffice to sign-in to the rerobots Web UI and visit

    https://rerobots.net/tokens

    where you can manage your API tokens.  Use add_token_header() of
    APIClient to automatically send an API token with each request.
    """


class APIClient(object):  # pylint: disable=too-many-public-methods
    """API client object
    """
    def __init__(self, api_token=None, headers=None, ignore_env=False, base_uri=None, verify=True):
        """Instantiate API client.

        `api_token` is some auth token obtained from https://rerobots.net/tokens
        In general this token has limited scope and might not be sufficient for
        some actions that this API client will try to do, leading to the
        exception WrongAuthToken.

        `headers` is a dictionary of headers to add to every request made by
        this client object. This is only of interest in special use-cases.

        `ignore_env` determines whether configuration data should be
        obtained from the process environment variable REROBOTS_API_TOKEN.
        Default (ignore_env=False) behavior is to try REROBOTS_API_TOKEN
        if `api_token` is not given.

        `base_uri` is the string prefix used to create API requests.
        In general the default value works, but special cases might
        motivate changing this, e.g., to use an unofficial proxy.

        `verify` determines whether the TLS certificates of the server
        are checked.  Except possibly during testing, this should not
        be False.
        """
        self.__api_token = api_token
        if self.__api_token is None and not ignore_env:
            self.__api_token = os.environ.get('REROBOTS_API_TOKEN', None)
        if headers is None:
            self.__headers = dict()
        else:
            self.__headers = headers.copy()
        if self.__api_token:
            self.__headers['Authorization'] = 'Bearer ' + self.__api_token
        if base_uri is None:
            self.__base_uri = 'https://api.rerobots.net'
        else:
            self.__base_uri = base_uri
        self.__verify_certs = verify

    def add_client_headers(self, headers=None):
        """Add request headers associated with this client.

        This method accumulates headers. E.g.,

            add_client_headers({'X-Example-1': 'ex1'})
            add_client_headers({'X-Example-2': 'ex2'})

        is equivalent to

            add_client_headers({'X-Example-1': 'ex1', 'X-Example-2': 'ex2'})

        Note that it is not possible to overwrite an existing API token with an
        Authorization header. In other words, if an Authorization header is
        included, then it will be ignored if there is already an API token
        associated with this client object.
        """
        if headers is None:
            headers = dict()
        else:
            headers = headers.copy()
        self.__headers.update(headers)
        if self.__api_token and 'Authorization' in headers:
            headers['Authorization'] = 'Bearer ' + self.__api_token

    def get_client_headers(self):
        """Get copy of all supplemental request headers.

        E.g., added by add_client_headers()
        """
        return self.__headers.copy()

    def clear_client_headers(self):
        """Clear (remove) all supplemental headers associated with this client.

        This method does not affect API tokens associated with
        this client, if any.
        """
        self.__headers = dict()

    def apply_auth_token(self, token):
        """Associate given API (auth) token with this client.

        If there is already an associated API token, it will be overwritten.
        """
        self.__api_token = token
        self.__headers['Authorization'] = 'Bearer ' + self.__api_token

    def get_wdeployments(self, query=None, maxlen=None, types=None, page=None, max_per_page=None):
        """Get list of workspace deployments.

        `types`, if given, should be a list of workspace types (str).
        The significance of parameters is described in the HTTP-based
        API documentation.

        The parameters `page` and `max_per_page` can be used for
        pagination, which restricts the maximum number of items in the
        list of instances returned in any one response.
        Cf. documentation of the HTTP API.
        """
        params = dict()
        if max_per_page is not None:
            params['max_per_page'] = max_per_page
            if page is not None:
                params['page'] = page
        if query is not None:
            params['q'] = query
        if maxlen is not None:
            params['maxlen'] = maxlen
        if types is not None:
            params['types'] = ','.join(types)
        res = requests.get(self.__base_uri + '/deployments', params=params, headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise Error(res.text)
        page_count = payload.get('page_count', None)
        wdeployments = []
        for wdeployment in payload['workspace_deployments']:
            payload = self.get_wdeployment_info(wdeployment)
            wdeployments.append({
                'id': wdeployment,
                'type': payload['type'],
            })
        if max_per_page is None:
            return wdeployments
        return wdeployments, page_count

    def get_wdeployment_info(self, wdeployment_id):
        """Get details about a workspace deployment.
        """
        res = requests.get(self.__base_uri + '/deployment/' + wdeployment_id, headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            raise Error(res.text)
        return payload

    def get_access_rules(self, to_user=None, wdeployment_id=None):
        """Get list of access control rules of workspace deployments.
        """
        params = dict()
        if to_user is not None:
            params['to_user'] = to_user
        if wdeployment_id is not None:
            params['wdeployment'] = wdeployment_id
        res = requests.get(self.__base_uri + '/rules', params=params,
                           headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'error_message' in payload:
                if payload['error_message'] == 'wrong authorization token':
                    raise WrongAuthToken('wrong authorization token')
                raise Error(payload['error_message'])
            raise Error(payload)
        return payload['rules']

    def add_access_rule(self, wdeployment_id, capability, to_user=None):
        """Add access control rule for workspace deployment.

        This operation is idempotent, i.e., adding the same rule more
        than once has no effect.
        """
        self._modify_access_rule(wdeployment_id=wdeployment_id, capability=capability, to_user=to_user, action='add')

    def del_access_rule(self, wdeployment_id, capability, to_user=None):
        """Delete access control rule from workspace deployment.

        It is an error to try to delete a rule that does not exist.
        """
        self._modify_access_rule(wdeployment_id=wdeployment_id, capability=capability, to_user=to_user, action='del')

    def _modify_access_rule(self, wdeployment_id, capability, action, to_user=None):
        body = {
            'do': action,
            'wd': wdeployment_id,
            'cap': capability,
        }
        if to_user is not None:
            body['user'] = to_user
        res = requests.post(self.__base_uri + '/rule', data=json.dumps(body),
                            headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_instances(self, include_terminated=False, page=None, max_per_page=None):
        """Get list of your instances.

        The parameters `page` and `max_per_page` can be used for
        pagination, which restricts the maximum number of items in the
        list of instances returned in any one response.
        Cf. documentation of the HTTP API.
        """
        params = dict()
        if include_terminated:
            params['include_terminated'] = ''
        if max_per_page is not None:
            params['max_per_page'] = max_per_page
            if page is not None:
                params['page'] = page
        res = requests.get(self.__base_uri + '/instances', params=params, headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'error_message' in payload:
                if payload['error_message'] == 'wrong authorization token':
                    raise WrongAuthToken('wrong authorization token')
                raise Error(payload['error_message'])
            raise Error(payload)
        if max_per_page is None:
            return payload['workspace_instances']
        return payload['workspace_instances'], payload['page_count']

    def get_instance_info(self, instance_id):
        """Get details about a workspace instance.

        This operation requires sufficient permissions by the
        requesting user.
        """
        res = requests.get(self.__base_uri + '/instance/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'error_message' in payload:
                if payload['error_message'] == 'instance not found':
                    raise InstanceNotFound('no instance with identifier {}'.format(instance_id))
                raise Error(payload['error_message'])
            raise Error(payload)
        return payload

    def terminate_instance(self, instance_id):
        """Terminate a workspace instance.
        """
        res = requests.post(self.__base_uri + '/terminate/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            try:
                payload = res.json()
            except:
                raise Error(res.text)
            if 'result_message' in payload:
                errmsg = payload['result_message']
                if errmsg.startswith('This instance is busy.'):
                    raise BusyWorkspaceInstance(errmsg)
                raise Error(errmsg)
            raise Error(payload)

    def request_instance(self, wdeployment_id, sshkey=None, vpn=False, reserve=False, event_url=None, duration=None):
        """Request new workspace instance.

        If given, sshkey is the public key of the key pair with which
        the user can sign-in to the instance. Otherwise (default), a
        key pair is automatically generated.

        If reserve=True, then create a reservation if the workspace
        deployment is not available at the time of this request.
        """
        payload = None
        body = dict()
        if sshkey is not None:
            body['sshkey'] = sshkey
        if duration is not None:
            body['expire_d'] = duration
        if vpn:
            body['vpn'] = vpn
        body['reserve'] = reserve
        if event_url is not None:
            body['eurl'] = event_url
        if body:
            res = requests.post(self.__base_uri + '/new/' + wdeployment_id, data=json.dumps(body), headers=self.__headers, verify=self.__verify_certs)
        else:
            res = requests.post(self.__base_uri + '/new/' + wdeployment_id, headers=self.__headers, verify=self.__verify_certs)
        if res.ok:
            payload = res.json()
        else:
            try:
                payload = res.json()
            except:
                raise Error('Response {}: {}'.format(res.status_code, res.content))
            errmsg = payload.get('result_message', None)
            if errmsg is None:
                errmsg = payload.get('error', None)
            if errmsg is None:
                raise Error(payload)
            if errmsg.startswith('All matching workspace deployments are busy'):
                raise BusyWorkspaceDeployment(errmsg)
            raise Error(errmsg)

        return payload

    def get_reservations(self):
        """Get list of your reservations.
        """
        res = requests.get(self.__base_uri + '/reservations', headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()['reservations']

    def cancel_reservation(self, reservation_id):
        """Cancel a reservation.

        This operation cannot be undone.
        """
        res = requests.delete(self.__base_uri + '/reservation/' + reservation_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_firewall_rules(self, instance_id):
        """Get list of firewall rules of an instance.

        These rules are also known as packet filter rules. They are
        similar to rule specifications of Linux iptables.
        """
        res = requests.get(self.__base_uri + '/firewall/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()['rules']

    def add_firewall_rule(self, instance_id, action, source_address=None):
        """Add a firewall rule.

        Related methods: get_firewall_rules(), flush_firewall_rules().
        """
        if action not in ['ACCEPT', 'DROP', 'REJECT']:
            raise Error('unrecognized firewall action')
        if source_address is None:
            payload = '{"action": "' + action + '"}'
        else:
            payload = '{"src": "' + source_address + '", "action": "' + action + '"}'
        res = requests.post(self.__base_uri + '/firewall/' + instance_id, data=payload, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def flush_firewall_rules(self, instance_id):
        """Remove all firewall rules.

        N.B., after this operation, any source address can send
        packets to the public address of your workspace instance.
        """
        res = requests.delete(self.__base_uri + '/firewall/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_vpn_newclient(self, instance_id):
        """Create new OpenVPN client.
        """
        res = requests.post(self.__base_uri + '/vpn/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)
        return res.json()

    def activate_addon_vnc(self, instance_id):
        """Activate the VNC add-on, if available.

        The VNC add-on must be activated before it can be started.  If
        the VNC connection should be reset, try first to stop and
        start it again, without deactivating the add-on.
        """
        res = requests.post(self.__base_uri + '/addon/vnc/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_vnc(self, instance_id):
        """Get status of the VNC add-on for this instance.
        """
        res = requests.get(self.__base_uri + '/addon/vnc/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        if res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def start_addon_vnc(self, instance_id):
        """Start user-visible connection of VNC add-on.

        Read more in the documentation of the method activate_addon_vnc().
        """
        res = requests.post(self.__base_uri + '/addon/vnc/' + instance_id + '/start', headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def stop_addon_vnc(self, instance_id):
        """Stop user-visible connection of VNC add-on.

        Read more in the documentation of the method activate_addon_vnc().
        """
        res = requests.post(self.__base_uri + '/addon/vnc/' + instance_id + '/stop', headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def deactivate_addon_vnc(self, instance_id):
        """Deactivate VNC add-on for this instance.

        Note that calling this is not required if the workspace
        instance will be terminated.
        """
        res = requests.delete(self.__base_uri + '/addon/vnc/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def activate_addon_mistyproxy(self, instance_id):
        """Activate mistyproxy add-on.

        Note that this add-on is unique to workspaces that involve
        Misty robots, e.g.,
        https://help.rerobots.net/workspaces/fixed_misty2fieldtrial.html

        When it is ready, proxy URLs can be obtained via
        status_addon_mistyproxy().
        """
        res = requests.post(self.__base_uri + '/addon/mistyproxy/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_mistyproxy(self, instance_id):
        """Get status of mistyproxy add-on for this instance.

        The response includes proxy URLs if any are defined.
        """
        res = requests.get(self.__base_uri + '/addon/mistyproxy/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        if res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def deactivate_addon_mistyproxy(self, instance_id):
        """Deactivate mistyproxy add-on.

        Note that a cycle of deactivate-activate of the mistyproxy
        add-on will create new proxy URLs.

        Note that calling this is not required if the workspace
        instance will be terminated.
        """
        res = requests.delete(self.__base_uri + '/addon/mistyproxy/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def activate_addon_cam(self, instance_id):
        """Activate cam (camera) add-on.
        """
        res = requests.post(self.__base_uri + '/addon/cam/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_cam(self, instance_id):
        """Get status of cam (camera) add-on for this instance.
        """
        res = requests.get(self.__base_uri + '/addon/cam/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        if res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def deactivate_addon_cam(self, instance_id):
        """Deactivate cam (camera) add-on.

        Note that calling this is not required if the workspace
        instance will be terminated.
        """
        res = requests.delete(self.__base_uri + '/addon/cam/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def get_snapshot_cam(self, instance_id, camera_id=0, coding=None, dformat=None):
        """Get image from camera via cam add-on.

        If coding=None (default), then returned data are not
        encoded. The only coding supported is base64, which can be
        obtained with coding='base64'.

        If dformat=None (default), then the image format is whatever
        the rerobots API provided. Currently, this can be 'jpeg' or
        'ndarray' (i.e., ndarray type of NumPy).

        Note that some coding and format combinations are not
        compatible. In particular, if dformat='ndarray', then coding
        must be None.
        """
        # pylint: disable=import-outside-toplevel
        if dformat is not None:
            dformat = dformat.lower()
            assert dformat in ['ndarray', 'jpeg']
        res = requests.get(self.__base_uri + '/addon/cam/{}/{}/img'.format(instance_id, camera_id), headers=self.__headers, verify=self.__verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        payload = res.json()
        if not payload['success']:
            return payload
        if 'coding' in payload and payload['coding'] != coding:
            if (coding is None) and payload['coding'] == 'base64':
                payload['data'] = base64.b64decode(payload['data'])
                payload['coding'] = None
        if (dformat is not None) and (payload['format'].lower() != dformat):
            if dformat == 'ndarray':
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

    def activate_addon_drive(self, instance_id):
        """Activate drive add-on.
        """
        res = requests.post(self.__base_uri + '/addon/drive/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def status_addon_drive(self, instance_id):
        """Get status of drive add-on for this instance.
        """
        res = requests.get(self.__base_uri + '/addon/drive/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok and res.status_code != 404:
            raise Error(res.text)
        if res.status_code == 404:
            payload = {'status': 'notfound'}
        else:
            payload = res.json()
        return payload

    def send_drive_command(self, instance_id, command):
        """Send motion command via drive add-on.
        """
        if command is None:
            command = {'linearv': 0, 'angularv': 0}
        res = requests.post(self.__base_uri + '/addon/drive/' + instance_id + '/tx',
                            json=command,
                            headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def deactivate_addon_drive(self, instance_id):
        """Deactivate drive add-on.

        Note that calling this is not required if the workspace
        instance will be terminated.
        """
        res = requests.delete(self.__base_uri + '/addon/drive/' + instance_id, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def revoke_token(self, token=None, sha256=None):
        """Revoke an API token.

        This action cannot be undone.
        """
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
        res = requests.post(self.__base_uri + '/revoke/' + sha256, headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)

    def purge(self):
        """Purge all valid API tokens.

        After this call succeeds, no existing API tokens associated
        with the requesting user are valid.

        This action cannot be undone.
        """
        res = requests.post(self.__base_uri + '/purge', headers=self.__headers, verify=self.__verify_certs)
        if not res.ok:
            raise Error(res.text)


class Instance(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """Manager for a workspace instance
    """
    def __init__(self, workspace_types=None, wdeployment_id=None, instance_id=None, api_token=None, headers=None, apic=None):
        """client for a workspace instance

        At least one of workspace_types or wdeployment_id must be
        given. If both are provided (not None), consistency is
        checked: the type of the workspace deployment of the given
        identifier is compared with the given type. If they differ, no
        instance is created, and ValueError is raised.

        If instance_id is given, then attempt to attach this class
        to an existing instance. In this case, neither workspace_types
        or wdeployment_id is required. If they are provided, then
        consistency is checked.

        The optional parameter `apic` is an instance of APIClient. If
        it is not given, then an APIClient object is instantiated
        internally from the parameters `api_token` etc., corresponding
        to parameters APIClient of the same name.
        """
        # pylint: disable=too-many-branches,too-many-arguments
        if workspace_types is None and wdeployment_id is None and instance_id is None:
            raise ValueError('at least workspace_types, wdeployment_id, or instance_id must be given')

        if apic is None:
            self.apic = APIClient(api_token=api_token, headers=headers)
        else:
            self.apic = apic

        if wdeployment_id is not None and workspace_types is not None:
            x = self.apic.get_wdeployment_info(wdeployment_id)
            if x['type'] not in workspace_types:
                raise ValueError('workspace deployment {} does not have type in {}'.format(wdeployment_id, workspace_types))

        if workspace_types is not None:
            candidates = self.apic.get_wdeployments(types=workspace_types)
            if not candidates:
                raise ValueError('no deployments found with any type in {}'.format(workspace_types))
            self._wdeployment_id = candidates[0]['id']

        else:
            self._wdeployment_id = wdeployment_id

        self._type = None

        if instance_id is None:
            payload = self.apic.request_instance(self._wdeployment_id, reserve=False)
            self._id = payload['id']
            self._status = 'INIT'  # Instance always begins at INIT
            if 'sshkey' in payload:
                self.__sshkey = payload['sshkey']
            else:
                self.__sshkey = None

        else:
            self._id = instance_id
            payload = self.apic.get_instance_info(self._id)
            if self._wdeployment_id is not None:
                assert payload['deployment'] == self._wdeployment_id
            else:
                self._wdeployment_id = payload['deployment']
            self._status = payload['status']
            self.__sshkey = None

        self._details = None

        self._conn = None
        self.__sshclient = None
        self.__sftpclient = None


    def get_wdeployment_info(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.get_wdeployment_info(self._wdeployment_id)


    def get_access_rules(self, to_user=None):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.get_access_rules(to_user=to_user, wdeployment_id=self._wdeployment_id)

    def add_access_rule(self, capability, to_user=None):
        """This is a wrapper for APIClient method of same name."""
        self.apic.add_access_rule(wdeployment_id=self._wdeployment_id, capability=capability, to_user=to_user)

    def del_access_rule(self, capability, to_user=None):
        """This is a wrapper for APIClient method of same name."""
        self.apic.del_access_rule(wdeployment_id=self._wdeployment_id, capability=capability, to_user=to_user)


    def get_firewall_rules(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.get_firewall_rules(self._id)

    def add_firewall_rule(self, action, source_address=None):
        """This is a wrapper for APIClient method of same name."""
        self.apic.add_firewall_rule(self._id, action=action, source_address=source_address)

    def flush_firewall_rules(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.flush_firewall_rules(self._id)


    def get_vpn_newclient(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.get_vpn_newclient(self._id)


    def activate_addon_cam(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.activate_addon_cam(self._id)

    def status_addon_cam(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.status_addon_cam(self._id)

    def get_snapshot_cam(self, camera_id=0, coding=None, dformat=None):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.get_snapshot_cam(self._id, camera_id=camera_id, coding=coding, dformat=dformat)

    def deactivate_addon_cam(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.deactivate_addon_cam(self._id)


    def activate_addon_drive(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.activate_addon_drive(self._id)

    def status_addon_drive(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.status_addon_drive(self._id)

    def send_drive_command(self, command):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.send_drive_command(instance_id=self._id, command=command)

    def deactivate_addon_drive(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.deactivate_addon_drive(self._id)


    def activate_addon_mistyproxy(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.activate_addon_mistyproxy(self._id)

    def status_addon_mistyproxy(self):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.status_addon_mistyproxy(self._id)

    def deactivate_addon_mistyproxy(self):
        """This is a wrapper for APIClient method of same name."""
        self.apic.deactivate_addon_mistyproxy(self._id)


    def get_status(self):
        """Get status of this workspace instance.

        For example, the status is `READY` when the instance is ready
        to be used, and `INIT` when it is initializing.
        """
        payload = self.apic.get_instance_info(self._id)
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
        """Get status and details about this workspace instance.
        """
        status = self.get_status()
        res = self._details.copy()
        res['status'] = status
        if self._conn is not None:
            res['conn'] = self._conn
        return res


    def terminate(self):
        """Terminate this instance.
        """
        self.stop_sshclient()
        self.apic.terminate_instance(self._id)


    def stop_sshclient(self):
        """Stop, close SSH client connection to instance, if it exists.
        """
        if self.__sshclient is not None:
            self.__sshclient.close()
            self.__sshclient = None
            self.__sftpclient = None


    def start_sshclient(self):
        """Create SSH client to instance.

        This method is a prerequisite to exec_ssh(), which executes
        remote terminal commands.
        """
        # pylint: disable=import-outside-toplevel
        import paramiko
        status = self.get_status()
        if status != 'READY':
            raise Exception('instance not ready')
        if 'ipv4' not in self._conn or 'port' not in self._conn or 'hostkeys' not in self._conn:
            self.get_details()
        host = self._conn['ipv4']
        port = self._conn['port']
        hostkey = self._conn['hostkeys'][0]

        fd, keypath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wt')
        fp.write(self.__sshkey)
        fp.close()

        fd, known_hosts = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wt')
        sshhost = '[{IPADDR}]:{PORT}'.format(IPADDR=host, PORT=port)
        fp.write(sshhost + ' ' + hostkey)
        fp.close()

        self.__sshclient = paramiko.client.SSHClient()
        self.__sshclient.load_system_host_keys(known_hosts)
        pkey = paramiko.rsakey.RSAKey.from_private_key_file(keypath)
        self.__sshclient.connect(host, port=port, username='root', pkey=pkey, timeout=5)

        os.unlink(keypath)
        os.unlink(known_hosts)


    def exec_ssh(self, command, timeout=None, get_files=False):
        """Execute command via SSH.

        https://docs.paramiko.org/en/2.4/api/client.html#paramiko.client.SSHClient.exec_command

        If get_files=True, then return files of stdin, stdout, and
        stderr.
        """
        assert self.__sshclient is not None
        stdin, stdout, stderr = self.__sshclient.exec_command(command, timeout=timeout)
        if get_files:
            return stdin, stdout, stderr
        return stdout.read()


    def put_file(self, localpath, remotepath):
        """Put local file onto remote host.

        For the general case, the underlying Paramiko SFTP object is
        available from sftp_client().
        """
        assert self.__sshclient is not None
        if self.__sftpclient is None:
            self.__sftpclient = self.__sshclient.open_sftp()
        return self.__sftpclient.put(localpath, remotepath)


    def get_file(self, remotepath, localpath):
        """Get file from remote host.

        For the general case, the underlying Paramiko SFTP object is
        available from sftp_client().
        """
        assert self.__sshclient is not None
        if self.__sftpclient is None:
            self.__sftpclient = self.__sshclient.open_sftp()
        return self.__sftpclient.get(remotepath, localpath)


    def sftp_client(self):
        """Get Paramiko SFTP client.

        Note that methods put_file() and get_file() are small wrappers
        to put() and get() of this Paramiko class.

        Read about it at https://docs.paramiko.org/en/2.4/api/sftp.html
        """
        assert self.__sshclient is not None
        if self.__sftpclient is None:
            self.__sftpclient = self.__sshclient.open_sftp()
        return self.__sftpclient

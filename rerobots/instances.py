"""
SCL <scott@rerobots.net>
Copyright (c) 2017-2019 rerobots, Inc.
"""
import os
import tempfile

from .api import APIClient

# inline: paramiko
# only required by Instance class


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

    def create_access_rule(self, capability, to_user=None):
        """This is a wrapper for APIClient method of same name."""
        return self.apic.create_access_rule(wdeployment_id=self._wdeployment_id, capability=capability, to_user=to_user)

    def del_access_rule(self, rule_id):
        """This is a wrapper for APIClient method of same name."""
        self.apic.del_access_rule(wdeployment_id=self._wdeployment_id, rule_id=rule_id)


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

#!/bin/env python
"""Command-line interface (CLI) to this API client library

The main design goal of this CLI is to be sufficiently expressive that
a user can install the Python client library and perform all of her
work using only the `rerobots` terminal program, i.e., without writing
any Python code.

Of course, parts of this package besides the CLI are intended to be
used by your Python code.


SCL <scott@rerobots.net>
Copyright (c) 2017-2019 rerobots, Inc.
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import json
import os.path
import random
import sys
import time
try:
    from time import monotonic as monotonic_unless_py2
except ImportError:
    from time import time as monotonic_unless_py2

from . import api as rerobots_api
from .__init__ import __version__

try:  # compatibility with Python 2.7
    input = raw_input  # pylint: disable=redefined-builtin,invalid-name
except NameError:
    pass


def handle_cli_id(apiclient, given_instance_id=None):
    """Infer instance ID given command-line interface arguments

    Note that if given_instance_id is not None, then this function
    returns it and takes no other action. Eventually this function
    might be changed to validate the given ID, e.g., check that it
    exists and that given API token is sufficient to use it.
    """
    if given_instance_id is not None:
        return given_instance_id
    active_instances = apiclient.get_instances()
    if len(active_instances) == 1:
        return active_instances[0]
    if len(active_instances) > 1:
        print('ambiguous command because more than one active instance')
    else: # len(active_instances) == 0:
        print('no active instances')
    return None


# TODO: refactor main() into smaller routines
# pylint: disable=too-many-branches,too-many-statements,too-many-return-statements,too-many-locals
def main(argv=None):
    """Process command-line arguments.
    """
    if argv is None:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(description='rerobots API command-line client', add_help=False)
    argparser.add_argument('-h', '--help', dest='print_help',
                           action='store_true', default=False,
                           help='print this help message and exit')
    argparser.add_argument('-V', '--version', dest='print_version',
                           action='store_true', default=False,
                           help='print version number and exit.')
    argparser.add_argument('-t', '--jwt', dest='jwt', metavar='FILE',
                           default=None,
                           help=('plaintext file containing API token; with this flag, '
                                 'the REROBOTS_API_TOKEN environment variable is ignored.'))

    subparsers = argparser.add_subparsers(dest='command')

    info_parser = subparsers.add_parser('info', help='print summary about instance.', add_help=False)
    info_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    info_parser.add_argument('-h', '--help', dest='print_info_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    isready_parser = subparsers.add_parser('isready', help='indicate whether instance is ready with exit code.', add_help=False)
    isready_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    isready_parser.add_argument('-h', '--help', dest='print_isready_help',
                                action='store_true', default=False,
                                help='print this help message and exit')

    addon_cam_parser = subparsers.add_parser('addon-cam', help='get image via add-on `cam`', add_help=False)
    addon_cam_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    addon_cam_parser.add_argument('-f', dest='output_file',
                                  help='write image to file, instead of stdout (default)')
    addon_cam_parser.add_argument('-c', dest='camera_id', metavar='CAMERA',
                                  default=0,
                                  help='camera ID; (default 0)')
    addon_cam_parser.add_argument('-h', '--help', dest='print_addon_cam_help',
                                  action='store_true', default=False,
                                  help='print this help message and exit')

    addon_mistyproxy_parser = subparsers.add_parser('addon-mistyproxy', help='get proxy URL via add-on `mistyproxy`', add_help=False)
    addon_mistyproxy_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    addon_mistyproxy_parser.add_argument('--http', dest='print_addon_mistyproxy_http',
                                         action='store_true', default=False,
                                         help='print the HTTP (non-encrypted) proxy URL instead')
    addon_mistyproxy_parser.add_argument('--restart', dest='restart_addon_mistyproxy',
                                         action='store_true', default=False,
                                         help='restart the mistyproxy add-on and generate new URLs')
    addon_mistyproxy_parser.add_argument('-h', '--help', dest='print_addon_mistyproxy_help',
                                         action='store_true', default=False,
                                         help='print this help message and exit')

    list_parser = subparsers.add_parser('list', help='list all instances owned by this user.', add_help=False)
    list_parser.add_argument('-h', '--help', dest='print_list_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    search_parser = subparsers.add_parser('search', help=(
        'search for matching deployments. '
        'empty query implies show all existing workspace deployments.'
    ), add_help=False)
    search_parser.add_argument('-h', '--help', dest='print_search_help',
                               action='store_true', default=False,
                               help='print this help message and exit')
    search_parser.add_argument('QUERY', nargs='?', default=None)

    wdinfo_parser = subparsers.add_parser('wdinfo', help='print summary about workspace deployment.', add_help=False)
    wdinfo_parser.add_argument('ID', default=None, help='workspace deployment ID')
    wdinfo_parser.add_argument('-h', '--help', dest='print_wdinfo_help',
                               action='store_true', default=False,
                               help='print this help message and exit')

    launch_parser = subparsers.add_parser('launch', help=(
        'launch instance from specified workspace deployment or type. '
        'if none is specified, then randomly select from those available.'
    ), add_help=False)
    launch_parser.add_argument('-h', '--help', dest='print_launch_help',
                               action='store_true', default=False,
                               help='print this help message and exit')
    launch_parser.add_argument('ID', nargs='?', default=None, help='deployment ID')
    launch_default_secretkeypath = 'key.pem'
    launch_parser.add_argument('--secret-key', metavar='FILE', dest='secretkeypath',
                               default=None,
                               help=('name of file in which to write new secret key '
                                     '(default {})'.format(launch_default_secretkeypath)))
    launch_parser.add_argument('-y', dest='assume_yes',
                               action='store_true', default=False,
                               help=('assume "yes" for any questions required to launch instance; '
                                     'otherwise, interactive prompts will appear '
                                     'to confirm actions as needed'))

    terminate_parser = subparsers.add_parser('terminate', help='terminate instance.', add_help=False)
    terminate_parser.add_argument('-h', '--help', dest='print_terminate_help',
                                  action='store_true', default=False,
                                  help='print this help message and exit')
    terminate_parser.add_argument('ID', nargs='?', default=None, help='instance ID')

    subparsers.add_parser('version', help='print version number and exit.')
    help_parser = subparsers.add_parser('help', help='print this help message and exit')
    help_parser.add_argument('help_target_command', metavar='COMMAND', type=str, nargs='?')

    # Workaround for Python 2.7 argparse, which does not accept empty COMMAND:
    # If `--help` or `-h` present and every argument before it begins with `-`,
    # then convert it to `help`.
    # If `-V` or `--version` present and every argument before it begins with `-`,
    # then convert it to `version.
    if sys.version_info.major < 3:
        try:
            ind = argv.index('--help')
        except ValueError:
            try:
                ind = argv.index('-h')
            except ValueError:
                ind = None
        if ind is not None:
            for k in range(ind):
                if argv[k][0] != '-':
                    ind = None
                    break
            if ind is not None:
                argv[ind] = 'help'
        try:
            ind = argv.index('--version')
        except ValueError:
            try:
                ind = argv.index('-V')
            except ValueError:
                ind = None
        if ind is not None:
            for k in range(ind):
                if argv[k][0] != '-':
                    ind = None
                    break
            if ind is not None:
                argv[ind] = 'version'

    args = argparser.parse_args(argv)
    if args.print_version or args.command == 'version':
        print(__version__)
        return 0

    if args.print_help or args.command is None or args.command == 'help':
        if hasattr(args, 'help_target_command') and args.help_target_command is not None:
            if args.help_target_command == 'info':
                info_parser.print_help()
            elif args.help_target_command == 'isready':
                isready_parser.print_help()
            elif args.help_target_command == 'addon-cam':
                addon_cam_parser.print_help()
            elif args.help_target_command == 'addon-mistyproxy':
                addon_mistyproxy_parser.print_help()
            elif args.help_target_command == 'wdinfo':
                wdinfo_parser.print_help()
            elif args.help_target_command == 'list':
                list_parser.print_help()
            elif args.help_target_command == 'search':
                search_parser.print_help()
            elif args.help_target_command == 'launch':
                launch_parser.print_help()
            elif args.help_target_command == 'terminate':
                terminate_parser.print_help()
            else:
                print('Error: unrecognized command {}'.format(args.help_target_command))
                return 1
        else:
            argparser.print_help()
        return 0

    if args.jwt is not None:
        with open(args.jwt) as fp:
            jwt = fp.read().strip()
        apic = rerobots_api.APIClient(api_token=jwt)
    else:
        apic = rerobots_api.APIClient()

    if args.command == 'search':
        if args.print_search_help:
            search_parser.print_help()
            return 0
        for wdinfo in apic.get_wdeployments(query=args.QUERY):
            print('{}\t{}'.format(wdinfo['id'], wdinfo['type']))

    elif args.command == 'wdinfo':
        if args.print_wdinfo_help:
            wdinfo_parser.print_help()
            return 0
        print(json.dumps(apic.get_wdeployment_info(args.ID), indent=2))

    elif args.command == 'list':
        if args.print_list_help:
            list_parser.print_help()
            return 0
        instances = apic.get_instances()
        if instances:
            print('\n'.join(apic.get_instances()))

    elif args.command == 'info':
        if args.print_info_help:
            info_parser.print_help()
            return 0
        instance_id = handle_cli_id(apic, args.ID)
        if instance_id is None:
            return 1
        print(json.dumps(apic.get_instance_info(instance_id), indent=2))

    elif args.command == 'isready':
        if args.print_isready_help:
            isready_parser.print_help()
            return 0
        instance_id = handle_cli_id(apic, args.ID)
        if instance_id is None:
            return 1
        payload = apic.get_instance_info(instance_id)
        if payload['status'] == 'READY':
            return 0
        return 1

    elif args.command == 'addon-cam':
        if args.print_addon_cam_help:
            addon_cam_parser.print_help()
            return 0
        instance_id = handle_cli_id(apic, args.ID)
        if instance_id is None:
            return 1
        start_time = monotonic_unless_py2()
        while monotonic_unless_py2() - start_time < 120:
            payload = apic.get_instance_info(instance_id)
            if payload['status'] == 'TERMINATED':
                print('cannot start `cam` because instance is terminated')
                return 1
            payload = apic.status_addon_cam(instance_id)
            if payload['status'] == 'active':
                snapshot_payload = apic.get_snapshot_cam(instance_id, camera_id=args.camera_id, dformat='jpeg')
                if snapshot_payload['success']:
                    break
            elif payload['status'] == 'notfound':
                apic.activate_addon_cam(instance_id)
            time.sleep(2)
        if payload['status'] != 'active' or not snapshot_payload['success']:
            raise Exception('timed out waiting for `cam` add-on to become active')
        if args.output_file:
            with open(args.output_file, 'wb') as fp:
                fp.write(snapshot_payload['data'])
        else:
            sys.stdout.write(snapshot_payload['data'])

    elif args.command == 'addon-mistyproxy':
        if args.print_addon_mistyproxy_help:
            addon_mistyproxy_parser.print_help()
            return 0
        instance_id = handle_cli_id(apic, args.ID)
        if instance_id is None:
            return 1
        payload = apic.get_instance_info(instance_id)
        if payload['status'] == 'TERMINATED':
            print('cannot start `mistyproxy` because instance is terminated')
            return 1
        if args.restart_addon_mistyproxy:
            start_time = monotonic_unless_py2()
            while monotonic_unless_py2() - start_time < 20:
                payload = apic.status_addon_mistyproxy(instance_id)
                if payload['status'] == 'active':
                    apic.deactivate_addon_mistyproxy(instance_id)
                elif payload['status'] == 'notfound':
                    break
                time.sleep(2)
            if payload['status'] != 'notfound':
                raise Exception('timed out waiting for `mistyproxy` add-on to stop')
        start_time = monotonic_unless_py2()
        while monotonic_unless_py2() - start_time < 20:
            payload = apic.status_addon_mistyproxy(instance_id)
            if payload['status'] == 'active':
                break
            elif payload['status'] == 'notfound':
                apic.activate_addon_mistyproxy(instance_id)
            time.sleep(2)
        if payload['status'] != 'active':
            raise Exception('timed out waiting for `mistyproxy` add-on to become active')
        if args.print_addon_mistyproxy_http:
            print(payload['url'][0])
        else:
            print(payload['url'][1])

    elif args.command == 'terminate':
        if args.print_terminate_help:
            terminate_parser.print_help()
            return 0
        instance_id = handle_cli_id(apic, args.ID)
        if instance_id is None:
            return 1
        apic.terminate_instance(instance_id)

    elif args.command == 'launch':
        if args.print_launch_help:
            launch_parser.print_help()
            return 0
        if args.secretkeypath is None:
            secretkeypath = launch_default_secretkeypath
        else:
            secretkeypath = args.secretkeypath
        if os.path.exists(secretkeypath) and not args.assume_yes:
            print('file already exists at {}'.format(secretkeypath))
            ui_input = None
            while ui_input not in ('y', 'yes'):
                print('overwrite it with new secret key? [y/N] ', end='')
                ui_input = input().lower()
                if ui_input in ('n', 'no', ''):
                    print('please provide a different value via --secret-key')
                    return 1
        secretkey_fd = os.open(secretkeypath, flags=os.O_CREAT|os.O_WRONLY|os.O_TRUNC, mode=0o600)
        if args.ID is None:
            available_wdeployments = apic.get_wdeployments()
            if len(available_wdeployments) == 1:
                wdeployment_id = available_wdeployments[0]
            elif len(available_wdeployments) > 1:
                wdeployment_id = available_wdeployments[random.randint(0, len(available_wdeployments)-1)]
            else: # len(available_wdeployments) == 0:
                print('no deployments are available')
                return 1
        else:
            wdeployment_id = args.ID

        payload = apic.request_instance(wdeployment_id)
        print('{}'.format(payload['id']))
        if 'sshkey' in payload:
            # TODO: echo only if verbose: writing secret key for ssh access to file key.pem...
            fp = os.fdopen(secretkey_fd, 'w')
            fp.write(payload['sshkey'])
            fp.close()

    else:
        print('Unrecognized command. Try `help`.')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/bin/env python
"""Command-line interface (CLI) to this API client library

The main design goal of this CLI is to be sufficiently expressive that
a user can install the Python client library and perform all of her
work using only the `rerobots` terminal program, i.e., without writing
any Python code.

Of course, parts of this package besides the CLI are intended to be
used by your Python code.


SCL <scott@rerobots.net>
Copyright (c) 2017, 2018 rerobots, Inc.
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import json
import random
import sys

from . import api as rerobots_api
from .__init__ import __version__


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
        print('\n'.join(apic.get_wdeployments(query=args.QUERY)))

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
        if args.ID is None:
            active_instances = apic.get_instances()
            if len(active_instances) == 1:
                instance_id = active_instances[0]
            elif len(active_instances) > 1:
                print('ambiguous command because more than one active instance')
                print('specify which instance to terminate')
                return 1
            else: # len(active_instances) == 0:
                print('no active instances')
                return 1
        else:
            instance_id = args.ID
        print(json.dumps(apic.get_instance_info(instance_id), indent=2))

    elif args.command == 'terminate':
        if args.print_terminate_help:
            terminate_parser.print_help()
            return 0
        if args.ID is None:
            active_instances = apic.get_instances()
            if len(active_instances) == 1:
                instance_id = active_instances[0]
            elif len(active_instances) > 1:
                print('ambiguous command because more than one active instance')
                print('specify which instance to terminate')
                return 1
            else: # len(active_instances) == 0:
                print('no active instances')
                return 1
        else:
            instance_id = args.ID
        apic.terminate_instance(instance_id)

    elif args.command == 'launch':
        if args.print_launch_help:
            launch_parser.print_help()
            return 0
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
        print('instance {}'.format(payload['id']))
        if 'sshkey' in payload:
            print('writing secret key for ssh access to file key.pem...')
            with open('key.pem', 'w') as fp:
                fp.write(payload['sshkey'])

    else:
        print('Unrecognized command. Try `help`.')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

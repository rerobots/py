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


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(description='rerobots API command-line client')
    argparser.add_argument('-t','--jwt', dest='jwt', metavar='FILE',
                           default=None,
                           help='plaintext file containing API token')
    subparsers = argparser.add_subparsers(dest='command')

    info_parser = subparsers.add_parser('info', help='print summary about instance.')
    info_parser.add_argument('ID', nargs='?', default=None, help='instance ID')

    subparsers.add_parser('list', help='list all instances owned by this user.')

    search_parser = subparsers.add_parser('search', help=(
        'search for matching deployments. '
        'empty query implies show all existing workspace deployments.'
    ))
    search_parser.add_argument('QUERY', nargs='?', default=None)

    launch_parser = subparsers.add_parser('launch', help=(
        'launch instance from specified workspace deployment or type. '
        'if none is specified, then randomly select from those available.'
    ))
    launch_parser.add_argument('ID', nargs='?', default=None, help='deployment ID')

    terminate_parser = subparsers.add_parser('terminate', help='terminate instance.')
    terminate_parser.add_argument('ID', nargs='?', default=None, help='instance ID')

    subparsers.add_parser('version', help='print version number and exit.')
    subparsers.add_parser('help', help='print this help message and exit')

    args = argparser.parse_args(argv)
    if args.command == 'version':
        print(__version__)
        return 0

    if args.command is None or args.command == 'help':
        argparser.print_help()
        return 0

    if args.jwt is not None:
        with open(args.jwt) as fp:
            jwt = fp.read().strip()
        apic = rerobots_api.APIClient(api_token=jwt)
    else:
        apic = rerobots_api.APIClient()

    if args.command == 'search':
        if args.QUERY is not None:
            print('nonempty queries not supported yet. Try `help`.')
            return 1
        else:
            print('\n'.join(apic.get_deployments()))

    elif args.command == 'list':
        print('\n'.join(apic.get_instances()))

    elif args.command == 'info':
        if args.ID is None:
            active_instances = apic.get_instances()
            if len(active_instances) == 0:
                print('no active instances')
                return 1
            elif len(active_instances) > 1:
                print('ambiguous command because more than one active instance')
                print('specify which instance to terminate')
                return 1
            else: # len(active_instances) == 1:
                instance_id = active_instances[0]
        else:
            instance_id = args.ID
        print(json.dumps(apic.get_instance_info(instance_id), indent=2))

    elif args.command == 'terminate':
        if args.ID is None:
            active_instances = apic.get_instances()
            if len(active_instances) == 0:
                print('no active instances')
                return 1
            elif len(active_instances) > 1:
                print('ambiguous command because more than one active instance')
                print('specify which instance to terminate')
                return 1
            else: # len(active_instances) == 1:
                instance_id = active_instances[0]
        else:
            instance_id = args.ID
        apic.terminate_instance(instance_id)

    elif args.command == 'launch':
        if args.ID is None:
            available_deployments = apic.get_deployments()
            if len(available_deployments) == 0:
                print('no deployments are available')
                return 1
            elif len(available_deployments) > 1:
                deployment_id = available_deployments[random.randint(0, len(available_deployments)-1)]
            else: # len(available_deployments) == 1:
                deployment_id = available_deployments[0]
        else:
            deployment_id = args.ID

        instance_id, key = apic.request_instance(deployment_id)
        print('instance {}'.format(instance_id))
        with open('key.pem', 'w') as fp:
            fp.write(key)

    else:
        print('Unrecognized command. Try `help`.')
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

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

import requests

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


def add_cli_info(subparsers):
    """Create subparser for `info`.
    """
    desc = 'print summary about instance.'
    info_parser = subparsers.add_parser('info', description=desc, help=desc, add_help=False)
    info_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    info_parser.add_argument('-h', '--help', dest='print_info_help',
                             action='store_true', default=False,
                             help='print this help message and exit')


def add_cli_isready(subparsers):
    """Create subparser for `isready`.
    """
    desc = 'indicate whether instance is ready with exit code.'
    isready_parser = subparsers.add_parser('isready', description=desc, help=desc, add_help=False)
    isready_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    isready_parser.add_argument('--blocking', dest='isready_blocking',
                                action='store_true', default=False,
                                help='do not return until instance is non-INIT')
    isready_parser.add_argument('-h', '--help', dest='print_isready_help',
                                action='store_true', default=False,
                                help='print this help message and exit')


def add_cli_addon_cam(subparsers):
    """Create subparser for `addon-cam`.
    """
    desc = 'get image via add-on `cam`'
    addon_cam_parser = subparsers.add_parser('addon-cam', description=desc, help=desc, add_help=False)
    addon_cam_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    addon_cam_parser.add_argument('-f', dest='output_file',
                                  help='write image to file, instead of stdout (default)')
    addon_cam_parser.add_argument('-c', dest='camera_id', metavar='CAMERA',
                                  default=0,
                                  help='camera ID; (default 0)')
    addon_cam_parser.add_argument('-h', '--help', dest='print_addon_cam_help',
                                  action='store_true', default=False,
                                  help='print this help message and exit')


def add_cli_addon_mistyproxy(subparsers):
    """Create subparser for `addon-mistyproxy`.
    """
    desc = 'get proxy URL via add-on `mistyproxy`'
    addon_mistyproxy_parser = subparsers.add_parser('addon-mistyproxy', description=desc, help=desc, add_help=False)
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


def add_cli_addon_drive(subparsers):
    """Create subparser for `addon-drive`.
    """
    desc = 'send motion commands via add-on `drive`'
    addon_drive_parser = subparsers.add_parser('addon-drive', description=desc, help=desc, add_help=False)
    addon_drive_parser.add_argument('ID', nargs='?', default=None, help='instance ID')
    addon_drive_parser.add_argument('-r', dest='motion_command', metavar='STRING',
                                    default=None,
                                    help='raw command (JSON)')
    addon_drive_parser.add_argument('-h', '--help', dest='print_addon_drive_help',
                                    action='store_true', default=False,
                                    help='print this help message and exit')


def add_cli_list(subparsers):
    """Create subparser for `list`.
    """
    desc = 'list all instances owned by this user.'
    list_parser = subparsers.add_parser('list', description=desc, help=desc, add_help=False)
    list_parser.add_argument('-h', '--help', dest='print_list_help',
                             action='store_true', default=False,
                             help='print this help message and exit')


def add_cli_search(subparsers):
    """Create subparser for `search`.
    """
    desc = (
        'search for matching deployments. '
        'empty query implies show all existing workspace deployments.'
    )
    search_parser = subparsers.add_parser('search', description=desc, help=desc, add_help=False)
    search_parser.add_argument('-h', '--help', dest='print_search_help',
                               action='store_true', default=False,
                               help='print this help message and exit')
    search_parser.add_argument('--include-user-provided', dest='include_user_provided',
                               action='store_true', default=False,
                               help='include user_provided workspace deployments in search')
    search_parser.add_argument('QUERY', nargs='?', default=None)


def add_cli_wdinfo(subparsers):
    """Create subparser for `wdinfo`.
    """
    desc = 'print summary about workspace deployment.'
    wdinfo_parser = subparsers.add_parser('wdinfo', description=desc, help=desc, add_help=False)
    wdinfo_parser.add_argument('ID', default=None, help='workspace deployment ID')
    wdinfo_parser.add_argument('-h', '--help', dest='print_wdinfo_help',
                               action='store_true', default=False,
                               help='print this help message and exit')


def add_cli_launch(subparsers):
    """Create subparser for `launch`.
    """
    desc = (
        'launch instance from specified workspace deployment or type. '
        'if none is specified, then randomly select from those available.'
    )
    launch_parser = subparsers.add_parser('launch', description=desc, help=desc, add_help=False)
    launch_parser.add_argument('-h', '--help', dest='print_launch_help',
                               action='store_true', default=False,
                               help='print this help message and exit')
    launch_parser.add_argument('ID', nargs='?', default=None, help='workspace type or deployment ID')
    launch_parser.add_argument('--secret-key', metavar='FILE', dest='secretkeypath',
                               default=None,
                               help=('name of file in which to write new secret key '
                                     '(default key.pem)'))
    launch_parser.add_argument('-y', dest='assume_yes',
                               action='store_true', default=False,
                               help=('assume "yes" for any questions required to launch instance; '
                                     'otherwise, interactive prompts will appear '
                                     'to confirm actions as needed'))
    launch_parser.add_argument('-n', dest='assume_no',
                               action='store_true', default=False,
                               help=('assume "no" for any questions required to launch instance; '
                                     'in practice, this prevents launching if doing so requires '
                                     'destructive actions, e.g., overwriting a local file'))
    launch_parser.add_argument('--public-key', metavar='FILE', dest='publickeypath',
                               default=None,
                               help=('path of public key to use; '
                                     'if not given, then a new key pair will be generated; '
                                     'this switch cannot be used with --secret-key'))


def add_cli_terminate(subparsers):
    """Create subparser for `terminate`.
    """
    desc = 'terminate instance.'
    terminate_parser = subparsers.add_parser('terminate', description=desc, help=desc, add_help=False)
    terminate_parser.add_argument('-h', '--help', dest='print_terminate_help',
                                  action='store_true', default=False,
                                  help='print this help message and exit')
    terminate_parser.add_argument('ID', nargs='?', default=None, help='instance ID')


def add_cli_list_ci_projects(subparsers):
    """Create subparser for `list-ci-projects`.
    """
    desc = 'list all CI projects of this user.'
    ci_list_proj_parser = subparsers.add_parser('list-ci-projects', description=desc, help=desc, add_help=False)
    ci_list_proj_parser.add_argument('-h', '--help', dest='print_list_ci_projects_help',
                                     action='store_true', default=False,
                                     help='print this help message and exit')


def add_cli_create_ci_project(subparsers):
    """Create subparser for `create-ci-project`.
    """
    desc = 'create a CI project for this user.'
    ci_create_proj_parser = subparsers.add_parser('create-ci-project', description=desc, help=desc, add_help=False)
    ci_create_proj_parser.add_argument('--repo-url', metavar='URL', dest='repo_url',
                                       default=None,
                                       help='URL of the Git repo for CI/CD')
    ci_create_proj_parser.add_argument('-h', '--help', dest='print_create_ci_project_help',
                                       action='store_true', default=False,
                                       help='print this help message and exit')

def add_cli_submit_ci_job(subparsers):
    """Create subparser for `submit-ci-job`.
    """
    desc = 'submit a CI job.'
    ci_submit_job_parser = subparsers.add_parser('submit-ci-job', description=desc, help=desc, add_help=False)
    ci_submit_job_parser.add_argument('--repo-branch', metavar='BRANCH', dest='repo_branch',
                                      default=None,
                                      help='branch of the repo for CI/CD')
    ci_submit_job_parser.add_argument('--repo-ref', metavar='REF', dest='repo_ref',
                                      default=None,
                                      help='commit hash of the Git repo for CI/CD')
    ci_submit_job_parser.add_argument('ID', default=None, help='project ID')
    ci_submit_job_parser.add_argument('-h', '--help', dest='print_submit_ci_job_help',
                                      action='store_true', default=False,
                                      help='print this help message and exit')


def py2_replace_help(argv):
    """

    Workaround for Python 2.7 argparse, which does not accept empty COMMAND

    If `--help` or `-h` present and every argument before it begins with `-`,
    then convert it to `help`.
    """
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
    return argv


def py2_replace_version(argv):
    """

    Workaround for Python 2.7 argparse, which does not accept empty COMMAND

    If `-V` or `--version` present and every argument before it begins with `-`,
    then convert it to `version.
    """
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
    return argv


def create_parser(argv=None):
    """Create CLI arguments and sub-arguments parsers.
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
    add_cli_info(subparsers)
    add_cli_isready(subparsers)
    add_cli_addon_cam(subparsers)
    add_cli_addon_mistyproxy(subparsers)
    add_cli_addon_drive(subparsers)
    add_cli_list(subparsers)
    add_cli_search(subparsers)
    add_cli_wdinfo(subparsers)
    add_cli_launch(subparsers)
    add_cli_terminate(subparsers)
    add_cli_list_ci_projects(subparsers)
    add_cli_create_ci_project(subparsers)
    add_cli_submit_ci_job(subparsers)

    subparsers.add_parser('version', help='print version number and exit.')
    help_parser = subparsers.add_parser('help', help='print this help message and exit')
    help_parser.add_argument('help_target_command', metavar='COMMAND', type=str, nargs='?')

    if sys.version_info.major < 3:
        argv = py2_replace_help(argv)
        argv = py2_replace_version(argv)

    return argparser.parse_args(argv), argparser, subparsers


def open_file_confirm(args, path, confirm_msg, fail_msg):
    """Open file for writing; confirm if path already exists.
    """
    if os.path.exists(path) and not args.assume_yes:
        print('file already exists at {}'.format(path))
        if args.assume_no:
            print(fail_msg)
            return -1
        ui_input = None
        while ui_input not in ('y', 'yes'):
            print(confirm_msg, end='')
            ui_input = input().lower()
            if ui_input in ('n', 'no', ''):
                print(fail_msg)
                return -1
    return os.open(path, flags=os.O_CREAT|os.O_WRONLY|os.O_TRUNC, mode=0o600)


def get_random_available_wd(apic):
    """Select random workspace deployment from those that are available.
    """
    available_wdeployments = apic.get_wdeployments()
    if len(available_wdeployments) == 1:
        wdeployment_id = available_wdeployments[0]
    elif len(available_wdeployments) > 1:
        wdeployment_id = available_wdeployments[random.randint(0, len(available_wdeployments)-1)]
    else: # len(available_wdeployments) == 0:
        print('no deployments are available')
        return None
    return wdeployment_id


def cli_launch(apic, args):
    """Implement CLI command `launch`.
    """
    if args.assume_yes and args.assume_no:
        print('Error: both -y and -n given')
        return 1
    if args.secretkeypath and args.publickeypath:
        print('Error: both --public-key and --secret-key given')
        return 1
    if args.publickeypath:
        secretkeypath = None
        with open(args.publickeypath, 'rt') as fp:
            publickey = fp.read()
    elif args.secretkeypath:
        secretkeypath = args.secretkeypath
        publickey = None
    else:
        secretkeypath = 'key.pem'
        publickey = None
    if secretkeypath:
        secretkey_fd = open_file_confirm(args, secretkeypath,
                                         'overwrite it with new secret key? [y/N] ',
                                         'please provide a different value via --secret-key')
        if secretkey_fd < 0:
            return -secretkey_fd
    if args.ID is None:
        wdeployment_id = get_random_available_wd(apic)
        if wdeployment_id is None:
            return 1
    else:
        wdeployment_id = args.ID

    payload = apic.request_instance(wdeployment_id, sshkey=publickey)
    print('{}'.format(payload['id']))
    if secretkeypath and 'sshkey' in payload:
        # TODO: echo only if verbose: writing secret key for ssh access to file key.pem...
        fp = os.fdopen(secretkey_fd, 'w')
        fp.write(payload['sshkey'])
        fp.close()

    return 0


def cli_addon_drive(apic, args):
    """Implement CLI command `addon-drive`.
    """
    try:
        motion_command = json.loads(args.motion_command)
    except ValueError:
        print('not valid JSON')
        return 1
    instance_id = handle_cli_id(apic, args.ID)
    if instance_id is None:
        return 1
    start_time = monotonic_unless_py2()
    while monotonic_unless_py2() - start_time < 120:
        payload = apic.get_instance_info(instance_id)
        if payload['status'] == 'TERMINATED':
            print('cannot start `drive` because instance is terminated')
            return 1
        payload = apic.status_addon_drive(instance_id)
        if payload['status'] == 'active':
            apic.send_drive_command(instance_id=instance_id, command=motion_command)
            break
        if payload['status'] == 'notfound':
            apic.activate_addon_drive(instance_id)
        time.sleep(1)
    if payload['status'] != 'active':
        raise Exception('timed out waiting for `drive` add-on to become active')
    return 0


def cli_addon_mistyproxy(apic, args):
    """Implement CLI command `addon-mistyproxy`.
    """
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
        if payload['status'] == 'notfound':
            apic.activate_addon_mistyproxy(instance_id)
        time.sleep(2)
    if payload['status'] != 'active':
        raise Exception('timed out waiting for `mistyproxy` add-on to become active')
    url_ind = 0 if args.print_addon_mistyproxy_http else 1
    print(payload['url'][url_ind])
    return 0


def cli_addon_cam(apic, args):
    """Implement CLI command `addon-cam`.
    """
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
        fp = os.fdopen(1, 'wb')
        fp.write(snapshot_payload['data'])
    return 0


def cli_isready(apic, args):
    """Implement CLI command `isready`.
    """
    instance_id = handle_cli_id(apic, args.ID)
    if instance_id is None:
        return 1
    while True:
        payload = apic.get_instance_info(instance_id)
        if payload['status'] == 'READY':
            return 0
        if payload['status'] != 'INIT' or not args.isready_blocking:
            return 1
        time.sleep(1)
    return 1


def cli_search(apic, args):
    """Implement CLI command `search`.
    """
    if args.include_user_provided:
        query = apic.get_wdeployments(query=args.QUERY)
    else:
        query = apic.get_wdeployments(query=args.QUERY, types=['!user_provided'])
    for wdinfo in query:
        print('{}\t{}'.format(wdinfo['id'], wdinfo['type']))
    return 0


def cli_wdinfo(apic, args):
    """Implement CLI command `wdinfo`.
    """
    wdinfo = apic.get_wdeployment_info(args.ID)
    if apic.has_api_token():
        wdinfo['cap'] = apic.get_access_rules(args.ID)
    print(json.dumps(wdinfo, indent=2))
    return 0


def cli_list(apic, args):
    """Implement CLI command `list`.
    """
    # pylint: disable=unused-argument
    instances = apic.get_instances()
    if instances:
        print('\n'.join(apic.get_instances()))
    return 0


def cli_info(apic, args):
    """Implement CLI command `info`.
    """
    instance_id = handle_cli_id(apic, args.ID)
    if instance_id is None:
        return 1
    print(json.dumps(apic.get_instance_info(instance_id), indent=2))
    return 0


def cli_terminate(apic, args):
    """Implement CLI command `terminate`.
    """
    instance_id = handle_cli_id(apic, args.ID)
    if instance_id is None:
        return 1
    apic.terminate_instance(instance_id)
    return 0


def cli_list_ci_projects(apic, args):
    """Implement CLI command `list-ci-projects`.
    """
    # pylint: disable=unused-argument
    ci_projs = apic.get_ci_projects()
    if ci_projs:
        for pid, attr in ci_projs.items():
            print('{}:'.format(pid))
            print('  url: https://ci.rerobots.net/p/{}'.format(pid))
            print('  repo_url: {}'.format(attr['repo_url']))
    return 0


def cli_create_ci_project(apic, args):
    """Implement CLI command `create-ci-project`.
    """
    # pylint: disable=unused-argument
    if args.repo_url is None:
        print('error: missing required argument: --repo-url')
        return 1
    proj_id = apic.create_ci_project(args.repo_url)
    print(proj_id)
    return 0


def cli_submit_ci_job(apic, args):
    """Implement CLI command `submit-ci-project`.
    """
    # pylint: disable=unused-argument
    if args.repo_branch is None or args.repo_ref is None:
        print('error: missing required arguments: --repo-branch or --repo-ref')
        return 1
    job_id = apic.submit_ci_job(args.ID, branch=args.repo_branch, ref=args.repo_ref)
    print(job_id)
    return 0


def main(argv=None):
    """Process command-line arguments.
    """
    args, argparser, subparsers = create_parser(argv)

    if args.print_version or args.command == 'version':
        print(__version__)
        return 0

    if args.print_help or args.command is None or args.command == 'help':
        if hasattr(args, 'help_target_command') and args.help_target_command is not None:
            if args.help_target_command in subparsers.choices:
                subparsers.choices[args.help_target_command].print_help()
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

    if args.command not in ['search', 'wdinfo', 'list', 'info', 'isready', 'addon-cam', 'addon-mistyproxy', 'addon-drive', 'terminate', 'launch', 'list-ci-projects', 'create-ci-project', 'submit-ci-job']:
        print('Unrecognized command. Try `help`.')
        return 1

    command = args.command.replace('-', '_')
    if getattr(args, 'print_{}_help'.format(command)):
        subparsers.choices[args.command].print_help()
        return 0
    try:
        return globals()['cli_' + command](apic, args)
    except rerobots_api.Error as err:
        print('error: {}'.format(err))
        return 1
    except requests.exceptions.ConnectionError:
        print('api.rerobots.net server cannot be reached.  Are you connected to the Internet?')
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/python3
""" Implementation of the console frontend of the Todoist backup utility """

import argparse
import sys

class ConsoleFrontend:
    """ Implementation of the console frontend for the Todoist backup tool """
    def __init__(self, controller_factory, controller_dependencies_factory):
        self.__controller_factory = controller_factory
        self.__controller_dependencies_factory = controller_dependencies_factory
        self.__controller = None

    def __parse_command_line_args(self, prog, arguments):
        example_str = "Example: {} --download-latest --token 0123456789abcdef".format(sys.argv[0])
        parser = argparse.ArgumentParser(prog=prog, epilog=example_str)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--list", action="store_true", help="list all available backups")
        group.add_argument("--download-latest", action="store_true",
                           help="download latest backup available")
        group.add_argument("--download-version", type=str, metavar="VERSION",
                           help="download specified backup version")
        parser.add_argument("--token", type=str, required=True,
                            help="todoist API token (see Settings --> Integration)")
        parser.add_argument("--verbose", action="store_true",
                            help="print details to console")
        return parser.parse_args(arguments)

    def run(self, prog, arguments):
        """ Runs the Todoist backup tool frontend with the specified command line arguments """
        args = self.__parse_command_line_args(prog, arguments)

        # Configure controller
        dependencies = self.__controller_dependencies_factory(args.token, args.verbose)
        controller = self.__controller_factory(dependencies)

        # Execute requested action
        if args.list:
            (backups, latest_backup) = controller.get_backups()
            print('{:<30} | {}'.format("VERSION", "URL"))
            for backup in backups:
                is_latest_str = " (latest)" if backup == latest_backup else ""
                print('{:<30} | {}'.format(backup.version + is_latest_str, backup.url))
        elif args.download_latest:
            controller.download_latest(".")
        elif args.download_version:
            controller.download_version(args.download_version, ".")

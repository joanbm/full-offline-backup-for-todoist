#!/usr/bin/python3
""" Implementation of the console frontend of the Todoist backup utility """

import argparse
import sys
from abc import ABCMeta, abstractmethod

class ConsoleFrontendDependencyInjector(object, metaclass = ABCMeta):
    """ Rudimentary dependency injection container for the console frontend """

    @abstractmethod
    def __init__(self, token, verbose):
        """ Initializes the dependencies according to the user configuration """

    @property
    @abstractmethod
    def tracer(self):
        """ Get an instance of the tracer """

    @property
    @abstractmethod
    def todoist_api(self):
        """ Gets an instance of the Todoist API """

    @property
    @abstractmethod
    def todoist_backup_downloader(self):
        """ Gets an instance of the Todoist backup downloader """


class ConsoleFrontend:
    """ Implementation of the console frontend for the Todoist backup tool """
    def __init__(self, dependencies_factory):
        self.__dependencies_factory = dependencies_factory
        self.__dependencies = None

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

    def __list_backups(self):
        backups = self.__dependencies.todoist_api.get_backups()

        print('{:<20} | {}'.format("VERSION", "URL"))
        for backup in backups:
            print('{:<20} | {}'.format(backup.version, backup.url))

    def __download_latest(self, ):
        self.__dependencies.todoist_backup_downloader.download_latest(".")

    def __download_version(self, version):
        self.__dependencies.todoist_backup_downloader.download_version(version, ".")

    def run(self, prog, arguments):
        """ Runs the Todoist backup tool frontend with the specified command line arguments """
        args = self.__parse_command_line_args(prog, arguments)

        # Configure dependencies
        self.__dependencies = self.__dependencies_factory(args.token, args.verbose)

        # Execute requested action
        if args.list:
            self.__list_backups()
        elif args.download_latest:
            self.__download_latest()
        elif args.download_version:
            self.__download_version(args.download_version)

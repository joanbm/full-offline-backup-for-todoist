#!/usr/bin/python3
""" Implementation of the console frontend of the Todoist backup utility """

import argparse

class ConsoleFrontend:
    """ Implementation of the console frontend for the Todoist backup tool """
    def __init__(self, controller_factory, controller_dependencies_factory):
        self.__controller_factory = controller_factory
        self.__controller_dependencies_factory = controller_dependencies_factory
        self.__controller = None

    def __parse_command_line_args(self, prog, arguments):
        example1_str = "Example: {} download LATEST --token 0123456789abcdef".format(prog)
        example2_str = "         {} --verbose list --token 0123456789abcdef".format(prog)
        parser = argparse.ArgumentParser(prog=prog, formatter_class=argparse.RawTextHelpFormatter,
                                         epilog=example1_str + '\r\n' + example2_str)
        parser.add_argument("--verbose", action="store_true", help="print details to console")
        subparsers = parser.add_subparsers(dest='action')
        subparsers.required = True

        # create the parser for the "list" command
        parser_list = subparsers.add_parser('list', help='list available backups')
        parser_list.set_defaults(func=self.handle_list)
        parser_list.add_argument("--token", type=str, required=True,
                                 help="todoist API token (see Settings --> Integration)")

        # create the parser for the "download" command
        parser_download = subparsers.add_parser('download', help='download specified backup')
        parser_download.set_defaults(func=self.handle_download)
        parser_download.add_argument("version", type=str, metavar="VERSIONSPEC|LATEST",
                                     help="backup version to download, or LATEST")
        parser_download.add_argument("--with-attachments", action="store_true",
                                     help="download attachments and attach to the backup file")
        parser_download.add_argument("--token", type=str, required=True,
                                     help="todoist API token (see Settings --> Integration)")

        return parser.parse_args(arguments)

    def run(self, prog, arguments):
        """ Runs the Todoist backup tool frontend with the specified command line arguments """
        args = self.__parse_command_line_args(prog, arguments)
        args.func(args)

    def handle_list(self, args):
        """ Handles the list subparser with the specified command line arguments """
        # Configure controller
        dependencies = self.__controller_dependencies_factory(args.token, args.verbose)
        controller = self.__controller_factory(dependencies)

        # Execute requested action
        (backups, latest_backup) = controller.get_backups()
        print("{:<30} | {}".format("VERSION", "URL"))
        for backup in backups:
            is_latest_str = " (LATEST)" if backup == latest_backup else ""
            print("{:<30} | {}".format(backup.version + is_latest_str, backup.url))

    def handle_download(self, args):
        """ Handles the download subparser with the specified command line arguments """

        # Configure controller
        dependencies = self.__controller_dependencies_factory(args.token, args.verbose)
        controller = self.__controller_factory(dependencies)

        # Execute requested action
        if args.version == 'LATEST':
            controller.download_latest(".", with_attachments=args.with_attachments)
        else:
            controller.download_version(args.version, ".", with_attachments=args.with_attachments)

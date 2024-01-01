#!/usr/bin/python3
""" Implementation of the console frontend of the Todoist backup utility """

import argparse
import os
import getpass
from pathlib import Path
from typing import Callable, List, Mapping, Optional
from .virtual_fs import ZipVirtualFs
from .controller import TodoistAuth, Controller, ControllerDependencyInjector

class ConsoleFrontend:
    """ Implementation of the console frontend for the Todoist backup tool """
    def __init__(self, controller_factory: Callable[[ControllerDependencyInjector], Controller],
                 controller_dependencies_factory: Callable[[TodoistAuth, bool],
                                                           ControllerDependencyInjector]):
        self.__controller_factory = controller_factory
        self.__controller_dependencies_factory = controller_dependencies_factory

    @staticmethod
    def __add_authorization_group(parser: argparse.ArgumentParser) -> None:
        token_group = parser.add_mutually_exclusive_group()
        token_group.add_argument("--token-file", type=str,
                                 help="path to a file containing the Todoist token")
        parser.add_argument("--email", type=str, help="Todoist email")
        parser.add_argument("--password-file", type=str,
                            help="path to a file containing the Todoist password")

        # Those options are deprecated, since they are easy to use incorrectly
        # (e.g. by getting the password logged to the history file)
        # Using either interactive console input, environment variables or files is recommended
        token_group.add_argument("--token", type=str, help=argparse.SUPPRESS)
        parser.add_argument("--password", type=str, help=argparse.SUPPRESS)

    def __parse_command_line_args(self, prog: str, arguments: List[str]) -> argparse.Namespace:
        epilog_str = f"Example: {prog} download\n"
        epilog_str += "(The necessary credentials will be asked through the command line.\n"
        epilog_str += " If you wish to automate backups, credentials can be passed through the\n"
        epilog_str += " TODOIST_TOKEN, TODOIST_EMAIL and TODOIST_PASSWORD environment variables)"
        parser = argparse.ArgumentParser(prog=prog, formatter_class=argparse.RawTextHelpFormatter,
                                         epilog=epilog_str)
        parser.add_argument("--verbose", action="store_true", help="print details to console")
        subparsers = parser.add_subparsers(dest='action')
        subparsers.required = True

        # create the parser for the "download" command
        parser_download = subparsers.add_parser('download', help='download specified backup')
        parser_download.set_defaults(func=self.handle_download)
        parser_download.add_argument("--with-attachments", action="store_true",
                                     help="download attachments and attach to the backup file")
        parser_download.add_argument("--output-file", type=str,
                                     help="name of the file that will store the backup")
        self.__add_authorization_group(parser_download)

        return parser.parse_args(arguments)

    def run(self, prog: str, arguments: List[str], environment: Mapping[str, str]) -> None:
        """ Runs the Todoist backup tool frontend with the specified command line arguments """
        args = self.__parse_command_line_args(prog, arguments)
        args.func(args, environment)

    @staticmethod
    def __huge_warning(text: str) -> None:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(text)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        while input("Type 'CONTINUE ANYWAY' to continue: ") != 'CONTINUE ANYWAY':
            pass

    @staticmethod
    def __get_auth(args: argparse.Namespace, environment: Mapping[str, str]) -> TodoistAuth:
        def get_credential(opt_file: Optional[str], opt_direct: Optional[str],
                           env_var: str, prompt: str, sensitive: bool) -> str:
            if opt_file:
                if sensitive and os.name == "posix": # OpenSSH-like check
                    file_stat = os.stat(opt_file)
                    if file_stat.st_uid == os.getuid() and file_stat.st_mode & 0o077 != 0:
                        ConsoleFrontend.__huge_warning(
                            f"WARNING: Reading credentials from file {opt_file} "
                            "accessible by other users is deprecated.")
                return Path(opt_file).read_text('utf-8')

            if sensitive and opt_direct:
                ConsoleFrontend.__huge_warning(
                     "WARNING: Passing credentials through the command line is deprecated.\n"
                    f"         Pass it through the {env_var} environment variable,\n"
                     "         or remove the parameter and type it through the console")
                return opt_direct

            if env_var in environment:
                return environment[env_var]
            return getpass.getpass(prompt + ": ") if sensitive else input(prompt + ": ")

        token = get_credential(args.token_file, args.token, "TODOIST_TOKEN",
                               "Todoist token (from https://todoist.com/app/settings/integrations/developer)", sensitive=True)
        email = get_credential(None, args.email, "TODOIST_EMAIL", "Todoist email https://todoist.com/app/settings/account",
                               sensitive=False) if args.with_attachments else None
        password = get_credential(None, args.password, "TODOIST_PASSWORD", "Todoist password (can be empty)",
                                  sensitive=True) if args.with_attachments else None
        return TodoistAuth(token, email, password)

    def handle_download(self, args: argparse.Namespace, environment: Mapping[str, str]) -> None:
        """ Handles the download subparser with the specified command line arguments """

        # Configure controller
        auth = self.__get_auth(args, environment)
        dependencies = self.__controller_dependencies_factory(auth, args.verbose)
        controller = self.__controller_factory(dependencies)

        # Setup zip virtual fs
        with ZipVirtualFs(args.output_file) as zipvfs:
            # Execute requested action
            controller.download(zipvfs, with_attachments=args.with_attachments)

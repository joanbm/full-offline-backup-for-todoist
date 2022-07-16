#!/usr/bin/python3
""" Defines the main function of the Todoist backup utility """

import sys
import os
from .frontend import ConsoleFrontend
from .controller import Controller
from .runtime import RuntimeControllerDependencyInjector

def main() -> None:
    """ Defines the main function of the Todoist backup utility """
    ConsoleFrontend(Controller, RuntimeControllerDependencyInjector).run(
        sys.argv[0], sys.argv[1:], os.environ)

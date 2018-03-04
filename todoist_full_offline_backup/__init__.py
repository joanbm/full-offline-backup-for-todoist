#!/usr/bin/python3
""" Entry point of the Todoist backup utility """

import sys
from .frontend import ConsoleFrontend
from .controller import Controller
from .runtime import RuntimeControllerDependencyInjector

def main():
    ConsoleFrontend(Controller, RuntimeControllerDependencyInjector).run(sys.argv[0], sys.argv[1:])

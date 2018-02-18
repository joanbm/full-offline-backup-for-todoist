#!/usr/bin/python3
""" Entry point of the Todoist backup utility """

import sys
from frontend import ConsoleFrontend
from controller import Controller
from runtime import RuntimeControllerDependencyInjector

# Run the actual program
if __name__ == "__main__":
    ConsoleFrontend(Controller, RuntimeControllerDependencyInjector).run(sys.argv[0], sys.argv[1:])

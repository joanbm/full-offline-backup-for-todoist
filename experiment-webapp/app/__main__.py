#!/usr/bin/python3

import sys
import json
import js # pylint: disable=E0401
import urllib
import glob
from pathlib import Path
import shlex

# -- HACK -- Patch URLLib to use a real JavaScript implementation,
#            since it seems hard to get emscripten to compile python with sockets

# 'Nullify' the "import urllib.request" that will be done in the real code
sys.modules['urllib.request']={}

# Implement the bare minimum to get urllib.request.urlopen to work
class URLLibRequestStub:
    @staticmethod
    def urlopen(url):
        print("HACK: URL Open Intercepted " + url)
        return URLLibRequestStub(url)

    def __init__(self, url):
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def read(self):
        return js.download_binary(self.url)

# Monkey patch urllib.request, so our code works
urllib.request = URLLibRequestStub

# Ask for the command line arguments
args = js.ask_command_line()
sys.argv = shlex.split(args)

# Finally, run the main function of the program
from .todoist_full_offline_backup.__init__ import main # pylint: disable=E0402
main()

# Finally! offer the downloaded backup to the user
name = glob.glob("TodoistBackup_*")[0]
backupzip = Path(name).read_bytes()
js.offer_download(backupzip, name)

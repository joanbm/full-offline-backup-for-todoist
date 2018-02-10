#!/usr/bin/python3
from todoist_api import TodoistApi
from tracer import ConsoleTracer
import os
import urllib.request
import re

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """

    def __init__(self, todoist_api, tracer):
        self.__todoist_api = todoist_api
        self.__tracer = tracer

    def __download_backup(self, backup, output_path):
        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        self.__tracer.trace("Downloading backup with version '{}'".format(backup.version))
        sanitized_file_name = re.sub(r'[^a-zA-Z0-9_\- ]', "_", backup.version) + ".zip"
        output_file_path = os.path.join(output_path, sanitized_file_name)

        if os.path.isfile(output_file_path):
            self.__tracer.trace("Duplicate '{}' already downloaded... skipping".format(
                sanitized_file_name))
            return

        self.__tracer.trace("Downloading from {} to file '{}'...".format(
            backup.url, sanitized_file_name))
        urllib.request.urlretrieve(backup.url, output_file_path)

    def download_latest(self, output_path):
        """ Downloads the latest (i.e. most recent) Todoist backup ZIP """
        self.__tracer.trace("Fetching backup list to find the latest backup...")
        backups = self.__todoist_api.get_backups()
        backup = max(backups, key=lambda x: x.version_date)
        self.__download_backup(backup, output_path)

    def download_version(self, version, output_path):
        """ Downloads the specified Todoist backup ZIP given by its version string """
        self.__tracer.trace("Fetching backup list to find the backup '{}'...".format(version))
        backups = self.__todoist_api.get_backups()
        backup = next((x for x in backups if x.version == version))
        self.__download_backup(backup, output_path)

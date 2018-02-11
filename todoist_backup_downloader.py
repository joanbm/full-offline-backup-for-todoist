#!/usr/bin/python3
""" Class to download Todoist backup ZIPs using the Todoist API """
import os
import urllib.request
import re

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """

    def __init__(self, tracer):
        self.__tracer = tracer

    def download(self, backup, output_path):
        """ Downloads the specified backup to the specified folder """

        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        self.__tracer.trace("Downloading backup with version '{}'".format(backup.version))
        sanitized_file_name = re.sub(r'[^a-zA-Z0-9_\- ]', "_", backup.version) + ".zip"
        output_file_path = os.path.join(output_path, sanitized_file_name)

        if not os.path.isfile(output_file_path):
            self.__tracer.trace("Downloading from {} to file '{}'...".format(
                backup.url, sanitized_file_name))
            urllib.request.urlretrieve(backup.url, output_file_path)
        else:
            self.__tracer.trace("File '{}' already downloaded... skipping".format(
                sanitized_file_name))

        return output_file_path

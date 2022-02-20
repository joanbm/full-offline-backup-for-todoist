#!/usr/bin/python3
""" Class to download Todoist backup ZIPs using the Todoist API """
import datetime
from .utils import sanitize_file_name

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """
    __ZIP_FLAG_BITS_UTF8 = 0x800

    def __init__(self, tracer, todoist_api):
        self.__tracer = tracer
        self.__todoist_api = todoist_api

    def download(self, vfs):
        """ Generates a Todoist backup and saves it to the given VFS """
        self.__tracer.trace("Generating backup from current Todoist status")

        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        backup_version = datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')
        vfs.set_path_hint(sanitize_file_name("TodoistBackup_" + backup_version))

        # Download the file
        if vfs.existed():
            self.__tracer.trace("File already downloaded... skipping")
            return

        self.__tracer.trace("Downloading project list from todoist API...")
        projects = self.__todoist_api.get_projects()

        for project in projects:
            export_csv_file_name = f"{sanitize_file_name(project.name)} [{project.identifier}].csv"
            export_csv_file_content = self.__todoist_api.export_project_as_csv(project)
            vfs.write_file(export_csv_file_name, export_csv_file_content)

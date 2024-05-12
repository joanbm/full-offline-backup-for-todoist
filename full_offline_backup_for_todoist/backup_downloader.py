#!/usr/bin/python3
""" Class to download Todoist backup ZIPs using the Todoist API """
import datetime
from .utils import sanitize_file_name
from .tracer import Tracer
from .todoist_api import TodoistApi
from .virtual_fs import VirtualFs

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """
    __tracer: Tracer
    __todoist_api: TodoistApi

    def __init__(self, tracer: Tracer, todoist_api: TodoistApi):
        self.__tracer = tracer
        self.__todoist_api = todoist_api

    def download(self, vfs: VirtualFs) -> None:
        """ Generates a Todoist backup and saves it to the given VFS """
        self.__tracer.trace("Generating backup from current Todoist status")

        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        backup_version = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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

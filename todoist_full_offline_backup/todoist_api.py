#!/usr/bin/python3
""" Provides access to a subset of the features of the Todoist API"""

import datetime
import json

class TodoistBackupInfo:
    """ Represents the properties of a Todoist backup """

    def __init__(self, version, url):
        self.version = version
        self.url = url

    @property
    def version_date(self):
        """ Parses the Todoist backup version as a date and time """
        return datetime.datetime.strptime(self.version, "%Y-%m-%d %H:%M")

class TodoistApi:
    """ Provides access to a subset of the features of the Todoist API"""

    __BACKUP_LIST_ENDPOINT = "https://todoist.com/api/v7/backups/get"

    def __init__(self, api_token, tracer, urldownloader):
        self.__api_token = api_token
        self.__tracer = tracer
        self.__urldownloader = urldownloader

    def get_backups(self):
        """ Obtains the list of all backups from the Todoist API """
        self.__tracer.trace("Fetching backups using the Todoist API...")
        backup_list_json = self.__urldownloader.get(
            self.__BACKUP_LIST_ENDPOINT, {"token": self.__api_token})

        self.__tracer.trace("Loading Todoist API backup JSON...")
        backup_list = json.loads(backup_list_json.decode())

        self.__tracer.trace("Parsing Todoist API backup JSON...")
        return [TodoistBackupInfo(row["version"], row["url"]) for row in backup_list]

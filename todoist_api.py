#!/usr/bin/python3

import urllib.request
import urllib.parse
import datetime
import json

class TodoistBackupInfo:
    """ Represents the properties of a Todoist backup """

    def __init__(self, version, url):
        self.version = version
        self.url = url

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def get_version_date(self):
        return datetime.datetime.strptime(self.version, "%Y-%m-%d %H:%M")

    version_date = property(get_version_date)

class TodoistApi:
    """ Provides access to a subset of the features of the Todoist API"""

    __BACKUP_LIST_ENDPOINT = "https://todoist.com/api/v7/backups/get"

    def __init__(self, api_token):
        self.__api_token = api_token

    def get_backups(self):
        """ Obtains the list of all backups from the Todoist API """
        token_data = urllib.parse.urlencode({ "token": self.__api_token}).encode()
        backup_list_request = urllib.request.urlopen(self.__BACKUP_LIST_ENDPOINT, data=token_data)
        backup_list_json = backup_list_request.read()

        backup_list = json.loads(backup_list_json)

        return [TodoistBackupInfo(row["version"], row["url"]) for row in backup_list]

#!/usr/bin/python3
""" Provides access to a subset of the features of the Todoist API"""

import json

class TodoistProjectInfo:
    """ Represents the properties of a Todoist project """

    def __init__(self, name, identifier):
        self.name = name
        self.identifier = identifier

class TodoistApi:
    """ Provides access to a subset of the features of the Todoist API"""

    __SYNC_ENDPOINT = "https://todoist.com/api/v7/sync"
    __EXPORT_PROJECT_AS_CSV_FILE_ENDPOINT = "https://todoist.com/api/v7/templates/export_as_file"

    def __init__(self, api_token, tracer, urldownloader):
        self.__api_token = api_token
        self.__tracer = tracer
        self.__urldownloader = urldownloader

    def get_projects(self):
        """ Obtains the list of all projects from the Todoist API """
        self.__tracer.trace("Fetching projects using the Todoist API...")
        project_list_json = self.__urldownloader.get(
            self.__SYNC_ENDPOINT, {
                "token": self.__api_token,
                "sync_token": '*',
                "resource_types": '["projects"]',
            })

        self.__tracer.trace("Loading Todoist API projects JSON...")
        project_list = json.loads(project_list_json.decode())

        self.__tracer.trace("Parsing Todoist API projects JSON...")
        return [TodoistProjectInfo(row["name"], row["id"]) for row in project_list["projects"]]

    def export_project_as_csv(self, project):
        """ Obtains the latest version of the specified project as a CSV file """
        self.__tracer.trace("Fetching project '{}' (ID {}) as CSV using the Todoist API...".format(
            project.name, project.identifier))

        return self.__urldownloader.get(
            self.__EXPORT_PROJECT_AS_CSV_FILE_ENDPOINT, {
                "token": self.__api_token,
                "project_id": project.identifier
            })

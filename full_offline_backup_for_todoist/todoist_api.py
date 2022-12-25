#!/usr/bin/python3
""" Provides access to a subset of the features of the Todoist API"""

import json
from typing import List
from .tracer import Tracer
from .url_downloader import URLDownloader

class TodoistProjectInfo:
    """ Represents the properties of a Todoist project """

    name: str
    identifier: str

    def __init__(self, name: str, identifier: str):
        self.name = name
        self.identifier = identifier

class TodoistApi:
    """ Provides access to a subset of the features of the Todoist API"""

    __BASE_URL = "https://api.todoist.com/sync/v9"
    __SYNC_ENDPOINT = __BASE_URL + "/sync"
    __EXPORT_PROJECT_AS_CSV_FILE_ENDPOINT = __BASE_URL + "/templates/export_as_file"

    __tracer: Tracer
    __urldownloader: URLDownloader

    def __init__(self, api_token: str, tracer: Tracer, urldownloader: URLDownloader):
        self.__tracer = tracer
        self.__urldownloader = urldownloader
        self.__urldownloader.set_bearer_token(api_token)

    def get_projects(self) -> List[TodoistProjectInfo]:
        """ Obtains the list of all projects from the Todoist API """
        self.__tracer.trace("Fetching projects using the Todoist API...")
        project_list_json = self.__urldownloader.get(
            self.__SYNC_ENDPOINT, {
                "sync_token": '*',
                "resource_types": '["projects"]',
            })

        self.__tracer.trace("Loading Todoist API projects JSON...")
        project_list = json.loads(project_list_json.decode())

        self.__tracer.trace("Parsing Todoist API projects JSON...")
        return [TodoistProjectInfo(row["name"], row["id"]) for row in project_list["projects"]]

    def export_project_as_csv(self, project: TodoistProjectInfo) -> bytes:
        """ Obtains the latest version of the specified project as a CSV file """
        self.__tracer.trace(f"Fetching project '{project.name}' (ID {project.identifier})"
            " as CSV using the Todoist API...")

        return self.__urldownloader.get(
            self.__EXPORT_PROJECT_AS_CSV_FILE_ENDPOINT, {
                "project_id": project.identifier
            })

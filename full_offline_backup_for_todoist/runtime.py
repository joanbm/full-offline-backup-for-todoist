#!/usr/bin/python3
""" Implementation of the dependency injection container for the actual runtime objects """

from .controller import ControllerDependencyInjector
from .todoist_api import TodoistApi
from .backup_downloader import TodoistBackupDownloader
from .backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from .tracer import ConsoleTracer, NullTracer
from .url_downloader import URLLibURLDownloader, TodoistAuthURLDownloader

class RuntimeControllerDependencyInjector(ControllerDependencyInjector):
    """ Implementation of the dependency injection container for the actual runtime objects """

    def __init__(self, auth, verbose):
        super(RuntimeControllerDependencyInjector, self).__init__(auth, verbose)
        self.__tracer = ConsoleTracer() if verbose else NullTracer()
        if "email" in auth and "password" in auth:
            self.__tracer.trace("NOTE: Using authentication workaround to download the attachments")
            urldownloader = TodoistAuthURLDownloader(self.__tracer, auth["email"], auth["password"])
        else:
            urldownloader = URLLibURLDownloader()
        todoist_api = TodoistApi(auth["token"], self.__tracer, urldownloader)
        self.__backup_downloader = TodoistBackupDownloader(self.__tracer, todoist_api)
        self.__backup_attachments_downloader = TodoistBackupAttachmentsDownloader(
            self.__tracer, urldownloader)

    @property
    def tracer(self):
        return self.__tracer

    @property
    def backup_downloader(self):
        return self.__backup_downloader

    @property
    def backup_attachments_downloader(self):
        return self.__backup_attachments_downloader

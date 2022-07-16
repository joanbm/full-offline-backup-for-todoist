#!/usr/bin/python3
""" Implementation of the dependency injection container for the actual runtime objects """

from .controller import ControllerDependencyInjector, TodoistAuth
from .todoist_api import TodoistApi
from .backup_downloader import TodoistBackupDownloader
from .backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from .tracer import Tracer, ConsoleTracer, NullTracer
from .url_downloader import URLDownloader, URLLibURLDownloader, TodoistAuthURLDownloader

class RuntimeControllerDependencyInjector(ControllerDependencyInjector):
    """ Implementation of the dependency injection container for the actual runtime objects """

    def __init__(self, auth: TodoistAuth, verbose: bool):
        super().__init__(auth, verbose)
        self.__tracer = ConsoleTracer() if verbose else NullTracer()
        urldownloader: URLDownloader
        if auth.email and auth.password:
            self.__tracer.trace("NOTE: Using authentication workaround to download the attachments")
            urldownloader = TodoistAuthURLDownloader(self.__tracer, auth.email, auth.password)
        else:
            urldownloader = URLLibURLDownloader()
        todoist_api = TodoistApi(auth.token, self.__tracer, urldownloader)
        self.__backup_downloader = TodoistBackupDownloader(self.__tracer, todoist_api)
        self.__backup_attachments_downloader = TodoistBackupAttachmentsDownloader(
            self.__tracer, urldownloader)

    @property
    def tracer(self) -> Tracer:
        return self.__tracer

    @property
    def backup_downloader(self) -> TodoistBackupDownloader:
        return self.__backup_downloader

    @property
    def backup_attachments_downloader(self) -> TodoistBackupAttachmentsDownloader:
        return self.__backup_attachments_downloader

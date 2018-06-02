#!/usr/bin/python3
""" Implementation of the dependency injection container for the actual runtime objects """

from .controller import ControllerDependencyInjector
from .todoist_api import TodoistApi
from .backup_downloader import TodoistBackupDownloader
from .backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from .tracer import ConsoleTracer, NullTracer
from .url_downloader import URLLibURLDownloader

class RuntimeControllerDependencyInjector(ControllerDependencyInjector):
    """ Implementation of the dependency injection container for the actual runtime objects """

    def __init__(self, token, verbose):
        super(RuntimeControllerDependencyInjector, self).__init__(token, verbose)
        self.__tracer = ConsoleTracer() if verbose else NullTracer()
        urldownloader = URLLibURLDownloader()
        todoist_api = TodoistApi(token, self.__tracer, urldownloader)
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

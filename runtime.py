#!/usr/bin/python3
""" Implementation of the dependency injection container for the actual runtime objects """

from controller import ControllerDependencyInjector
from todoist_api import TodoistApi
from todoist_backup_downloader import TodoistBackupDownloader
from todoist_backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from tracer import ConsoleTracer, NullTracer

class RuntimeControllerDependencyInjector(ControllerDependencyInjector):
    """ Implementation of the dependency injection container for the actual runtime objects """

    def __init__(self, token, verbose):
        super(RuntimeControllerDependencyInjector, self).__init__(token, verbose)
        self.__tracer = ConsoleTracer() if verbose else NullTracer()
        self.__todoist_api = TodoistApi(token, self.__tracer)
        self.__todoist_backup_downloader = TodoistBackupDownloader(self.__tracer)
        self.__todoist_backup_attachments_downloader = TodoistBackupAttachmentsDownloader(self.__tracer)

    @property
    def tracer(self):
        return self.__tracer

    @property
    def todoist_api(self):
        return self.__todoist_api

    @property
    def todoist_backup_downloader(self):
        return self.__todoist_backup_downloader

    @property
    def todoist_backup_attachments_downloader(self):
        return self.__todoist_backup_attachments_downloader

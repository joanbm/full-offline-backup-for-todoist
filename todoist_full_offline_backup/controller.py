#!/usr/bin/python3
""" Provides frontend-independent access to the functions of the interface """

from abc import ABCMeta, abstractmethod

class BackupNotFoundException(Exception):
    """ Thrown when the user requests a download of a backup that does not exist """
    pass

class ControllerDependencyInjector(object, metaclass=ABCMeta):
    """ Rudimentary dependency injection container for the controller """

    @abstractmethod
    def __init__(self, token, verbose):
        """ Initializes the dependencies according to the user configuration """

    @property
    @abstractmethod
    def tracer(self):
        """ Get an instance of the tracer """

    @property
    @abstractmethod
    def todoist_api(self):
        """ Gets an instance of the Todoist API """

    @property
    @abstractmethod
    def backup_downloader(self):
        """ Gets an instance of the Todoist backup downloader """

    def backup_attachments_downloader(self):
        """ Gets an instance of the Todoist backup attachment downloader """

class Controller:
    """ Provides frontend-independent access to the functions of the interface """

    def __init__(self, dependencies):
        self.__dependencies = dependencies

    def get_backups(self):
        """ Gets the list of backups along with the latest backup """
        backups = self.__dependencies.todoist_api.get_backups()
        return (backups, self.__get_latest(backups))

    def download_latest(self, vfs, with_attachments):
        """ Downloads the latest (i.e. most recent) Todoist backup ZIP """
        self.__dependencies.tracer.trace("Fetching backup list to find the latest backup...")
        backups = self.__dependencies.todoist_api.get_backups()
        backup = self.__get_latest(backups)
        if backup is None:
            raise BackupNotFoundException()
        self.__dependencies.backup_downloader.download(backup, vfs)
        if with_attachments:
            self.__dependencies.backup_attachments_downloader.download_attachments(vfs)

    def download_version(self, version, vfs, with_attachments):
        """ Downloads the specified Todoist backup ZIP given by its version string """
        self.__dependencies.tracer.trace(
            "Fetching backup list to find the backup '{}'...".format(version))
        backups = self.__dependencies.todoist_api.get_backups()
        backup = self.__find_version(backups, version)
        if backup is None:
            raise BackupNotFoundException()
        self.__dependencies.backup_downloader.download(backup, vfs)
        if with_attachments:
            self.__dependencies.backup_attachments_downloader.download_attachments(vfs)

    @staticmethod
    def __get_latest(backups):
        return max(backups, key=lambda x: x.version_date, default=None)

    @staticmethod
    def __find_version(backups, version):
        return next((x for x in backups if x.version == version), None)

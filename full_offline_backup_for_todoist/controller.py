#!/usr/bin/python3
""" Provides frontend-independent access to the functions of the interface """

from abc import ABCMeta, abstractmethod

class ControllerDependencyInjector(metaclass=ABCMeta):
    """ Rudimentary dependency injection container for the controller """

    @abstractmethod
    def __init__(self, auth, verbose):
        """ Initializes the dependencies according to the user configuration """

    @property
    @abstractmethod
    def tracer(self):
        """ Gets an instance of the debug tracer """

    @property
    @abstractmethod
    def backup_downloader(self):
        """ Gets an instance of the Todoist backup downloader """

    @property
    @abstractmethod
    def backup_attachments_downloader(self):
        """ Gets an instance of the Todoist backup attachment downloader """

class Controller:
    """ Provides frontend-independent access to the functions of the interface """

    def __init__(self, dependencies):
        self.__dependencies = dependencies

    def download(self, vfs, with_attachments):
        """ Generates a Todoist backup ZIP from the current Todoist items """
        self.__dependencies.backup_downloader.download(vfs)
        if with_attachments:
            self.__dependencies.backup_attachments_downloader.download_attachments(vfs,
                with_attachments == 'ignore-forbidden')

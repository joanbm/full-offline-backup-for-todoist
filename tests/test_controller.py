#!/usr/bin/python3
""" Tests for the controller class that gives access to most classes of the system """
# pylint: disable=invalid-name
import unittest
from unittest.mock import Mock, ANY
from full_offline_backup_for_todoist.tracer import NullTracer
from full_offline_backup_for_todoist.controller import ControllerDependencyInjector, Controller

class TestControllerDependencyInjector(ControllerDependencyInjector):
    """ Rudimentary dependency injection container for the tests """

    def __init__(self, test_tracer, test_todoist_downloader,
                 test_todoist_attachments_downloader):
        self.__test_tracer = test_tracer
        self.__test_todoist_downloader = test_todoist_downloader
        self.__test_todoist_attachments_downloader = test_todoist_attachments_downloader

    @property
    def tracer(self):
        return self.__test_tracer

    @property
    def backup_downloader(self):
        return self.__test_todoist_downloader

    @property
    def backup_attachments_downloader(self):
        return self.__test_todoist_attachments_downloader

class TestController(unittest.TestCase):
    """ Tests for the controller class that gives access to most classes of the system """

    @staticmethod
    def test_on_existing_version_with_attachments_calls_download_attachments():
        """ Tests that the backup + attachments downloader is called
            when attempting to download an specific version of an existing backup w/attachments """
        # Arrange
        downloader_attachments_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(), downloader_attachments_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download(".", with_attachments=True)

        # Assert
        downloader_attachments_mock.download_attachments.assert_called_with(ANY)

    @staticmethod
    def test_on_latest_version_calls_download_for_that_version():
        """ Tests that the backup + attachments downloader is called
            when attempting to download the latest existing backup """
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), downloader_mock, Mock())
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download(".", with_attachments=False)

        # Assert
        downloader_mock.download.assert_called_with(".")

    @staticmethod
    def test_on_latest_version_with_attachments_calls_download_attachments():
        """ Tests that the backup downloader is called
            when attempting to download the latest existing backup w/attachments """
        # Arrange
        downloader_attachments_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(), downloader_attachments_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download(".", with_attachments=True)

        # Assert
        downloader_attachments_mock.download_attachments.assert_called_with(ANY)

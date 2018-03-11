#!/usr/bin/python3
""" Tests for the controller class that gives access to most classes of the system """
# pylint: disable=invalid-name
import unittest
from unittest.mock import Mock, ANY
from ..todoist_api import TodoistBackupInfo
from ..tracer import NullTracer
from ..controller import ControllerDependencyInjector, Controller, BackupNotFoundException

class TestControllerDependencyInjector(ControllerDependencyInjector):
    """ Rudimentary dependency injection container for the tests """

    def __init__(self, test_tracer, test_todoist_api, test_todoist_downloader,
                 test_todoist_attachments_downloader):
        super(TestControllerDependencyInjector, self).__init__("", False)
        self.__test_tracer = test_tracer
        self.__test_todoist_api = test_todoist_api
        self.__test_todoist_downloader = test_todoist_downloader
        self.__test_todoist_attachments_downloader = test_todoist_attachments_downloader

    @property
    def tracer(self):
        return self.__test_tracer

    @property
    def todoist_api(self):
        return self.__test_todoist_api

    @property
    def backup_downloader(self):
        return self.__test_todoist_downloader

    @property
    def backup_attachments_downloader(self):
        return self.__test_todoist_attachments_downloader

class TestController(unittest.TestCase):
    """ Tests for the controller class that gives access to most classes of the system """
    def setUp(self):
        """ Creates the test sample data """
        self.__old_backup = TodoistBackupInfo("2016-01-01 12:30", "file://backup1.zip")
        self.__latest_backup = TodoistBackupInfo("2016-01-02 14:56", "file://backup2.zip")
        self.__test_data = [self.__old_backup, self.__latest_backup]

    def test_on_get_backups_returns_correct_list_and_latest_backup(self):
        """ Tests that a valid operation to get the list of backups returns the expected result """
        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), Mock(), Mock())
        controllerinst = Controller(controllerdi)

        # Act
        (backups, latest_backup) = controllerinst.get_backups()

        # Assert
        self.assertEqual(backups, self.__test_data)
        self.assertEqual(latest_backup, self.__latest_backup)

    def test_on_get_backups_with_no_backups_returns_empty_list_and_no_latest_backup(self):
        """ Tests that getting an empty list of backups is correctly handled """
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: []), downloader_mock, Mock())
        controllerinst = Controller(controllerdi)

        # Act
        (backups, latest_backup) = controllerinst.get_backups()

        # Assert
        self.assertEqual(backups, [])
        self.assertEqual(latest_backup, None)

    def test_on_nonexisting_version_throws_exception(self):
        """ Tests that an exception is thrown
            when attempting to download a non-existing backup version """

        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), Mock(), Mock())
        controllerinst = Controller(controllerdi)

        # Act/Assert
        self.assertRaises(BackupNotFoundException, controllerinst.download_version,
                          "2016-01-03 11:22", "/", with_attachments=False)

    def test_on_existing_version_calls_download_for_that_version(self):
        """ Tests that the backup downloader is called
            when attempting to download an specific version of an existing backup """
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), downloader_mock, Mock())
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_version(self.__old_backup.version, ".", with_attachments=False)

        # Assert
        downloader_mock.download.assert_called_with(self.__old_backup, ".")

    def test_on_existing_version_with_attachments_calls_download_attachments(self):
        """ Tests that the backup + attachments downloader is called
            when attempting to download an specific version of an existing backup w/attachments """
        # Arrange
        downloader_attachments_mock = Mock()
        controllerdi = TestControllerDependencyInjector(NullTracer(), Mock(
            get_backups=lambda: self.__test_data), Mock(), downloader_attachments_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_version(self.__old_backup.version, ".", with_attachments=True)

        # Assert
        downloader_attachments_mock.download_attachments.assert_called_with(ANY)

    def test_on_nonexisting_latest_throws_exception(self):
        """ Tests that an exception is thrown
            when attempting to download the latest backup, if there is none """
        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: []), Mock(), Mock())
        controllerinst = Controller(controllerdi)

        # Act/Assert
        self.assertRaises(BackupNotFoundException,
                          controllerinst.download_latest, "/", with_attachments=False)

    def test_on_latest_version_calls_download_for_that_version(self):
        """ Tests that the backup + attachments downloader is called
            when attempting to download the latest existing backup """
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), downloader_mock, Mock())
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_latest(".", with_attachments=False)

        # Assert
        downloader_mock.download.assert_called_with(self.__latest_backup, ".")

    def test_on_latest_version_with_attachments_calls_download_attachments(self):
        """ Tests that the backup downloader is called
            when attempting to download the latest existing backup w/attachments """
        # Arrange
        downloader_attachments_mock = Mock()
        controllerdi = TestControllerDependencyInjector(NullTracer(), Mock(
            get_backups=lambda: self.__test_data), Mock(), downloader_attachments_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_latest(".", with_attachments=True)

        # Assert
        downloader_attachments_mock.download_attachments.assert_called_with(ANY)

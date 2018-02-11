import unittest
from unittest.mock import Mock
from todoist_api import TodoistBackupInfo
from tracer import NullTracer
from controller import ControllerDependencyInjector, Controller, BackupNotFoundException

class TestControllerDependencyInjector(ControllerDependencyInjector):
    """ Rudimentary dependency injection container for the tests """

    def __init__(self, test_tracer, test_todoist_api, test_todoist_downloader):
        self.__test_tracer = test_tracer
        self.__test_todoist_api = test_todoist_api
        self.__test_todoist_downloader = test_todoist_downloader

    @property
    def tracer(self):
        return self.__test_tracer

    @property
    def todoist_api(self):
        return self.__test_todoist_api

    @property
    def todoist_backup_downloader(self):
        return self.__test_todoist_downloader

class TestController(unittest.TestCase):
    def setUp(self):
        # Create sample test data
        self.__old_backup = TodoistBackupInfo("2016-01-01 12:30", "file://backup1.zip")
        self.__latest_backup = TodoistBackupInfo("2016-01-02 14:56", "file://backup2.zip")
        self.__test_data = [self.__old_backup, self.__latest_backup]

    def test_on_get_backups_returns_correct_list_and_latest_backup(self):
        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), Mock())
        controllerinst = Controller(controllerdi)

        # Act
        (backups, latest_backup) = controllerinst.get_backups()

        # Assert
        self.assertEqual(backups, self.__test_data)
        self.assertEqual(latest_backup, self.__latest_backup)

    def test_on_get_backups_with_no_backups_returns_empty_list_and_no_latest_backup(self):
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: []), downloader_mock)
        controllerinst = Controller(controllerdi)

        # Act
        (backups, latest_backup) = controllerinst.get_backups()

        # Assert
        self.assertEqual(backups, [])
        self.assertEqual(latest_backup, None)

    def test_on_nonexisting_version_throws_exception(self):
        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), Mock())
        controllerinst = Controller(controllerdi)

        # Act/Assert
        self.assertRaises(BackupNotFoundException, controllerinst.download_version, "2016-01-03 11:22", "/")

    def test_on_existing_version_calls_download_for_that_version(self):
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), downloader_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_version(self.__old_backup.version, ".")

        # Assert
        downloader_mock.download.assert_called_with(self.__old_backup, ".")

    def test_on_nonexisting_latest_throws_exception(self):
        # Arrange
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: []), Mock())
        controllerinst = Controller(controllerdi)

        # Act/Assert
        self.assertRaises(BackupNotFoundException, controllerinst.download_latest, "/")

    def test_on_latest_version_calls_download_for_that_version(self):
        # Arrange
        downloader_mock = Mock()
        controllerdi = TestControllerDependencyInjector(
            NullTracer(), Mock(get_backups=lambda: self.__test_data), downloader_mock)
        controllerinst = Controller(controllerdi)

        # Act
        controllerinst.download_latest(".")

        # Assert
        downloader_mock.download.assert_called_with(self.__latest_backup, ".")

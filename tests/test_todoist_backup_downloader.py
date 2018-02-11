import unittest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock
from todoist_api import TodoistApi, TodoistBackupInfo
from todoist_backup_downloader import TodoistBackupDownloader
from tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    def setUp(self):
        # Create sample filesystem structure and test data
        self.__test_dir = tempfile.mkdtemp()
        self.__input1_path = os.path.join(self.__test_dir, "input1.zip")
        self.__input2_path = os.path.join(self.__test_dir, "input2.zip")
        self.__backup1 = TodoistBackupInfo("2016-01-01 12:30", "file://" + self.__input1_path)
        self.__backup2 = TodoistBackupInfo("2016-01-02 14:56", "file://" + self.__input2_path)
        self.__test_data = [self.__backup1, self.__backup2]

        Path(self.__input1_path).write_text("input1")
        Path(self.__input2_path).write_text("input2")

    def tearDown(self):
        # Destroy sample filesystem structure
        shutil.rmtree(self.__test_dir)

    def test_on_nonexisting_version_throws_exception(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(
            Mock(get_backups=lambda: self.__test_data), NullTracer())

        # Act/Assert
        self.assertRaises(Exception, backup_downloader.download_version, "2016-01-03 11:22", "/")

    def test_on_existing_version_downloads_file_with_sanitized_filename(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(
            Mock(get_backups=lambda: self.__test_data), NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-01 12_30.zip")

        # Act
        dstpath = backup_downloader.download_version("2016-01-01 12:30", self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertEqual(Path(dstpath).read_text(), "input1")

    def test_on_latest_version_downloads_file_with_sanitized_filename(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(
            Mock(get_backups=lambda: self.__test_data), NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-02 14_56.zip")

        # Act
        dstpath = backup_downloader.download_latest(self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertEqual(Path(expected_dstpath).read_text(), "input2")

    def test_on_latest_version_and_existing_destionation_doesnt_overwrite(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(
            Mock(get_backups=lambda: self.__test_data), NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-02 14_56.zip")
        Path(expected_dstpath).write_text("i am untouchable")

        # Act
        dstpath = backup_downloader.download_latest(self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertEqual(Path(expected_dstpath).read_text(), "i am untouchable")
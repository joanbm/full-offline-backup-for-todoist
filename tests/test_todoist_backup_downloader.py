import unittest
import tempfile
import shutil
import os
from pathlib import Path
from todoist_api import TodoistBackupInfo
from todoist_backup_downloader import TodoistBackupDownloader
from tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    def setUp(self):
        # Create sample filesystem structure
        self.__test_dir = tempfile.mkdtemp()
        self.__input_path = os.path.join(self.__test_dir, "input1.zip")
        self.__backup = TodoistBackupInfo("2016-01-01 12:30", "file://" + self.__input_path)
        Path(self.__input_path).write_text("input1")

    def tearDown(self):
        # Destroy sample filesystem structure
        shutil.rmtree(self.__test_dir)

    def test_on_nonexisting_version_throws_exception(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        fake_backup = TodoistBackupInfo("123", "file:///this/path/does/not/exist/hopefully.zip")

        # Act/Assert
        self.assertRaises(Exception, backup_downloader.download, fake_backup, "/")

    def test_on_existing_version_downloads_file_with_sanitized_filename(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-01 12_30.zip")

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertEqual(Path(dstpath).read_text(), "input1")

    def test_on_latest_version_and_existing_destionation_doesnt_overwrite(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-01 12_30.zip")
        Path(expected_dstpath).write_text("i am untouchable")

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertEqual(Path(expected_dstpath).read_text(), "i am untouchable")
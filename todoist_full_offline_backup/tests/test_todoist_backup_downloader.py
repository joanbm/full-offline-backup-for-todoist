import unittest
import tempfile
import shutil
import os
import zipfile
from pathlib import Path
from .todoist_api import TodoistBackupInfo
from .todoist_backup_downloader import TodoistBackupDownloader
from .tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    def setUp(self):
        # Create sample filesystem structure
        self.__test_dir = tempfile.mkdtemp()
        self.__input_path = os.path.join(self.__test_dir, "input1.zip")
        self.__backup = TodoistBackupInfo("2016-01-01 12:30", "file://" + self.__input_path)

        with zipfile.ZipFile(self.__input_path, "w") as _:
            pass

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
        self.assertTrue(zipfile.is_zipfile(expected_dstpath))

    def test_on_latest_version_and_existing_destionation_doesnt_overwrite(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "2016-01-01 12_30.zip")

        with zipfile.ZipFile(expected_dstpath, "w") as _:
            pass

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertTrue(zipfile.is_zipfile(expected_dstpath))

    def test_on_zip_with_no_utf8_flag_sets_flag(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())

        # This is a prepared ZIP file with UTF-8 filenames but without the UTF-8 filenames set,
        # like those that come from Todoist backups...
        Path(self.__input_path).write_bytes(bytearray.fromhex(
            '504b03040a03000000000b90524c0000000000000000000000000d00000041534349494e414d452e747874' + 
            '504b03040a03000000000f90524c00000000000000000000000014000000554e49434f44454e414d4520f09f92a92e747874' + 
            '504b01023f030a03000000000b90524c0000000000000000000000000d0024000000000000002080a4810000000041534349494e414d452e7478740a0020000000000001001800005773f6d9a8d301005773f6d9a8d301005773f6d9a8d301' +
            '504b01023f030a03000000000f90524c000000000000000000000000140024000000000000002080a4812b000000554e49434f44454e414d4520f09f92a92e7478740a002000000000000100180080749ffad9a8d30180749ffad9a8d30180749ffad9a8d301' +
            '504b05060000000002000200c50000005d0000000000'))

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        with zipfile.ZipFile(dstpath, "r") as zip_file:
            self.assertEqual(zip_file.testzip(), None)
            self.assertIn("ASCIINAME.txt", zip_file.namelist())
            self.assertTrue(zip_file.getinfo("ASCIINAME.txt").flag_bits & 0x800)
            self.assertIn("UNICODENAME 💩.txt", zip_file.namelist())
            self.assertTrue(zip_file.getinfo("UNICODENAME 💩.txt").flag_bits & 0x800)

    def test_on_zip_with_utf8_flag_does_not_break(self):
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())

        # This is a prepared ZIP file with UTF-8 filenames but without the UTF-8 filenames set,
        # like those that come from Todoist backups...
        Path(self.__input_path).write_bytes(bytearray.fromhex(
            '504b03040a03000800000b90524c0000000000000000000000000d00000041534349494e414d452e747874' + 
            '504b03040a03000800000f90524c00000000000000000000000014000000554e49434f44454e414d4520f09f92a92e747874' + 
            '504b01023f030a03000800000b90524c0000000000000000000000000d0024000000000000002080a4810000000041534349494e414d452e7478740a0020000000000001001800005773f6d9a8d301005773f6d9a8d301005773f6d9a8d301' +
            '504b01023f030a03000800000f90524c000000000000000000000000140024000000000000002080a4812b000000554e49434f44454e414d4520f09f92a92e7478740a002000000000000100180080749ffad9a8d30180749ffad9a8d30180749ffad9a8d301' +
            '504b05060000000002000200c50000005d0000000000'))

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        with zipfile.ZipFile(dstpath, "r") as zip_file:
            self.assertEqual(zip_file.testzip(), None)
            self.assertIn("ASCIINAME.txt", zip_file.namelist())
            self.assertTrue(zip_file.getinfo("ASCIINAME.txt").flag_bits & 0x800)
            self.assertIn("UNICODENAME 💩.txt", zip_file.namelist())
            self.assertTrue(zip_file.getinfo("UNICODENAME 💩.txt").flag_bits & 0x800)

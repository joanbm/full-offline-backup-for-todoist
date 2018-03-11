#!/usr/bin/python3
""" Tests for the Todoist backup downloader class """
# pylint: disable=invalid-name
import unittest
import tempfile
import shutil
import hashlib
import os
import zipfile
from pathlib import Path
from ..todoist_api import TodoistBackupInfo
from ..backup_downloader import TodoistBackupDownloader
from ..tracer import NullTracer

class TestBackupAttachmentsDownloader(unittest.TestCase):
    """ Tests for the Todoist backup downloader class """
    def setUp(self):
        """ Creates the sample filesystem structure for the test """
        self.__test_dir = tempfile.mkdtemp()
        self.__input_path = os.path.join(self.__test_dir, "input1.zip")
        self.__backup = TodoistBackupInfo("2016-01-01 12:30", "file://" + self.__input_path)

        with zipfile.ZipFile(self.__input_path, "w") as _:
            pass

    def tearDown(self):
        """ Destroys the sample filesystem structure for the test """
        shutil.rmtree(self.__test_dir)

    def test_on_nonexisting_version_throws_exception(self):
        """ Tests that an exception is thrown when one attempts to download a backup
            that does not exist on the server """
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        fake_backup = TodoistBackupInfo("123", "file:///this/path/does/not/exist/hopefully.zip")

        # Act/Assert
        self.assertRaises(Exception, backup_downloader.download, fake_backup, "/")

    def test_on_existing_version_downloads_file_with_sanitized_filename(self):
        """ Tests that if a backup contains disallowed characters in its name,
            it is correctly sanitized to a restricted character set
            (for broad filesystem compatibility) """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "TodoistBackup_2016-01-01 12_30.zip")

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        self.assertTrue(zipfile.is_zipfile(expected_dstpath))

    def test_on_latest_version_and_existing_destination_doesnt_overwrite(self):
        """ Tests that if the backup already exists in the destination path,
            it is not overwriten """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())
        expected_dstpath = os.path.join(self.__test_dir, "TodoistBackup_2016-01-01 12_30.zip")

        with zipfile.ZipFile(expected_dstpath, "w") as zip_file:
            zip_file.writestr("dummy.txt", "dummy data for the test MD5")

            # Otherwise the downloader patches the ZIP anyway, if it exists...
            zip_file.getinfo("dummy.txt").flag_bits |= 0x800

        original_hash = hashlib.md5(Path(expected_dstpath).read_bytes()).hexdigest()

        # Act
        dstpath = backup_downloader.download(self.__backup, self.__test_dir)

        # Assert
        self.assertEqual(dstpath, expected_dstpath)
        new_hash = hashlib.md5(Path(expected_dstpath).read_bytes()).hexdigest()
        self.assertEqual(original_hash, new_hash)

    def test_on_zip_with_no_utf8_flag_sets_flag(self):
        """ Tests that, if the server provides a backup ZIP file with no UTF-8 filename flag,
            it is patched to include it (since the Todoist servers provide ZIPs without it)
            and the backup files can be correctly parsed """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())

        # This is a prepared ZIP file with UTF-8 filenames but without the UTF-8 filenames set,
        # like those that come from Todoist backups...
        # pylint: disable=line-too-long
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
        """ Tests that, if the server provides a backup ZIP file with the UTF-8 filename flag,
            the backup files can be correctly parsed """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer())

        # This is a prepared ZIP file with UTF-8 filenames and with the UTF-8 filenames set
        # pylint: disable=line-too-long
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

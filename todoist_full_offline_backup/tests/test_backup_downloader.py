#!/usr/bin/python3
""" Tests for the Todoist backup downloader class """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock
import io
import zipfile
from ..todoist_api import TodoistBackupInfo
from ..backup_downloader import TodoistBackupDownloader
from ..tracer import NullTracer
from .test_util_memory_vfs import InMemoryVfs

class TestBackupDownloader(unittest.TestCase):
    """ Tests for the Todoist backup downloader class """
    def setUp(self):
        """ Creates the sample instrastructure for the test """
        self.__backup = TodoistBackupInfo("2016-01-01 12:30", "http://www.example.com/backup.zip")

        empty_zip_bytes_io = io.BytesIO()
        with zipfile.ZipFile(empty_zip_bytes_io, "w") as _:
            pass
        empty_zip_bytes = empty_zip_bytes_io.getvalue()

        self.__urlmap = {"http://www.example.com/backup.zip": empty_zip_bytes}
        self.__fake_urldownloader = MagicMock(get=lambda url: self.__urlmap[url])


    def test_on_nonexisting_version_throws_exception(self):
        """ Tests that an exception is thrown when one attempts to download a backup
            that does not exist on the server """
        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer(), self.__fake_urldownloader)
        fake_backup = TodoistBackupInfo("123", "file:///this/path/does/not/exist/hopefully.zip")

        # Act/Assert
        self.assertRaises(Exception, backup_downloader.download, fake_backup, "/")

    def test_on_latest_version_and_existing_destination_doesnt_overwrite(self):
        """ Tests that if the backup already exists in the destination path,
            it is not overwriten """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer(), self.__fake_urldownloader)
        vfs = InMemoryVfs()
        vfs.write_file("test", b'testdata')

        # Act
        backup_downloader.download(self.__backup, vfs)

        # Assert
        self.assertEqual(vfs.file_list(), ["test"])
        self.assertEqual(vfs.read_file("test"), b'testdata')

    def test_on_zip_with_no_utf8_parses_utf8_filename(self):
        """ Tests that, if the server provides a backup ZIP file with no UTF-8 filename flag,
            it is patched to include it (since the Todoist servers provide ZIPs without it)
            and the backup files can be correctly parsed """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer(), self.__fake_urldownloader)
        vfs = InMemoryVfs()

        # This is a prepared ZIP file with UTF-8 filenames but without the UTF-8 filenames set,
        # like those that come from Todoist backups...
        # pylint: disable=line-too-long
        self.__urlmap = {"http://www.example.com/backup.zip": bytearray.fromhex(
            '504b03040a03000000000b90524c0000000000000000000000000d00000041534349494e414d452e747874' +
            '504b03040a03000000000f90524c00000000000000000000000014000000554e49434f44454e414d4520f09f92a92e747874' +
            '504b01023f030a03000000000b90524c0000000000000000000000000d0024000000000000002080a4810000000041534349494e414d452e7478740a0020000000000001001800005773f6d9a8d301005773f6d9a8d301005773f6d9a8d301' +
            '504b01023f030a03000000000f90524c000000000000000000000000140024000000000000002080a4812b000000554e49434f44454e414d4520f09f92a92e7478740a002000000000000100180080749ffad9a8d30180749ffad9a8d30180749ffad9a8d301' +
            '504b05060000000002000200c50000005d0000000000')}

        # Act
        backup_downloader.download(self.__backup, vfs)

        # Assert
        self.assertIn("ASCIINAME.txt", vfs.file_list())
        self.assertIn("UNICODENAME 💩.txt", vfs.file_list())

    def test_on_zip_with_utf8_flag_does_not_break(self):
        """ Tests that, if the server provides a backup ZIP file with the UTF-8 filename flag,
            the backup files can be correctly parsed """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer(), self.__fake_urldownloader)
        vfs = InMemoryVfs()

        # This is a prepared ZIP file with UTF-8 filenames and with the UTF-8 filenames set
        # pylint: disable=line-too-long
        self.__urlmap = {"http://www.example.com/backup.zip": bytearray.fromhex(
            '504b03040a03000800000b90524c0000000000000000000000000d00000041534349494e414d452e747874' +
            '504b03040a03000800000f90524c00000000000000000000000014000000554e49434f44454e414d4520f09f92a92e747874' +
            '504b01023f030a03000800000b90524c0000000000000000000000000d0024000000000000002080a4810000000041534349494e414d452e7478740a0020000000000001001800005773f6d9a8d301005773f6d9a8d301005773f6d9a8d301' +
            '504b01023f030a03000800000f90524c000000000000000000000000140024000000000000002080a4812b000000554e49434f44454e414d4520f09f92a92e7478740a002000000000000100180080749ffad9a8d30180749ffad9a8d30180749ffad9a8d301' +
            '504b05060000000002000200c50000005d0000000000')}

        # Act
        backup_downloader.download(self.__backup, vfs)

        # Assert
        self.assertIn("ASCIINAME.txt", vfs.file_list())
        self.assertIn("UNICODENAME 💩.txt", vfs.file_list())

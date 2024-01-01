#!/usr/bin/python3
""" Tests for the Todoist backup downloader class """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock
from full_offline_backup_for_todoist.backup_downloader import TodoistBackupDownloader
from full_offline_backup_for_todoist.tracer import NullTracer
from .test_util_memory_vfs import InMemoryVfs

class TestBackupDownloader(unittest.TestCase):
    """ Tests for the Todoist backup downloader class """
    def setUp(self):
        """ Creates the sample instrastructure for the test """
        self.__urlmap = {}
        self.__fake_urldownloader = MagicMock(get=lambda url: self.__urlmap[url])

    def test_on_existing_destination_doesnt_overwrite(self):
        """ Tests that if the backup already exists in the destination path,
            it is not overwriten """

        # Arrange
        backup_downloader = TodoistBackupDownloader(NullTracer(), self.__fake_urldownloader)
        vfs = InMemoryVfs()
        vfs.write_file("test", b'testdata')

        # Act
        backup_downloader.download(vfs)

        # Assert
        self.assertEqual(vfs.file_list(), ["test"])
        self.assertEqual(vfs.read_file("test"), b'testdata')

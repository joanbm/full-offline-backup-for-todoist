#!/usr/bin/python3
""" Tests for the Todoist backup + attachments downloader class """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock
import io
import csv
import json
from full_offline_backup_for_todoist.backup_attachments_downloader import (
    TodoistBackupAttachmentsDownloader)
from full_offline_backup_for_todoist.tracer import NullTracer
from .test_util_memory_vfs import InMemoryVfs

class TestTodoistBackupAttachmentsDownloader(unittest.TestCase):
    """ Tests for the Todoist backup + attachments downloader class """
    _TEST_CSV_FILE_NAME = "My Test [123456789].csv"

    _TEST_FILE_JPG_URL = "http://www.example.com/image.jpg"
    _TEST_FILE_JPG_BYTES = "it's a JPG"

    _TEST_ATTACHMENT_INI_URL = "http://www.example.com/file.ini"
    _TEST_ATTACHMENT_INI_BYTES = "it's an INI"

    def setUp(self):
        """ Creates the sample instrastructure for the test """
        self.__urlmap = {
            self._TEST_FILE_JPG_URL: self._TEST_FILE_JPG_BYTES.encode(),
            self._TEST_ATTACHMENT_INI_URL: self._TEST_ATTACHMENT_INI_BYTES.encode(),
        }
        self.__fake_urldownloader = MagicMock(get=lambda url: self.__urlmap[url])

    @staticmethod
    def __make_note_row(content):
        return ["note", f" [[file {json.dumps(content)}]]", "test"]

    def test_on_simple_download_downloads_attachments(self):
        """ Does a basic test with valid data to ensure attachments are downloaded """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "this_is_an_image.jpg",
            "file_url": self._TEST_FILE_JPG_URL
        }))

        vfs = InMemoryVfs()
        vfs.write_file(self._TEST_CSV_FILE_NAME, output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/this_is_an_image.jpg", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/this_is_an_image.jpg").decode(),
                         self._TEST_FILE_JPG_BYTES)

    def test_on_file_only_link_no_name_doesnt_crash_or_download_anything(self):
        """ Does a basic test with a note that contains a list
            (which is stored as a file, but without a file name or URL) """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "How to shoot on iPhone 7", "4"])
        writer.writerow(self.__make_note_row({
            "site_name": "Apple",
            "title": "How to shoot on iPhone - Photography",
            "url": "https://www.apple.com/iphone/photography-how-to/"
        }))

        vfs = InMemoryVfs()
        vfs.write_file(self._TEST_CSV_FILE_NAME, output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertEqual(vfs.file_list(), [self._TEST_CSV_FILE_NAME])

    def test_filename_with_slash_is_sanitized(self):
        """ Tests that a filename containing a slash in sanitized before ZIPing it
            (instead of failing or creating a subdirectory inside the ZIP file) """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "image.jpg",
            "file_url": self._TEST_FILE_JPG_URL
        }))

        writer.writerow(["task", "This is another random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "file.ini",
            "file_url": self._TEST_ATTACHMENT_INI_URL
        }))
        writer.writerow(["", "", ""])

        vfs = InMemoryVfs()
        vfs.write_file(self._TEST_CSV_FILE_NAME, output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/image.jpg", vfs.file_list())
        self.assertIn("attachments/file.ini", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/image.jpg").decode(), self._TEST_FILE_JPG_BYTES)
        self.assertEqual(vfs.read_file("attachments/file.ini").decode(),
                         self._TEST_ATTACHMENT_INI_BYTES)

    def test_on_download_with_already_downloaded_doesnt_overwrite(self):
        """ Does a test where an attachment has already been downloaded,
            to ensure it is not downloaded again """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "image.jpg",
            "file_url": self._TEST_FILE_JPG_URL
        }))

        vfs = InMemoryVfs()
        vfs.write_file(self._TEST_CSV_FILE_NAME, output.getvalue().encode())
        vfs.write_file("attachments/image.jpg", self._TEST_FILE_JPG_BYTES)
        vfs_mock = MagicMock(wraps=vfs)

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs_mock)

        # Assert
        self.assertEqual(vfs_mock.write_file.called, False)

    def test_on_download_with_colliding_names_renames_attachments(self):
        """ Does a test where there are multiple files with the same name,
            to ensure they are renamed in order not to collide in the filesystem """

        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "image.jpg",
            "file_url": self._TEST_FILE_JPG_URL
        }))

        writer.writerow(["task", "This is another random task", "4"])
        writer.writerow(self.__make_note_row({
            "file_type": "image/jpg",
            "file_name": "image.jpg",
            "file_url": self._TEST_ATTACHMENT_INI_URL
        }))
        writer.writerow(["", "", ""])

        vfs = InMemoryVfs()
        vfs.write_file(self._TEST_CSV_FILE_NAME, output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/image.jpg", vfs.file_list())
        self.assertIn("attachments/image_2.jpg", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/image.jpg").decode(), self._TEST_FILE_JPG_BYTES)
        self.assertEqual(vfs.read_file("attachments/image_2.jpg").decode(),
                         self._TEST_ATTACHMENT_INI_BYTES)

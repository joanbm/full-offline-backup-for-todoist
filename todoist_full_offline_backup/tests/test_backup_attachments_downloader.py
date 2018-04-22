#!/usr/bin/python3
""" Tests for the Todoist backup + attachments downloader class """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock
import io
import csv
import json
from ..backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from ..tracer import NullTracer
from .test_util_memory_vfs import InMemoryVfs

class TestTodoistBackupAttachmentsDownloader(unittest.TestCase):
    """ Tests for the Todoist backup + attachments downloader class """

    def setUp(self):
        """ Creates the sample instrastructure for the test """
        self.__urlmap = {
            "http://www.example.com/image.jpg": "it's a PNG".encode(),
            "http://www.example.com/file.ini": "it's a INI".encode(),
        }
        self.__fake_urldownloader = MagicMock(get=lambda url: self.__urlmap[url])

    def test_on_simple_download_downloads_attachments(self):
        """ Does a basic test with valid data to ensure attachments are downloaded """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(["note", " [[file {}]]".format(json.dumps({
            "file_type": "image/png",
            "file_name": "this/is/an/image.png",
            "file_url": "http://www.example.com/image.jpg"
        })), "test"])

        vfs = InMemoryVfs()
        vfs.write_file("My Test [123456789].csv", output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/this_is_an_image.png", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/this_is_an_image.png").decode(),
                         "it's a PNG")

    def test_filename_with_slash_is_sanitized(self):
        """ Tests that a filename containing a slash in sanitized before ZIPing it
            (instead of failing or creating a subdirectory inside the ZIP file) """
        # Arrange
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
        writer.writerow(["task", "This is a random task", "4"])
        writer.writerow(["note", " [[file {}]]".format(json.dumps({
            "file_type": "image/png",
            "file_name": "image.png",
            "file_url": "http://www.example.com/image.jpg"
        })), "test"])

        writer.writerow(["task", "This is another random task", "4"])
        writer.writerow(["note", " [[file {}]]".format(json.dumps({
            "file_type": "image/png",
            "file_name": "file.ini",
            "file_url": "http://www.example.com/file.ini"
        })), "test"])
        writer.writerow(["", "", ""])

        vfs = InMemoryVfs()
        vfs.write_file("My Test [123456789].csv", output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/image.png", vfs.file_list())
        self.assertIn("attachments/file.ini", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/image.png").decode(), "it's a PNG")
        self.assertEqual(vfs.read_file("attachments/file.ini").decode(), "it's a INI")

    def test_on_download_with_already_downloaded_doesnt_overwrite(self):
        """ Does a test where an attachment has already been downloaded,
            to ensure it is not downloaded again """
        # Arrange
        vfs_mock = MagicMock()
        vfs_mock.existed.return_value = True

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
        writer.writerow(["note", " [[file {}]]".format(json.dumps({
            "file_type": "image/png",
            "file_name": "image.png",
            "file_url": "http://www.example.com/image.jpg"
        })), "test"])

        writer.writerow(["task", "This is another random task", "4"])
        writer.writerow(["note", " [[file {}]]".format(json.dumps({
            "file_type": "image/png",
            "file_name": "image.png",
            "file_url": "http://www.example.com/file.ini"
        })), "test"])
        writer.writerow(["", "", ""])

        vfs = InMemoryVfs()
        vfs.write_file("My Test [123456789].csv", output.getvalue().encode())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(vfs)

        # Assert
        self.assertIn("attachments/image.png", vfs.file_list())
        self.assertIn("attachments/image_2.png", vfs.file_list())
        self.assertEqual(vfs.read_file("attachments/image.png").decode(), "it's a PNG")
        self.assertEqual(vfs.read_file("attachments/image_2.png").decode(), "it's a INI")

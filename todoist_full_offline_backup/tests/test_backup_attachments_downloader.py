#!/usr/bin/python3
""" Tests for the Todoist backup + attachments downloader class """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock
import tempfile
import shutil
import os
import io
import csv
import zipfile
import json
import hashlib
from pathlib import Path
from ..backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from ..tracer import NullTracer

class TestTodoistBackupAttachmentsDownloader(unittest.TestCase):
    """ Tests for the Todoist backup + attachments downloader class """

    def setUp(self):
        """ Creates the sample filesystem structure for the test """
        self.__test_dir = tempfile.mkdtemp()
        self.__zip_path = os.path.join(self.__test_dir, "input1.zip")

        self.__urlmap = {
            "http://www.example.com/image.jpg": "it's a PNG".encode(),
            "http://www.example.com/file.ini": "it's a INI".encode(),
        }
        self.__fake_urldownloader = MagicMock(get=lambda url: self.__urlmap[url])

    def tearDown(self):
        """ Destroys the sample filesystem structure for the test """
        shutil.rmtree(self.__test_dir)

    def test_on_simple_download_downloads_attachments(self):
        """ Does a basic test with valid data to ensure attachments are downloaded """
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
            writer.writerow(["task", "This is a random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "this/is/an/image.png",
                "file_url": "http://www.example.com/image.jpg"
            })), "test"])
            zip_file.writestr("My Test [123456789].csv", output.getvalue())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        with zipfile.ZipFile(self.__zip_path, 'r') as zip_file:
            self.assertIn("attachments/this_is_an_image.png", zip_file.namelist())
            self.assertEqual(zip_file.read("attachments/this_is_an_image.png").decode(),
                             "it's a PNG")

    def test_filename_with_slash_is_sanitized(self):
        """ Tests that a filename containing a slash in sanitized before ZIPing it
            (instead of failing or creating a subdirectory inside the ZIP file) """
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
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
            zip_file.writestr("My Test [123456789].csv", output.getvalue())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        with zipfile.ZipFile(self.__zip_path, 'r') as zip_file:
            self.assertIn("attachments/image.png", zip_file.namelist())
            self.assertIn("attachments/file.ini", zip_file.namelist())
            self.assertEqual(zip_file.read("attachments/image.png").decode(), "it's a PNG")
            self.assertEqual(zip_file.read("attachments/file.ini").decode(), "it's a INI")

    def test_on_download_with_already_downloaded_doesnt_overwrite(self):
        """ Does a test where an attachment has already been downloaded,
            to ensure it is not downloaded again """
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
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
            zip_file.writestr("My Test [123456789].csv", output.getvalue())
            zip_file.writestr("attachments/image.png", "it's a PNG (dummy data for the test MD5)")
            zip_file.writestr("attachments/file.ini", "it's a INI (dummy data for the test MD5)")

        original_hash = hashlib.md5(Path(self.__zip_path).read_bytes()).hexdigest()
        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        new_hash = hashlib.md5(Path(self.__zip_path).read_bytes()).hexdigest()
        self.assertEqual(original_hash, new_hash)

    def test_on_download_with_colliding_names_renames_attachments(self):
        """ Does a test where there are multiple files with the same name,
            to ensure they are renamed in order not to collide in the filesystem """

        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
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
            zip_file.writestr("My Test [123456789].csv", output.getvalue())

        backup_downloader = TodoistBackupAttachmentsDownloader(
            NullTracer(), self.__fake_urldownloader)

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        with zipfile.ZipFile(self.__zip_path, 'r') as zip_file:
            self.assertIn("attachments/image.png", zip_file.namelist())
            self.assertIn("attachments/image_2.png", zip_file.namelist())
            self.assertEqual(zip_file.read("attachments/image.png").decode(), "it's a PNG")
            self.assertEqual(zip_file.read("attachments/image_2.png").decode(), "it's a INI")

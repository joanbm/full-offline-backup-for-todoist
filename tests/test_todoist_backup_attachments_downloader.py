import unittest
import tempfile
import shutil
import os
import io
import csv
import zipfile
import json
import hashlib
from pathlib import Path
from todoist_api import TodoistBackupInfo
from todoist_backup_attachments_downloader import TodoistBackupAttachmentsDownloader
from tracer import NullTracer, ConsoleTracer

class TestTodoistBackupAttachmentsDownloader(unittest.TestCase):
    def setUp(self):
        # Create sample filesystem structure
        self.__test_dir = tempfile.mkdtemp()
        self.__attached_image_path = os.path.join(self.__test_dir, "image.jpg")
        self.__attached_file_path = os.path.join(self.__test_dir, "file.ini")
        Path(self.__attached_image_path).write_text("it's a PNG")
        Path(self.__attached_file_path).write_text("it's a INI")
        self.__zip_path = os.path.join(self.__test_dir, "input1.zip")

    def tearDown(self):
        # Destroy sample filesystem structure
        shutil.rmtree(self.__test_dir)

    def test_on_simple_download_downloads_attachments(self):
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
            writer.writerow(["task", "This is a random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "image.png",
                "file_url": "file://" + self.__attached_image_path
            })), "test"])

            writer.writerow(["task", "This is another random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "file.ini",
                "file_url": "file://" + self.__attached_file_path
            })), "test"])
            writer.writerow(["", "", ""])
            zip_file.writestr("My Test [123456789].csv", output.getvalue())

        backup_downloader = TodoistBackupAttachmentsDownloader(NullTracer())

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        with zipfile.ZipFile(self.__zip_path, 'r') as zip_file:
            self.assertIn("attachments/image.png", zip_file.namelist())
            self.assertIn("attachments/file.ini", zip_file.namelist())
            self.assertEqual(zip_file.read("attachments/image.png").decode('utf-8'), "it's a PNG")
            self.assertEqual(zip_file.read("attachments/file.ini").decode('utf-8'), "it's a INI")

    def test_on_download_with_already_downloaded_does_nothing(self):
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
            writer.writerow(["task", "This is a random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "image.png",
                "file_url": "file://" + self.__attached_image_path
            })), "test"])

            writer.writerow(["task", "This is another random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "file.ini",
                "file_url": "file://" + self.__attached_file_path
            })), "test"])
            writer.writerow(["", "", ""])
            zip_file.writestr("My Test [123456789].csv", output.getvalue())
            zip_file.writestr("attachments/image.png", "it's a PNG")
            zip_file.writestr("attachments/file.ini", "it's a INI")

        original_hash = hashlib.md5(Path(self.__zip_path).read_bytes()).hexdigest()
        backup_downloader = TodoistBackupAttachmentsDownloader(NullTracer())

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        new_hash = hashlib.md5(Path(self.__zip_path).read_bytes()).hexdigest()
        self.assertEqual(original_hash, new_hash)

    def test_on_download_with_colliding_names_renames_attachments(self):
        # Arrange
        with zipfile.ZipFile(self.__zip_path, 'w') as zip_file:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["TYPE", "CONTENT", "PRIORITY"])
            writer.writerow(["task", "This is a random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "image.png",
                "file_url": "file://" + self.__attached_image_path
            })), "test"])

            writer.writerow(["task", "This is another random task", "4"])
            writer.writerow(["note", " [[file {}]]".format(json.dumps({
                "file_type": "image/png",
                "file_name": "image.png",
                "file_url": "file://" + self.__attached_file_path
            })), "test"])
            writer.writerow(["", "", ""])
            zip_file.writestr("My Test [123456789].csv", output.getvalue())

        backup_downloader = TodoistBackupAttachmentsDownloader(NullTracer())

        # Act
        backup_downloader.download_attachments(self.__zip_path)

        # Assert
        with zipfile.ZipFile(self.__zip_path, 'r') as zip_file:
            self.assertIn("attachments/image.png", zip_file.namelist())
            self.assertIn("attachments/image_2.png", zip_file.namelist())
            self.assertEqual(zip_file.read("attachments/image.png").decode('utf-8'), "it's a PNG")
            self.assertEqual(zip_file.read("attachments/image_2.png").decode('utf-8'), "it's a INI")

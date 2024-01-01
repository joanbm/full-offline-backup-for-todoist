#!/usr/bin/python3
""" Tests for the VFS (Virtual FS) """
# pylint: disable=invalid-name
import unittest
import tempfile
import os
import zipfile
from full_offline_backup_for_todoist.virtual_fs import ZipVirtualFs

class Test(unittest.TestCase):
    """ Tests for the VFS (Virtual FS) """

    def setUp(self):
        """ Creates the temporary real directory for the test """

        # Move to a temp directory where the backup will be saved
        self.__test_dir = tempfile.mkdtemp()
        os.chdir(self.__test_dir)

    def test_on_zip_vfs_from_scratch_has_no_files(self):
        """ Tests that an newly-created VFS has no files """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act

            # Assert
            self.assertEqual(zvfs.existed(), False)
            self.assertEqual(zvfs.file_list(), [])

    def test_on_zip_vfs_read_nonexisting_throws_exception(self):
        """ Tests that trying to read a non-existing file throws an exception """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act/Assert
            self.assertRaises(Exception, zvfs.read_file, "non_existing.txt")

    def test_on_zip_vfs_write_new_is_written_and_can_be_read(self):
        """ Tests that a file can be written (and then read back) correctly """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act
            zvfs.write_file("test_file.txt", b"hello world")
            new_file_list = zvfs.file_list()
            new_file_content = zvfs.read_file("test_file.txt")

            # Act/Assert
            self.assertEqual(new_file_list, ["test_file.txt"])
            self.assertEqual(new_file_content, b"hello world")

    def test_on_zip_vfs_write_new_with_nonascii_chars_is_written_and_can_be_read(self):
        """ Tests that a file containing non-ASCII characters can be written
            (and then read back) correctly """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act
            zvfs.write_file("test_🦋.txt", b"hello world")

            # Act/Assert
            self.assertEqual(zvfs.file_list(), ["test_🦋.txt"])
            self.assertEqual(zvfs.read_file("test_🦋.txt"), b"hello world")

    def test_on_zip_vfs_write_file_in_folder_is_written_and_can_be_read(self):
        """ Tests that files can be written (and then read back) inside a folder correctly """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act
            zvfs.write_file("folder/test_file.txt", b"hello world")
            new_file_list = zvfs.file_list()
            new_file_content = zvfs.read_file("folder/test_file.txt")

            # Act/Assert
            self.assertEqual(new_file_list, ["folder/test_file.txt"])
            self.assertEqual(new_file_content, b"hello world")

    def test_on_zip_vfs_write_to_disk_is_written_using_path_hint(self):
        """ Tests that a VFS can be written from disk (ZIP) correctly """
        # Arrange
        with ZipVirtualFs(None) as zvfs:
            # Act
            zvfs.set_path_hint("testfile")
            zvfs.write_file("test_file.txt", b"hello world")

        # Assert
        with zipfile.ZipFile("./testfile.zip") as zipf:
            self.assertEqual(zipf.namelist(), ["test_file.txt"])
            self.assertEqual(zipf.read("test_file.txt"), b"hello world")

    def test_on_zip_vfs_read_from_disk(self):
        """ Tests that files can be read from disk (ZIP) correctly """
        # Arrange
        with zipfile.ZipFile("./testfile.zip", "w") as zipf:
            zipf.writestr("test_file.txt", b'hello world')

        # Act
        with ZipVirtualFs("testfile.zip") as zvfs:
            # Assert
            self.assertEqual(zvfs.existed(), True)
            self.assertEqual(zvfs.file_list(), ["test_file.txt"])
            self.assertEqual(zvfs.read_file("test_file.txt"), b"hello world")

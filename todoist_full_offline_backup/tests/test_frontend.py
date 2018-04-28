#!/usr/bin/python3
""" Tests for the console frontend """
# pylint: disable=invalid-name
import unittest
from unittest.mock import Mock, MagicMock, patch, ANY
import io
import tempfile
from ..frontend import ConsoleFrontend
from ..todoist_api import TodoistBackupInfo

class TestFrontend(unittest.TestCase):
    """ Tests for the console frontend """

    def test_on_list_backups_prints_list_to_console(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            backup1 = TodoistBackupInfo("BACKUP1", "file:///test1.zip")
            backup2 = TodoistBackupInfo("BACKUP2", "file:///test2.zip")
            backups = [backup1, backup2]

            controller = Mock(get_backups=lambda: (backups, backup2))
            frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

            # Act
            frontend.run("util", ["list", "--token", "1234"])

            # Assert
            self.assertRegex(mock_stdout.getvalue(), "BACKUP1")
            self.assertRegex(mock_stdout.getvalue(), "file:///test1.zip")
            self.assertRegex(mock_stdout.getvalue(), r"BACKUP2 \(LATEST\)")
            self.assertRegex(mock_stdout.getvalue(), "file:///test2.zip")

    def test_on_list_backups_with_token_from_file(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with tempfile.NamedTemporaryFile(delete=False) as tmpf:
                tmpf.write(b'1234')

                backup1 = TodoistBackupInfo("BACKUP1", "file:///test1.zip")
                backup2 = TodoistBackupInfo("BACKUP2", "file:///test2.zip")
                backups = [backup1, backup2]

                controller = Mock(get_backups=lambda: (backups, backup2))
                frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

                # Act
                frontend.run("util", ["list", "--token-file", tmpf.name])

                # Assert
                self.assertRegex(mock_stdout.getvalue(), "BACKUP1")
                self.assertRegex(mock_stdout.getvalue(), "file:///test1.zip")
                self.assertRegex(mock_stdout.getvalue(), r"BACKUP2 \(LATEST\)")
                self.assertRegex(mock_stdout.getvalue(), "file:///test2.zip")

    @staticmethod
    def test_on_download_version_calls_controller_with_that_version():
        """ Tests that when attempting to download an specific version of a backup,
            the corresponding method of the controller is called """

        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["download", "4321", "--token", "1234"])

        # Assert
        controller.download_version.assert_called_with("4321", ANY, with_attachments=False)

    @staticmethod
    def test_on_download_latest_version_calls_controller_latest_version():
        """ Tests that when attempting to download the latest backup,
            the corresponding method of the controller is called """
        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["download", "LATEST", "--token", "1234"])

        # Assert
        controller.download_latest.assert_called_with(ANY, with_attachments=False)

from frontend import ConsoleFrontend
import unittest
from unittest.mock import Mock, MagicMock, patch, ANY
import io
from todoist_api import TodoistBackupInfo

class TestFrontend(unittest.TestCase):
    def test_on_list_backups_prints_list_to_console(self):
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            backup1 = TodoistBackupInfo("BACKUP1", "file:///test1.zip")
            backup2 = TodoistBackupInfo("BACKUP2", "file:///test2.zip")
            backups = [backup1, backup2]

            controller = Mock(get_backups=lambda: (backups, backup2))
            frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

            # Act
            frontend.run("util", ["--token", "1234", "--list"])

            # Assert
            self.assertRegex(mock_stdout.getvalue(), "BACKUP1")
            self.assertRegex(mock_stdout.getvalue(), "file:///test1.zip")
            self.assertRegex(mock_stdout.getvalue(), r"BACKUP2 \(latest\)")
            self.assertRegex(mock_stdout.getvalue(), "file:///test2.zip")

    def test_on_download_version_calls_controller_with_that_version(self):
        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["--token", "1234", "--download-version", "4321"])

        # Assert
        controller.download_version.assert_called_with("4321", ANY)

    def test_on_download_latest_version_calls_controller_latest_version(self):
        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["--token", "1234", "--download-latest"])

        # Assert
        controller.download_latest.assert_called_with(ANY)

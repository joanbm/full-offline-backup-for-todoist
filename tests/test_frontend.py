#!/usr/bin/python3
""" Tests for the console frontend """
# pylint: disable=invalid-name
import unittest
from unittest.mock import Mock, MagicMock, ANY
from full_offline_backup_for_todoist.frontend import ConsoleFrontend

class TestFrontend(unittest.TestCase):
    """ Tests for the console frontend """

    @staticmethod
    def test_on_download_calls_controller():
        """ Tests that when attempting to download a backup (without attachments),
            the corresponding method of the controller is called """

        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["download"], {"TODOIST_TOKEN": "1234"})

        # Assert
        controller.download.assert_called_with(ANY, with_attachments=False)

    @staticmethod
    def test_on_download_with_attachments_calls_controller_with_attachments():
        """ Tests that when attempting to download a backup (with attachments),
            the corresponding method of the controller is called (with attachments) """
        # Arrange
        controller = MagicMock()
        frontend = ConsoleFrontend(Mock(return_value=controller), Mock())

        # Act
        frontend.run("util", ["download", "--with-attachments"],
                     {"TODOIST_TOKEN": "1234"})

        # Assert
        controller.download.assert_called_with(ANY, with_attachments=True)

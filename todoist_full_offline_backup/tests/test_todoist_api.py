#!/usr/bin/python3
""" Tests for the Todoist API wrapper """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock, ANY
import datetime
from ..todoist_api import TodoistApi
from ..tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    """ Tests for the Todoist API wrapper """

    def test_on_empty_json_returns_empty_list(self):
        """ Tests that when the operation to get the backups returns an empty JSON list,
            an empty list of backups is returned """
        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = "[]"

        # Act
        backups = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader).get_backups()

        # Assert
        self.assertEqual(len(backups), 0)

    def test_on_valid_json_returns_associated_backups(self):
        """ Tests that when the operation to get the backups returns a valid JSON list,
            the correct list of backups is returned """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = """[
            {"version":"2016-01-13 02:03","url":"https://www.example.com/1.zip"},
            {"version":"2016-01-12 06:03","url":"https://www.example.com/2.zip"}
        ]"""

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act
        backups = todoist_api.get_backups()

        # Assert
        self.assertEqual(len(backups), 2)
        self.assertEqual(backups[0].version, "2016-01-13 02:03")
        self.assertEqual(backups[0].version_date, datetime.datetime(2016, 1, 13, 2, 3))
        self.assertEqual(backups[0].url, "https://www.example.com/1.zip")

        self.assertEqual(backups[1].version, "2016-01-12 06:03")
        self.assertEqual(backups[1].version_date, datetime.datetime(2016, 1, 12, 6, 3))
        self.assertEqual(backups[1].url, "https://www.example.com/2.zip")

    @staticmethod
    def test_on_call_with_token_calls_download_with_token():
        """ Tests that the token is correctly URL encoded when using the Todoist API """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = "[]"

        todoist_api = TodoistApi("FAKE TOKEN", NullTracer(), mock_urldownloader)

        # Act
        todoist_api.get_backups()

        # Assert
        mock_urldownloader.get.assert_called_with(ANY, {'token': 'FAKE TOKEN'})

    def test_on_invalid_json_throws_exception(self):
        """ Tests that an exception is thrown when the Todoist API returns an invalid JSON """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = "["

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act/Assert
        self.assertRaises(Exception, todoist_api.get_backups)

    def test_on_http_fail_throws_exception(self):
        """ Tests that an exception is thrown on a HTTP error when using the Todoist API """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.side_effect = Exception('Test')

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act/Assert
        self.assertRaises(Exception, todoist_api.get_backups)

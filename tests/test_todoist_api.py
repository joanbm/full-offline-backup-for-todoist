#!/usr/bin/python3
""" Tests for the Todoist API wrapper """
# pylint: disable=invalid-name
import unittest
from unittest.mock import MagicMock, ANY
from full_offline_backup_for_todoist.todoist_api import TodoistApi
from full_offline_backup_for_todoist.tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    """ Tests for the Todoist API wrapper """

    def test_on_empty_projects_json_returns_empty_list(self):
        """ Tests that when the operation to get the projects returns an empty JSON list,
            an empty list of projects is returned """
        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = b'{"projects": []}'

        # Act
        projects = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader).get_projects()

        # Assert
        self.assertEqual(len(projects), 0)

    def test_on_valid_projects_json_returns_associated_projects(self):
        """ Tests that when the operation to get the projects returns a valid JSON list,
            the correct list of projects is returned """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = b"""{ "projects" : [
            { "id" : 2181147711, "name" : "Not Work" },
            { "id" : 2181147713, "name" : "Work" }
        ]}"""

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act
        projects = todoist_api.get_projects()

        # Assert
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].identifier, 2181147711)
        self.assertEqual(projects[0].name, "Not Work")

        self.assertEqual(projects[1].identifier, 2181147713)
        self.assertEqual(projects[1].name, "Work")

    @staticmethod
    def test_on_call_get_projects_with_token_calls_download_with_token():
        """ Tests that the token is correctly URL encoded when using the Todoist API """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = b'{"projects": []}'

        todoist_api = TodoistApi("FAKE TOKEN", NullTracer(), mock_urldownloader)

        # Act
        todoist_api.get_projects()

        # Assert
        mock_urldownloader.set_bearer_token.assert_called_with('FAKE TOKEN')
        mock_urldownloader.get.assert_called_with(ANY, {
            'sync_token': '*',
            'resource_types': '["projects"]'
        })

    def test_on_invalid_projects_json_throws_exception(self):
        """ Tests that an exception is thrown when the Todoist API returns an invalid JSON """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.return_value = b"["

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act/Assert
        self.assertRaises(Exception, todoist_api.get_projects)

    def test_on_projects_http_fail_throws_exception(self):
        """ Tests that an exception is thrown on a HTTP error when using the Todoist API """

        # Arrange
        mock_urldownloader = MagicMock()
        mock_urldownloader.get.side_effect = Exception('Test')

        todoist_api = TodoistApi("FAKE_TOKEN", NullTracer(), mock_urldownloader)

        # Act/Assert
        self.assertRaises(Exception, todoist_api.get_projects)

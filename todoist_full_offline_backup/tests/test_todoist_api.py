import unittest
import datetime
from unittest.mock import patch, Mock, ANY
from todoist_api import TodoistApi
from tracer import NullTracer

class TestTodoistApi(unittest.TestCase):
    def test_on_empty_json_returns_empty_list(self):
        # Arrange
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = Mock(read=lambda: "[]")
            todoist_api = TodoistApi("FAKE_TOKEN", NullTracer())

            # Act
            backups = TodoistApi("FAKE_TOKEN", NullTracer()).get_backups()

            # Assert
            self.assertEqual(len(backups), 0)

    def test_on_valid_json_returns_associated_backups(self):
        # Arrange
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = Mock(read=lambda: """[
                {"version":"2016-01-13 02:03","url":"https://www.example.com/1.zip"},
                {"version":"2016-01-12 06:03","url":"https://www.example.com/2.zip"}
            ]""")
            todoist_api = TodoistApi("FAKE_TOKEN", NullTracer())

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

    def test_on_call_with_token_calls_urllib_with_encoded_token(self):
        # Arrange
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = Mock(read=lambda: "[]")
            todoist_api = TodoistApi("FAKE TOKEN", NullTracer())

            # Act
            todoist_api.get_backups()

            # Assert
            mock_urlopen.assert_called_with(ANY, data=b'token=FAKE+TOKEN')

    def test_on_invalid_json_throws_exception(self):
        # Arrange
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value = Mock(read=lambda: "[")
            todoist_api = TodoistApi("FAKE_TOKEN", NullTracer())

            # Act/Assert
            self.assertRaises(Exception, todoist_api.get_backups)

    def test_on_http_fail_throws_exception(self):
        # Arrange
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Mock(side_effect=Exception('Test'))
            todoist_api = TodoistApi("FAKE_TOKEN", NullTracer())

            # Act/Assert
            self.assertRaises(Exception, todoist_api.get_backups)
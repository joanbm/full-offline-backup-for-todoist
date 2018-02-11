import unittest
import io
from unittest.mock import patch
from tracer import NullTracer, ConsoleTracer

class TestTracer(unittest.TestCase):
    def test_console_tracer_traces_to_console(self):
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Act
            ConsoleTracer().trace("this is a string")

            # Assert
            self.assertEqual(mock_stdout.getvalue().strip(), "this is a string")

    def test_null_tracer_doesnt_trace_to_console(self):
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Act
            NullTracer().trace("this is a string")

            # Assert
            self.assertEqual(mock_stdout.getvalue().strip(), "")
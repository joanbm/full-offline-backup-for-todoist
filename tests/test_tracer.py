#!/usr/bin/python3
""" Tests for the tracer classes """
# pylint: disable=invalid-name
import unittest
from unittest.mock import patch
import io
from full_offline_backup_for_todoist.tracer import NullTracer, ConsoleTracer

class TestTracer(unittest.TestCase):
    """ Tests for the tracer classes """

    def test_console_tracer_traces_to_console(self):
        """ Tests that the console tracer class traces the messages to the console """
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracer = ConsoleTracer()

            # Act
            tracer.trace("this is a string")

            # Assert
            self.assertEqual(mock_stdout.getvalue().strip(), "this is a string")

    def test_null_tracer_doesnt_trace_to_console(self):
        """ Tests that the null tracer class doesn't trace the messages to the console """
        # Arrange
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracer = NullTracer()

            # Act
            tracer.trace("this is a string")

            # Assert
            self.assertEqual(mock_stdout.getvalue().strip(), "")

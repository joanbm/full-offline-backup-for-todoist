#!/usr/bin/python3
""" Tests for the URL downloader """
# pylint: disable=invalid-name
import unittest
import time
import socket
import sys
from unittest.mock import patch
from full_offline_backup_for_todoist.url_downloader import URLLibURLDownloader
from full_offline_backup_for_todoist.tracer import NullTracer
from .test_util_static_http_request_handler import TestStaticHTTPServer

@patch.object(time, 'sleep', lambda secs: None) # For faster tests
class TestFrontend(unittest.TestCase):
    """ Tests for the URL downloader """

    def setUp(self):
        """ Creates the sample HTTP server for the test """

        # Set up a quick and dirty HTTP server
        route_responses = {
            ("GET", "/sample.txt", None, None):
                b"this is a sample",
            ("POST", "/sample.txt", b"param=value", None):
                b"this is a sample with a parameter",
        }

        self.__httpd = TestStaticHTTPServer(("127.0.0.1", 33327), route_responses)
        self.__flaky_httpd = TestStaticHTTPServer(("127.0.0.1", 33328), route_responses, True)

    def tearDown(self):
        """ Destroys the sample HTTP server for the test """
        self.__httpd.shutdown()
        self.__flaky_httpd.shutdown()

    def test_urldownloader_can_download_local_file(self):
        """ Tests that the downloader can successfully download an existing file """
        # Arrange
        urldownloader = URLLibURLDownloader(NullTracer())

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt")

        # Assert
        self.assertEqual(data.decode(), "this is a sample")

    def test_urldownloader_can_retry(self):
        """ Tests that the downloader can successfully retry downloading a file from a
            flaky server which may occasionally fail """
        # Arrange
        urldownloader = URLLibURLDownloader(NullTracer())

        # Act
        data = urldownloader.get("http://127.0.0.1:33328/sample.txt")

        # Assert
        self.assertEqual(data.decode(), "this is a sample")

    def test_urldownloader_can_pass_request_params(self):
        """ Tests that the downloader can successfully download an existing file,
            passing parameters in the URL """
        # Arrange
        urldownloader = URLLibURLDownloader(NullTracer())

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt", {'param': 'value'})

        # Assert
        self.assertEqual(data.decode(), "this is a sample with a parameter")

    def test_urldownloader_throws_on_not_found(self):
        """ Tests that the downloader raises an exception on a non-existing file """
        # Arrange
        urldownloader = URLLibURLDownloader(NullTracer())

        # Act/Assert
        self.assertRaises(Exception, urldownloader.get, "http://127.0.0.1:33327/notfound.txt")

    def test_urldownloader_throws_on_timeout(self):
        """ Tests that the downloader raises an exception on a non-existing file """
        # Arrange
        urldownloader = URLLibURLDownloader(NullTracer(), 0.3)

        # Act/Assert
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 33329))
            s.listen()
            # See https://docs.python.org/3/whatsnew/3.10.html#socket
            exception = TimeoutError if sys.version_info >= (3, 10) else socket.timeout
            self.assertRaises(exception, urldownloader.get, "http://127.0.0.1:33329")

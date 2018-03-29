#!/usr/bin/python3
""" Tests for the URL downloader """
# pylint: disable=invalid-name
import unittest
from .test_util_static_http_request_handler import TestStaticHTTPServer
from ..url_downloader import URLLibURLDownloader

class TestFrontend(unittest.TestCase):
    """ Tests for the URL downloader """

    def setUp(self):
        """ Creates the sample HTTP server for the test """

        # Set up a quick and dirty HTTP server
        route_responses = {
            "/sample.txt": "this is a sample".encode("utf-8"),
            "/sample.txt?param=value": "this is a sample with a parameter".encode("utf-8"),
        }

        self.__httpd = TestStaticHTTPServer(("127.0.0.1", 33327), route_responses)

    def tearDown(self):
        """ Destroys the sample HTTP server for the test """
        self.__httpd.shutdown()

    def test_urldownloader_can_download_local_file(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        urldownloader = URLLibURLDownloader()

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt")

        # Assert
        self.assertEqual(data.decode(), "this is a sample")

    def test_urldownloader_can_pass_request_params(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        urldownloader = URLLibURLDownloader()

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt", {'param': 'value'})

        # Assert
        self.assertEqual(data.decode(), "this is a sample with a parameter")

    def test_urldownloader_throws_on_not_found(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        urldownloader = URLLibURLDownloader()

        # Act/Assert
        self.assertRaises(Exception, urldownloader.get, "http://127.0.0.1:33327/notfound.txt")

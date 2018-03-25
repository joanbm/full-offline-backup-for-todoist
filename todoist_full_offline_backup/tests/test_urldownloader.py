#!/usr/bin/python3
""" Tests for the URL downloader """
# pylint: disable=invalid-name
import unittest
from pathlib import Path
import tempfile
import http.server
import socketserver
import os
import threading
import shutil
from ..url_downloader import URLLibURLDownloader

class TestTCPServer(socketserver.TCPServer):
    """ TCP server, which stores the last requested URL path (for assertions on it) """

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super(TestTCPServer, self).__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.last_requested_path = None

class TestHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """ HTTP Request handler, which stores the last requested URL path (for assertions on it) """

    # pylint: disable=redefined-builtin
    def log_message(self, format, *args):
        # Disable console logging
        pass

    def do_GET(self):
        self.server.last_requested_path = self.path
        return super(TestHTTPRequestHandler, self).do_GET()

class TestFrontend(unittest.TestCase):
    """ Tests for the URL downloader """

    def setUp(self):
        """ Creates the sample filesystem structure and HTTP server for the test """
        self.__test_dir = tempfile.mkdtemp()
        self.__sample_file = os.path.join(self.__test_dir, "sample.txt")
        Path(self.__sample_file).write_text("this is a sample")

        # Set up a quick and dirty HTTP server
        os.chdir(self.__test_dir)
        socketserver.TCPServer.allow_reuse_address = True
        self.__httpd = TestTCPServer(("", 33327), TestHTTPRequestHandler)
        self.__httpd_thread = threading.Thread(target=self.__httpd.serve_forever)
        self.__httpd_thread.start()

    def tearDown(self):
        """ Destroys the sample filesystem structure and HTTP server for the test """
        self.__httpd.shutdown()
        self.__httpd_thread.join()
        self.__httpd.server_close()

        shutil.rmtree(self.__test_dir)

    def test_urldownloader_can_download_local_file(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        urldownloader = URLLibURLDownloader()

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt")

        # Assert
        self.assertEqual(self.__httpd.last_requested_path, "/sample.txt")
        self.assertEqual(data.decode(), "this is a sample")

    def test_urldownloader_can_pass_request_params(self):
        """ Tests that the list backups operation prints the list of backups to the console """
        # Arrange
        urldownloader = URLLibURLDownloader()

        # Act
        data = urldownloader.get("http://127.0.0.1:33327/sample.txt", {'param': 'value'})

        # Assert
        self.assertEqual(self.__httpd.last_requested_path, "/sample.txt?param=value")
        self.assertEqual(data.decode(), "this is a sample")

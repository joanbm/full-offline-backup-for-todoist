#!/usr/bin/python3
""" Static mapping HTTP Server for the tests """
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class TestStaticHTTPServer:
    """ Static mapping HTTP Server for the tests """
    def __init__(self, server_address, route_responses):
        handler = TestStaticHTTPServer.make_test_http_request_handler(route_responses)
        self.__httpd = HTTPServer(server_address, handler)
        self.__httpd_thread = threading.Thread(target=self.__httpd.serve_forever)
        self.__httpd_thread.start()

    def shutdown(self):
        """ Destroys the sample HTTP server for the test """
        self.__httpd.shutdown()
        self.__httpd_thread.join()
        self.__httpd.server_close()

    @staticmethod
    def make_test_http_request_handler(route_responses):
        """ Creates an HTTP Request Handler class with a static
            route mapping defined by the given parameter. """

        class TestHTTPRequestHandler(BaseHTTPRequestHandler):
            """ Static HTTP Request Handler class for the tests """

            def log_message(self, format, *args): # pylint: disable=redefined-builtin
                """ Disables console output for the HTTP Request Handler """

            def do_GET(self): # pylint: disable=invalid-name
                """ Handles a request using the defined static mapping """
                self.send_response(200 if self.path in route_responses else 404)

                self.send_header('Content-type', 'text/plain')
                self.end_headers()

                if self.path in route_responses:
                    self.wfile.write(route_responses[self.path])

        return TestHTTPRequestHandler

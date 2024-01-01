#!/usr/bin/python3
""" Static mapping HTTP Server for the tests """
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class TestStaticHTTPServer:
    """ Static mapping HTTP Server for the tests """
    def __init__(self, server_address, route_responses, flaky=False):
        handler = TestStaticHTTPServer.make_test_http_request_handler(route_responses, flaky)
        self.__httpd = HTTPServer(server_address, handler)
        self.__httpd_thread = threading.Thread(target=self.__httpd.serve_forever,
                                               # Use a lower value for faster shutdown on tests
                                               kwargs={"poll_interval": 0.05})
        self.__httpd_thread.start()
        self._handled = set()

    def shutdown(self):
        """ Destroys the sample HTTP server for the test """
        self.__httpd.shutdown()
        self.__httpd_thread.join()
        self.__httpd.server_close()

    @staticmethod
    def make_test_http_request_handler(route_responses, flaky):
        """ Creates an HTTP Request Handler class with a static
            route mapping defined by the given parameter. """
        handled = set()

        class TestHTTPRequestHandler(BaseHTTPRequestHandler):
            """ Static HTTP Request Handler class for the tests """
            def log_message(self, format, *args): # pylint: disable=redefined-builtin
                """ Disables console output for the HTTP Request Handler """

            def __find_response_for_request_key(self, request_key):
                authorization_header = self.headers.get('Authorization')
                if authorization_header is not None and authorization_header.startswith("Bearer "):
                    token = authorization_header[len("Bearer "):]
                    key_with_auth = request_key + (token,)
                    if key_with_auth in route_responses:
                        return route_responses[key_with_auth]

                key_without_auth = request_key + (None,)
                return route_responses.get(key_without_auth)

            def __handle_request(self, request_key):
                if flaky and self.path not in handled:
                    handled.add(self.path)
                    self.send_response(503)
                    self.end_headers()
                    return

                response = self.__find_response_for_request_key(request_key)
                self.send_response(200 if response else 404)

                self.send_header('Content-type', 'text/plain')
                self.end_headers()

                if response:
                    self.wfile.write(response)

            def do_GET(self): # pylint: disable=invalid-name
                """ Handles a GET request using the defined static mapping """
                self.__handle_request(('GET', self.path, None))

            def do_POST(self): # pylint: disable=invalid-name
                """ Handles a POST request using the defined static mapping """
                body_length = int(self.headers.get('Content-Length'))
                body = self.rfile.read(body_length)
                self.__handle_request(('POST', self.path, body))

        return TestHTTPRequestHandler

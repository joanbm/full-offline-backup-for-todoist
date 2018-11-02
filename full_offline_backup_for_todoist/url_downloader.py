#!/usr/bin/python3
""" Implementation of a class to download the contents of an URL """
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import http.cookiejar

class URLDownloader(object, metaclass=ABCMeta):
    """ Implementation of a class to download the contents of an URL """

    @abstractmethod
    def get(self, url, data=None):
        """ Download the contents of the specified URL with a GET request.
            You can specify any additional data parameters to pass to the destination. """

class URLLibURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib """

    def get(self, url, data=None):
        real_url = url
        if data is not None:
            real_url += "?" + urllib.parse.urlencode(data)

        with urllib.request.urlopen(real_url) as url_handle:
            return url_handle.read()

class TodoistAuthURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib,
        authenticating before with Todoist's servers using a username/password """

    URL_SHOWLOGIN='https://todoist.com/Users/showLogin'
    URL_POSTLOGIN='https://todoist.com/Users/login'
    URL_FILE_TO_DOWNLOAD="https://files.todoist.com/VxxTiO9w6TCd_gHiHxpovh3oLL71OllvLxXFgv70jhxJkMSuu6veoX7fVnasbZpc/by/15956439/as/IMG_3285.JPG"

    LOGIN_PARAM_CSRF="csrf"
    LOGIN_PARAM_EMAIL="email"
    LOGIN_PARAM_PASSWORD="password"

    def __init__(self, tracer, email, password):
        self.__tracer = tracer
        self.__email = email
        self.__password = password
        self.__opener = None

    def get(self, url, data=None):
        if self.__opener is None:
            # Set up a cookie jar, to gather the login's cookies
            cookiejar = http.cookiejar.CookieJar()
            cookie_process = urllib.request.HTTPCookieProcessor(cookiejar)
            self.__opener = urllib.request.build_opener(cookie_process)

            self.__tracer.trace("Auth Step 1: Get CSRF token")

            # Ping the login page, in order to get a CSRF token as a cookie
            with self.__opener.open(TodoistAuthURLDownloader.URL_SHOWLOGIN) as get_csrf_response:
                pass

            self.__tracer.trace("Auth Step 2: Building login request params")

            # Build the parameters (CSRF, email and password) for the login POST request
            csrf_value = next(c.value for c in cookiejar if c.name == TodoistAuthURLDownloader.LOGIN_PARAM_CSRF)
            params = {
                TodoistAuthURLDownloader.LOGIN_PARAM_CSRF: csrf_value,
                TodoistAuthURLDownloader.LOGIN_PARAM_EMAIL: self.__email,
                TodoistAuthURLDownloader.LOGIN_PARAM_PASSWORD: self.__password}
            params_str = urllib.parse.urlencode(params).encode('utf-8')

            self.__tracer.trace("Auth Step 3: Send login request")

            # Send the login POST request, which will give us our identifier cookie
            with self.__opener.open(TodoistAuthURLDownloader.URL_POSTLOGIN, params_str) as login_response:
                pass

            self.__tracer.trace("Auth completed")

        real_url = url
        if data is not None:
            real_url += "?" + urllib.parse.urlencode(data)

        self.__tracer.trace("Downloading URL: {}".format(real_url))
        with self.__opener.open(real_url) as url_handle:
            return url_handle.read()

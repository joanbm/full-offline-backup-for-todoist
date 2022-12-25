#!/usr/bin/python3
""" Implementation of a class to download the contents of an URL """
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import http.cookiejar
import time
from typing import cast, Dict, Optional
from .tracer import Tracer

NUM_RETRIES = 3

class URLDownloader(metaclass=ABCMeta):
    """ Implementation of a class to download the contents of an URL """

    _tracer: Tracer

    def __init__(self, tracer: Tracer):
        self._tracer = tracer

    def _download(self, opener: urllib.request.OpenerDirector, url: str) -> bytes:
        """ Downloads the specified URL as bytes using the specified opener """
        with opener.open(url) as url_handle:
            return cast(bytes, url_handle.read())

    def _download_with_retry(self, opener: urllib.request.OpenerDirector, url: str) -> bytes:
        """ Downloads the specified URL as bytes using the specified opener, retrying on failure """
        for i in range(NUM_RETRIES):
            try:
                return self._download(opener, url)
            except urllib.error.URLError as exception:
                self._tracer.trace(f"Got exception: {exception}, retrying...")
                time.sleep(3**i)

        return self._download(opener, url)

    @abstractmethod
    def get(self, url: str, data: Optional[Dict[str, str]]=None) -> bytes:
        """ Download the contents of the specified URL with a GET request.
            You can specify any additional data parameters to pass to the destination. """

    @staticmethod
    def _build_opener_with_app_useragent(
        *handlers: urllib.request.BaseHandler) -> urllib.request.OpenerDirector:
        opener = urllib.request.build_opener(*handlers)
        opener.addheaders = [('User-agent', 'full-offline-backup-for-todoist')]
        return opener

class URLLibURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib """

    def get(self, url: str, data: Optional[Dict[str, str]]=None) -> bytes:
        real_url = url
        if data:
            real_url += "?" + urllib.parse.urlencode(data)

        opener = self._build_opener_with_app_useragent()
        return self._download_with_retry(opener, real_url)

class TodoistAuthURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib,
        authenticating before with Todoist's servers using a username/password """

    URL_SHOWLOGIN = 'https://todoist.com/Users/showLogin'
    URL_POSTLOGIN = 'https://todoist.com/Users/login'

    LOGIN_PARAM_CSRF = "csrf"
    LOGIN_PARAM_EMAIL = "email"
    LOGIN_PARAM_PASSWORD = "password"

    __email: str
    __password: str
    __opener: Optional[urllib.request.OpenerDirector]

    def __init__(self, tracer: Tracer, email: str, password: str):
        super().__init__(tracer)
        self.__email = email
        self.__password = password
        self.__opener = None

    def get(self, url: str, data: Optional[Dict[str, str]]=None) -> bytes:
        if not self.__opener:
            # Set up a cookie jar, to gather the login's cookies
            cookiejar = http.cookiejar.CookieJar()
            cookie_process = urllib.request.HTTPCookieProcessor(cookiejar)
            self.__opener = self._build_opener_with_app_useragent(cookie_process)

            self._tracer.trace("Auth Step 1: Get CSRF token")

            # Ping the login page, in order to get a CSRF token as a cookie
            with self.__opener.open(TodoistAuthURLDownloader.URL_SHOWLOGIN) as _:
                pass

            self._tracer.trace("Auth Step 2: Building login request params")

            # Build the parameters (CSRF, email and password) for the login POST request
            csrf_value = next(c.value for c in cookiejar
                              if c.name == TodoistAuthURLDownloader.LOGIN_PARAM_CSRF)
            params = {
                TodoistAuthURLDownloader.LOGIN_PARAM_CSRF: csrf_value,
                TodoistAuthURLDownloader.LOGIN_PARAM_EMAIL: self.__email,
                TodoistAuthURLDownloader.LOGIN_PARAM_PASSWORD: self.__password}
            params_str = urllib.parse.urlencode(params).encode('utf-8')

            self._tracer.trace("Auth Step 3: Send login request")

            # Send the login POST request, which will give us our identifier cookie
            with self.__opener.open(TodoistAuthURLDownloader.URL_POSTLOGIN, params_str) as _:
                pass

            self._tracer.trace("Auth completed")

        real_url = url
        if data:
            real_url += "?" + urllib.parse.urlencode(data)

        return self._download_with_retry(self.__opener, real_url)

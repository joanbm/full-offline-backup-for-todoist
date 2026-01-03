#!/usr/bin/python3
""" Implementation of a class to download the contents of an URL """
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import time
from typing import cast, Dict, Optional, NamedTuple
from .tracer import Tracer

NUM_RETRIES = 3

class _Request(NamedTuple):
    url: str
    method: str
    params: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, str]] = None

class URLDownloaderException(Exception):
    """ Thrown when the download of an URL fails """

class URLDownloader(metaclass=ABCMeta):
    """ Implementation of a class to download the contents of an URL """

    _tracer: Tracer
    _bearer_token: Optional[str]

    def __init__(self, tracer: Tracer, timeout: int = 300):
        self._tracer = tracer
        self._timeout = timeout
        self._bearer_token = None

    def set_bearer_token(self, bearer_token: Optional[str]) -> None:
        """ Sets the value of the 'Authorization: Bearer XXX' HTTP header """
        self._bearer_token = bearer_token

    @abstractmethod
    def _download(self, request: _Request) -> bytes:
        """ Download the contents of the specified URL with the specified request. """

    def get(self, url: str, params: Optional[Dict[str, str]] = None) -> bytes:
        """ Download the contents of the specified URL with a GET request.
            You can specify additional data to pass as URL query parameters. """
        return self._download(_Request(url=url, method='GET', params=params))

    def post(self, url: str, data: Optional[Dict[str, str]] = None) -> bytes:
        """ Download the contents of the specified URL with a POST request.
            You can specify additional data to pass as a form-encoded body. """
        return self._download(_Request(url=url, method='POST', data=data))

class URLLibURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib """

    def _download_once(self, opener: urllib.request.OpenerDirector, request: _Request) -> bytes:
        try:
            encoded_params = urllib.parse.urlencode(request.params) if request.params else None
            encoded_url = f"{request.url}?{encoded_params}" if encoded_params else request.url
            encoded_data = urllib.parse.urlencode(request.data).encode() if request.data else None
            with opener.open(encoded_url, encoded_data, self._timeout) as url_handle:
                return cast(bytes, url_handle.read())
        except urllib.error.HTTPError as exception:
            # urllib.error.HTTPError contains a file-like object and needs to be closed, see:
            # - https://github.com/pytest-dev/pytest/issues/13308
            # - https://docs.python.org/3.14/library/urllib.error.html
            # Closing it avoids a ResourceWarning on e.g. Python 3.14.2.
            with exception:
                raise URLDownloaderException(exception.reason) from exception
        except urllib.error.URLError as exception:
            raise URLDownloaderException(exception.reason) from exception


    def _download(self, request: _Request) -> bytes:
        opener = self._build_opener_with_app_useragent()
        for i in range(NUM_RETRIES):
            try:
                return self._download_once(opener, request)
            except URLDownloaderException as exception:
                self._tracer.trace(f"Got exception: {exception}, retrying...")
                time.sleep(3**i)

        return self._download_once(opener, request)

    def _build_opener_with_app_useragent(
        self, *handlers: urllib.request.BaseHandler) -> urllib.request.OpenerDirector:
        opener = urllib.request.build_opener(*handlers)
        opener.addheaders = ([('User-agent', 'full-offline-backup-for-todoist')] +
            ([('Authorization', 'Bearer ' + self._bearer_token)] if self._bearer_token else []))
        return opener

#!/usr/bin/python3
""" Implementation of a class to download the contents of an URL """
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import time
from typing import cast, Dict, Optional
from .tracer import Tracer

NUM_RETRIES = 3

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
    def get(self, url: str, data: Optional[Dict[str, str]]=None) -> bytes:
        """ Download the contents of the specified URL with a GET request.
            You can specify any additional data parameters to pass to the destination. """

class URLLibURLDownloader(URLDownloader):
    """ Implementation of a class to download the contents of an URL through URLLib """

    def _download(self, opener: urllib.request.OpenerDirector, url: str,
                  data: Optional[Dict[str, str]]=None) -> bytes:
        """ Downloads the specified URL as bytes using the specified opener """
        encoded_data = urllib.parse.urlencode(data).encode() if data else None
        with opener.open(url, encoded_data, self._timeout) as url_handle:
            return cast(bytes, url_handle.read())

    def _download_with_retry(self, opener: urllib.request.OpenerDirector, url: str,
                             data: Optional[Dict[str, str]]=None) -> bytes:
        """ Downloads the specified URL as bytes using the specified opener, retrying on failure """
        for i in range(NUM_RETRIES):
            try:
                return self._download(opener, url, data)
            except urllib.error.URLError as exception:
                self._tracer.trace(f"Got exception: {exception}, retrying...")
                time.sleep(3**i)

        return self._download(opener, url, data)

    def _build_opener_with_app_useragent(
        self, *handlers: urllib.request.BaseHandler) -> urllib.request.OpenerDirector:
        opener = urllib.request.build_opener(*handlers)
        opener.addheaders = ([('User-agent', 'full-offline-backup-for-todoist')] +
            ([('Authorization', 'Bearer ' + self._bearer_token)] if self._bearer_token else []))
        return opener

    def get(self, url: str, data: Optional[Dict[str, str]]=None) -> bytes:
        opener = self._build_opener_with_app_useragent()
        return self._download_with_retry(opener, url, data)

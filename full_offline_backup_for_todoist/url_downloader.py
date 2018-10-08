#!/usr/bin/python3
""" Implementation of a class to download the contents of an URL """
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse

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

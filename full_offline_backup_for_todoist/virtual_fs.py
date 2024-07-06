#!/usr/bin/python3
""" Definitions and implementations of a simple logging / tracing method """
from abc import ABCMeta, abstractmethod
import os.path
import io
import zipfile
from pathlib import Path
from types import TracebackType
from typing import IO, List, Optional, Type

class VirtualFs(metaclass=ABCMeta):
    """ An abstract layer over the filesystem
        (e.g. can represent a real folder, a ZIP file, etc.) """

    @abstractmethod
    def set_path_hint(self, dst_path: str) -> None:
        """ Sets the associated physical path of this filesystem (if possible) """

    @abstractmethod
    def existed(self) -> bool:
        """ Checks if the filesystem previously existed, or is newly created """

    @abstractmethod
    def file_list(self) -> List[str]:
        """ Gets the list of files in this virtual file system """

    @abstractmethod
    def read_file(self, file_path: str) -> bytes:
        """ Reads a file from this virtual file system """

    @abstractmethod
    def write_file(self, file_path: str, file_data: bytes) -> None:
        """ Adds a file to the filesystem """

class ZipVirtualFs(VirtualFs):
    """ Represents a virtual filesystem over a ZIP file """
    src_path: Optional[str]
    dst_path: Optional[str]
    _zip_file: Optional[zipfile.ZipFile]
    _backing_storage: Optional[IO[bytes]]

    def __init__(self, src_path: str):
        self.src_path = src_path
        self.dst_path = src_path
        self._zip_file = None
        self._backing_storage = None

    def __enter__(self) -> VirtualFs: # Type should be Self, but isn't well supported on old Python
        if self.src_path and os.path.isfile(self.src_path) and zipfile.is_zipfile(self.src_path):
            self._backing_storage = open(self.src_path, "ab+")
        else:
            self._backing_storage = io.BytesIO()

        self._zip_file = zipfile.ZipFile(self._backing_storage, 'a')

        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        if self._zip_file:
            self._zip_file.close()
            self._zip_file = None

        if self._backing_storage:
            if not exc_value and isinstance(self._backing_storage, io.BytesIO) and self.dst_path:
                Path(self.dst_path).write_bytes(self._backing_storage.getvalue())
            self._backing_storage.close()
            self._backing_storage = None

    def set_path_hint(self, dst_path: str) -> None:
        if not self.dst_path:
            self.dst_path = os.path.join(".", dst_path + ".zip")

    def existed(self) -> bool:
        assert self._backing_storage
        return not isinstance(self._backing_storage, io.BytesIO)

    def file_list(self) -> List[str]:
        assert self._zip_file
        return self._zip_file.namelist()

    def read_file(self, file_path: str) -> bytes:
        assert self._zip_file
        return self._zip_file.read(file_path)

    def write_file(self, file_path: str, file_data: bytes) -> None:
        assert self._zip_file
        self._zip_file.writestr(file_path, file_data)

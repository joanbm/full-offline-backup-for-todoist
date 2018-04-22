#!/usr/bin/python3
""" Class to download Todoist backup ZIPs using the Todoist API """
import zipfile
import io
from .utils import sanitize_file_name

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """
    __ZIP_FLAG_BITS_UTF8 = 0x800

    def __init__(self, tracer, urldownloader):
        self.__tracer = tracer
        self.__urldownloader = urldownloader

    def download(self, backup, vfs):
        """ Downloads the specified backup to the specified folder """
        self.__tracer.trace("Downloading backup with version '{}'".format(backup.version))

        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        vfs.set_path_hint(sanitize_file_name("TodoistBackup_" + backup.version))

        # Download the file
        if vfs.existed():
            self.__tracer.trace("File already downloaded... skipping")
            return

        self.__tracer.trace("Downloading from {}...".format(
            backup.url))
        raw_zip_bytes = self.__urldownloader.get(backup.url)
        with zipfile.ZipFile(io.BytesIO(raw_zip_bytes), "r") as zipf:
            for info in zipf.infolist():
                # Todoist backup ZIPs may contain filenames encoded in UTF-8, but they will not
                # actually have the UTF-8 filename flag set in the ZIP file.
                # This causes some ZIP parsers, such as Python's own parser, to consider the
                # file names in the legacy CP-437 format.
                # To fix this, let's re-encode the filenames in CP-437 to get the original
                # bytes back, then properly decode them to UTF-8.
                if info.flag_bits & self.__ZIP_FLAG_BITS_UTF8:
                    encoding_file_name = info.filename
                else:
                    encoding_file_name = info.filename.encode('cp437').decode("utf-8")

                vfs.write_file(encoding_file_name, zipf.read(info.filename))

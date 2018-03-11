#!/usr/bin/python3
""" Class to download Todoist backup ZIPs using the Todoist API """
import os
import urllib.request
import zipfile
from pathlib import Path
import struct
from .utils import sanitize_file_name

class TodoistBackupDownloader:
    """ Class to download Todoist backup ZIPs using the Todoist API """
    __ZIP_FLAG_BITS_UTF8 = 0x800

    def __init__(self, tracer):
        self.__tracer = tracer

    def __fixup_zip_utf8_flags(self, backup_zip_path):
        """ Todoist backup ZIPs may contain filenames encoded in UTF-8, but they will not
            actually have the UTF-8 filename flag set in the ZIP file.
            This causes some ZIP parsers, such as Python's own parser, to consider the
            file names in the legacy CP-437 format.
            To fix this, we add the flag ourselves after downloading the ZIP. """
        self.__tracer.trace("Fixing ZIP UTF-8 flags of '{}'...".format(backup_zip_path))

        # Read the ZIP into a byte array in order to patch it...
        # since Python's zipfile can't update the file without rebuilding
        # it all from scratch
        zipbytes = bytearray(Path(backup_zip_path).read_bytes())
        modified = False

        with zipfile.ZipFile(backup_zip_path, 'r') as zip_file:
            for z_i in zip_file.infolist():
                # If the flag is already set, nothing to do
                if z_i.flag_bits & TodoistBackupDownloader.__ZIP_FLAG_BITS_UTF8:
                    self.__tracer.trace("Local header @{} already OK".format(
                        hex(z_i.header_offset)))
                    continue

                modified = True

                # Patch the bits in the local file header. This is pretty easy,
                # since zipfile tells us where it starts
                self.__tracer.trace("Patching local header @{}".format(hex(z_i.header_offset)))
                orig_local_flags = struct.unpack_from("<h", zipbytes, z_i.header_offset+6)[0]
                struct.pack_into("<h", zipbytes, z_i.header_offset+6,
                                 orig_local_flags | TodoistBackupDownloader.__ZIP_FLAG_BITS_UTF8)

                # Patch the bits in the central file header. This is tricky,
                # because Python doesn't tell us where it is!
                # To avoid having parse the whole ZIP (which is a freaking mess),
                # we build the part of the file that we have to patch from Python's data,
                # and then find it in the actual file. This is very inefficient,
                # but at least, it shouldn't fail under normal circumstances...
                dosdate = (z_i.date_time[0] - 1980) << 9 | z_i.date_time[1] << 5 | z_i.date_time[2]
                dostime = z_i.date_time[3] << 11 | z_i.date_time[4] << 5 | (z_i.date_time[5] // 2)
                cd_header = struct.pack("<4s4B4HL2L", b"PK\001\002",
                                        z_i.create_version, z_i.create_system,
                                        z_i.extract_version, z_i.reserved,
                                        z_i.flag_bits, z_i.compress_type, dostime, dosdate,
                                        z_i.CRC, z_i.compress_size, z_i.file_size)
                central_header_offset = zipbytes.find(cd_header)

                self.__tracer.trace("Patching central header @{}".format(
                    hex(central_header_offset)))
                orig_local_flags = struct.unpack_from("<h", zipbytes, central_header_offset+8)[0]
                struct.pack_into("<h", zipbytes, central_header_offset+8,
                                 orig_local_flags | TodoistBackupDownloader.__ZIP_FLAG_BITS_UTF8)

        if modified:
            self.__tracer.trace("Writing back patched ZIP file...")
            Path(backup_zip_path).write_bytes(zipbytes)


    def download(self, backup, output_path):
        """ Downloads the specified backup to the specified folder """

        # Sanitize the file name for platforms such as Windows,
        # which don't accept some characters in file names, such as a colon (:)
        self.__tracer.trace("Downloading backup with version '{}'".format(backup.version))
        sanitized_file_name = sanitize_file_name("TodoistBackup_" + backup.version + ".zip")
        output_file_path = os.path.join(output_path, sanitized_file_name)

        # Download the file
        if not os.path.isfile(output_file_path):
            self.__tracer.trace("Downloading from {} to file '{}'...".format(
                backup.url, output_file_path))
            urllib.request.urlretrieve(backup.url, output_file_path)
        else:
            self.__tracer.trace("File '{}' already downloaded... skipping".format(
                output_file_path))

        # Fix UTF-8 flags
        self.__fixup_zip_utf8_flags(output_file_path)

        return output_file_path

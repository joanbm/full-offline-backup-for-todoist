#!/usr/bin/python3
""" Utility to download the attachments associated with a Todoist backup VFS
    The downloaded attachments are packed to the same VFS """

import csv
import re
import json
import itertools
import os
from typing import Set, List, Optional
from .utils import sanitize_file_name
from .virtual_fs import VirtualFs
from .tracer import Tracer
from .url_downloader import URLDownloader

class TodoistAttachmentInfo:
    """ Represents the properties of a Todoist attachment """
    file_name: str
    file_url: str

    def __init__(self, file_name: str, file_url: str):
        self.file_name = file_name
        self.file_url = file_url

class TodoistBackupAttachmentsDownloader:
    """ Provides utilities for downloading the attachments of a Todoist backup """

    __TODOIST_ATTACHMENT_REGEXP = re.compile(r"\[\[\s*file\s*(.+)\s*\]\]")
    __ATTACHMENT_FOLDER = "attachments/"

    __tracer: Tracer
    __urldownloader: URLDownloader

    def __init__(self, tracer: Tracer, urldownloader: URLDownloader):
        self.__tracer = tracer
        self.__urldownloader = urldownloader

    @staticmethod
    def __fetch_attachment_info_from_json(json_str: str) -> Optional[TodoistAttachmentInfo]:
        """ Fetches the information of an attachment of a Todoist backup CSV file,
            given the JSON content of a task with an attachment """
        json_data = json.loads(json_str)

        # Exclude those files that are created from e.g. external website links
        if "file_name" not in json_data or "file_url" not in json_data:
            return None

        return TodoistAttachmentInfo(sanitize_file_name(json_data["file_name"]),
                                     json_data["file_url"])

    def __fetch_attachment_infos_from_csv(self, csv_string: str) -> List[TodoistAttachmentInfo]:
        """ Fetches the information of all the attachments of a Todoist backup CSV file,
            given a CSV file as a single string """
        attachment_infos = []

        csv_reader = csv.DictReader(csv_string.split('\n'))
        for row in csv_reader:
            matches = self.__TODOIST_ATTACHMENT_REGEXP.findall(row["CONTENT"])
            for matchstr in matches:
                attachment_info = self.__fetch_attachment_info_from_json(matchstr)
                if attachment_info:
                    attachment_infos.append(attachment_info)

        return attachment_infos

    def __fetch_attachment_infos(self, vfs: VirtualFs) -> List[TodoistAttachmentInfo]:
        """ Fetches the information of all the attachment_infos
            of the current Todoist backup VFS """
        self.__tracer.trace("Reading VFS...")

        attachment_infos = []

        # We iterate over the sorted file name list, so the resulting list
        # is always in a consistent order independently of quirks in the VFS
        for name in sorted(vfs.file_list()):
            self.__tracer.trace(f"Parsing CSV file '{name}'...")
            csv_string = vfs.read_file(name).decode('utf-8-sig')
            attachment_infos.extend(self.__fetch_attachment_infos_from_csv(csv_string))

        return attachment_infos

    @staticmethod
    def __deduplicate_file_name(original_file_name: str, file_names_to_avoid: Set[str]) -> str:
        """ Modifies the given file name in order to avoid all of the file names
           in the given list of file names to avoid """
        name_without_ext, ext = os.path.splitext(original_file_name)
        for i in itertools.count(2):
            new_file_name = name_without_ext + "_" + str(i) + ext
            if new_file_name not in file_names_to_avoid:
                return new_file_name

        assert False, "Unreachable code" # pragma: no cover

    def __deduplicate_attachments_names(self,
                                        attachment_infos: List[TodoistAttachmentInfo]) -> None:
        """ Modifies the attachment names, if necessary, in order to
            avoid duplicate file names """
        included_attachment_names: Set[str] = set()

        for attachment_info in attachment_infos:
            if attachment_info.file_name in included_attachment_names:
                new_file_name = self.__deduplicate_file_name(
                    attachment_info.file_name, included_attachment_names)
                self.__tracer.trace("Duplicate attachment name found - "
                    f"Renaming {attachment_info.file_name} to {new_file_name}...")
                attachment_info.file_name = new_file_name

            included_attachment_names.add(attachment_info.file_name)

    def __download_and_pack_attachments(self, attachment_infos: List[TodoistAttachmentInfo],
                                              vfs: VirtualFs) -> None:
        """ Downloads and packs the given attachments in a folder 'attachments'
            of the current Todoist backup VFS """
        for idx, attachment_info in enumerate(attachment_infos):
            self.__tracer.trace(f"[{idx+1}/{len(attachment_infos)}] "
                f"Downloading attachment '{attachment_info.file_name}'...")

            data = self.__urldownloader.get(attachment_info.file_url)

            vfs.write_file(self.__ATTACHMENT_FOLDER + attachment_info.file_name, data)

            self.__tracer.trace(f"[{idx+1}/{len(attachment_infos)}] "
                f"Downloaded attachment '{attachment_info.file_name}'...")

    def download_attachments(self, vfs: VirtualFs) -> None:
        """ Downloads all the attachments of the current Todoist backup VFS
            and packs them in a folder 'attachments' to the same VFS """

        # Ensure that we haven't already processed this file...
        if any(name.startswith(self.__ATTACHMENT_FOLDER) for name in vfs.file_list()):
            self.__tracer.trace("File already has attachments folder, skipping.")
            return

        # Fetch the information of all the attachments
        attachment_infos = self.__fetch_attachment_infos(vfs)
        self.__tracer.trace(f"Found {len(attachment_infos)} attachments.")
        self.__deduplicate_attachments_names(attachment_infos)
        self.__download_and_pack_attachments(attachment_infos, vfs)

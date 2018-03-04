#!/usr/bin/python3
""" Utility to download the attachments associated with a Todoist backup ZIP
    The downloaded attachments are packed to the same ZIP file """

import zipfile
import csv
import re
import json
import urllib.request
import itertools
import os

class TodoistAttachmentInfo:
    """ Represents the properties of a Todoist attachment """
    def __init__(self, file_name, file_url):
        self.file_name = file_name
        self.file_url = file_url

class TodoistBackupAttachmentsDownloader:
    """ Provides utilities for downloading the attachments of a Todoist backup """

    __TODOIST_ATTACHMENT_REGEXP = re.compile(r"^\s*\[\[\s*file\s*(.+)\s*\]\]$")
    __ATTACHMENT_FOLDER = "attachments/"

    def __init__(self, tracer):
        self.__tracer = tracer

    def __fetch_attachment_info_from_json(self, json_str):
        """ Fetches the information of an attachment of a Todoist backup CSV file,
            given the JSON content of a task with an attachment """
        json_data = json.loads(json_str)
        return TodoistAttachmentInfo(json_data["file_name"], json_data["file_url"])

    def __fetch_attachment_infos_from_csv(self, csv_string):
        """ Fetches the information of all the attachments of a Todoist backup CSV file,
            given a CSV file as a single string """
        attachment_infos = []

        csv_reader = csv.DictReader(csv_string.split('\n'))
        for row in csv_reader:
            match = self.__TODOIST_ATTACHMENT_REGEXP.match(row["CONTENT"])
            if match != None:
                attachment_infos.append(self.__fetch_attachment_info_from_json(match.group(1)))

        return attachment_infos

    def __fetch_attachment_infos_from_zip(self, zip_file):
        """ Fetches the information of all the attachment_infos
            of the current Todoist backup ZIP file """
        self.__tracer.trace("Reading ZIP file...")

        attachment_infos = []

        # We iterate over the sorted file name list, so the resulting list
        # is always in a consistent order independently of quirks
        # in the ZIP format
        for name in sorted(zip_file.namelist()):
            self.__tracer.trace("Parsing CSV file '{}'...".format(name))
            csv_string = zip_file.read(name).decode('utf-8-sig')
            attachment_infos.extend(self.__fetch_attachment_infos_from_csv(csv_string))

        return attachment_infos

    def __deduplicate_file_name(self, original_file_name, file_names_to_avoid):
        """ Modifies the given file name in order to avoid all of the file names
           in the given list of file names to avoid """
        name_without_ext, ext = os.path.splitext(original_file_name)
        for i in itertools.count(2):
            new_file_name = name_without_ext + "_" + str(i) + ext
            if new_file_name not in file_names_to_avoid:
                return new_file_name

    def __deduplicate_attachments_names(self, attachment_infos):
        """ Modifies the attachment names, if necessary, in order to
            avoid duplicate file names """
        included_attachment_names = set()

        for attachment_info in attachment_infos:
            if attachment_info.file_name in included_attachment_names:
                new_file_name = self.__deduplicate_file_name(
                    attachment_info.file_name, included_attachment_names)
                self.__tracer.trace("Duplicate attachment name found - Renaming {} to {}...".format(
                    attachment_info.file_name, new_file_name))
                attachment_info.file_name = new_file_name

            included_attachment_names.add(attachment_info.file_name)

    def __download_and_pack_attachments(self, attachment_infos, zip_file):
        """ Downloads and packs the given attachments in a folder 'attachments'
            of the current Todoist backup ZIP file """
        for idx, attachment_info in enumerate(attachment_infos):
            self.__tracer.trace ("[{}/{}] Downloading attachment '{}'... ".format(
                idx+1, len(attachment_infos), attachment_info.file_name))
                
            response = urllib.request.urlopen(attachment_info.file_url)
            data = response.read()

            zip_file.writestr(self.__ATTACHMENT_FOLDER + attachment_info.file_name, data)

            self.__tracer.trace ("[{}/{}] Downloaded attachment '{}'... ".format(
                idx+1, len(attachment_infos), attachment_info.file_name))

    def download_attachments(self, zip_file_path):
        """ Downloads all the attachments of the current Todoist backup ZIP file
            and packs them in a folder 'attachments' to the same ZIP """

        with zipfile.ZipFile(zip_file_path, 'a') as zip_file:
            # Ensure that we haven't already processed this file...
            if any(name.startswith(self.__ATTACHMENT_FOLDER) for name in zip_file.namelist()):
                self.__tracer.trace("File already has attachments folder, skipping.")
                return

            # Fetch the information of all the attachments
            attachment_infos = self.__fetch_attachment_infos_from_zip(zip_file)
            self.__tracer.trace("Found {} attachments.".format(len(attachment_infos)))
            self.__deduplicate_attachments_names(attachment_infos)
            self.__download_and_pack_attachments(attachment_infos, zip_file)

#!/usr/bin/python3
""" Utility to download the attachments associated with a Todoist backup ZIP
    The downloaded attachments are packed to the same ZIP file """

import sys
import zipfile
import csv
import re
import json
import urllib.request
import itertools
import os

TODOIST_ATTACHMENT_REGEXP = re.compile(r"^\s*\[\[\s*file\s*(.+)\s*\]\]$")
ATTACHMENT_FOLDER = "attachments/"

class TodoistAttachmentInfo:
    """ Represents the properties of a Todoist attachment """
    def __init__(self, file_name, file_url):
        self.file_name = file_name
        self.file_url = file_url

class TodoistBackupZipAttachmentDownloader:
    """ Provides utilities for downloading the attachments of a Todoist backup """

    def __init__(self, zip_file_path):
        self.zip_file_path = zip_file_path
        self.zip_file = None

    def __enter__(self):
        self.zip_file = zipfile.ZipFile(self.zip_file_path, 'a')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.zip_file.close()

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
            match = TODOIST_ATTACHMENT_REGEXP.match(row["CONTENT"])
            if match != None:
                attachment_infos.append(self.__fetch_attachment_info_from_json(match.group(1)))

        return attachment_infos

    def __fetch_attachment_infos_from_zip(self):
        """ Fetches the information of all the attachment_infos
            of the current Todoist backup ZIP file """
        print("Reading ZIP file...")

        attachment_infos = []

        for name in self.zip_file.namelist():
            print("Parsing CSV file '{}'...".format(name))
            csv_string = self.zip_file.read(name).decode('utf-8-sig')
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
                print("Duplicate attachment name found - Renaming {} to {}...".format(
                    attachment_info.file_name, new_file_name))
                attachment_info.file_name = new_file_name

            included_attachment_names.add(attachment_info.file_name)

    def __download_and_pack_attachments(self, attachment_infos):
        """ Downloads and packs the given attachments in a folder 'attachments'
            of the current Todoist backup ZIP file """
        for idx, attachment_info in enumerate(attachment_infos):
            print ("[{}/{}] Downloading attachment '{}'... ".format(
                idx+1, len(attachment_infos), attachment_info.file_name), end="", flush=True)
                
            response = urllib.request.urlopen(attachment_info.file_url)
            data = response.read()

            self.zip_file.writestr(ATTACHMENT_FOLDER + attachment_info.file_name, data)

            print("Done")

    def download(self):
        """ Downloads all the attachments of the current Todoist backup ZIP file
            and packs them in a folder 'attachments' to the same ZIP """

        # Ensure that we haven't already processed this file...
        if any(name.startswith(ATTACHMENT_FOLDER) for name in self.zip_file.namelist()):
            print("File already has attachments folder, skipping.")
            return

        # Fetch the information of all the attachments
        attachment_infos = self.__fetch_attachment_infos_from_zip()
        print("Found {} attachments.".format(len(attachment_infos)))
        self.__deduplicate_attachments_names(attachment_infos)
        self.__download_and_pack_attachments(attachment_infos)

def download_attachments_from_zip(zip_file_path):
    """ Downloads all the attachments of a Todoist backup ZIP file given its file path """
    with TodoistBackupZipAttachmentDownloader(zip_file_path) as downloader:
        downloader.download()

if __name__ == "__main__":
    download_attachments_from_zip(sys.argv[1])

#!/usr/bin/python3
""" Implementation of a VFS over memory, for the tests """
# pylint: disable=invalid-name
from full_offline_backup_for_todoist.virtual_fs import VirtualFs

class InMemoryVfs(VirtualFs):
    """ Implementation of a VFS over memory, for the tests """
    def __init__(self):
        self.files = {}

    def set_path_hint(self, dst_path):
        pass

    def existed(self):
        return len(self.files) != 0

    def file_list(self):
        return list(self.files.keys())

    def read_file(self, file_path):
        return self.files[file_path]

    def write_file(self, file_path, file_data):
        self.files[file_path] = file_data

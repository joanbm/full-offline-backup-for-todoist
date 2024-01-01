#!/usr/bin/python3
""" Tests for the runtime dependency injection container """
# pylint: disable=invalid-name
import unittest
from full_offline_backup_for_todoist.controller import TodoistAuth
from full_offline_backup_for_todoist.runtime import RuntimeControllerDependencyInjector

class TestRuntime(unittest.TestCase):
    """ Tests for the runtime dependency injection container """

    def test_runtime_dependency_injector_caches_values(self):
        """ Tests that the DI container always returns the same (valid) instances for the
            dependencies instead of creating new ones every call """
        # Arrange

        # Act
        runtimedi = RuntimeControllerDependencyInjector(TodoistAuth("1234"), False)
        tracer1 = runtimedi.tracer
        tracer2 = runtimedi.tracer
        backup_downloader1 = runtimedi.backup_downloader
        backup_downloader2 = runtimedi.backup_downloader
        backup_attachments_dl1 = runtimedi.backup_attachments_downloader
        backup_attachments_dl2 = runtimedi.backup_attachments_downloader

        # Assert
        self.assertIs(tracer1, tracer2)
        self.assertIsNotNone(tracer1)
        self.assertIs(backup_downloader1, backup_downloader2)
        self.assertIsNotNone(backup_downloader1)
        self.assertIs(backup_attachments_dl1, backup_attachments_dl2)
        self.assertIsNotNone(backup_attachments_dl1)

import unittest
from ..runtime import RuntimeControllerDependencyInjector

class TestMain(unittest.TestCase):
    def test_runtime_dependency_injector_caches_values(self):
        # Arrange

        # Act
        runtimedi = RuntimeControllerDependencyInjector("1234", True)
        tracer1 = runtimedi.tracer
        tracer2 = runtimedi.tracer
        todoist_api1 = runtimedi.todoist_api
        todoist_api2 = runtimedi.todoist_api
        todoist_backup_downloader1 = runtimedi.todoist_backup_downloader
        todoist_backup_downloader2 = runtimedi.todoist_backup_downloader
        todoist_backup_attachments_dl1 = runtimedi.todoist_backup_attachments_downloader
        todoist_backup_attachments_dl2 = runtimedi.todoist_backup_attachments_downloader

        # Assert
        self.assertIs(tracer1, tracer2)
        self.assertIs(todoist_api1, todoist_api2)
        self.assertIs(todoist_backup_downloader1, todoist_backup_downloader2)
        self.assertIs(todoist_backup_attachments_dl1, todoist_backup_attachments_dl2)
from setuptools import setup, find_packages
setup(
    name="todoist-full-offline-backup",
    version="0.1",
    packages=find_packages(),

    author="Joan Bruguera Micó",
    author_email="joanbrugueram@gmail.com",
    description="Small, dependency-less Python script to make a backup of all Todoist tasks and attachments that is accessible offline",
    license="GPLv3",
    keywords="todoist online backup attachments local full whole files",
    url="https://github.com/joanbm/todoist-full-offline-backup",
    project_urls={
        "Bug Tracker": "https://github.com/joanbm/todoist-full-offline-backup/issues",
        "Source Code": "https://github.com/joanbm/todoist-full-offline-backup",
    }
)

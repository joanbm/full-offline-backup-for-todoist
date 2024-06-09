from setuptools import setup, find_packages
setup(
    name="full-offline-backup-for-todoist",
    version="0.5.1",
    packages=find_packages(exclude=("tests",)),

    author="Joan Bruguera Micó",
    author_email="joanbrugueram@gmail.com",
    description="Small, dependency-less Python script to make a backup of all Todoist tasks and attachments that is accessible offline",
    license="GPLv3",
    keywords="todoist online backup attachments local full whole files",
    url="https://github.com/joanbm/full-offline-backup-for-todoist",
    scripts = ['bin/full-offline-backup-for-todoist'],
    project_urls={
        "Bug Tracker": "https://github.com/joanbm/full-offline-backup-for-todoist/issues",
        "Source Code": "https://github.com/joanbm/full-offline-backup-for-todoist",
    }
)

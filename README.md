# todoist-full-offline-backup

[![Build Status](https://travis-ci.org/joanbm/todoist-full-offline-backup.svg?branch=master)](https://travis-ci.org/joanbm/todoist-full-offline-backup)

## download_todoist_backup_attachments.py

### What does it solve?

With Todoist Premium, you can **attach files or photos to tasks as comments**, which is can be very convenient for everyday use, e.g. you can attach a photo of a bill to a task about paying it.

Furthermore, Todoist has a **backup functionality**, which allows exporting the task data to a local computer in the form of a ZIP file, e.g. for offline usage or in the event of an incident with Todoist servers.

Unfortunately, the two don't mix: **The backup functionality doesn't back up any of the attachments assigned to tasks**. Instead, only an URL to download the attachments is included in the backup, which isn't useful or ideal for most scenarios.

### How does it solve it?

The script is given a Todoist backup file (in the form of a ZIP file), and **it fetches the information of all the attachments, downloads them, and packs them** inside the ZIP file, so the backup file contains all the information needed to restore the tasks *and* the attachments without any access to Todoist's servers.

### Status

Early version - enough for basic use, but not tested under every possible scenario under the sun.

### Requirements

* Python 3 (tested with Python 3.6.4, but it should work with many more versions). No additional dependencies needed.

### Usage
``python3 download_todoist_backup_attachments.py my_backup_file.zip``
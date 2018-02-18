# todoist-full-offline-backup

[![Build Status](https://travis-ci.org/joanbm/todoist-full-offline-backup.svg?branch=master)](https://travis-ci.org/joanbm/todoist-full-offline-backup)

[![Coverage Status](https://coveralls.io/repos/github/joanbm/todoist-full-offline-backup/badge.svg)](https://coveralls.io/github/joanbm/todoist-full-offline-backup)

## Quick description

It is a utility that allows you to download a complete backup of your Todoist tasks, including all attachments, to your local computer, so you remain in control of all your data.

## What is the main aim of this tool?

With Todoist Premium, you can **attach files or photos to tasks as comments**, which is can be very convenient for everyday use, e.g. you can attach a photo of a bill to a task about paying it.

Furthermore, Todoist has a **backup functionality**, which allows exporting the task data to a local computer in the form of a ZIP file, e.g. for offline usage or in the event of an incident with Todoist servers.

Unfortunately, the two don't mix: **The backup functionality doesn't back up any of the attachments assigned to tasks**. Instead, only an URL to download the attachments is included in the backup, which isn't useful or ideal for most scenarios.

## Full feature list

* Can downloads the backups from Todoist's servers through the Todoist API

* Can download all attachments of the tasks associated to your Todoist backup

* Automatically fixes Todoist backup ZIPs when you have projects that contain non-ASCII characters (i.e. Unicode characters like 💓) so they can be correctly handled by ZIP tools.

* Can list all available backups through the Todoist API

* Can be easily automated to download your backups periodically

## Status

Early version - enough for basic use, but not tested under every possible scenario under the sun.

## Requirements

* Python 3 (tested with Python 3.6.4, but it should work with many more versions). No additional dependencies needed.

## Usage examples

Download latest backup from Todoist's servers, including attachments:

``python3 main.py download LATEST --with-attachments --token 0123456789abcdef``

Download a specific backup from Todoist's servers, without including attachments:

``python3 main.py download "2018-02-16 06:46" --token 0123456789abcdef``

Download a specific backup from Todoist's servers, including attachments, and with tracing/progress info:

``python3 main.py --verbose download "2018-02-16 06:46" --token 0123456789abcdef``

List available backups:

``python3 main.py list --token 0123456789abcdef``

Print full help:

``python3 main.py -h``

**IMPORTANT:** To use this tool you will need to replace the "0123456789abcdef" string above with your Todoist API token.

## How to get my Todoist API token?

The easiest way to get one is to open the **web version of Todoist**, go to the **Settings** section, then to the **Integrations** sections and you will see a API token there in the **"Token API"** section.
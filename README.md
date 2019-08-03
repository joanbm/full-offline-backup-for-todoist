# full-offline-backup-for-todoist

[![Build Status](https://travis-ci.org/joanbm/full-offline-backup-for-todoist.svg?branch=master)](https://travis-ci.org/joanbm/full-offline-backup-for-todoist)

[![Coverage Status](https://coveralls.io/repos/github/joanbm/full-offline-backup-for-todoist/badge.svg)](https://coveralls.io/github/joanbm/full-offline-backup-for-todoist)

## Quick description

It is a utility that allows you to download a complete backup of your Todoist tasks, including all attachments, to your local computer, so you remain in control of all your data.

## What is the main aim of this tool?

With Todoist Premium, you can **attach files or photos to tasks as comments**, which is can be very convenient for everyday use, e.g. you can attach a photo of a bill to a task about paying it.

Furthermore, Todoist has a **backup functionality**, which allows exporting the task data to a local computer in the form of a ZIP file, e.g. for offline usage or in the event of an incident with Todoist servers.

Unfortunately, the two don't mix: **The backup functionality doesn't back up any of the attachments assigned to tasks**. Instead, only an URL to download the attachments is included in the backup, which isn't useful or ideal for most scenarios.

This tool aims to allow you to make a complete backup, including all attachments, so you can easily keep all your task data secure on your own computer.

## Full feature list

* Can downloads the backups from Todoist's servers through the Todoist API.

* Can download all attachments of the tasks associated to your Todoist backup.

* Unlike Todoist's automatic backup ZIPs, valid ZIPs are generated  when you have projects that contain non-ASCII characters (i.e. Unicode characters like 💓) so they can be correctly handled by ZIP tools.

* Can be easily automated to download your backups periodically.

## Status

Early version - enough for basic use, but not tested under every possible scenario under the sun.

## Requirements

* Python 3 (tested with Python 3.6.4, but it should work with many more versions). No additional dependencies needed.

## Usage examples

Create a backup from Todoist's servers, without including attachments:

``python3 __main__.py download --token 0123456789abcdef``

Create a backup from Todoist's servers, including attachments, and with tracing/progress info:

``python3 __main__.py --verbose download --with-attachments --token 0123456789abcdef --email myemail@example.com --password P4ssW0rD``

**NOTE:** The email and password is **required** to download the attachments, as a workaround due to security restriction introduced by Todoist in 2018 (see [issue #1](https://github.com/joanbm/full-offline-backup-for-todoist/issues/1)). As of today, there is no official way provided by Todoist to automate attachment download, and the current workaround may break at any time.

Print full help:

``python3 __main__.py -h``

**IMPORTANT:** To use this tool you will need to replace the "0123456789abcdef" string above with your Todoist API token (and similarly for your email and password).

## How to get my Todoist API token?

The easiest way to get one is to open the **web version of Todoist**, go to the **Settings** section, then to the **Integrations** sections and you will see a API token there in the **"Token API"** section.

# Disclaimer

This is **NOT** an official application. This application is not created by, affiliated with, or supported by Doist.

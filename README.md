# full-offline-backup-for-todoist

[![Build Status](https://github.com/joanbm/full-offline-backup-for-todoist/actions/workflows/run-tests.yml/badge.svg?branch=master)](https://github.com/joanbm/full-offline-backup-for-todoist/actions/workflows/run-tests.yml)

[![Coverage Status](https://coveralls.io/repos/github/joanbm/full-offline-backup-for-todoist/badge.svg)](https://coveralls.io/github/joanbm/full-offline-backup-for-todoist)

## Quick description

It is a utility that allows you to download a complete backup of your Todoist tasks, including all attachments, to your local computer, so you remain in control of all your data.

## What is the main aim of this tool?

With Todoist Premium, you can **attach files or photos to tasks as comments**, which can be very convenient for everyday use, e.g. you can attach a photo of a bill to a task about paying it.

Furthermore, Todoist has a **backup functionality**, which allows exporting the task data to a local computer in the form of a ZIP file, e.g. for offline usage or in the event of an incident with Todoist's servers.

Unfortunately, the two don't mix: **The backup functionality doesn't back up any of the attachments assigned to tasks**. Instead, only a URL to download the attachment is included in the backup, which isn't useful or ideal for most scenarios.

This tool aims to allow you to make a complete backup, including all attachments, so you can easily keep all your task data secure on your own computer.

## Full feature list

* Can download the backups from Todoist's servers through the Todoist API.

* Can download all attachments of the tasks associated with your Todoist backup.

* Can be easily automated to download your backups periodically.

## Status

Stable, but not tested under every possible scenario under the sun.

## Requirements

* Python 3 (tested with Python 3.8+). No additional dependencies needed.

## Usage examples

Download the repository and open a terminal at the root folder.

To create a backup from Todoist's servers, without including attachments (you will be asked for your Todoist API Token through the command line):

``python3 -m full_offline_backup_for_todoist download``

To create a backup from Todoist's servers, including attachments, and with tracing/progress info:

``python3 -m full_offline_backup_for_todoist --verbose download --with-attachments``

Print full help:

``python3 -m full_offline_backup_for_todoist -h``

## How to get my Todoist API token?

The easiest way to get one is to open the **web version of Todoist**, go to the **Settings** section, then to the **Integrations** sections, and you will see an API token there in the **"Token API"** section.

## How can I automate the backup process?

To automate the backup process, you can use any automation tool you want (e.g. cron, Jenkins) that can run the utility. In order to pass the credentials non-interactively, you can set the `TODOIST_TOKEN` environment variable before running it from your automation tool.

# Disclaimer

This is **NOT** an official application. This application is not created by, affiliated with, or supported by Doist.

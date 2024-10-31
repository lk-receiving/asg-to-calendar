#!/usr/bin/env python3
# Program Name:         settings.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Imports configurations

# ::IMPORTS ------------------------------------------------------------------------ #
import os

import csv

from google.oauth2.credentials import Credentials

# ::SETUP -------------------------------------------------------------------------- #
INPUT_DIR: str = 'input'
OUTPUT_DIR: str = 'output'

# Create the input/output directories
for io_dir in [INPUT_DIR, OUTPUT_DIR]:
    try:
        os.mkdir(io_dir)
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{io_dir}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Google Calendar API Creds Setup
SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar.events"]
SERVICE_NAME: str = "calendar"
SERVICE_VERSION: str = "v3"
EVENTS_OUTFILE: str = "output/events.json"
CREDS: Credentials = ''
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    CREDS = Credentials.from_authorized_user_file("token.json", SCOPES)

# Logger file
LOGFILE: str = OUTPUT_DIR + '/debug.log'

# Commands
COMMANDS: dict[str] = {
    'display': {
        'method': 'display_events',
        'description':'Displays Google Calendar events from today'
    },
    'create': {
        'method': 'create_events',
        'description': 'Creates Google Calendar events from either a .csv or .json file'
    },
    'delete': {
        'method': 'delete_events',
        'description':'Deletes Google Calendar events from a .json file'
    },
    'help': {
        'method': 'display_cmds',
        'description':'Displays available commands'
    },
    'exit': {
        'method': 'exit',
        'description':'Exits the program'
    }
}

# User Prompts
PROMPTS = {
    "command": 'Enter a [bold cyan1]command[default]',
    "file": (
        f'\nEnter the [bold cyan1]filepath '
        f'[default]for either a [bold yellow].csv[default] '
        f'or [bold yellow].json[default] file to import'
    ),
    "file_delete": (
        f'\nEnter the [bold yellow].json[default] [bold cyan1]filepath[default] '
        f'that contains the event objects to delete'
    ),
    "date_format": (
        f'\nProvide the [yellow]date format[default] for the supplied dates '
        f'in the "[bold cyan1]due_date[default]" column. Default is "%Y-%m-%d".\n'
        f'For additional format codes, type "[orange]help[default]"'
    ),
    "course_key": (
        f'\nProvide the [yellow]course key[default] for the gradebook/columns '
        f'"[bold cyan1].json[default]" file'
    ),
    "exit": ' (or type [bright_red]"exit"[default] to exit)\n'
}
STRFTIME_COLS: tuple[tuple] = (
    ("Directive", "right", "cyan"),
    ("Meaning", "left", "magenta"),
    ("Example", "left", "green")
)
STRFTIME_ROWS: tuple[tuple[str]] = (
    ("%d", "Day of the month as a zero-padded decimal number.", "01, 02, …, 31"),
    ("%b", "Month as locales abbreviated name.", "Jan, Feb, …, Dec (en_US); Jan, Feb, …, Dez (de_DE)"),
    ("%B", "Month as locales full name.", "January, February, …, December (en_US); Januar, Februar, …, Dezember (de_DE)"),
    ("%m", "Month as a zero-padded decimal number.", "01, 02, …, 12"),
    ("%y", "Year without century as a zero-padded decimal number.", "00, 01, …, 99"),
    ("%Y", "Year with century as a decimal number.", "0001, 0002, …, 2013, 2014, …, 9998, 9999"),
    ("%H", "Hour (24-hour clock) as a zero-padded decimal number.", "00, 01, …, 23"),
    ("%M", "Minute as a zero-padded decimal number.", "00, 01, …, 59"),
    ("%S", "Second as a zero-padded decimal number", "00, 01, …, 59"),
    ("%f", "Microsecond as a decimal number, zero-padded to 6 digits.", "000000, 000001, …, 999999"),
    ("%Z", "Time zone name (empty string if the object is naive).", "(empty), UTC, GMT")
)

# For ImportEvents module
CSV_FIELDS: list[str] = [
    "course_key",       # Course Key "COSC-2436"
    "course_name",      # Course Name "Prg III"
    "asg_name",         # Assignment Name "Lab1"
    "asg_desc",         # Assignment Description "Use course materials for lab 1."
    "due_date",         # Assignment Due date "yyyy-mm-dd"
    "due_location"      # Assignment Due Location "Blackboard"
]
EVENT_MAP: dict = {
    "summary": "summary",         # (str)
    "due_date": "start",     # (date), in the format "yyyy-mm-dd", if this is an all-day event.
    "description": "description", # (str)	Description of the event. Can contain HTML. Optional.
    "due_location": "location"    # (str) Geographic location of the event as free-form text. Optional.
}
FILE_MAP: dict = {
    "csv": {
        "import": "_Events__import_csv",
        "generate": "_Events__get_csv_events"
    },
    "json": {
        "import": "_Events__import_json",
        "generate": "_Events__get_json_events"
    }
}
TEMPLATE_CSV = 'input/template.csv'

# Write a template csv file to input dir
with open(TEMPLATE_CSV, 'w', newline='') as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(CSV_FIELDS)
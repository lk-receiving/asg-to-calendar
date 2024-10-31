
#!/usr/bin/env python3
# Program Name:         program14.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Takes a spreadsheet of classes and assignments, and adds them as events to a
#   google calendar

# ::IMPORTS ------------------------------------------------------------------------ #
from src.logger import logger as log
from src.settings import CSV_FIELDS, EVENT_MAP, STRFTIME_COLS, STRFTIME_ROWS

import pandas as pd
import csv

import json

from typing import Generator

import dateutil.parser

# # CLI output functions
# from rich import print
# from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# # Display functions
# from .events import display_cmds, display_error, display_panel, display_prompt
# from .events import Events, ExitProgram


# ::SETUP -------------------------------------------------------------------------- #


# ::GLOBALS ------------------------------------------------------------------------ #


# ::CORE LOGIC --------------------------------------------------------------------- #
def import_csv(csv_file) -> list[dict]:
    '''
    Retrieve data as a list from csv file
    ---
    Args:
        csv_file (str): csv file to import
    Returns
        records (list[dict]): The data from the csv file

    '''
    records = []

    try:
        with open(csv_file, 'r') as file:
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(csv_file.read(1024))

            if has_header:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    records.append(row)
            else:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    record = dict(zip(CSV_FIELDS, row))
                    records.append(record)
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception:
        raise

    return records

# def import_csv2(csv_file, date_format='%Y-%m-%d') -> pd.DataFrame:
#     '''
#     Retrieve data as a list from csv file
#     ---
#     Args:
#         csv_file (str): csv file to import
#     Returns
#         df (pd.Dataframe): The data from the csv file

#     '''
#     log.debug('Starting __get_csv()')
#     df = None

#     # Prompt user for date format
#     date_col = CSV_FIELDS[4]
#     str_cols = [col for col in CSV_FIELDS if col != date_col]

#     try:
#         df = pd.read_csv(
#             csv_file,
#             header=0,
#             usecols=CSV_FIELDS,
#             parse_dates=[date_col],
#             date_format=date_format,
#             dtype={col: str for col in str_cols}
#         )
#         if str(df['due_date'].dtype) != "datetime64[ns]":
#             raise ValueError(
#                 'Invalid date_format param. Date column did not format into date object.'
#             )
#     except ValueError:
#         raise
#     except FileNotFoundError:
#         raise
#     except Exception:
#         raise

#     return df

# def get_csv_events(self, df) -> Generator[dict, None, None]:
#     '''
#     Transform data into Google Calendar events objects
#     '''
#     log.debug('Starting __create_events()')

#     events_gen = None
#     summary_col = CSV_FIELDS[0:3:2]
#     desc_col = CSV_FIELDS[1:5:2]

#     # Extract subset of csv to create google event col/vals
#     if not df.empty:
#         events_df = df.iloc[:, 4:]
#         events_df['due_date'] = events_df['due_date'].map(lambda x: x.strftime('%Y-%m-%d'))
#         events_df['end'] = events_df['due_date']
#         events_df['summary'] = df[summary_col].agg(': '.join, axis=1)
#         events_df['description'] = df[desc_col].agg('<br>'.join, axis=1)
#         events_df = events_df.rename(columns=EVENT_MAP)

#         display_df('Transformed data', events_df)

#         # Set df to new events_df
#         events_list = events_df.to_dict(orient='records')
        
#         # Change "start" date into a dictionary
#         for item in events_list:
#             item['start'] = {'date': item['start']}
#             item['end'] = {'date': item['end']}

#         events_gen = (event for event in events_list)
        
#     return events_gen

# def import_json(self, jsonFile) -> list[dict]:
#     '''
#     Retrieve data as a list from json file
#     ---
#     Args:
#         jsonFile (str) : The json file to load.
#     Returns
#         data (list[dict]): Results data from file

#     '''
#     log.debug('Starting __get_json()')
#     data = []

#     try:
#         with open(jsonFile, 'r') as in_file:
#             data = json.load(in_file)
#     except json.JSONDecodeError:
#         raise
#     except FileNotFoundError:
#         raise
#     except Exception:
#         raise

#     return data

# def get_json_events(self, data) -> Generator[dict, None, None]:
#     '''
#     Transform data into Google Calendar events objects
#     ---
#     Args:
#         course_key (str): The course key to append to the summary
#     Returns
#         (Generator[dict, None, None]): Generator for event data
#     '''
#     log.debug('Starting __create_events()')

#     is_event_obj = Confirm.ask(
#         f'Is the data already in Google Calendar Event format?\n'
#         f'(If unsure, type "n".)'
#     )

#     if not is_event_obj:
#         try:
#             course_key: str = display_prompt(PROMPTS['course_key'])
#         except ExitProgram:
#             raise

#         parsed = []

#         if data:
#             for item in data:
#                 date_iso = item['grading'].get('due')

#                 if date_iso:
#                     summary = course_key + ': ' + item.get('name')
#                     date_utc = datetime.fromisoformat(date_iso)
#                     date_local = date_utc.astimezone().strftime('%Y-%m-%d')
#                     event = {
#                         "summary": summary,
#                         "start": {"date": date_local},
#                         "end": {"date": date_local},
#                         "location": "Blackboard"
#                     }
#                     parsed.append(event)

#             display_console(f'Transformed data')
#             print(parsed)

#             events_gen = (item for item in parsed)
#     else:
#         events_list = self.strip_event_data(data)

#         display_console(f'Transformed data')
#         print(events_list)

#         events_gen = (item for item in events_list)

#     return events_gen

# def write_events(self, events) -> None:
#     '''
#     Writes events to output file
#     '''
#     try:
#         with open(EVENTS_OUTFILE, 'w', encoding='utf-8') as f:
#             json.dump(events, f, ensure_ascii=False, indent=4)
#     except FileNotFoundError:
#         raise

#     display_panel(f'Wrote events to [yellow]"{EVENTS_OUTFILE}"', 'Success')

# def strip_event_data(self, data) -> list[dict]:
#     '''
#     Strips down existing event data into event template format
#     '''
#     events_list = []

#     for item in data:
#         new_event = {}
        
#         for key, val in item.items():
#             if key in ['summary', 'start', 'end', 'location', 'description']:
#                 new_event[key] = val

#         events_list.append(new_event)

#     return events_list

def display_strftime() -> None:
    '''
    Display common strftime codes.  For more information, see here:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    '''
    log.debug('Starting display_strftime()...')
    console = Console()

    table = Table(title="strftime codes")

    for name, justify, style in STRFTIME_COLS:
        table.add_column(name, justify=justify, style=style, no_wrap=True)

    for code, desc, ex in STRFTIME_ROWS:
        table.add_row(code, desc, ex)
    
    console.print(table)

def display_error(msg):
    '''
    Displays a custom error message
    '''
    print()
    print(Panel(
            msg,
            border_style='dark_red',
            title='[bold bright_red]Error',
            title_align='left'
))
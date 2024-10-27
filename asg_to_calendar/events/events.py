#!/usr/bin/env python3
# Program Name:         Calendar.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Create an Events object that allows read and edit actions for Events

# ::IMPORTS ------------------------------------------------------------------------ #
from logger import logger as log

from datetime import datetime, timezone

from settings import CREDS, SCOPES, SERVICE_NAME, SERVICE_VERSION, CSV_FIELDS, EVENT_MAP
from settings import FILE_MAP, COMMANDS, STRFTIME_COLS, STRFTIME_ROWS, PROMPTS, EVENTS_OUTFILE

from typing import Generator

# Manipulating csv file
import pandas as pd

# Manipulating JSON files
import json

# For path related functions
from pathlib import Path

# Google Calendar API (REQUIRED)- For more information, go here:
# https://developers.google.com/calendar/api/quickstart/python
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

# CLI output functions
from rich import print
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.console import Console
from rich.table import Table

# ::SETUP -------------------------------------------------------------------------- #
console = Console()

# ::GLOBALS ------------------------------------------------------------------------ #


# ::CORE LOGIC --------------------------------------------------------------------- #
class ExitProgram(Exception):      
    ''' Custom Exception to raise when user declares to exit program'''    
    pass

class Events:
    # If modifying these scopes, delete the file token.json.
    __PROMPTS: dict[str:str] = PROMPTS
    __FILE_MAP: dict = FILE_MAP
    __EVENTS_OUTFILE: str = EVENTS_OUTFILE
    __CSV_FIELDS: list[str] = CSV_FIELDS
    __EVENT_MAP: dict = EVENT_MAP
    SCOPES: list[str] = SCOPES
    SERVICE_NAME: str = SERVICE_NAME
    SERVICE_VERSION: str = SERVICE_VERSION

    def __init__(self) -> None:
        self._log = log
        self.__now = naive_utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        self.__service = self.__set_service()

    def __auth(self) -> Credentials:
        '''
        Authenticates user into Google Calendar API
        ---
        Args:
            None
        Returns
            None
        '''
        self._log.debug('Starting self.__auth()')
        creds = CREDS
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self._log.debug('__auth(): Creds expired...Refreshing Credentials')
                creds.refresh(Request())
            else:
                self._log.debug('__auth(): Grabbing credentials.json for Creds')
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", Events.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                self._log.debug('__auth(): Writing token.json for Creds')
                token.write(creds.to_json())

        self._log.debug('End  self.__auth()')
        return creds

    def __set_service(self) -> Resource:
        '''
        Construct a Resource object for interacting with an API. The serviceName and
        version are the names from the Discovery service.
        '''
        self._log.debug('Starting __set_service()')
        try:
            self._log.debug('End __set_service()')
            return build(Events.SERVICE_NAME, Events.SERVICE_VERSION, credentials=self.__auth())
        except HttpError as error:
            raise

    def display_events(self) -> bool:
        '''
        Displays events from the calendar
        '''
        success: bool = False

        try:
            maxResults = display_IntPrompt('Enter the number of events to retrieve')
            events = self.get_events(maxResults)
        except ExitProgram:
            raise ExitProgram
        except HttpError:
            raise
        
        if events:
             # Prints the start and name of the next 10 events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

            success = True
            to_file = Confirm.ask('Would you like to save the event objects to a file?')

            if to_file:
                self.__write_events(events)
        else:
            print("No upcoming events found.")

        return success

    def get_events(self, maxResults) -> bool:
        '''
        Retrieves events from the Calendar
        '''
        self._log.debug('Starting get_events()')
        events: list[dict] = []

        try:
            # Call the Calendar API
            print(f'Getting the upcoming {maxResults} events')
            events_result = (
                self.__service.events()
                .list(
                    calendarId="primary",
                    timeMin=self.__now,
                    maxResults=maxResults,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
        except HttpError:
            raise
        
        return events

    def create_events(self) -> bool:
        '''
        Create a Calendar event
        '''
        self._log.debug('Starting create_events()')

        created = False
        events_gen = self.__get_data()

        try:
            events_list = []

            for item in events_gen:
                try:
                    event = self.__service.events().insert(calendarId='primary', body=item).execute()
                    events_list.append(event)
                    print(f'Event created: {event.get('htmlLink')}')
                except Exception:
                    raise

            display_panel('Created all events.', 'Success')
            
            to_file = Confirm.ask('Would you like to save the event objects to a file?')

            if to_file:
                self.__write_events(events_list)

            created = True

        except TypeError:
            raise

        return created
    
    def delete_events(self) -> bool:
        '''
        Delete Google Calendar events
        '''
        self._log.debug('Starting delete_events()')

        deleted = False
        events_list = self.__get_delete_data()

        # Have user validate data
        confirmation = Confirm.ask(
            f'Confirm if the transformed data above is correct '
            f'and to continue to delete from calendar'
        )

        if not confirmation:
            display_error(
                'User has confirmed that the data is [bold bright_red]incorrect.\n'
                'Exiting program...'
            )
            raise ExitProgram("User prompted to exit program.")

        if events_list and confirmation:
            for sum, id in events_list:
                print(f'Deleting event: "{sum} - [green]{id}"')
                try:
                    self.__service.events().delete(calendarId='primary', eventId=id).execute()
                except Exception:
                    raise

            display_panel(f'Deleted all events.', 'Success')
            deleted = True
        
        return deleted

    
    def __get_data(self) -> Generator[dict, None, None]:
        '''
        Retrieves file from user, imports data and returns formatted event data
        as a generator object
        '''
        self._log.debug('Starting __get_data()...')
        success = False
        events_gen = None

        # Get file from user
        user_file: str = display_prompt(Events.__PROMPTS['file'], help_func=display_cwd)

        while not Path(user_file).is_file():
            display_error(f'"{user_file}" is not recognized as a file.')
            user_file = display_prompt(Events.__PROMPTS['file'], help_func=display_cwd)

        try:
            file_ext = user_file.split('.')[-1] # Retrieve file extension

            # Call the methods based on file type
            import_method = getattr(self, Events.__FILE_MAP[file_ext]["import"])
            gen_method = getattr(self, Events.__FILE_MAP[file_ext]["generate"])

            data = import_method(user_file)
            events_gen = gen_method(data)
            
            # Have user validate data
            confirmation = Confirm.ask(
                f'Confirm if the transformed data above is correct '
                f'and to continue to add to calendar'
            )

            if not confirmation:
                display_error(
                    'User has confirmed that the data is [bold bright_red]incorrect.\n'
                    'Exiting program...'
                )
                raise ExitProgram("User prompted to exit program.")
            else:
                success = confirmation
            
        except ExitProgram:
            raise
        except KeyError as e:
            self._log.debug(e, stack_info=True, exc_info=True)
            display_error(f'File "{user_file}" is not a supported filetype.')
        except ValueError as e:
            self._log.debug(e, stack_info=True, exc_info=True)
            display_error(f'Invalid argument value.')
        except FileNotFoundError as e:
            self._log.debug(e, stack_info=True, exc_info=True)
            display_error(f'File "{user_file}" was not found.')
        except json.JSONDecodeError as e:
            self._log.debug(e, stack_info=True, exc_info=True)
            display_error(f'File "{user_file}" contained invalid JSON syntax')
        except Exception as e:
            self._log.debug(e, stack_info=True, exc_info=True)
            display_error(f'Issue importing file: "{user_file}".')

        if not success:
            raise ExitProgram

        return events_gen
    
    def __get_delete_data(self) -> list[str]:
        '''
        Gets JSON Event objects to delete
        '''
        user_file: str = display_prompt(Events.__PROMPTS['file_delete'], help_func=display_cwd)

        while not Path(user_file).is_file():
            display_error(f'"{user_file}" is not recognized as a file.')
            user_file = display_prompt(Events.__PROMPTS['file_delete'], help_func=display_cwd)

        data: list[dict] = []
        events: list[str] = []

        try:
            with open(user_file, 'r') as inFile:
                data = json.load(inFile)
                events = [(item.get('summary'), item.get('id')) for item in data]
        except FileNotFoundError:
            raise
        except TypeError:
            raise
        except json.JSONDecodeError:
            raise

        print(events)

        return events


    def __import_csv(self, csv_file) -> pd.DataFrame:
        '''
        Retrieve data as a list from csv file
        ---
        Args:
            csv_file (str): csv file to import
        Returns
            df (pd.Dataframe): The data from the csv file

        '''
        self._log.debug('Starting __get_csv()')

        # Prompt user for date format
        try:
            date_format: str = display_prompt(
                Events.__PROMPTS['date_format'],
                help_func=display_strftime
            )
        except ExitProgram:
            raise

        date_col = Events.__CSV_FIELDS[4]
        str_cols = [col for col in Events.__CSV_FIELDS if col != date_col]

        try:
            df = pd.read_csv(
                csv_file,
                header=0,
                usecols=Events.__CSV_FIELDS,
                parse_dates=[date_col],
                date_format=date_format,
                dtype={col: str for col in str_cols}
            )
            if str(df['due_date'].dtype) == "datetime64[ns]":
                display_panel(f'Retrieved "{csv_file}"', 'Success')
                display_df(csv_file, df) # Display original csv data
                return df
            else:
                raise ValueError
        except ValueError:
            raise
        except FileNotFoundError:
            raise
        except Exception:
            raise

    def __get_csv_events(self, df) -> Generator[dict, None, None]:
        '''
        Transform data into Google Calendar events objects
        '''
        self._log.debug('Starting __create_events()')

        events_gen = None
        summary_col = Events.__CSV_FIELDS[0:3:2]
        desc_col = Events.__CSV_FIELDS[1:5:2]

        # Extract subset of csv to create google event col/vals
        if not df.empty:
            events_df = df.iloc[:, 4:]
            events_df['due_date'] = events_df['due_date'].map(lambda x: x.strftime('%Y-%m-%d'))
            events_df['end'] = events_df['due_date']
            events_df['summary'] = df[summary_col].agg(': '.join, axis=1)
            events_df['description'] = df[desc_col].agg('<br>'.join, axis=1)
            events_df = events_df.rename(columns=Events.__EVENT_MAP)

            display_df('Transformed data', events_df)

            # Set df to new events_df
            events_list = events_df.to_dict(orient='records')
            
            # Change "start" date into a dictionary
            for item in events_list:
                item['start'] = {'date': item['start']}
                item['end'] = {'date': item['end']}

            events_gen = (event for event in events_list)
            
        return events_gen
    
    def __import_json(self, jsonFile) -> list[dict]:
        '''
        Retrieve data as a list from json file
        ---
        Args:
            jsonFile (str) : The json file to load.
        Returns
            data (list[dict]): Results data from file

        '''
        self._log.debug('Starting __get_json()')

        try:
            with open(jsonFile, 'r') as in_file:
                data = json.load(in_file)
                display_panel(f'Retrieved "{jsonFile}"', 'Success')
                display_console(f'Original JSON data: {jsonFile}')

                if isinstance(data, dict):
                    data = data.get('results')

                print(data)

                return data
        except json.JSONDecodeError:
            raise
        except FileNotFoundError:
            raise
        except Exception:
            raise

    def __get_json_events(self, data) -> Generator[dict, None, None]:
        '''
        Transform data into Google Calendar events objects
        ---
        Args:
            course_key (str): The course key to append to the summary
        Returns
            (Generator[dict, None, None]): Generator for event data
        '''
        self._log.debug('Starting __create_events()')

        is_event_obj = Confirm.ask(
            f'Is the data already in Google Calendar Event format?\n'
            f'(If unsure, type "n".)'
        )

        if not is_event_obj:
            try:
                course_key: str = display_prompt(Events.__PROMPTS['course_key'])
            except ExitProgram:
                raise

            parsed = []

            if data:
                for item in data:
                    date_iso = item['grading'].get('due')

                    if date_iso:
                        summary = course_key + ': ' + item.get('name')
                        date_utc = datetime.fromisoformat(date_iso)
                        date_local = date_utc.astimezone().strftime('%Y-%m-%d')
                        event = {
                            "summary": summary,
                            "start": {"date": date_local},
                            "end": {"date": date_local},
                            "location": "Blackboard"
                        }
                        parsed.append(event)

                display_console(f'Transformed data')
                print(parsed)

                events_gen = (item for item in parsed)
        else:
            events_list = self.__strip_event_data(data)

            display_console(f'Transformed data')
            print(events_list)

            events_gen = (item for item in events_list)

        return events_gen
    
    def __write_events(self, events) -> None:
        '''
        Writes events to output file
        '''
        try:
            with open(Events.__EVENTS_OUTFILE, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            raise

        display_panel(f'Wrote events to [yellow]"{Events.__EVENTS_OUTFILE}"', 'Success')

    def __strip_event_data(self, data) -> list[dict]:
        '''
        Strips down existing event data into event template format
        '''
        events_list = []

        for item in data:
            new_event = {}
            
            for key, val in item.items():
                if key in ['summary', 'start', 'end', 'location', 'description']:
                    new_event[key] = val

            events_list.append(new_event)

        return events_list
        
# ::Functions --------------------------------------------------------------------- #
def naive_utcnow() -> datetime:
    '''
    Converts a timezone aware now datatime object to a naive now
    '''
    aware_now = datetime.now(timezone.utc)
    naive_now = aware_now.replace(tzinfo=None)
    return naive_now

def display_prompt(
    msg: str,
    choices=None,
    help_func=None
) -> str:
    '''
    Prompts user and allows them to exit program
    '''
    answer = Prompt.ask(
        msg + PROMPTS['exit'],
        choices=choices
    )

    if help_func:
        while answer == 'help':
            help_func()
            answer = Prompt.ask(
                msg + PROMPTS['exit'],
                choices=choices
            )

    if answer.lower() == 'exit':
        print()
        print(Panel(
                'Exiting Program...',
                border_style='dark_red',
                title='[bold bright_red]Exit',
                title_align='left'
        ))
        raise ExitProgram("User prompted to exit program.")

    return answer

def display_IntPrompt(msg: str,
    choices=None,
    max=50,
    help_func=None
) -> str:
    '''
    Prompts user for an integer and allows them to exit program
    '''
    msg = (
        f'{msg} (or enter [cyan1]"-1"[/cyan1] to [bright_red]exit)[/bright_red]\n'

    )
    print()
    answer = IntPrompt.ask(msg, choices=choices)

    while answer < -1 or answer > max or answer == 0:
        display_error(f'Value cannot be less than -1 or exceed the max {max}')
        answer = IntPrompt.ask(msg, choices=choices)

    if help_func:
        while answer == 'help':
            help_func()
            answer = IntPrompt.ask(msg, choices=choices)

    if answer == -1:
        print()
        print(Panel(
                'Exiting Program...',
                border_style='dark_red',
                title='[bold bright_red]Exit',
                title_align='left'
        ))
        raise ExitProgram("User prompted to exit program.")

    return answer

def display_cwd():
    '''
    Displays the current working directory
    '''
    msg: str = (
        f'The current working directory is:\n[yellow]{Path.cwd()}[/yellow]\n\n'
        f'If providing a relative file path, check if file is '
        f' in [yellow]"input/"[default] directory\ne.g. [cyan1]"input/template.csv"'
    )
    print()
    print(Panel(
            msg,
            border_style='bright_green',
            title='[bold bright_green]Help',
            title_align='left'
    ))

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

def display_panel(msg: str, title: str, style: str='bright_green'):
    '''
    Displays a panel with a message
    '''
    print()
    print(Panel(
            msg,
            border_style=style,
            title=f'[bold {style}]{title}',
            title_align='left'
    ))

def display_cmds() -> None:
    '''
    Displays commands
    '''
    log.debug('Starting display_cmds()...')
    cmds = COMMANDS
    body = ''
    for key, val in cmds.items():
        line = f'[bold cyan1]{key}\t\t[default]{val.get('description')}\n'
        body += line

    print()
    print(Panel(
            body.strip(),
            border_style='dark_green',
            title='[bold dark_green]Commands',
            title_align='left'
    ))

def display_strftime() -> None:
    '''
    Display common strftime codes.  For more information, see here:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    '''
    log.debug('Starting display_strftime()...')
    print()

    table = Table(title="strftime codes")

    for name, justify, style in STRFTIME_COLS:
        table.add_column(name, justify=justify, style=style, no_wrap=True)

    for code, desc, ex in STRFTIME_ROWS:
        table.add_row(code, desc, ex)
    
    console.print(table)

def display_df(user_file: str, df):
    '''
    Displays a dataframe as a Rich table
    '''
    log.debug('Starting display_df()...')
    print()
    table = Table(title=user_file)

    # Add columns to the table
    for col in df.columns:
        table.add_column(col)

    # Add rows to the table
    for row in df.values.tolist():
        table.add_row(*[str(x) for x in row])

    # Print the table using the console
    console.print(table)

def display_console(msg: str, justify="center") -> None:
    '''
    Displays console message
    '''
    console.print(msg, justify=justify)
#!/usr/bin/env python3
# Program Name:         program14.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Takes a spreadsheet of classes and assignments, and adds them as events to a
#   google calendar

# ::IMPORTS ------------------------------------------------------------------------ #
import logging
# from asg_to_calendar.src import logger as log
from utils import logger as log
from utils import import_csv, display_strftime, display_error

import typer
from typing_extensions import Annotated

from pathlib import Path

# from asg_to_calendar.settings import COMMANDS, PROMPTS

# # Calendar methods
# from asg_to_calendar.events import Events

# # Reporting google calendar http errors
# from googleapiclient.errors import HttpError

# CLI output functions
from rich import print
from rich.prompt import Confirm

# # Display functions
# from .events import display_cmds, display_error, display_panel, display_prompt
# from .events import Events, ExitProgram


# ::SETUP -------------------------------------------------------------------------- #
# def callback(verbose: bool = False):
#     """
#     Manage users in the awesome CLI app.
#     """
#     print("Hello World again.")
#     if verbose:
#         log.setLevel(logging.DEBUG)
#         log.debug('Verbose mode has been selected. Switching to logging.DEBUG level')

app = typer.Typer(help="Awesome CLI user manager.")

# ::GLOBALS ------------------------------------------------------------------------ #


# ::CORE LOGIC --------------------------------------------------------------------- #
@app.command()
def create_events(
    file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    date_format: Annotated[
        str,
        typer.Option(
            help=display_strftime(), rich_help_panel="Customization and Utils"
        ),
    ] = False
) -> bool:
    '''
    Creates a Calendar event from a file
    '''
    log.debug('Starting create_events()')

    # Import file
    try:
        file_type = str(file).split('.')[-1] # Retrieve file extension
    except ValueError:
        raise ValueError('Could not find file type.')

    log.info(file_type)

    # service = Events()

    # created = False
    # events_gen = service.get_data()

    # try:
    #     events_list = []

    #     for item in events_gen:
    #         try:
    #             event = service.events().insert(calendarId='primary', body=item).execute()
    #             events_list.append(event)
    #             log.info(f'Event created: {event.get('htmlLink')}')
    #         except Exception:
    #             raise

    #     display_panel('Created all events.', 'Success')
        
    #     to_file = Confirm.ask('Would you like to save the event objects to a file?')

    #     if to_file:
    #         service.write_events(events_list)

    #     created = True

    # except TypeError:
    #     raise

    # return created

def delete_events(self) -> bool:
    '''
    Delete Google Calendar events
    '''
    self._log.debug('Starting delete_events()')

    deleted = False
    events_list = self.get_delete_data()

    # # Have user validate data
    # confirmation = Confirm.ask(
    #     f'Confirm if the transformed data above is correct '
    #     f'and to continue to delete from calendar'
    # )

    # if not confirmation:
    #     display_error(
    #         'User has confirmed that the data is [bold bright_red]incorrect.\n'
    #         'Exiting program...'
    #     )
    #     raise ExitProgram("User prompted to exit program.")

    # if events_list and confirmation:
    #     for sum, id in events_list:
    #         print(f'Deleting event: "{sum} - [green]{id}"')
    #         try:
    #             self.__service.events().delete(calendarId='primary', eventId=id).execute()
    #         except Exception:
    #             raise

    #     display_panel(f'Deleted all events.', 'Success')
    #     deleted = True
    
    return deleted

# ::EXECUTE ------------------------------------------------------------------------ #
if __name__ == "__main__":
    app()
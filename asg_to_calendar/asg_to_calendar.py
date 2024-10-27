#!/usr/bin/env python3
# Program Name:         program14.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Takes a spreadsheet of classes and assignments, and adds them as events to a
#   google calendar

# ::IMPORTS ------------------------------------------------------------------------ #
import logging
from logger import logger as log

from settings import COMMANDS, PROMPTS

import argparse

# Calendar methods
from events import Events

# Reporting google calendar http errors
from googleapiclient.errors import HttpError

# CLI output functions
from rich import print

# Display functions
from events import display_cmds, display_error, display_panel, display_prompt
from events import Events, ExitProgram


# ::SETUP -------------------------------------------------------------------------- #


# ::GLOBALS ------------------------------------------------------------------------ #


# ::CORE LOGIC --------------------------------------------------------------------- #
def main(
    verbose: str = False
):
    '''
    Driver for program14, providing CLI to user for Calendar methods
    ---
    Args:
        verbose (str): Enables debugging logs.  Defaults to false
    Returns:
        None
    '''
    # ::Parse Args ---------------------------------------------------------------- #
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug('Verbose mode has been selected. Switching to logging.DEBUG level')

    
    # ::Begin CLI ----------------------------------------------------------------- #
    # Define commands
    commands = COMMANDS
    choices = list(commands.keys())

    # Prompt user for a command
    try:
        user_cmd: str = display_prompt(
            PROMPTS['command'],
            help_func=display_cmds,
            choices=choices
        )
        display_panel(
            f'Command selected: [cyan1]{user_cmd}[/cyan1]',
            'Starting Process'
        )
    except ExitProgram:
        user_cmd = choices[-1]

    # Continue while choice != 'exit'
    while user_cmd != choices[-1]:
        success: bool = False
        args = None

        # Initialize Calendar object
        try:
            service = Events()
        except HttpError as e:
            log.debug(e, stack_info=True, exc_info=True)

        # Retrieve the Events method
        call_method = getattr(service, commands[user_cmd]['method'])

        try:
            success = call_method()
        except TypeError as e:
            log.debug(e, stack_info=True, exc_info=True)
            display_error('Could not convert the data into events')
        except ExitProgram as e:
            log.debug(e, stack_info=True, exc_info=True)
            break
        except Exception as e:
            log.debug(e, stack_info=True, exc_info=True)
            display_error('Exception occured. Try again')

        if success:
            title = 'Process Completed'
            msg_style = 'bright_green'
        else:
            title = 'Process Failed'
            msg_style = 'bright_red'

        display_panel(
            "Returning to [bold dark_green]command[default] menu...",
            title,
            style=msg_style
        )

        try:
            user_cmd: str = display_prompt(
                PROMPTS['command'],
                help_func=display_cmds,
                choices=choices
            )
            display_panel(
                f'Command selected: [cyan1]{user_cmd}[/cyan1]',
                'Starting Process'
            )
        except ExitProgram:
            user_cmd = choices[-1]

    # ::Requirement 3 -------------------------------------------------------------- #
    print('\n[bright_red]Requirement 3\n')
    print(
        f'I would award myself an "A" for this program.  I was able to fulfil the \n'
        f'requirements and showcase to the faux company the knowledge and skills\n'
        f'required to start as a python developer.  The program includes basic\n'
        f'logging, exception handling, and a cli for users to interface with. The\n'
        f'only knack I would give is that the CLI utilizes prompts, which was\n'
        f'a requirement in the assignment. Otherwise, I would have build it as a\n'
        f'standalone app or interfaced directly with main() arguments.'
    )

    # ::Requirement 4 -------------------------------------------------------------- #
    print('\n[bright_red]Requirement 4\n')
    print(
        f'I started with trying to find a problem that I wanted to solve.  I realized\n'
        f'copying and pasting assignments and due dates into a google calendar was\n'
        f'laborious.  I decided to create my own version of adding to a calendar\n'
        f'based off of the Blackboard API endpoint "gradebook/columns".  I am\n'
        f'satisfied with the overall result but disappointed I could not interact\n'
        f'with the blackboard API directly without violating any school policies.'
    )

# ::EXECUTE ------------------------------------------------------------------------ #
if __name__ == "__main__":
    main()
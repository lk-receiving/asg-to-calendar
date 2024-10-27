#!/usr/bin/env python3
# Program Name:         logger.py
# Program Author:       Lew Kim
# Date Created:         10/21/24
# Program Description:
#   Configures and creates a logger object for debugging.

# ::IMPORTS ------------------------------------------------------------------------ #
import logging

from rich.logging import RichHandler

from settings import LOGFILE


# ::Execute ------------------------------------------------------------------------- #
logger = logging.getLogger(__name__)

# the handler determines where the logs go: stdout/file
shell_handler = RichHandler(rich_tracebacks=True)
file_handler = logging.FileHandler(LOGFILE, mode='w')

logger.setLevel(logging.INFO)
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# The formatter determines what our logs will look like
fmt_shell = '%(message)s'
fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

shell_formatter = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)

# Hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(shell_handler)
logger.addHandler(file_handler)
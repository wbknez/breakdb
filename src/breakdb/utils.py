"""
Contains classes and functions that are intended as utilities.
"""
import logging
import string
import sys
from itertools import zip_longest


class ColorizingLogFormatter(logging.Formatter):
    """
    Represents an implementation of :class: 'Formatter' that adds color
    capability to a logging stream intended for use with a standard ANSI
    terminal.

    Please note that disabling colorized output allows this formatter to be
    used as a drop-in replacement for new-style formatted strings with
    project-style output.

    Attributes:
        colors (dict): A collection of ANSI color sequences associated by level.
    """

    CLEAR = {
        "debug": " - {}",
        "error": " !! {}",
        "info": "{}",
        "var": "{}",
        "warning": " * : {}"
    }

    COLORS = {
        "debug": " - {}",
        "error": " \033[1;91m!!\033[0m {}",
        "info": "{}",
        "var": "\033[1;37m{}\033[0m",
        "warning": " \033[1;93m*\033[0m {}"
    }

    def __init__(self, use_color):
        super().__init__()

        self.colors = ColorizingLogFormatter.COLORS if use_color else \
            ColorizingLogFormatter.CLEAR

    def format(self, record):
        message = record.msg if not record.args else self.formatMessage(record)
        return self.colors[record.levelname.lower()].format(message)

    def format_arg(self, arg, fmt):
        """
        Formats and colorizes a single argument.

        :param arg: The argument to format.
        :param fmt: The format to use.
        :return: A colorized argument.
        """
        is_float_fmt = fmt[2].startswith(".") and \
                       (fmt[2].endswith("f") or fmt[2].endswith("d"))
        arg_fmt = "{" + fmt[2] + "}" if not is_float_fmt else \
            "{" + fmt[1] + ":" + fmt[2] + "}"

        return self.colors["var"].format(arg_fmt.format(arg))

    def formatMessage(self, record):
        formats = string.Formatter().parse(record.msg)
        message = ""

        for arg, fmt in zip_longest(record.args, formats):
            message += fmt[0]

            if arg is not None:
                message += self.format_arg(arg, fmt)

        return message


def initialize_logging(quiet, use_color, verbose):
    """
    Initializes and configures Python's logging system to use colorized
    output and new(er) string formatting behavior.

    :param quiet: Whether or not to silence console output.
    :param use_color: Whether or not to use colorized output.
    :param verbose: Whether or not to enable verbose, or debug, output.
    """
    if quiet:
        return

    root = logging.getLogger()
    logger = logging.getLogger()

    root.handlers = []

    console_formatter = ColorizingLogFormatter(use_color)
    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

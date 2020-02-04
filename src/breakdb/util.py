"""
Contains classes and functions that are intended as utilities.
"""
import logging
import os
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
        "var": "\033[1m{}\033[0m",
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


def format_dataset(ds, indent=0, hide_code=False, hide_desc=False,
                   hide_value=False, top_level=False, flat=False,
                   use_color=True):
    """
    Returns the specified DICOM dataset as a printable string.

    :param ds: The dataset to format.
    :param indent: The indentation level.
    :param hide_code: Whether or not to display hexadecimal tag codes.
    :param hide_desc: Whether or not to display tag descriptions.
    :param hide_value: Whether or not to display tag values.
    :param top_level: Whether or not to only display top-level tags.
    :param flat: Whether or not to disable indentation entirely.
    :param use_color: Whether or not to use ANSI color codes.
    :return: A DICOM dataset as a formatted string.
    """
    def describe_element(elem):
        return elem.description()[:elem.descripWidth].ljust(elem.descripWidth)

    def format_element(elem):
        return "{}{}{}{}{}{}{}".format(
            "\033[1;37m" if use_color else "",
            str(elem.tag) if not hide_code else "",
            "\033[0m" if use_color else "",
            " " if not hide_code else "",
            describe_element(elem) if not hide_desc else "",
            " " if not hide_desc else "",
            elem.repval if not hide_value else "",
        )

    def format_sequence(seq):
        return "{}{}{}{}{}{}{} {}".format(
            "\033[1;37m" if use_color else "",
            str(seq.tag) if not hide_code else "",
            "\033[0m" if use_color else "",
            " " if not hide_code else "",
            seq.description() if not hide_desc else "",
            "   " if not hide_desc else "",
            str(len(seq.value)) if not hide_value else "",
            " item(s)" if not hide_value else ""
        )

    indent_str = "   " * indent if not flat else ""
    output = []

    for data in ds:
        if data.VR == "SQ":
            output.append(f"{indent_str}{format_sequence(data)}")

            if not top_level:
                for value in data:
                    output.append(format_dataset(value, indent + 1, hide_code,
                                                 hide_desc,
                                                 hide_value, top_level,
                                                 flat, use_color))
        else:
            output.append(f"{indent_str}{format_element(data)}")

    return "\n".join(output)


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


def supports_color_output():
    """
    Performs a minor check to determine whether or not the current output
    device (usually a terminal) supports ANSI color codes.

    :return: Whether or not ANSI color codes are supported.
    """
    has_ansi_term = 'TERM' in os.environ and os.environ['TERM'] == 'ANSI'
    has_tty_output = True

    for handle in [sys.stdout, sys.stderr]:
        has_tty_output &= handle.isatty()

    return has_ansi_term or has_tty_output

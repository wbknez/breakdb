"""
Contains classes and functions related to all actions that may be invoked
via the command line.
"""
from enum import IntEnum

from pydicom import dcmread

from breakdb.util import format_dataset


class ExitCode(IntEnum):
    """
    Represents the exit codes this project may produce.
    """

    FAILURE = 1
    """
    Represents a logic failure.
    """

    SUCCESS = 0
    """
    Represents a successful invocation.
    """


def print_tags(args):
    """
    Pretty-prints all tags in a specified file with options.

    This function is designed to be used in batch scripts and will always
    fail silently by returning a non-zero exit code.

    :param args: The user-chosen options to use.
    :return: An exit code (0 if success, otherwise 1).
    """
    try:
        ds = dcmread(args.FILE)

        print(format_dataset(ds, 0, args.hide_code, args.hide_desc,
                             args.hide_value, args.top_level,
                             args.flat, args.use_color))

        return ExitCode.SUCCESS
    except:
        return ExitCode.FAILURE

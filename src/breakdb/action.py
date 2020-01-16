"""
Contains classes and functions related to all actions that may be invoked
via the command line.
"""
import logging
from enum import IntEnum
from functools import partial
from multiprocessing.pool import Pool
from traceback import print_exc

import pandas as pd
from pydicom import dcmread

from breakdb.io import filter_files, COLUMN_NAMES, write_database, \
    read_database
from breakdb.merge import organize_parsed, merge_dicom
from breakdb.parse import parse_dicom
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


def create_database(args):
    """
    Creates a Pandas dataframe from DICOM files found by searching one or
    more user-specified directories.

    :param args: The user-chosen options to use.
    :return: An exit code (0 if success, otherwise 1).
    """
    logger = logging.getLogger(__name__)

    parser = partial(parse_dicom, skip_broken=args.skip_broken)
    merger = partial(merge_dicom, skip_broken=args.skip_broken)

    try:
        with Pool(processes=args.parallel) as pool:
            logger.info("Searching directories for DICOM files: {}.",
                        args.PATHS)
            logger.info("Parsing DICOM files...")

            parsed = pool.map(parser, filter_files(args.PATHS,
                                                   extensions=".dcm",
                                                   relative=args.relative))
            logger.debug("Parsed {} files.", len(parsed))
            logger.debug("Parsing complete.")

            logger.info("Organizing and merging parsed datasets into single "
                        "entries...")
            merged = pool.map(merger, organize_parsed(parsed))

            logger.debug("Merged {} parsed datasets into {} entries.",
                         len(parsed), len(merged))
            logger.debug("Merging complete.")

            logger.info("Creating database from entries...")
            db = pd.DataFrame(filter(None, merged), columns=COLUMN_NAMES)

            logger.debug("Deleted {} empty rows.", len(merged) - len(db))
            logger.debug("Final database size is {} entries.", len(db))

            logger.info("Serializing database to disk...")
            write_database(db, args.output)

            logger.debug("Wrote to file: {}.", args.output)

            logger.info("Database creation complete.")

        return ExitCode.SUCCESS
    except Exception as ex:
        logger.error("Could not create database: {}.", ex)

        if not args.quiet and args.verbose:
            print()
            print("Stack trace:")
            print_exc()

        return ExitCode.FAILURE


def export_database(args):
    """
    Exports a user-specified database in one format to another.

    :param args: The user-chosen options to use.
    :return: An exit code (0 if success, otherwise 1).
    """
    logger = logging.getLogger(__name__)

    try:
        write_database(read_database(args.FILE), args.output)

        return ExitCode.SUCCESS
    except Exception as ex:
        logger.error("Could not convert database to alternate format: {}.", ex)

        if not args.quiet and args.verbose:
            print()
            print("Stack trace:")
            print_exc()

        return ExitCode.FAILURE


def print_tags(args):
    """
    Pretty-prints all tags in a specified file with options.

    This function is designed to be used in batch scripts and will always
    fail silently by returning a non-zero exit code.

    :param args: The user-chosen options to use.
    :return: An exit code (0 if success, otherwise 1).
    """
    logger = logging.getLogger(__name__)

    try:
        ds = dcmread(args.FILE)

        print(format_dataset(ds, 0, args.hide_code, args.hide_desc,
                             args.hide_value, args.top_level,
                             args.flat, args.use_color))

        return ExitCode.SUCCESS
    except Exception as ex:
        logger.error("Could not read metadata: {}.", ex)

        return ExitCode.FAILURE

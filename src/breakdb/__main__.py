#!/usr/bin/env python3

"""
The main driver for the fracture (break) detection database project.
"""
import sys
from argparse import ArgumentParser

from breakdb.action import print_tags, create_database
from breakdb.util import initialize_logging, supports_color_output


def parse_args():
    """
    Creates and configures the command line parser for this project with all
    necessary options and their data (arguments, descriptions).

    :return: A collection of command line arguments, if any.
    """
    parser = ArgumentParser("breakdb", description="A utility to collate "
                                                   "X-ray imaging data into a "
                                                   "database for machine "
                                                   "learning algorithms.")

    parser.add_argument("-c", "--color", choices=["auto", "on", "off"],
                        help="enable colored console output", default="auto")
    parser.add_argument("-q", "--quiet", action="store_true",
                          help="disable console output", default=False)
    parser.add_argument("-v", "--verbose", action="store_true",
                          help="enable verbose console output", default=False)

    subparsers = parser.add_subparsers(dest="subparsers", required=True)

    create = subparsers.add_parser(name="create",
                                   description="Create a database from one "
                                               "or more DICOM files in a "
                                               "directory.")

    create.set_defaults(func=create_database)

    create.add_argument("-o", "--output", type=str,
                        help="file to output database to", required=True)
    create.add_argument("-p", "--parallel", type=int,
                        help="number of parallel processes", default=2)
    create.add_argument("-s", "--skip-broken", action="store_true",
                        help="ignore malformed DICOM files", default=False)
    create.add_argument("-r", "--relative", action="store_true",
                        help="encode relative paths", default=False)

    create.add_argument("PATHS", nargs="+", type=str,
                        help="")

    tags = subparsers.add_parser(name="print-tags",
                                 description="show all DICOM metadata tags "
                                             "in a file")
    tags.set_defaults(func=print_tags)

    tags.add_argument("--flat", action="store_true",
                      help="disable indentation", default=False)
    tags.add_argument("--hide-code", action="store_true",
                      help="do not print hexadecimal tag codes", default=False)
    tags.add_argument("--hide-desc", action="store_true",
                      help="do not print tag descriptions", default=False)
    tags.add_argument("--hide-value", action="store_true",
                      help="do not print tag values", default=False)
    tags.add_argument("--top-level", action="store_true",
                      help="only show top-level tags", default=False)
    tags.add_argument("FILE", help="file with one or more DICOM tags",
                      type=str)

    return parser.parse_args()


def main():
    """
    The application entry point.

    :return: An exit code.
    """
    args = parse_args()
    args.use_color = supports_color_output()

    if args.color == "off":
        args.use_color = False

    initialize_logging(args.quiet, args.use_color, args.verbose)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

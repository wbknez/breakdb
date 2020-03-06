#!/usr/bin/env python3

"""
The main driver for the fracture (break) detection database project.
"""
import sys
from argparse import ArgumentParser

from breakdb.action import print_tags, create_database, convert_database, \
    export_database
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

    convert = subparsers.add_parser(name="convert",
                                   description="convert a database in one "
                                               "format to another")

    convert.set_defaults(func=convert_database)

    convert.add_argument("-o", "--output", type=str,
                        help="file to output database to", required=True)

    convert.add_argument("FILE", type=str,
                        help="database file to convert")

    create = subparsers.add_parser(name="create",
                                   description="create a database from one "
                                               "or more DICOM files in a "
                                               "directory")

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
                        help="directories containing one or more DICOM files")

    export = subparsers.add_parser(name="export",
                                   description="export a database to the "
                                               "file system in a specific "
                                               "format")

    export.set_defaults(func=export_database)

    export.add_argument("-d", "--directory", required=True)
    export.add_argument("-f", "--force", action="store_true", default=False,
                        help="overwrite existing files and directories")
    export.add_argument("-n", "--no-master-list", action="store_true",
                        default=False, help="do not produce a master list")
    export.add_argument("-p", "--parallel", type=int,
                        help="number of parallel processes", default=2)
    export.add_argument("-s", "--skip-broken", action="store_true",
                        help="ignore malformed DICOM files", default=False)
    export.add_argument("-t", "--type", type=str, choices=["voc", "yolov3"],
                        required=True, help="the export format type")

    export.add_argument("--keep-aspect-ratio", action="store_true",
                        default=False, help="force resizing to obey aspect "
                                            "ratio")
    export.add_argument("--ignore-scaling", action="store_true",
                        default=False, help="ignore scaling parameters")
    export.add_argument("--ignore-windowing", action="store_true",
                        default=False, help="ignore windowing parameters")
    export.add_argument("--no-upscale", action="store_true", default=False,
                        help="disallow image upscaling")
    export.add_argument("--target-height", type=int, default=None,
                        help="target image height")
    export.add_argument("--target-width", type=int, default=None,
                        help="target image width")

    export.add_argument("FILE", type=str, help="database file to export")

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

"""
Contains classes and functions pertaining to database serialization.
"""
import os

from breakdb.io.export.voc import VOCDatabaseEntryExporter
from breakdb.io.export.yolo import YOLODatabaseEntryExporter
from breakdb.io.reading import CsvDatabaseReader, ExcelDatabaseReader, \
    JsonDatabaseReader
from breakdb.io.writing import CsvDatabaseWriter, ExcelDatabaseWriter, \
    JsonDatabaseWriter


_EXPORTERS = {
    "voc": VOCDatabaseEntryExporter(),
    "yolov3": YOLODatabaseEntryExporter()
}


_READERS = {
    ".csv": CsvDatabaseReader(),
    ".xlsx": ExcelDatabaseReader(),
    ".json": JsonDatabaseReader()
}


_WRITERS = {
    ".csv": CsvDatabaseWriter(),
    ".xlsx": ExcelDatabaseWriter(),
    ".json": JsonDatabaseWriter()
}


COLUMN_NAMES = [
    "ID",               # The SOP instance UID.
    "Series",           # The series UID.
    "Study",            # The study UID.
    "Classification",   # Whether or not a fracture is present (ground-truth).
    "Body Part",        # The type of body part imaged.
    "Width",            # The image width (in pixels).
    "Height",           # The image height (in pixels).
    "File Path",        # Location of image file on disk.
    "Scaling",          # Whether there is any scaling information.
    "Windowing",        # Whether or not there is any windowing information.
    "Annotation"        # All discovered annotations.
]


def filter_files(paths, extensions=None, relative=False):
    """
    Searches for all files in the specified collection of paths and filters
    them by the specified collection of admissible extensions.

    :param paths: A collection of directories to search.
    :param extensions: A collection of extensions to filter by.
    :param relative: Whether or not to use relative paths.
    :return: A generator over a collection of filtered files.
    """
    if not extensions:
        raise ValueError("At least one extension must be provided.")

    if isinstance(extensions, str):
        extensions = [extensions]

    resolver = os.path.abspath if not relative else os.path.relpath

    for file_path in paths:
        for root, _, files in os.walk(file_path, topdown=False):
            root = resolver(root)

            for file in files:
                for extension in extensions:
                    if file.endswith(extension):
                        yield os.path.join(root, file)


def get_entry_exporter(format_name):
    """
    Searches for and returns the database entry exporter associated with the
    specified format name.

    :param format_name: The file format to use.
    :return: A database entry exporter.
    """
    if format_name not in _EXPORTERS:
        raise KeyError(f"Cannot find exporter - unknown format: "
                       f"{format_name}.")

    return _EXPORTERS[format_name]


def read_database(file_path):
    """
    Reads a database located from the specified file on disk.

    :param file_path: The file to read a database from.
    :return: A database.
    :raises KeyError: If a reader cannot be found for a particular file path.
    """
    _, extension = os.path.splitext(file_path)

    if extension not in _READERS:
        raise KeyError(f"Cannot read database - unknown file extension:"
                       f" {file_path}.")

    with open(file_path, "r") as stream:
        return _READERS[extension].read(stream)


def write_database(db, file_path):
    """
    Writes the specified database to the specified file on disk.

    :param db: The database to write.
    :param file_path: The file to write the database to.
    :raises KeyError: If a writer cannot be found for a particular file path.
    """
    _, extension = os.path.splitext(file_path)

    if extension not in _WRITERS:
        raise KeyError(f"Cannot write database - unknown file extension: "
                       f"{file_path}")

    with open(file_path, "w") as stream:
        _WRITERS[extension].write(db, stream)

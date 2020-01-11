"""
Contains classes and functions related to decoding a database from various
formats.
"""
from abc import ABCMeta, abstractmethod
from csv import QUOTE_NONNUMERIC

from pandas import read_json, read_csv


class DatabaseReader(metaclass=ABCMeta):
    """
    Represents a mechanism for reading X-ray image databases from different
    formats on disk.
    """

    @abstractmethod
    def read(self, file_path):
        """
        Reads a database from the specified file on disk.

        :param file_path: The file to read a database from.
        :return: A database.
        """
        pass


class CsvDatabaseReader(DatabaseReader):
    """
    Represents an implementation of :class: 'DatabaseReader' that reads a
    previously created X-ray image database from a CSV file.
    """

    def read(self, file_path):
        with open(file_path, "r") as stream:
            return read_csv(stream, comment="#", encoding="utf-8",
                            memory_map=True, quoting=QUOTE_NONNUMERIC, sep=",")


class JsonDatabaseReader(DatabaseReader):
    """
    Represents an implementation of :class: 'DatabaseReader' that reads a
    previously created X-ray image database from a JSON file.
    """

    def read(self, file_path):
        with open(file_path, "r") as stream:
            return read_json(stream, typ="frame", orient="records")

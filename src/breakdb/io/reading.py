"""
Contains classes and functions related to encoding a database in various
formats.
"""
from abc import ABCMeta, abstractmethod

from pandas import read_json


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


class JsonDatabaseReader(DatabaseReader):
    """
    Represents an implementation of :class: 'DatabaseReader' that reads a
    previously created X-ray image database from a JSON file.
    """

    def read(self, file_path):
        with open(file_path, "r") as stream:
            return read_json(stream, typ="frame", orient="records")

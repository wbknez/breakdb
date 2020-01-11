"""
Contains classes and functions related to encoding a database in various
formats.
"""
from abc import abstractmethod, ABCMeta
from csv import QUOTE_NONNUMERIC


class DatabaseWriter(metaclass=ABCMeta):
    """
    Represents a mechanism for writing X-ray image databases from different
    formats to disk.
    """

    @abstractmethod
    def write(self, db, file_path):
        """
        Reads a database from the specified file on disk.

        :param db: The database to write.
        :param file_path: The file to write a database to.
        """
        pass


class CsvDatabaseWriter(DatabaseWriter):
    """
    Represents an implementation of :class: 'DatabaseWrite' that writes an
    X-ray image database to a CSV file.
    """

    def write(self, db, file_path):
        with open(file_path, "w") as stream:
            db.to_csv(stream, encoding="utf-8", header=True, index=True,
                      quoting=QUOTE_NONNUMERIC, sep=",")


class JsonDatabaseWriter(DatabaseWriter):
    """
    Represents an implementation of :class: 'DatabaseWrite' that writes an
    X-ray image database to a JSON file.
    """

    def write(self, db, file_path):
        with open(file_path, "w") as stream:
            db.to_json(stream, index=True, orient="records")

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
    def write(self, db, stream):
        """
        Reads a database from the specified file on disk.

        :param db: The database to write.
        :param stream: The stream to write a database to.
        """
        pass


class CsvDatabaseWriter(DatabaseWriter):
    """
    Represents an implementation of :class: 'DatabaseWrite' that writes an
    X-ray image database to a CSV file.
    """

    def write(self, db, stream):
        db.to_csv(stream, encoding="utf-8", header=True, index=False,
                  quoting=QUOTE_NONNUMERIC, sep=",")


class ExcelDatabaseWriter(DatabaseWriter):
    """
    Represents an implementation of :class: 'DatabaseWrite' that writes an
    X-ray image database to an Excel spreadsheet.
    """

    def write(self, db, stream):
        db.to_excel(stream, encoding="utf-8", header=True, index=False)


class JsonDatabaseWriter(DatabaseWriter):
    """
    Represents an implementation of :class: 'DatabaseWrite' that writes an
    X-ray image database to a JSON file.
    """

    def write(self, db, stream):
        db.to_json(stream, orient="records")

"""
Contains classes and functions pertaining to database serialization.
"""
import os


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

    for file_path in paths:
        for root, _, files in os.walk(file_path, topdown=False):
            root = os.path.abspath(root) if not relative else root

            for file in files:
                for extension in extensions:
                    if file.endswith(extension):
                        yield os.path.join(root, file)
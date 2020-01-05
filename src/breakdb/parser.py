"""
Contains classes and functions concerning the parsing of DICOM metadata into
usable programmatic structures.
"""
from breakdb.tag import CommonTag


class MissingTag(Exception):
    """
    Represents an exception that is raised when an expected tag is missing.
    """

    def __init__(self, tag):
        super().__init__(f"{tag} is expected but missing.")


def _get_tag_value(ds, tag):
    """
    Returns the value associated with the specified tag in the specified
    dataset.

    :param ds: The dataset to read.
    :param tag: The tag to find.
    :return: The value associated with a tag.
    :raises MissingTag: If the requested tag could not be found.
    """
    if tag.value not in ds:
        raise MissingTag(tag)

    return ds[tag]


def parse_common(ds):
    """
    Parses and returns a dictionary of the values of all common tags required
    to be in a DICOM dataset for this project.

    Please note that for a DICOM dataset that references another, the series
    identifier will be replaced to match the one contained in the referred
    file.  This function does not perform that operation.

    :param ds: The dataset to search.
    :return: A dictionary of common tag values.
    :raises MissingTag: If one or more tags could not be found.
    """
    return {
        _get_tag_value(ds, CommonTag.SOP_CLASS),
        _get_tag_value(ds, CommonTag.SOP_INSTANCE),
        _get_tag_value(ds, CommonTag.SERIES)
    }


def parse_dataset(ds):
    """
    Searches for, parses, and returns a dictionary of the values of as many
    tags as possible available in the specified DICOM dataset.

    :param ds: The dataset to search.
    :return: A dictionary of available tag values.
    :raises MissingTag: If one or more expected tags could not be found.
    """
    tags = {}

    tags += parse_common(ds)

    return tags
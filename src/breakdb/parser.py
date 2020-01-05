"""
Contains classes and functions concerning the parsing of DICOM metadata into
usable programmatic structures.
"""
from breakdb.tag import CommonTag, ReferenceTag


class MalformedSequence(Exception):
    """
    Represents an exception that is raised when an expected sequence is
    present but not formatted correctly.
    """

    def __init__(self, tag):
        super().__init__(f"{tag} is not a valid sequence.")


class MissingSequence(Exception):
    """
    Represents an exception that is raised when an expected sequence is
    missing.
    """

    def __init__(self, tag):
        super().__init__(f"{tag} is present but not a sequence.")


class MissingTag(Exception):
    """
    Represents an exception that is raised when an expected tag is missing.
    """

    def __init__(self, tag):
        super().__init__(f"{tag} is expected but missing.")


def _make_tag_dict(*values):
    """
    Converts the specified collection of tag values into a dictionary
    associated by tags.

    :param values: The collection of tag values to use.
    :return: A dictionary of tags and their associated values.
    """
    return {value.tag: value.value for value in values}


def get_sequence_value(ds, index, tag):
    """
    Returns the value associated with the specified tag in a sequence
    contained in the specified dataset.

    :param ds: The dataset to read.
    :param index: The index to use.
    :param tag: The tag to find.
    :return: The value associated with a tag in a sequence.
    :raises MalformedSequence: If the requested tag exists but is not a
    sequence.
    :raises MissingSequence: If the requested tag could not be found.
    """
    if tag.value not in ds:
        raise MissingSequence(tag)

    if ds[tag.value].VR != 'SQ' or len(ds[tag.value].value) <= index:
        raise MalformedSequence(tag)

    return ds[tag.value][index]


def get_tag_value(ds, tag):
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

    return ds[tag.value]


def has_reference(ds):
    """
    Returns whether or not the specified DICOM dataset contains a reference to
    another.

    :param ds: The dataset to search.
    :return: Whether or not a DICOM reference sequence is present.
    """
    return ReferenceTag.SEQUENCE.value in ds and \
        len(get_tag_value(ds, ReferenceTag.SEQUENCE).value) == 1 and \
        len(get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)) == 2


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
    return _make_tag_dict(
        get_tag_value(ds, CommonTag.SOP_CLASS),
        get_tag_value(ds, CommonTag.SOP_INSTANCE),
        get_tag_value(ds, CommonTag.SERIES)
    )


def parse_reference(ds):
    """
    Parses and returns a dictionary of the values of all tags associated
    with one DICOM referencing another for this project.

    :param ds: The dataset to search.
    :return: A dictionary of reference tag values.
    :raises MalformedSequence: If a tag exists but is not a sequence.
    :raises MissingSequence: If one or more sequence tags could not be found.
    :raises MissingTag: If one or more tags could not be found.
    """
    seq = get_sequence_value(ds, 0, ReferenceTag.SEQUENCE)
    obj = get_sequence_value(seq, 0, ReferenceTag.OBJECT)

    return {
        "ref": _make_tag_dict(
            get_tag_value(obj, ReferenceTag.SOP_CLASS),
            get_tag_value(obj, ReferenceTag.SOP_INSTANCE),
            get_tag_value(seq, ReferenceTag.SERIES)
    )}


def parse_dataset(ds):
    """
    Searches for, parses, and returns a dictionary of the values of as many
    tags as possible available in the specified DICOM dataset.

    :param ds: The dataset to search.
    :return: A dictionary of available tag values.
    :raises MissingTag: If one or more expected tags could not be found.
    """
    parsed = {}

    parsed += parse_common(ds)

    if has_reference(ds):
        parsed += parse_reference(ds)

    return parsed

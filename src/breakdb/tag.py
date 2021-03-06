"""
Contains classes and functions related to working with DICOM metadata tags.
"""
from enum import Enum, unique

from pydicom.tag import Tag


@unique
class AnnotationTag(Enum):
    """
    Represents a collection of DICOM tags that indicate whether one or more
    annotations are contained in a file and the data they may contain.
    """

    COUNT = Tag(0x0070, 0x0021)
    """
    Represents the number of individual points that comprise a geometry.
    
    For this project, this should always be "5" for an closed quadrilateral.
    """

    DATA = Tag(0x0070, 0x0022)
    """
    Represents the individual points as a pair of two-dimensional coordinates 
    that comprise a geometry.    
    """

    DIMENSIONS = Tag(0x0070, 0x0020)
    """
    Represents the planar dimensions (one dimensional, two dimensional, 
    etc.) coordinates are given as.
    
    For this project, this should always be "2".
    """

    OBJECT = Tag(0x0070, 0x0009)
    """
    Represents a single annotation.
    """

    SEQUENCE = Tag(0x0070, 0x0001)
    """
    Represents a collection of  annotations.    
    """

    TYPE = Tag(0x0070, 0x0023)
    """
    Represents the type of geometry.
    
    For this project, this should always be "POLYLINE".    
    """

    UNITS = Tag(0x0070, 0x0005)
    """
    Represents the dimension metric.
    
    For this project, this should always be "PIXEL".
    """


@unique
class CommonTag(Enum):
    """
    Represents a collection of DICOM tags that every file used as input to
    this project must have.
    """

    SOP_CLASS = Tag(0x0008, 0x0016)
    """
    Represents the (unique) SOP class identifier.
    """

    SOP_INSTANCE = Tag(0x0008, 0x0018)
    """
    Represents the (unique) SOP instance identifier.
    
    This tag is unique per file.
    """

    SERIES = Tag(0x0020, 0x000e)
    """
    Represents the (unique) series identifier.
    
    This tag is unique per series.
    """

    STUDY = Tag(0x0020, 0x000d)
    """
    Represents the (unique) study identifier.
    
    This tag is unique per study.    
    """


@unique
class MiscTag(Enum):
    """
    Represents a collection of DICOM tags that specify additional useful
    information.
    """

    BODY_PART = Tag(0x0018, 0x0015)
    """
    Represents the (specific) part of a subject's body under study for a 
    particular DICOM file.
    """


@unique
class PixelTag(Enum):
    """
    Represents a collection of DICOM tags that specify how an image
    contained within is formatted.
    """

    BITS_ALLOCATED = Tag(0x0028, 0x0100)
    """
    Represents the number of bits allocated per pixel.    
    """

    BITS_STORED = Tag(0x0028, 0x0101)
    """
    Represents the number of bits used (out of the total number allocated) per 
    pixel.    
    """

    COLUMNS = Tag(0x0028, 0x0011)
    """
    Represents the number of columns in an image.
    
    Please note this is not necessarily the same as the width, as the DICOM 
    standard specifies that this may be a multiple of the horizontal 
    downsampling factor.
    """

    DATA = Tag(0x7fe0, 0x0010)
    """
    Represents the (raw) pixel data in a single image.
    
    For purposes of this project, each DICOM may have a maximum of one image
    (buffer of pixel data) associated with it.
    """

    PHOTOMETRIC_INTERPRETATION = Tag(0x0028, 0x0004)
    """
    Represents the color space that bounds the (raw) pixel data which, 
    in turn, defines what color(s) each pixel may contain.
    
    For this project, most DICOM files with be in MONOCHROME1 or MONOCHROME2.
    """

    REPRESENTATION = Tag(0x0028, 0x0103)
    """
    Represents whether or not the (raw) pixel data is intended to be signed 
    or unsigned.    
    
    This value is expected to be either 0 (unsigned) or 1 (signed).
    """

    ROWS = Tag(0x0028, 0x0010)
    """
    Represents the number of rows in an image.
    
    Please note this is not necessarily the same as the height, as the DICOM 
    standard specifies that this may be a multiple of the vertical 
    downsampling factor.
    """

    SAMPLES_PER_PIXEL = Tag(0x0028, 0x0002)
    """
    Represents the number of color channels in each individual pixel.
    
    This value is expected to be 1 for grayscale images, otherwise 3.
    """


@unique
class ReferenceTag(Enum):
    """
    Represents a collection of DICOM tags that specify how one DICOM
    may reference information contained in another.
    """

    OBJECT = Tag(0x0008, 0x1140)
    """
    Represents a single reference to another DICOM file.
    """

    SEQUENCE = Tag(0x0008, 0x1115)
    """
    Represents a collection of references to other DICOM files.    
    """

    SERIES = Tag(0x0020, 0x000e)
    """
    Represents the (unique) series identifier.
        
    This tag is unique per series.
    """

    SOP_CLASS = Tag(0x0008, 0x1150)
    """
    Represents the (unique) SOP class identifier.            
    """

    SOP_INSTANCE = Tag(0x0008, 0x1155)
    """
    Represents the (unique) SOP instance identifier.
    
    This tag is unique per file.
    """


@unique
class ScalingTag(Enum):
    """
    Represents a collection of DICOM tags that specify how pixel data
    is converted from a storage format to visualization.
    """

    INTERCEPT = Tag(0x0028, 0x1052)
    """
    Represents the intercept of a linear transformation between pixel formats.
    """

    SLOPE = Tag(0x0028, 0x1053)
    """
    Represents the slope of a linear transformation between pixel formats.    
    """

    TYPE = Tag(0x0028, 0x1054)
    """
    Represents the units of visualization of a data image.
    """


class WindowingTag(Enum):
    """
    Represents a collection of DICOM tags that specify how pixel data is
    clipped, or bounded, to fit within a specific range.
    """

    CENTER = Tag(0x0028, 0x1050)
    """
    Represents the scaled window center.
    """

    FUNCTION = Tag(0x0028, 0x1056)
    """
    Represents the kind of function to use with a scaled window center and 
    width.
    """

    WIDTH = Tag(0x0028, 0x1051)
    """
    Represents the scaled window width.
    """


class MalformedSequence(Exception):
    """
    Represents an exception that is raised when an expected sequence is
    present but not formatted correctly.
    """

    def __init__(self, tag):
        super().__init__(f"Tag is not a valid sequence: {tag}.")


class MissingSequence(Exception):
    """
    Represents an exception that is raised when an expected sequence is
    missing.
    """

    def __init__(self, tag):
        super().__init__(f"Tag is present but not a sequence: {tag}.")


class MissingTag(Exception):
    """
    Represents an exception that is raised when an expected tag is missing.
    """

    def __init__(self, tag):
        super().__init__(f"Tag is expected but missing: {tag}.")


def check_sequence_length(ds, tag, expected_length):
    """
    Checks that the value of the specified tag in the specified dataset is
    equivalent to the specified expected value.

    :param ds: The dataset to read.
    :param tag: The tag to check.
    :param expected_length: The tag value to compare to.
    :return: Whether or not the check succeeded.
    :raises MissingTag: If the requested tag could not be found.
    """
    if not has_tag(ds, tag):
        raise MissingSequence(tag)

    return len(ds[tag.value].value) == expected_length


def check_tag(ds, tag, expected_value):
    """
    Checks that the value of the specified tag in the specified dataset is
    equivalent to the specified expected value.

    :param ds: The dataset to read.
    :param tag: The tag to check.
    :param expected_value: The tag value to compare to.
    :return: Whether or not the check succeeded.
    :raises MissingTag: If the requested tag could not be found.
    """
    if not has_tag(ds, tag):
        raise MissingTag(tag)

    return ds[tag.value].value == expected_value


def get_sequence(ds, tag):
    """
    Returns the sequence associated with the specified tag in the specified
    dataset.

    :param ds: The dataset to read.
    :param tag: The tag to find.
    :return: The sequence associated with a tag.
    :raises MalformedSequence: If the value associated with the requested
    tag is not a sequence.
    :raises MissingSequence: If the requested sequence could not be found.
    """
    if not has_tag(ds, tag):
        raise MissingSequence(tag)

    if ds[tag.value].VR != 'SQ':
        raise MalformedSequence(tag)

    return ds[tag.value]


def get_tag(ds, tag):
    """
    Returns the value associated with the specified tag in the specified
    dataset.

    :param ds: The dataset to read.
    :param tag: The tag to find.
    :return: The value associated with a tag.
    :raises MissingTag: If the requested tag could not be found.
    """
    if not has_tag(ds, tag):
        raise MissingTag(tag)

    return ds[tag.value]


def get_tag_at(ds, index, tag):
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
    if not has_tag(ds, tag):
        raise MissingSequence(tag)

    if ds[tag.value].VR != 'SQ' or len(ds[tag.value].value) <= index:
        raise MalformedSequence(tag)

    return ds[tag.value][index]


def has_sequence(ds, tag):
    """
    Returns whether or not a sequence with the specified tag is present in the
    specified dataset.

    :param ds: The dataset to search.
    :param tag: The tag to search for.
    :return: Whether or not a DICOM sequence is present.
    """
    return tag.value in ds and ds[tag.value].VR == 'SQ'


def has_tag(ds, tag):
    """
    Returns whether or not the specified tag is present in the specified
    dataset.

    :param ds: The dataset to search.
    :param tag: The tag to search for.
    :return: Whether or not a DICOM tag is present.
    """
    return tag.value in ds


def make_tag_dict(*values):
    """
    Converts the specified collection of tag values into a dictionary
    associated by tags.

    :param values: The collection of tag values to use.
    :return: A dictionary of tags and their associated values.
    """
    return {value.tag: value.value for value in values}


def make_tag_list(*values):
    """
    Converts the specified collection of tag values into a list.

    :param values: The collection of tag values to use.
    :return: A list of tag values.
    """
    return [value.value for value in values]


def replace_tag(src, src_tag, dest_tag=None):
    """
    Creates a new, small dictionary of tag values for use in overwriting
    the specified destination tag.

    :param src: The dataset to read from.
    :param src_tag: The source tag to find.
    :param dest_tag: The destination tag to replace.
    :return: A copy of the destination with updated tag(s) and value(s).
    :raises MissingTag: If the requested tag could not be found.
    """
    if not dest_tag:
        dest_tag = src_tag

    if not has_tag(src, src_tag):
        raise MissingTag(src_tag)

    return {dest_tag.value: src[src_tag.value]}

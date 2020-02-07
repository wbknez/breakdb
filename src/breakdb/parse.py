"""
Contains classes and functions concerning the parsing of DICOM metadata into
usable programmatic structures.
"""
import logging

from pydicom import dcmread
from pydicom.errors import InvalidDicomError

from breakdb.tag import CommonTag, ReferenceTag, AnnotationTag, get_tag, \
    get_tag_at, make_tag_dict, has_tag, get_sequence, has_sequence, PixelTag, \
    ScalingTag, MissingTag, MalformedSequence, MissingSequence, replace_tag, \
    MiscTag, check_tag, check_sequence_length, WindowingTag


class ParsingError(Exception):
    """
    Represents an exception that is raised when a problem is encountered
    while parsing a DICOM file for this project.
    """
    def init(self, file_path):
        super().__init__(f"Could not parse DICOM file: {file_path}")


def has_annotation(ds):
    """
    Returns whether or not the specified dataset contains a single annotation.

    :param ds: The dataset to search.
    :return: Whether or not a DICOM annotation is present.
    """
    return has_tag(ds, AnnotationTag.COUNT) and \
        has_tag(ds, AnnotationTag.DATA) and \
        has_tag(ds, AnnotationTag.DIMENSIONS) and \
        has_tag(ds, AnnotationTag.TYPE) and \
        has_tag(ds, AnnotationTag.UNITS) and \
        check_tag(ds, AnnotationTag.COUNT, 5) and \
        check_tag(ds, AnnotationTag.DIMENSIONS, 2) and \
        check_tag(ds, AnnotationTag.TYPE, "POLYLINE") and \
        check_tag(ds, AnnotationTag.UNITS, "PIXEL") and \
        check_sequence_length(ds, AnnotationTag.DATA, 10)


def has_annotations(ds):
    """
    Returns whether or not the specified DICOM dataset contains at least one
    (image) annotation.

    :param ds: The dataset to search.
    :return: Whether or not a DICOM annotation sequence is present.
    """
    if has_sequence(ds, AnnotationTag.SEQUENCE):
        for seq in get_sequence(ds, AnnotationTag.SEQUENCE):
            if has_sequence(seq, AnnotationTag.OBJECT):
                for obj in get_sequence(seq, AnnotationTag.OBJECT):
                    if has_annotation(obj):
                        return True

    return False


def has_misc(ds):
    """
    Returns whether or not the specified DICOM dataset contains miscellaneous
    information (e.g.: body part).

    :param ds: The dataset to search.
    :return: Whether or not miscellaneous DICOM data is present.
    """
    return has_tag(ds, MiscTag.BODY_PART)


def has_pixels(ds):
    """
    Returns whether or not the specified DICOM dataset contains raw imaging
    information (pixels).

    :param ds: The dataset to search.
    :return: Whether or not DICOM image data is present.
    """
    return has_tag(ds, PixelTag.BITS_ALLOCATED) and \
        has_tag(ds, PixelTag.BITS_STORED) and \
        has_tag(ds, PixelTag.COLUMNS) and \
        has_tag(ds, PixelTag.DATA) and \
        has_tag(ds, PixelTag.PHOTOMETRIC_INTERPRETATION) and \
        has_tag(ds, PixelTag.REPRESENTATION) and \
        has_tag(ds, PixelTag.ROWS) and \
        has_tag(ds, PixelTag.SAMPLES_PER_PIXEL)


def has_reference(ds):
    """
    Returns whether or not the specified DICOM dataset contains a reference to
    another.

    For purposes of this project, only one reference is allowed to be present.

    :param ds: The dataset to search.
    :return: Whether or not a DICOM reference sequence is present.
    """
    return has_sequence(ds, ReferenceTag.SEQUENCE) and \
        check_sequence_length(ds, ReferenceTag.SEQUENCE, 1) and \
        len(get_tag_at(ds, 0, ReferenceTag.SEQUENCE)) == 2


def has_scaling(ds):
    """
    Returns whether or not the specified DICOM dataset contains scaling
    information to convert imaging information (pixels) from a storage
    format to its original values for visualization.

    :param ds: The dataset to search.
    :return: Whether or not DICOM scaling parameters for image data is present.
    """
    return has_tag(ds, ScalingTag.INTERCEPT) and \
        has_tag(ds, ScalingTag.SLOPE) and \
        has_tag(ds, ScalingTag.TYPE)


def has_windowing(ds):
    """
    Returns whether or not the specified DICOM dataset contains windowing
    information to clip imaging information (pixels) into a specified range.

    :param ds: The dataset to search.
    :return: Whether or not DICOM windowing parameters for image data is
    present.
    """
    return has_tag(ds, WindowingTag.CENTER) and \
        has_tag(ds, WindowingTag.WIDTH)


def parse_annotation(ds):
    """
    Parses and returns a dictionary of values associated with a single
    annotation in a DICOM file for this project.

    :param ds: The dataset to search.
    :return: A dictionary of annotation tag values.
    :raises MissingTag: If one or more tags could not be found.
    """
    return [coord for coord in get_tag(ds, AnnotationTag.DATA)]


def parse_annotations(ds):
    """
    Parses and returns a dictionary of all annotations in a DICOM dataset
    for this project.

    :param ds: The dataset to search.
    :return: A dictionary of a collection of annotations.
    :raises MissingTag: If one or more tags could not be found.
    """
    annotations = []

    for seq in get_sequence(ds, AnnotationTag.SEQUENCE):
        if has_sequence(seq, AnnotationTag.OBJECT):
            for obj in get_sequence(seq, AnnotationTag.OBJECT):
                annotations.append(parse_annotation(obj))

    if not annotations:
        raise MissingTag(AnnotationTag.OBJECT)

    return {AnnotationTag.SEQUENCE.value: annotations}


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
    return make_tag_dict(
        get_tag(ds, CommonTag.SOP_CLASS),
        get_tag(ds, CommonTag.SOP_INSTANCE),
        get_tag(ds, CommonTag.SERIES),
        get_tag(ds, CommonTag.STUDY)
    )


def parse_misc(ds):
    """
    Parses and returns a dictionary of miscellaneous information in a DICOM
    dataset for this project.

    :param ds: The dataset to search.
    :return: A dictionary of miscellaneous information.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, MiscTag.BODY_PART)
    )


def parse_pixels(ds):
    """
    Parses and returns a dictionary of imaging information in a DICOM
    dataset for this project.

    :param ds: The dataset to search.
    :return: A dictionary of imaging information.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, PixelTag.COLUMNS),
        get_tag(ds, PixelTag.ROWS),
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
    seq = get_tag_at(ds, 0, ReferenceTag.SEQUENCE)
    obj = get_tag_at(seq, 0, ReferenceTag.OBJECT)

    return {
        ReferenceTag.SEQUENCE.value: make_tag_dict(
            get_tag(obj, ReferenceTag.SOP_CLASS),
            get_tag(obj, ReferenceTag.SOP_INSTANCE),
            get_tag(seq, ReferenceTag.SERIES)
        )}


def parse_scaling(ds):
    """
    Parses and returns a dictionary of image scaling information in a DICOM
    dataset for this project.

    :param ds: The dataset to search.
    :return: A dictionary of image scaling information.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, ScalingTag.INTERCEPT),
        get_tag(ds, ScalingTag.SLOPE),
        get_tag(ds, ScalingTag.TYPE),
    )


def parse_windowing(ds):
    """
    Parses and returns a dictionary of image windowing information in a
    DICOM dataset for this project.

    :param ds: The dataset to search.
    :return: A dictionary of image windowing information.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, WindowingTag.CENTER),
        get_tag(ds, WindowingTag.WIDTH)
    )


def parse_dataset(ds):
    """
    Searches for, parses, and returns a dictionary of the values of as many
    tags as possible available in the specified DICOM dataset.

    :param ds: The dataset to search.
    :return: A dictionary of available tag values.
    :raises MissingTag: If one or more expected tags could not be found.
    """
    parsed = parse_common(ds)

    if has_annotations(ds):
        parsed.update(parse_annotations(ds))

    if has_misc(ds):
        parsed.update(parse_misc(ds))

    if has_pixels(ds):
        parsed.update(parse_pixels(ds))

    if has_reference(ds):
        parsed.update(parse_reference(ds))

    if has_scaling(ds):
        parsed.update(parse_scaling(ds))

    if has_windowing(ds):
        parsed.update(parse_windowing(ds))

    return parsed


def parse_dicom(file_path, skip_broken):
    """
    Parses the specified DICOM file and returns a dictionary of all found
    tags and associated values relevant to this project.

    Setting :arg: 'skip_broken' to True will result in this function always
    succeeding.  Instead of throwing an exception, it will instead simply
    log any errors that occur as warnings and supply an empty dictionary.

    :param file_path: The path to the DICOM file to parse.
    :param skip_broken: Log but otherwise ignore any exceptions that take
    place, returning an empty dictionary as the result.
    :return: A dictionary of parsed tags and associated values.
    :raises InvalidDicomError: If no valid DICOM header is found.
    :raises MalformedSequence: If a sequence is unexpectedly empty.
    :raises MissingSequence: If one or more expected sequences could not be
    found.
    :raises MissingTag: If one or more expected tags could not be found.
    """
    logger = logging.getLogger(__name__)

    try:
        logger.debug("Parsing: {}.", file_path)

        with dcmread(file_path) as ds:
            parsed = parse_dataset(ds)

            if has_tag(parsed, PixelTag.COLUMNS) and \
                    has_tag(parsed, PixelTag.ROWS):
                parsed.update({PixelTag.DATA.value: file_path})

            if has_tag(parsed, ReferenceTag.SEQUENCE):
                ref = get_tag(parsed, ReferenceTag.SEQUENCE)

                parsed.update(replace_tag(ref, ReferenceTag.SOP_CLASS,
                                          CommonTag.SOP_CLASS))
                parsed.update(replace_tag(ref, ReferenceTag.SOP_INSTANCE,
                                          CommonTag.SOP_INSTANCE))
                parsed.update(replace_tag(ref, ReferenceTag.SERIES,
                                          CommonTag.SERIES))

            return file_path, parsed
    except (InvalidDicomError, MalformedSequence, MissingSequence,
            MissingTag) as ex:
        if skip_broken:
            logger.warning("Could not parse DICOM file: {}.", file_path)
            logger.warning("  Reason: {}.", ex)
            return file_path, {}
        else:
            raise ParsingError(file_path) from ex

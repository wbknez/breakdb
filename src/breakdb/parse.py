"""
Contains classes and functions concerning the parsing of DICOM metadata into
usable programmatic structures.
"""
from breakdb.tag import CommonTag, ReferenceTag, AnnotationTag, get_tag, \
    get_tag_at, make_tag_dict, has_tag, get_sequence, has_sequence, PixelTag, \
    ScalingTag


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
        has_tag(ds, AnnotationTag.UNITS)


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


def has_pixels(ds):
    """
    Returns whether or not the specified DICOM dataset contains raw imaging
    information (pixels).

    :param ds: The dataset to search.
    :return: Whether or not DICOM image data is present.
    """
    return has_tag(ds, PixelTag.COLUMNS) and \
        has_tag(ds, PixelTag.DATA) and \
        has_tag(ds, PixelTag.ROWS)


def has_reference(ds):
    """
    Returns whether or not the specified DICOM dataset contains a reference to
    another.

    For purposes of this project, only one reference is allowed to be present.

    :param ds: The dataset to search.
    :return: Whether or not a DICOM reference sequence is present.
    """
    return has_sequence(ds, ReferenceTag.SEQUENCE) and \
        len(get_sequence(ds, ReferenceTag.SEQUENCE).value) == 1 and \
        len(get_tag_at(ds, 0, ReferenceTag.SEQUENCE)) == 2


def has_scaling(ds):
    """
    Returns whether or not the specified DICOM dataset contains scaling
    information to convert imaging information (pixels) from a storage
    format to its original values for visualization.

    :param ds: The dataset to search.
    :return: Whether or not DICOM scaling data for image data is present.
    """
    return has_tag(ds, ScalingTag.CENTER) and \
        has_tag(ds, ScalingTag.INTERCEPT) and \
        has_tag(ds, ScalingTag.SLOPE) and \
        has_tag(ds, ScalingTag.TYPE) and \
        has_tag(ds, ScalingTag.WIDTH)


def parse_annotation(ds):
    """
    Parses and returns a dictionary of values associated with a single
    annotation in a DICOM file for this project.

    :param ds: The dataset to search.
    :return: A dictionary of annotation tag values.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, AnnotationTag.COUNT),
        get_tag(ds, AnnotationTag.DATA),
        get_tag(ds, AnnotationTag.DIMENSIONS),
        get_tag(ds, AnnotationTag.TYPE),
        get_tag(ds, AnnotationTag.UNITS)
    )


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
        get_tag(ds, CommonTag.SERIES)
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


def parse_scaling(ds):
    """
    Parses and returns a dictionary of image scaling information in a DICOM
    dataset for this project.

    :param ds: The dataset to search.
    :return: A dictionary of image scaling information.
    :raises MissingTag: If one or more tags could not be found.
    """
    return make_tag_dict(
        get_tag(ds, ScalingTag.CENTER),
        get_tag(ds, ScalingTag.INTERCEPT),
        get_tag(ds, ScalingTag.SLOPE),
        get_tag(ds, ScalingTag.TYPE),
        get_tag(ds, ScalingTag.WIDTH)
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

    if has_annotations(ds):
        parsed += parse_annotations(ds)

    if has_pixels(ds):
        parsed += parse_pixels(ds)

    if has_reference(ds):
        parsed += parse_reference(ds)

    if has_scaling(ds):
        parsed += parse_scaling(ds)

    return parsed

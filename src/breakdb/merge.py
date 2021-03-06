"""
Contains classes and functions concerning the merging of DICOM metadata
during data discovery.
"""
import logging
from collections import defaultdict

from breakdb.tag import has_tag, get_tag, CommonTag, AnnotationTag, \
    ScalingTag, PixelTag, MiscTag, MissingTag, WindowingTag
from breakdb.util import remove_duplicates


class DuplicateDICOM(Exception):
    """
    Represents an exception that is raised alongside a :class: 'TagConflict'
    for pixel data only.
    """

    def __init__(self, uid, original, duplicate):
        super().__init__(f"Duplicate image found for: {uid}.\n"
                         f"  Pixel data in: {original} and: {duplicate}.")


class MergingError(Exception):
    """
    Represents an exception that is raised when a problem is encountered
    while parsing a DICOM file for this project.
    """

    def __init__(self, uid):
        super().__init__(f"Could not merge datasets for: {uid}")


class TagConflict(Exception):
    """
    Represents an exception that is raised when an attempt is made to merge
    a tag that already exists in a destination dataset and whose value is
    expected to be identical to another source.
    """

    def __init__(self, tag, src, dest):
        super().__init__(f"{tag} differs between expected identical "
                         f"datasets.  Value should be "
                         f"{get_tag(dest, tag)} but is {get_tag(src, tag)}.")


def make_database_entry(merged):
    """
    Creates and returns a collection of relevant and correctly formatted DICOM
    tag values from the specified merged dataset for use as a single row in
    a Pandas dataframe.

    :param merged: The dataset to search.
    :return: A collection of tag values.
    :raises MissingTag: If a requested tag could not be found.
    """
    return [
        get_tag(merged, CommonTag.SOP_INSTANCE),
        get_tag(merged, CommonTag.SERIES),
        get_tag(merged, CommonTag.STUDY),
        len(get_tag(merged, AnnotationTag.SEQUENCE)) > 0,
        get_tag(merged, MiscTag.BODY_PART) \
            if has_tag(merged, MiscTag.BODY_PART) else "Unknown",
        get_tag(merged, PixelTag.COLUMNS),
        get_tag(merged, PixelTag.ROWS),
        get_tag(merged, PixelTag.DATA),
        has_tag(merged, ScalingTag.INTERCEPT) and \
            has_tag(merged, ScalingTag.SLOPE),
        has_tag(merged, WindowingTag.CENTER) and \
            has_tag(merged, WindowingTag.WIDTH),
        remove_duplicates(get_tag(merged, AnnotationTag.SEQUENCE))
    ]


def merge_sequence(src, dest, tag):
    """
    Attempts to copy the list of values associated with the specified tag in
    the specified source dataset into the specified destination.

    :param src: The source dataset to read from.
    :param dest: The destination dataset to write to.
    :param tag: The tag to use.
    :return: A new, merged dataset.
    """
    if not has_tag(src, tag):
        return dest

    if not has_tag(dest, tag):
        dest[tag.value] = []

    return {tag.value: dest[tag.value] + src[tag.value]}


def merge_tag(src, dest, tag):
    """
    Attempts to copy the value associated with the specified tag in the
    specified source dataset into the specified destination.

    This function utilizes the following rules to merge a single tag:
        - If the source dataset does not contain the tag, or the source
        dataset and destination both contain the tag with the same value,
        then the destination is returned unmodified.
        - If the destination and source both contain the tag but the values
        differ, then an exception is thrown.
        - If the destination does not contain the tag and the source does,
        then the value of that tag is copied from the source to the
        destination and the modified dataset is returned.

    :param src: The source dataset to read from.
    :param dest: The destination dataset to write to.
    :param tag: The tag to use.
    :return: A new, merged dataset.
    :raises TagConflict: If both dest and src contain the same tag but the
    value associated with it is different.
    """
    if not has_tag(src, tag):
        return dest

    if has_tag(dest, tag) and \
            get_tag(dest, tag) != get_tag(src, tag):
        raise TagConflict(tag, src, dest)

    return {tag.value: get_tag(src, tag)}


def merge_dataset(src, dest):
    """
    Combines any relevant data from the specified source dataset with that
    of the destination dataset.

    :param src: The source dataset to search.
    :param dest: The destination dataset to write to.
    :return: A modified destination dataset.
    :raises DuplicateDICOM: If conflicting pixel data tags are found.
    :raises TagConflict: If a source tag conflicts with a previously set
    destination.
    """
    tags = [
        CommonTag.SOP_CLASS,
        CommonTag.SOP_INSTANCE,
        CommonTag.SERIES,
        CommonTag.STUDY,
        MiscTag.BODY_PART,
        PixelTag.COLUMNS,
        PixelTag.ROWS,
        ScalingTag.INTERCEPT,
        ScalingTag.SLOPE,
        ScalingTag.TYPE,
        WindowingTag.CENTER,
        WindowingTag.WIDTH
    ]

    for tag in tags:
        dest.update(merge_tag(src, dest, tag))

    dest.update(merge_sequence(src, dest, AnnotationTag.SEQUENCE))

    try:
        dest.update(merge_tag(src, dest, PixelTag.DATA))
    except TagConflict:
        raise DuplicateDICOM(get_tag(dest, CommonTag.SOP_INSTANCE),
                             get_tag(dest, PixelTag.DATA),
                             get_tag(src, PixelTag.DATA))

    return dest


def merge_dicom(parsed, skip_broken, ignore_duplicates=False):
    """
    Attempts to merge all of the specified parsed datasets into a single
    database entry.

    :param parsed: The collection of parsed datasets to merge.
    :param skip_broken: Whether or not to ignore malformed datasets.
    :param ignore_duplicates: Whether or not to ignore duplicate but
    mismatched pixel data entries.
    :return: A collection of relevant DICOM tags.
    :raises MissingTag: If a requested tag could not be found.
    :raises TagConflict: If a source tag conflicts with a previously set
    destination.
    """
    logger = logging.getLogger(__name__)
    merged = {AnnotationTag.SEQUENCE.value: []}

    uid, to_merge = parsed

    logger.debug("Merging {} datasets for: {}.", len(to_merge), uid[0])

    for ds in to_merge:
        try:
            merged = merge_dataset(ds, merged)
        except DuplicateDICOM as dd:
            if ignore_duplicates:
                logger.warning("Did not merge datasets from duplicate DICOMs.")
                logger.warning("  Reason: {}.", dd)
            else:
                raise MergingError(uid[0]) from dd
        except TagConflict as tc:
            if skip_broken:
                logger.warning("Could not merge datasets for: {}.", uid[0])
                logger.warning("  Reason: {}.", tc)
            else:
                raise MergingError(uid[0]) from tc

    try:
        return make_database_entry(merged)
    except MissingTag as mt:
        if skip_broken:
            logger.warning("Could not create database entry for: {}.", uid[0])
            logger.warning("  Reason: {}.", mt)
            return {}
        else:
            logger.error("Could not create database entry for: {}.", uid[0])
            raise MergingError(uid[0]) from mt


def organize_parsed(parsed):
    """
    Organizes the specified parsed datasets into a dictionary of lists,
    where each list contains all datasets with a particular SOP instance
    identifier.

    By design, this function silently skips broken datasets (empty
    datasets).  This is because if such datasets are present, then it
    follows that the parsing function was instructed to skip broken or
    malformed DICOM files as well.  This function then works as a
    best-effort attempt to organize all fragments of a dataset into a usable
    whole.

    :param parsed: A collection of parsed DICOM files.
    :return: A dictionary of datasets associated by SOP instance UID.
    """
    to_merge = defaultdict(list)

    for file_path, ds in parsed:
        if ds:
            uid = (get_tag(ds, CommonTag.SOP_INSTANCE),
                   get_tag(ds, CommonTag.SERIES))
            to_merge[uid].append(ds)

    return list(to_merge.items())

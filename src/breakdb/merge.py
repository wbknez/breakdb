"""
Contains classes and functions concerning the merging of DICOM metadata
during data discovery.
"""
import logging
from collections import defaultdict

from breakdb.tag import has_tag, get_tag, CommonTag, AnnotationTag, \
    ScalingTag, PixelTag, MiscTag, MissingTag


class TagConflict(Exception):
    """
    Represents an exception that is raised when an attempt is made to merge
    a tag that already exists in a destination dataset and whose value is
    expected to be identical to another source.
    """

    def __init__(self, tag):
        super().__init__(f"{tag} differs between expected identical datasets.")


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
        len(get_tag(merged, AnnotationTag.SEQUENCE)) > 0,
        get_tag(merged, MiscTag.BODY_PART) \
            if has_tag(merged, MiscTag.BODY_PART) else "Unknown",
        get_tag(merged, PixelTag.COLUMNS),
        get_tag(merged, PixelTag.ROWS),
        get_tag(merged, PixelTag.DATA),
        [
            get_tag(merged, ScalingTag.CENTER),
            get_tag(merged, ScalingTag.WIDTH),
            get_tag(merged, ScalingTag.SLOPE),
            get_tag(merged, ScalingTag.INTERCEPT),
            get_tag(merged, ScalingTag.TYPE)
        ],
        get_tag(merged, AnnotationTag.SEQUENCE)
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
        raise TagConflict(tag)

    return {tag.value: get_tag(src, tag)}


def merge_dataset(src, dest):
    """
    Combines any relevant data from the specified source dataset with that
    of the destination dataset.

    :param src: The source dataset to search.
    :param dest: The destination dataset to write to.
    :return: A modified destination dataset.
    :raises TagConflict: If a source tag conflicts with a previously set
    destination.
    """
    tags = [
        CommonTag.SOP_CLASS,
        CommonTag.SOP_INSTANCE,
        CommonTag.SERIES,
        MiscTag.BODY_PART,
        PixelTag.COLUMNS,
        PixelTag.DATA,
        PixelTag.ROWS,
        ScalingTag.CENTER,
        ScalingTag.INTERCEPT,
        ScalingTag.SLOPE,
        ScalingTag.TYPE,
        ScalingTag.WIDTH
    ]

    for tag in tags:
        dest.update(merge_tag(src, dest, tag))

    dest.update(merge_sequence(src, dest, AnnotationTag.SEQUENCE))

    return dest


def merge_dicom(parsed, skip_broken):
    """
    Attempts to merge all of the specified parsed datasets into a single
    database entry.

    :param parsed: The collection of parsed datasets to merge.
    :param skip_broken: Whether or not to ignore malformed datasets.
    :return: A collection of relevant DICOM tags.
    :raises MissingTag: If a requested tag could not be found.
    :raises TagConflict: If a source tag conflicts with a previously set
    destination.
    """
    logger = logging.getLogger(__name__)
    merged = {AnnotationTag.SEQUENCE.value: []}

    file_path, to_merge = parsed

    for ds in to_merge:
        try:
            merged = merge_dataset(ds, merged)
        except TagConflict as tc:
            if skip_broken:
                logger.warning("Could not merge datasets for: {}.", file_path)
                logger.warning("  Reason: {}.", tc)
            else:
                logger.error("Could not merge datasets for: {}.", file_path)
                raise

    try:
        return make_database_entry(merged)
    except MissingTag as mt:
        if skip_broken:
            logger.warning("Could not create database entry for: {}.",
                           file_path)
            logger.warning("  Reason: {}.", mt)
            return {}
        else:
            logger.error("Could not create database entry for: {}.", file_path)
            raise


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
            to_merge[get_tag(ds, CommonTag.SOP_INSTANCE)].append(ds)

    return list(to_merge.items())

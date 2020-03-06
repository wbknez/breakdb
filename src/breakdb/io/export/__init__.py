"""
Contains classes and functions related to exporting collated DICOM databases to
different file structures.
"""
import os
import shutil
from abc import ABCMeta, abstractmethod


from breakdb.io.image import read_from_dataset, format_as


class ExportEntryFormatError(Exception):
    """
    Represents an exception that is raised when an error is encountered
    while attempting to export a DICOM database entry to an annotated file
    format.
    """

    def __init__(self, name, export_type):
        super().__init__(f"Could not format entry: {name} as: {export_type}.")


class DatabaseEntryExporter(metaclass=ABCMeta):
    """
    Represents a mechanism for exporting a single entry from a collated DICOM
    database to a file-based annotation.
    """

    @abstractmethod
    def create_directory_structure(self, base_dir, force=False):
        """
        Creates the directory structure expected for a custom formatted
        dataset.

        :param base_dir: The directory in which to create the directory
        structure.
        :param force: Whether or not to overwrite a directory if it already
        exists.
        :return: A tuple containing the annotation, image, and master list
        directory paths.
        """
        pass

    @abstractmethod
    def export(self, ds, name, base_dir, target_width=None, target_height=None,
               ignore_scaling=False, ignore_windowing=True,
               keep_aspect_ratio=True, no_upscale=False, skip_broken=False):
        """
        Exports the specified database entry

        :param ds: The DICOM dataset to use.
        :param name: The base name to use for exportation.
        :param base_dir: The directory in which to export the entry.
        :param target_width: The maximum width to resize the image to.
        :param target_height: The maximum height to resize the image to.
        :param ignore_scaling: Whether or not to ignore, or not apply,
        any applicable scaling operations.
        :param ignore_windowing: Whether or not to ignore, or not apply,
        any applicable windowing operations.
        :param keep_aspect_ratio: Whether or not to ensure the aspect ratio
        stays the same during (any) resize operations.
        :param no_upscale: Whether or not to forbid upscaling.
        :param skip_broken: Whether or not to ignore I/O errors.
        :return: A tuple containing the master list identifier and
        classification.
        """
        pass


def export_image(ds, file_path, target_width=None, target_height=None,
                 ignore_scaling=False, ignore_windowing=False,
                 keep_aspect_ratio=True, no_upscale=False):
    """
    Exports an image from the specified dataset with the specified parameters.

    :param ds: The DICOM dataset to use.
    :param file_path: The file to save the image data to.
    :param target_width: The maximum width to resize the image to.
    :param target_height: The maximum height to resize the image to.
    :param ignore_scaling: Whether or not to ignore, or not apply,
    any applicable scaling operations.
    :param ignore_windowing: Whether or not to ignore, or not apply,
    any applicable windowing operations.
    :param keep_aspect_ratio: Whether or not to ensure the aspect ratio
    stays the same during (any) resize operations.
    :param no_upscale: Whether or not to forbid upscaling.
    :return: A tuple containing the exported image dimensions and
    transformation for coordinate conversion.
    """
    attrs, arr = read_from_dataset(ds, ignore_scaling=ignore_scaling,
                                   ignore_windowing=ignore_windowing)
    image, transform = format_as(attrs, arr, target_width,
                                 target_height, keep_aspect_ratio,
                                 no_upscale)

    image.save(file_path)

    return (image.width, image.height, attrs[2]), transform


def make_directory(dir_path, force=False):
    """
    Creates the specified directory if it does not exist, otherwise
    overwrites it if the specified flag is set.

    If the directory exists and the flag is not set then an exception will
    be raised.

    :param dir_path: The path to the directory to create.
    :param force: Whether or not to overwrite a directory if it already exists.
    :raises FileExistsError: If a directory alreadt exists and the force
    flag is not set.
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        if force:
            shutil.rmtree(dir_path)
            os.mkdir(dir_path)
        else:
            raise

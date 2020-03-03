"""

"""
from abc import ABCMeta, abstractmethod


from breakdb.io.image import read_from_dataset, format_as


class ExportEntryFormatError(Exception):
    """
    Represents an exception that is raised when an error is encountered
    while attempting to export a DICOM database entry to an annotated file
    format.
    """

    def __init__(self, index, file_path, export_type):
        super().__init__(f"Could not format row {index} as {export_type} "
                         f"with image: {file_path}.")


class AnnotationExporter(metaclass=ABCMeta):
    """
    Represents a mechanism for exporting a collated DICOM database to a
    file-based annotation structure.
    """

    @abstractmethod
    def create_bounding_box(self, coords, width, height):
        """
        Converts the specified collection of coordinates and specified image
        dimensions into a format compatible bounding box.

        :param coords: The DICOM annotation as a list of single coordinates.
        :param width: The maximum bounding width.
        :param height: The maximum bounding height.
        :return: A formatted bounding box.
        """
        pass


def export_image(ds, file_path, target_width=None, target_height=None,
                 ignore_scaling=False, ignore_windowing=False,
                 keep_aspect_ratio=True, no_upscale=False):
    """
    Exports an image from the specified dataset with the specified parameters.

    :param ds: The DICOM dataset to use.
    :param file_path: The
    :param target_width: The maximum width to resize the image to.
    :param target_height: The maximum height to resize the image to.
    :param ignore_scaling: Whether or not to ignore, or not apply,
    any applicable scaling operations.
    :param ignore_windowing: Whether or not to ignore, or not apply,
    any applicable windowing operations.
    :param keep_aspect_ratio: Whether or not to ensure the aspect ratio
    stays the same during (any) resize operations.
    :param no_upscale: Whether or not to forbid upscaling.
    :return: A transformation for coordinate conversion.
    """
    attrs, arr = read_from_dataset(ds, ignore_scaling=ignore_scaling,
                                   ignore_windowing=ignore_windowing)
    image, transform = format_as(attrs, arr, target_width,
                                 target_height, keep_aspect_ratio,
                                 no_upscale)

    image.save(file_path)

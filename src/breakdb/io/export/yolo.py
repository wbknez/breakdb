"""
Contains classes and functions pertaining to the creation of YOLOv3 datasets
from a collated DICOM database.

Please note that there is no standard YOLOv3 data format.  This module
exports a DICOM database to the format expected for a custom dataset usable
by the following YOLOv3 implementation:
    https://github.com/eriklindernoren/PyTorch-YOLOv3
"""
import numpy as np


def create_bounding_box(coords, width, height):
    """
    Converts the specified collection of coordinates and specified image
    dimensions into a YOLOv3 compatible bounding box.

    :param coords: The DICOM annotation as a list of single coordinates.
    :param width: The width of an image.
    :param height: The height of an image.
    :return: A YOLOv3 bounding box.
    """
    x = np.array([value for value in coords[0::2]], dtype=np.float)
    y = np.array([value for value in coords[1::2]], dtype=np.float)

    x_ratio = (np.max(x) - np.min(x)) / width
    y_ratio = (np.max(y) - np.min(y)) / height

    return [x_ratio / 2.0, y_ratio / 2.0, x_ratio, y_ratio]

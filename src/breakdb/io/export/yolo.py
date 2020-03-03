"""
Contains classes and functions pertaining to the creation of YOLOv3 datasets
from a collated DICOM database.

Please note that there is no standard YOLOv3 data format.  This module
exports a DICOM database to the format expected for a custom dataset usable
by the following YOLOv3 implementation:
    https://github.com/eriklindernoren/PyTorch-YOLOv3
"""
import logging
import os

import numpy as np

from breakdb.io.export import AnnotationExporter
from breakdb.io.image import read_from_dataset, format_as, \
    transform_coordinate_collection


class YOLOEntryFormatError(Exception):
    """
    Represents an exception that is raised when an error is encountered
    while attempting to format a DICOM database entry as a YOLOv3 dataset.
    """

    def __init__(self, index, file_path):
        super().__init__(f"Could not format row {index} as a YOLO entry with "
                         f"image: {file_path}.")


class YOLOAnnotationExporter(AnnotationExporter):
    """

    """

    def __init__(self):
        super().__init__()

    def create_bounding_box(self, coords, width, height):
        x = np.array([value for value in coords[0::2]], dtype=np.float)
        y = np.array([value for value in coords[1::2]], dtype=np.float)

        x_max = np.max(x)
        x_min = np.min(x)

        y_max = np.max(y)
        y_min = np.min(y)

        return [
            (x_max + x_min) / (2.0 * width),
            (y_max + y_min) / (2.0 * height),
            (x_max - x_min) / width,
            (y_max - y_min) / height
        ]


def create_annotation(classification, coords, width, height):
    """
    Creates a single YOLOv3 compatible text annotation with the specified
    classification and collection of coordinates, each of which is scaled to
    the specifiied width and height.

    :param classification: The classification, or label, of an annotated image.
    :param coords: The DICOM annotation as a list of single coordinates.
    :param width: The width of an annotated image.
    :param height: The height of an annotated image.
    :return: A YOLOv3 annotation.
    """
    return f"{classification} " \
           f"{' '.join(map(str, create_bounding_box(coords, width, height)))}"


def create_annotations(classification, annotations, width, height):
    """
    Creates a collection of YOLOv3 compatible text annotations for the
    specified annotation collection, each with the specified classification
    and scaled to the specified width and height.

    :param classification: The classification, or label, of an annotated image.
    :param annotations: A collection of annotations from an image.
    :param width: The width of an annotated image.
    :param height: The height of an annotated image.
    :return: A collection of YOLOv3 annotations.
    """
    if not annotations:
        return ["0 0.0 0.0 0.0 0.0"]

    txts = []

    for annot in annotations:
        txts.append(
            create_annotation(classification, annot, width, height)
        )

    return txts


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


def create_directory_structure(dir_path):
    """
    Creates the directory structure expected for a Yolov3 custom dataset.

    :param dir_path: The directory in which to create the directory structure.
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    os.mkdir(os.path.join(dir_path, "images"))
    os.mkdir(os.path.join(dir_path, "labels"))


def convert_entry_to_yolo(index, db, annotation_path, image_path,
                          resize_width=None, resize_height=None,
                          skip_broken=False):
    """
    Converts a single entry with the specified index in the specified
    database to a YOLOv3 compatible annotation with associated image that is
    stored in the specified path.

    :param index: The (row) index to use.
    :param db: The database to search.
    :param annotation_path: The Pascal VOC annotation storage path.
    :param image_path: The Pascal VOC image storage path.
    :param resize_width: The width to resize the image to (optional).
    :param resize_height: The height to resize the image to (optional).
    :param skip_broken: Whether or not to ignore malformed datasets.
    """
    logger = logging.getLogger(__name__)

    try:
        ds = db.iloc[index, :]

        annotations = ds["Annotation"]
        classification = int(ds["Classification"])
        width = ds["Width"]
        height = ds["Height"]

        base_name = f"{index:0{len(str(len(db)))}}"
        image_path = os.path.join(image_path, base_name) + ".jpg"
        label_path = os.path.join(annotation_path, base_name) + ".txt"

        logger.info("Exporting row: {} using base name: {}.", index, base_name)

        logger.debug("Loading image for row: {} with file name: {}.", index,
                     ds["File Path"])

        attrs, arr = read_from_dataset(index, db, ignore_windowing=True)
        image = format_as(attrs, arr, resize_width, resize_height)

        logger.debug("Saving image for row: {} to: {}.", index, image_path)
        image.save(image_path)
        print("Wrote: {} successfully.", image_path)

        logger.debug("Creating YOLO annotation for row: {}.", index)

        if resize_width or resize_height:
            logger.debug("Scaling annotation coordinates to new image size: "
                         "{}x{} -> {}x{}.", width, height, image.width,
                         image.height)
            annotations = transform_coordinate_collection(annotations,
                                                          width, height,
                                                          image.width,
                                                          image.height)

        txts = create_annotations(classification, annotations, width, height)

        logger.debug("Saving YOLO annotation for row: {} to: {}.", index,
                     label_path)
        with open(label_path, "w") as label:
            for txt in txts:
                print(txt, file=label)

        logger.debug("Wrote: {} successfully.", label_path)
    except Exception as ex:
        if skip_broken:
            logger.warning("Could not create YOLO entry for index: {}.", index)
            logger.warning("  Reason: {}.", ex)
        else:
            raise YOLOEntryFormatError(index, db["File Path"][index]) from ex


def write_auxiliary_files(dir_path, class_names):
    """
    Outputs additional files to complete the YOLOv3 dataset, including
    class names.

    :param dir_path: The directory in which to create the files.
    :param class_names: The collection of class names to use.
    """
    with open(os.path.join(dir_path, "classes.names"), "w") as class_file:
        for name in class_names:
            print(name, file=class_file)

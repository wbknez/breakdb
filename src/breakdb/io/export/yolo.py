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

from breakdb.io.export import DatabaseEntryExporter, make_directory, \
    export_image, ExportEntryFormatError
from breakdb.io.image import transform_coordinate_collection


class YOLODatabaseEntryExporter(DatabaseEntryExporter):
    """
    Represents a mechanism to export a single entry of a collated DICOM
    database to the format used by a PyTorch YOLOv3 algorithm.
    """

    def __init__(self):
        super().__init__()

    def create_directory_structure(self, base_dir, force=False):
        annotation_dir = os.path.join(base_dir, "labels")
        image_dir = os.path.join(base_dir, "images")

        make_directory(base_dir, force)
        make_directory(annotation_dir, force)
        make_directory(image_dir, force)

        return annotation_dir, image_dir, base_dir

    def export(self, entry, base_dir, target_width=None, target_height=None,
               ignore_scaling=False, ignore_windowing=True,
               keep_aspect_ratio=True, no_upscale=False, skip_broken=False):
        logger = logging.getLogger(__name__)

        ds, name = entry

        try:
            annotation_path = os.path.join(base_dir, "labels", name) + ".txt"
            image_path = os.path.join(base_dir, "images", name) + ".jpg"

            logger.info("Exporting database entry: {}.", name)
            logger.debug("Exporting image for: {} to: {}.", name, image_path)

            dims, transform = export_image(ds, image_path, target_width,
                                           target_height, ignore_scaling,
                                           ignore_windowing, keep_aspect_ratio,
                                           no_upscale)

            if ds.Annotation:
                logger.debug("Exporting annotations for: {} to: {}.", name,
                             annotation_path)

                ds.Annotation = transform_coordinate_collection(ds.Annotation,
                                                                transform[0],
                                                                transform[1])
                txts = create_annotations(int(ds.Classification), ds.Annotation,
                                          dims[0], dims[1])

                with open(annotation_path, "w") as f:
                    for txt in txts:
                        print(txt, file=f)
            else:
                logger.debug("No annotations to export for: {}.", name)

            write_auxiliary_files(base_dir, ["negative", "positive"])

            return annotation_path, int(ds.Classification)
        except Exception as ex:
            if skip_broken:
                logger.warning("Could not export database entry: {}.", name)
                logger.warning("  Reason: {}.", ex)

                return ()
            else:
                raise ExportEntryFormatError(name, "YOLOv3") from ex


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

"""
Contains classes and functions pertaining to the creation of Pascal VOC
datasets from a collated DICOM database.
"""
import os


def create_bounding_box(annot):
    """

    :param annot:
    :return:
    """
    pass


def create_annotation(ds, width=None, height=None,
                      ignore_scaling=False, ignore_windowing=False):
    """

    :param ds:
    :param width:
    :param height:
    :param ignore_scaling:
    :param ignore_windowing:
    :return:
    """
    pass


def create_directory_structure(dir_path):
    """
    Creates the standard directory structure expected for a Pascal VOC dataset.

    :param dir_path: The directory in which to create the directory structure.
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    os.mkdir(os.path.join(dir_path, "Annotations"))
    os.mkdir(os.path.join(dir_path, "ImageSets"))
    os.mkdir(os.path.join(dir_path, "ImageSets/Main"))

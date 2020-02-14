"""
Contains classes and functions pertaining to the creation of Pascal VOC
datasets from a collated DICOM database.
"""
import os
from xml.etree.ElementTree import Element


def create_annotation(file_path, ):
    """

    :return:
    """
    pass


def create_bounding_box(coords):
    """

    :param coords: The DICOM annotation as a list of single coordinates.
    :return:
    """
    x = [value for value in coords[0::2]]
    y = [value for value in coords[1::2]]

    return create_element('bndbox', children=[
        create_element('xmin', text_value=str(min(x))),
        create_element('ymin', text_value=str(min(y))),
        create_element('xmax', text_value=str(max(x))),
        create_element('ymax', text_value=str(max(y))),
    ])


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


def create_element(name, text_value=None, children=None, *args, **kwargs):
    """
    Creates a single XML tag with the associated name, text, children (if
    any), and additional arguments.

    :param name: The tag name, to use.
    :param text_value: The text, or tag value, to use.
    :param children: A collection of children to add (optional).
    :param args: Additional arguments (optional).
    :param kwargs: Additional keyword arguments (optional).
    :return: A configured XML tag.
    """
    elem = Element(name, *args, **kwargs)

    if text_value:
        elem.text = text_value

    if children:
        for child in children:
            elem.append(child)

    return elem


def create_object(name, coords):
    """

    :param name:
    :param coords:
    :return:
    """
    return create_element("object", children=[
        create_element("name", text_value=name),
        create_element("pose", text_value="Unspecified"),
        create_element("truncated", text_value="0"),
        create_element("difficult", text_value="0"),
        create_bounding_box(coords)
    ])

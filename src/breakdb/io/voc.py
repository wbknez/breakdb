"""
Contains classes and functions pertaining to the creation of Pascal VOC
datasets from a collated DICOM database.
"""
import os
from xml.etree.ElementTree import Element


def create_annotation(file_path, width, height, depth, annotations):
    """
    Creates a Pascal VOC compatible XML annotation for the specified file
    with the specified attributes (width, height, and depth) with the
    specified collection of annotations, if any.

    :param file_path: The path to an annotated image.
    :param width: The width of an annotated image.
    :param height: The height of an annotated image.
    :param depth: The depth of an annotated image.
    :param annotations: The collection of annotations (optional).
    :return:
    """
    xml = create_element("annotation", children=[
        create_element("folder",
                       text_value=os.path.basename(os.path.dirname(file_path))),
        create_element("filename", text_value=os.path.basename(file_path)),
        create_element("path", text_value=file_path),
        create_element("source", children=[
            create_element("database", text_value="Unknown")
        ]),
        create_element("size", children=[
            create_element("width", text_value=str(width)),
            create_element("height", text_value=str(height)),
            create_element("depth", text_value=str(depth))
        ]),
        create_element("segmented", text_value="0"),

    ])

    if annotations:
        obj_name = f"{os.path.basename(os.path.splitext(file_path)[0])}-"

        for index, annot in enumerate(annotations):
            xml.append(create_object(f"{obj_name}{str(index + 1)}", annot))

    return xml


def create_bounding_box(coords):
    """
    Converts the specified collection of coordinates into a Pascal VOC
    compatible bounding box.

    :param coords: The DICOM annotation as a list of single coordinates.
    :return: A Pascal VOC bounding box.
    """
    x = [value for value in coords[0::2]]
    y = [value for value in coords[1::2]]

    return create_element("bndbox", children=[
        create_element("xmin", text_value=str(min(x))),
        create_element("ymin", text_value=str(min(y))),
        create_element("xmax", text_value=str(max(x))),
        create_element("ymax", text_value=str(max(y))),
    ])


def create_directory_structure(dir_path):
    """
    Creates the standard directory structure expected for a Pascal VOC dataset.

    :param dir_path: The directory in which to create the directory structure.
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    os.mkdir(os.path.join(dir_path, "Annotations"))
    os.mkdir(os.path.join(dir_path, "Images"))
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
    Converts the specified collection of coordinates and associated
    identifier into a single Pascal VOC compatible annotation.

    :param name: The unique annotation identifier to use.
    :param coords: The DICOM annotation as a list of single coordinates.
    :return: A Pascal VOC compatible annotation.
    """
    return create_element("object", children=[
        create_element("name", text_value=name),
        create_element("pose", text_value="Unspecified"),
        create_element("truncated", text_value="0"),
        create_element("difficult", text_value="0"),
        create_bounding_box(coords)
    ])

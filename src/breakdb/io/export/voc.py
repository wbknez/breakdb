"""
Contains classes and functions pertaining to the creation of Pascal VOC
datasets from a collated DICOM database.
"""
import logging
import os
from xml.etree.ElementTree import Element, ElementTree

from breakdb.io.image import read_from_database, format_as


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
    :return: A Pascal VOC annotation.
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
    os.mkdir(os.path.join(dir_path, "JPEGImages"))
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


def convert_entry_to_voc(index, db, annotation_path, image_path,
                         resize_width=None, resize_height=None):
    """
    Converts a single entry with the specified index in the specified
    database to a Pascal VOC compatible annotation with associated image
    that is stored in the specified path.

    :param index: The (row) index to use.
    :param db: The database to search.
    :param annotation_path: The Pascal VOC annotation storage path.
    :param image_path: The Pascal VOC image storage path.
    :param resize_width: The width to resize the image to (optional).
    :param resize_height: The height to resize the image to (optional).
    """
    logger = logging.getLogger(__name__)

    base_name = f"{index:0{len(str(len(db)))}}"
    ds = db.iloc[index, :]
    image_path = os.path.join(image_path, base_name) + ".jpg"
    xml_path = os.path.join(annotation_path, base_name) + ".xml"

    logger.info("Exporting row: {} using base name: {}.", index, base_name)

    logger.debug("Loading image for row: {} with file name: {}.", index,
                 ds["File Path"])
    attrs, arr = read_from_database(index, db, ignore_windowing=True)
    image = format_as(attrs, arr, resize_width, resize_height)

    logger.debug("Creating VOC annotation for row: {}.", index)
    xml = create_annotation(xml_path, image.width, image.height,
                            1 if image.mode == "L" else 3, ds["Annotation"])

    logger.debug("Saving image for row: {} to: {}.", index, image_path)
    try:
        image.save(image_path)
        print("Wrote: {} successfully.", image_path)
    except Exception as ex:
        print("Could not write: " + image_path)
        print(ex)

    logger.debug("Saving VOC annotation for row: {} to: {}.", index, xml_path)
    ElementTree(xml).write(xml_path)



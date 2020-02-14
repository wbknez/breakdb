"""
Contains unit tests to ensure single database items are created correctly in a
Pascal VOC compatible format.
"""
import os
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from breakdb.io.voc import create_annotation
from tests.helpers.dataset import create_random_string
from tests.helpers.xml import match


class TestCreateAnnotation:
    """
    Test suite for :function: 'create_annotation'.
    """

    def test_create_annotation_does_not_create_annotation_if_empty(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)
        depth = np.random.choice([1, 3], 1)[0]

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        random_paths = [create_random_string(10) for _ in range(5)]
        file_path = os.path.join(*random_paths) + ".png"

        xml = create_annotation(file_path, width, height, depth, [])
        expected = Element("annotation")

        folder = SubElement(expected, 'folder')
        filename = SubElement(expected, 'filename')
        path = SubElement(expected, 'path')
        source = SubElement(expected, 'source')
        size = SubElement(expected, 'size')
        segmented = SubElement(expected, 'segmented')

        database = SubElement(source, 'database')

        width_tag = SubElement(size, 'width')
        height_tag = SubElement(size, 'height')
        depth_tag = SubElement(size, 'depth')

        folder.text = os.path.basename(os.path.dirname(file_path))
        filename.text = os.path.basename(file_path)
        path.text = file_path
        segmented.text = "0"

        database.text = "Unknown"

        width_tag.text = str(width)
        height_tag.text = str(height)
        depth_tag.text = str(depth)

        match(xml, expected)

    def test_create_annotation_creates_well_formed_xml(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)
        depth = np.random.choice([1, 3], 1)[0]

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)
        coords = [coord for coords in zip(x, y) for coord in coords]

        random_paths = [create_random_string(10) for _ in range(5)]
        file_path = os.path.join(*random_paths) + ".png"

        xml = create_annotation(file_path, width, height, depth, [coords])
        expected = Element("annotation")

        folder = SubElement(expected, 'folder')
        filename = SubElement(expected, 'filename')
        path = SubElement(expected, 'path')
        source = SubElement(expected, 'source')
        size = SubElement(expected, 'size')
        segmented = SubElement(expected, 'segmented')
        obj = SubElement(expected, 'object')

        database = SubElement(source, 'database')

        width_tag = SubElement(size, 'width')
        height_tag = SubElement(size, 'height')
        depth_tag = SubElement(size, 'depth')

        name = SubElement(obj, "name")
        pose = SubElement(obj, "pose")
        truncated = SubElement(obj, "truncated")
        difficult = SubElement(obj, "difficult")
        bndbox = SubElement(obj, "bndbox")

        x_min = SubElement(bndbox, "xmin")
        y_min = SubElement(bndbox, "ymin")
        x_max = SubElement(bndbox, "xmax")
        y_max = SubElement(bndbox, "ymax")

        folder.text = os.path.basename(os.path.dirname(file_path))
        filename.text = os.path.basename(file_path)
        path.text = file_path
        segmented.text = "0"

        database.text = "Unknown"

        width_tag.text = str(width)
        height_tag.text = str(height)
        depth_tag.text = str(depth)

        name.text = f"{os.path.basename(os.path.splitext(file_path)[0])}-1"
        pose.text = "Unspecified"
        truncated.text = "0"
        difficult.text = "0"

        x_min.text = str(np.min(x))
        y_min.text = str(np.min(y))
        x_max.text = str(np.max(x))
        y_max.text = str(np.max(y))

        match(xml, expected)

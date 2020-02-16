"""
Contains unit tests to ensure individual image annotation objects are created
correctly in a Pascal VOC compatible format.
"""
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from breakdb.io.export.voc import create_object
from tests.helpers.dataset import create_random_string
from tests.helpers.xml import match


class TestCreateBoundingBox:
    """
    Test suite for :function: "create_object".
    """

    def test_create_object_creates_well_formed_xml(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)
        coords = [coord for coords in zip(x, y) for coord in coords]

        obj_name = create_random_string(20)

        obj = create_object(obj_name, coords)
        expected = Element("object")

        name = SubElement(expected, "name")
        pose = SubElement(expected, "pose")
        truncated = SubElement(expected, "truncated")
        difficult = SubElement(expected, "difficult")
        bndbox = SubElement(expected, "bndbox")

        x_min = SubElement(bndbox, "xmin")
        y_min = SubElement(bndbox, "ymin")
        x_max = SubElement(bndbox, "xmax")
        y_max = SubElement(bndbox, "ymax")

        name.text = obj_name
        pose.text = "Unspecified"
        truncated.text = "0"
        difficult.text = "0"

        x_min.text = str(np.min(x))
        y_min.text = str(np.min(y))
        x_max.text = str(np.max(x))
        y_max.text = str(np.max(y))

        match(obj, expected)

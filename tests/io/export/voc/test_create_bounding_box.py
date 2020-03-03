"""
Contains unit tests to ensure bounding boxes are converted correctly from
a DICOM annotation to a Pascal VOC compatible format.
"""
from xml.etree.ElementTree import Element, SubElement

import numpy as np
import pytest

from breakdb.io.export.voc import VOCAnnotationExporter
from tests.helpers.xml import match


@pytest.fixture()
def exporter():
    return VOCAnnotationExporter()


class TestCreateBoundingBox:
    """
    Test suite for :function: 'create_bounding_box'.
    """

    def test_create_bounding_box_computes_extrema_correctly(self, exporter):
        coords = np.random.randint(0, 1200, 10)
        x = coords[0::2]
        y = coords[1::2]

        bndbox = exporter.create_bounding_box(coords)

        x_max = bndbox.findall('xmax')[0]
        y_max = bndbox.findall('ymax')[0]
        x_min = bndbox.findall('xmin')[0]
        y_min = bndbox.findall('ymin')[0]

        assert int(x_max.text) == np.max(x)
        assert int(y_max.text) == np.max(y)
        assert int(x_min.text) == np.min(x)
        assert int(y_min.text) == np.min(y)

    def test_create_bounding_box_creates_well_formed_xml(self, exporter):
        coords = np.random.randint(0, 1200, 10)
        x = coords[0::2]
        y = coords[1::2]

        bndbox = exporter.create_bounding_box(coords)
        expected = Element('bndbox')

        x_min = SubElement(expected, "xmin")
        y_min = SubElement(expected, "ymin")
        x_max = SubElement(expected, "xmax")
        y_max = SubElement(expected, "ymax")

        x_min.text = str(np.min(x))
        y_min.text = str(np.min(y))
        x_max.text = str(np.max(x))
        y_max.text = str(np.max(y))

        match(bndbox, expected)

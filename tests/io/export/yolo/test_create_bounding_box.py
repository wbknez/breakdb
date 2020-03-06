"""
Contains unit tests to ensure bounding boxes are converted correctly from
a DICOM annotation to a YOLO compatible format.
"""
import numpy as np

from breakdb.io.export.yolo import create_bounding_box


class TestCreateBoundingBox:
    """
    Test suite for :function: 'create_bounding_box'.
    """

    def test_create_bounding_box_scales_appropriately(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)
        coords = [coord for coords in zip(x, y) for coord in coords]

        x_max = np.max(x)
        x_min = np.min(x)
        y_max = np.max(y)
        y_min = np.min(y)

        bndbox = create_bounding_box(coords, width, height)
        expected = [
            (x_max + x_min) / (2.0 * width),
            (y_max + y_min) / (2.0 * height),
            (x_max - x_min) / width,
            (y_max - y_min) / height
        ]

        assert np.array_equal(bndbox, expected)

"""
Contains unit tests to ensure that coordinate collection transformation
works correctly.
"""
import numpy as np

from breakdb.io.image import transform_coordinate_collection


class TestTransformCoordinateCollection:
    """
    Test suite for :function: 'transform_coordinate_collection'.
    """

    def test_transform_coordinate_collection_does_nothing_if_same(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        num_annotations = np.random.randint(1, 10)
        coords = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            coords.append([coord for xy in zip(x, y) for coord in xy])

        transformed = transform_coordinate_collection(coords, width, height,
                                                      width, height)
        expected = coords

        assert transformed == expected

    def test_transform_coordinate_collection_scales_correctly(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)
        new_width = np.random.randint(100, 1920)
        new_height = np.random.randint(100, 1200)

        num_annotations = np.random.randint(1, 10)
        coords = []
        expected = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            coords.append([coord for xy in zip(x, y) for coord in xy])

            x = x.astype(np.float) * (new_width / width)
            y = y.astype(np.float) * (new_height / height)

            expected.append([coord for xy in zip(x, y) for coord in xy])

        transformed = transform_coordinate_collection(coords, width, height,
                                                      new_width, new_height)

        transformed = np.array(transformed)
        expected = np.array(expected)

        assert np.array_equal(transformed, expected)

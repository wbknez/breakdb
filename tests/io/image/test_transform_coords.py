"""
Contains unit tests to ensure that the transformation of bounding box
coordinates from one image to another after scaling is correct.
"""
import numpy as np

from breakdb.io.image import transform_coords


class TestTransformCoords:
    """
    Test suite for :function: 'transform_coords'.
    """

    def test_transform_coords_does_nothing_if_scales_are_the_same(self):
        width = np.random.randint(1, 1920)
        height = np.random.randint(1, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)
        transformed = transform_coords(coords, width, height, width, height)

        assert np.array_equal(transformed, coords)

    def test_transform_coords_applies_new_width_correctly(self):
        width = np.random.randint(1, 1920)
        height = np.random.randint(1, 1200)

        new_width = np.random.randint(1, 1920)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)
        transformed = transform_coords(coords, width, height, new_width,
                                       height)
        expected = np.array([c for xy in zip(x * (new_width / width), y)
                             for c in xy])

        assert np.array_equal(transformed, expected)

    def test_transform_coords_applies_new_height_correctly(self):
        width = np.random.randint(1, 1920)
        height = np.random.randint(1, 1200)

        new_height = np.random.randint(1, 1920)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)
        transformed = transform_coords(coords, width, height, width,
                                       new_height)
        expected = np.array([c for xy in zip(x, y * (new_height / height))
                             for c in xy])

        assert np.array_equal(transformed, expected)

    def test_transform_coords_applies_new_width_and_height_correctly(self):
        width = np.random.randint(1, 1920)
        height = np.random.randint(1, 1200)

        new_width = np.random.randint(1, 1920)
        new_height = np.random.randint(1, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)
        transformed = transform_coords(coords, width, height, new_width,
                                       new_height)
        expected = np.array([c for xy in zip(x * (new_width / width),
                                             y * (new_height / height))
                             for c in xy])

        assert np.array_equal(transformed, expected)

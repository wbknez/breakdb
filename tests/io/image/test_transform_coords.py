"""
Contains unit tests to ensure that the transformation of bounding box
coordinates from one image to another after scaling is correct.
"""
import numpy as np

from breakdb.io.image import transform_coords, compute_resize_transform


class TestTransformCoords:
    """
    Test suite for :function: 'transform_coords'.
    """

    def transform_coords_does_nothing_if_unity(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)

        origin, ratios = (0.0, 0.0), (1.0, 1.0)
        transformed = transform_coords(coords, origin, ratios)

        assert np.array_equal(transformed, coords)

    def transform_coords_downscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(10, width - 1)
        target_height = np.random.randint(10, height - 1)

        resize_width = np.random.randint(1, target_width - 1)
        resize_height = np.random.randint(1, target_height - 1)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)

        origin, ratios = compute_resize_transform(width, height,
                                                  target_width,
                                                  target_height,
                                                  resize_width, resize_height)
        transformed = transform_coords(coords, origin, ratios)
        expected = np.array([c for xy in zip(x * ratios[0] + origin[0],
                                             y * ratios[1] + origin[1])
                             for c in xy])

        assert np.array_equal(transformed, expected)

    def transform_coords_upscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 2, 3840)
        target_height = np.random.randint(height + 2, 2400)

        resize_width = np.random.randint(width + 1, target_width - 1)
        resize_height = np.random.randint(height + 1, target_height - 1)

        x = np.random.randint(0, width, 5)
        y = np.random.randint(0, height, 5)

        coords = np.array([c for xy in zip(x, y) for c in xy], np.float)

        origin, ratios = compute_resize_transform(width, height,
                                                  target_width,
                                                  target_height,
                                                  resize_width, resize_height)
        transformed = transform_coords(coords, origin, ratios)
        expected = np.array([c for xy in zip(x * ratios[0] + origin[0],
                                             y * ratios[1] + origin[1])
                             for c in xy])

        assert np.array_equal(transformed, expected)

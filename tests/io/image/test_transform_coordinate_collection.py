"""
Contains unit tests to ensure that coordinate collection transformation
works correctly.
"""
import numpy as np

from breakdb.io.image import transform_coordinate_collection, \
    compute_resize_transform


class TestTransformCoordinateCollection:
    """
    Test suite for :function: 'transform_coordinate_collection'.
    """

    def test_transform_coordinate_collection_does_nothing_if_unity(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        num_annotations = np.random.randint(1, 10)
        coords = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            coords.append([coord for xy in zip(x, y) for coord in xy])

        origin, ratios = compute_resize_transform(width, height, width,
                                                  height, width, height)
        transformed = transform_coordinate_collection(coords, origin, ratios)

        assert np.array_equal(transformed, coords)

    def test_transform_coordinate_collection_downscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(10, width - 1)
        target_height = np.random.randint(10, height - 1)

        resize_width = np.random.randint(1, target_width - 1)
        resize_height = np.random.randint(1, target_height - 1)

        num_annotations = np.random.randint(1, 10)
        coords = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            coords.append([coord for xy in zip(x, y) for coord in xy])

        origin, ratios = compute_resize_transform(width, height,
                                                  target_width,
                                                  target_height,
                                                  resize_width, resize_height)
        transformed = transform_coordinate_collection(coords, origin, ratios)
        expected = []

        for coord in coords:
            x_c = np.array(coord[0::2], np.float)
            y_c = np.array(coord[1::2], np.float)

            expected.append(
                np.array([c for xy in zip(x_c * ratios[0] + origin[0],
                                          y_c * ratios[1] + origin[1])
                          for c in xy])
            )

        assert np.array_equal(transformed, expected)

    def test_transform_coordinate_collection_upscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 1340)
        target_height = np.random.randint(height + 1, 2400)

        resize_width = np.random.randint(width + 1, target_width - 1)
        resize_height = np.random.randint(height + 1, target_height - 1)

        num_annotations = np.random.randint(1, 10)
        coords = []

        for _ in range(num_annotations):
            x = np.random.randint(0, width, 5)
            y = np.random.randint(0, height, 5)

            coords.append([coord for xy in zip(x, y) for coord in xy])

        origin, ratios = compute_resize_transform(width, height,
                                                  target_width,
                                                  target_height,
                                                  resize_width, resize_height)
        transformed = transform_coordinate_collection(coords, origin, ratios)
        expected = []

        for coord in coords:
            x_c = np.array(coord[0::2], np.float)
            y_c = np.array(coord[1::2], np.float)

            expected.append(
                np.array([c for xy in zip(x_c * ratios[0] + origin[0],
                                          y_c * ratios[1] + origin[1])
                          for c in xy])
            )

        assert np.array_equal(transformed, expected)

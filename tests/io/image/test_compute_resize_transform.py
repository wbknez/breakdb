"""
Contains unit tests to ensure that computing the transformation information
for converting coordinates from one image to its rescaled form works correctly.
"""
import numpy as np

from breakdb.io.image import compute_resize_transform


class TestComputeResizeTransform:
    """
    Test suite for :function: 'compute_resize_transform'.
    """

    def test_compute_resize_transform_does_nothing_if_dimension_is_same(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        origin, ratios = compute_resize_transform(width, height, width,
                                                  height, width, height)

        assert origin == (0.0, 0.0)
        assert ratios == (1.0, 1.0)

    def test_compute_resize_transform_downscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(10, width - 1)
        target_height = np.random.randint(10, height - 1)

        resize_width = np.random.randint(1, target_width - 1)
        resize_height = np.random.randint(1, target_height - 1)

        origin, ratios = compute_resize_transform(width, height, target_width,
                                                  target_height, resize_width,
                                                  resize_height)

        expected_origin = (
            (target_width - resize_width) / 2.0,
            (target_height - resize_height) / 2.0
        )
        expected_ratios = (resize_width / width, resize_height / height)

        assert origin == expected_origin
        assert ratios == expected_ratios

    def test_compute_resize_transform_origin_is_zero_when_resize_is_target(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width0 = np.random.randint(1, width - 1)
        target_height0 = np.random.randint(1, height - 1)

        target_width1 = np.random.randint(width + 1, 3840)
        target_height1 = np.random.randint(height + 1, 2400)

        origin0, _ = compute_resize_transform(width, height, target_width0,
                                              target_height0, target_width0,
                                              target_height0)
        origin1, _ = compute_resize_transform(width, height, target_width1,
                                              target_height1, target_width1,
                                              target_height1)

        assert origin0 == (0.0, 0.0)
        assert origin1 == (0.0, 0.0)

    def test_compute_resize_transform_upscales(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 2, 3840)
        target_height = np.random.randint(height + 2, 2400)

        resize_width = np.random.randint(width + 1, target_width - 1)
        resize_height = np.random.randint(height + 1, target_height - 1)

        origin, ratios = compute_resize_transform(width, height, target_width,
                                                  target_height, resize_width,
                                                  resize_height)

        expected_origin = (
            (target_width - resize_width) / 2.0,
            (target_height - resize_height) / 2.0
        )
        expected_ratios = (resize_width / width, resize_height / height)

        assert origin == expected_origin
        assert ratios == expected_ratios

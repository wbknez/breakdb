"""
Contains unit tests to ensure that resize proportion calculation(s) are
performed correctly in order to make sure the resize ratio is respected.
"""
import numpy as np

from breakdb.io.image import compute_resize_ratio


class TestComputeResizeRatio:
    """
    Test suite for :function: 'compute_resize_ratio'
    """

    def test_compute_resize_ratio_allows_upscaling(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 3000)
        target_height = np.random.randint(height + 1, 2400)

        ratio = compute_resize_ratio(width, height, target_width,
                                     target_height, False)
        expected = np.min([target_width / width, target_height / height])

        assert ratio == expected

    def test_compute_resize_ratio_allows_downscaling(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(1, width - 1)
        target_height = np.random.randint(1, height - 1)

        ratio = compute_resize_ratio(width, height, target_width,
                                     target_height, False)
        expected = np.min([target_width / width, target_height / height])

        assert ratio == expected

    def test_compute_resize_ratio_does_not_upscale_if_set(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = width + 1
        target_height = height + 1

        ratio = compute_resize_ratio(width, height, target_width,
                                     target_height, True)

        assert ratio == 1.0

"""

"""
import numpy as np

from breakdb.io.image import compute_resize_dimensions


class TestComputeResizeDimensions:
    """
    Test suite for :function: 'test_compute_resize_dimensions'.
    """

    def test_compute_resize_dimensions_allows_upscaling_with_no_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 3000)
        target_height = np.random.randint(height + 1, 2400)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, False, False)

        assert resize[0] == target_width
        assert resize[1] == target_height

    def test_compute_resize_dimensions_allows_upscaling_with_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 3000)
        target_height = np.random.randint(height + 1, 2400)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, True, False)

        ratio = np.min([target_width / width, target_height / height])
        expected = (
            np.min([np.floor(width * ratio), target_width]),
            np.min([np.floor(height * ratio), target_height])
        )

        assert resize == expected

    def test_compute_resize_dimensions_disallows_upscaling_with_no_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 3000)
        target_height = np.random.randint(height + 1, 2400)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, False, True)

        assert resize[0] == width
        assert resize[1] == height

    def test_compute_resize_dimensions_disallows_upscaling_with_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(width + 1, 3000)
        target_height = np.random.randint(height + 1, 2400)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, True, True)

        assert resize[0] == width
        assert resize[1] == height

    def test_compute_resize_dimensions_downscales_with_no_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(1, width - 1)
        target_height = np.random.randint(1, height - 1)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, False, True)

        assert resize[0] == target_width
        assert resize[1] == target_height

    def test_compute_resize_dimensions_downscales_with_ratio(self):
        width = np.random.randint(100, 1920)
        height = np.random.randint(100, 1200)

        target_width = np.random.randint(1, width - 1)
        target_height = np.random.randint(1, height - 1)

        resize = compute_resize_dimensions(width, height, target_width,
                                           target_height, True, False)

        ratio = np.min([target_width / width, target_height / height])
        expected = (
            np.min([np.floor(width * ratio), target_width]),
            np.min([np.floor(height * ratio), target_height])
        )

        assert resize == expected

    def test_compute_resize_dimensions_has_upscale_bound_with_no_ratio(self):
        width = np.random.randint(100, 1920)

        target_width = (width + 1) * 2

        resize = compute_resize_dimensions(width, width, target_width,
                                           target_width, False, True)

        assert resize[0] == width
        assert resize[1] == width

"""
Contains unit tests to ensure that the normalization of images - usually
grayscale - works correctly.
"""
import numpy as np

from breakdb.io.image import normalize


class TestNormalize:
    """
    Test suite for :function: 'normalize'.
    """

    def test_normalize_forces_positive_interval_with_negative_data(self):
        arr = np.random.rand(1000) * (-1500 - -100)
        result = normalize(arr)

        assert result.min() == 0.0
        assert result.max() == 255.0

    def test_normalize_forces_positive_interval_with_mixed_data(self):
        arr = np.random.rand(1000) * (1000 - -100) - 100
        result = normalize(arr)

        assert result.min() == 0.0
        assert result.max() == 255.0

    def test_normalize_forces_positive_interval_with_positive_data(self):
        arr = np.random.rand(1000) * (1500 - 50)
        result = normalize(arr)

        assert result.min() == 0.0
        assert result.max() == 255.0

    def test_normalize_is_zero_with_all_zeros(self):
        arr = np.zeros(1000)
        result = normalize(arr)

        assert np.array_equal(result, np.zeros(1000, np.float))

    def test_normalize_is_correct_with_mixed_data(self):
        arr = np.random.rand(1000) * (1240 - -100)
        result = normalize(arr)

        arr -= arr.min()
        arr /= arr.max()
        arr *= 255.0

        assert result.min() == 0.0
        assert result.max() == 255.0
        assert np.array_equal(result, arr)

    def test_normalize_is_correct_with_negative_data(self):
        arr = np.random.rand(1000) * (1500 - 50)
        result = normalize(arr)

        arr -= arr.min()
        arr /= arr.max()
        arr *= 255.0

        assert result.min() == 0.0
        assert result.max() == 255.0
        assert np.array_equal(result, arr)

    def test_normalize_is_correct_with_positive_data(self):
        arr = np.random.rand(1000) * (1500 - 50)
        result = normalize(arr)

        arr -= arr.min()
        arr /= arr.max()
        arr *= 255.0

        assert result.min() == 0.0
        assert result.max() == 255.0
        assert np.array_equal(result, arr)
